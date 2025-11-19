import sqlite3
import os
import logging

class Database:
    def __init__(self, db_name="scores.db"):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    score INTEGER NOT NULL
                )
            ''')
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            # LOG DE ERRO DE BANCO
            logging.error(f"DATABASE ERROR - Falha ao inicializar banco de dados: {e}")

    def add_score(self, name, score):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO scores (name, score) VALUES (?, ?)', (name, score))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            # LOG DE TENTATIVA INVÁLIDA / ERRO
            logging.error(f"DATABASE ERROR - Falha ao salvar score ({name}: {score}): {e}")

    def get_top_scores(self, limit=10):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('SELECT name, score FROM scores ORDER BY score DESC LIMIT ?', (limit,))
            data = cursor.fetchall()
            conn.close()
            return data
        except sqlite3.Error as e:
            # LOG DE ERRO DE LEITURA
            logging.error(f"DATABASE ERROR - Falha ao ler placar: {e}")
            return [] # Retorna lista vazia para não travar o jogo