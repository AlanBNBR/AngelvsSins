# Manual de Execução: Angel vs Sins
Este manual descreve os pré-requisitos, o processo de instalação das dependências e como executar o jogo "Angel vs Sins".
# Feito por: Alan, João Faé e Ronaldo
# 1. Pré-requisitos
Antes de iniciar, certifique-se de ter instalado em sua máquina:
Python 3.10 ou superior: Baixar Python
Nota: Durante a instalação no Windows, marque a opção "Add Python to PATH".

# 2. Estrutura de Arquivos
Para o jogo funcionar, todos os scripts .py devem estar na mesma pasta. Verifique se você possui os seguintes arquivos:
main.py (Arquivo principal)
menu.py
player.py
enemy.py
projectile.py
tile.py
map_data.py
hud.py
settings.py
particles.py
database.py
Pasta audio/: Deve conter os arquivos de som (menu.mp3, game1.mp3, tiro.ogg, etc.).
Arquivo de Fonte: 8bit.ttf (ou o jogo usará Arial padrão).
Nota: Os arquivos scores.db (Banco de Dados) e error.log (Registro de Erros) serão criados automaticamente pelo jogo na primeira execução.

# 3. Instalação das Dependências
Este projeto depende da biblioteca Pygame. As bibliotecas sqlite3, logging, os e math já são nativas do Python e não precisam de instalação.
Passo A: Criar o arquivo de requisitos (Já vem pré-instalado)
Crie um arquivo chamado requirements.txt na pasta do projeto e escreva dentro dele:
Plaintext
pygame>=2.5.0

Passo B: Instalar via Terminal
Abra o terminal (CMD ou PowerShell) na pasta do jogo e execute o comando:
Opção 1 (Usando requirements.txt):
Bash
pip install -r requirements.txt

Opção 2 (Instalação direta):
Bash
pip install pygame


# 4. Como Rodar o Jogo
Abra o terminal na pasta onde estão os arquivos.
Execute o comando:
Bash
python main.py

(Se o comando python não funcionar, tente python3 ou py).

# 5. Solução de Problemas Comuns
Erro: "Module not found: pygame"
Solução: Você não instalou a dependência. Repita o passo 3.
Erro: Jogo fecha imediatamente ou tela preta
Solução: Verifique o arquivo error.log que foi criado na pasta. Ele dirá exatamente o que falhou (provavelmente um arquivo de áudio ou imagem faltando).
Som não toca ou Volume não muda
Solução: Verifique se os arquivos de áudio estão na pasta audio/ com os nomes corretos definidos em settings.py.
Banco de Dados não salva
Solução: Verifique se a pasta tem permissão de escrita. O arquivo scores.db precisa ser criado/atualizado pelo script.

# 6. Funcionalidades do Sistema
Leaderboard: O progresso é salvo automaticamente em um banco SQLite local (scores.db).
Log de Erros: Falhas de carregamento de assets e erros críticos são salvos em error.log para facilitar a manutenção.
Controle de Volume: Ajuste música e efeitos sonoros no menu Settings.

