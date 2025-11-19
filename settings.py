import pygame

# Tela
WIDTH = 1280
HEIGHT = 720
FPS = 60
TILE_SIZE = 64

# --- PALETA DE CORES ---
BG_COLOR = (20, 5, 5)
FLOOR_BG_COLOR = (20, 5, 5)
FLOOR_GRID_COLOR = (40, 10, 10)

# Paredes
WALL_TOP_COLOR = (100, 20, 20)
WALL_FRONT_COLOR = (60, 10, 10)
WALL_OUTLINE_COLOR = (20, 0, 0)

# Entidades
PLAYER_COLOR = (0, 255, 255)
ENEMY_COLOR = (200, 0, 0)
BULLET_COLOR = (255, 255, 100)
LAVA_COLOR = (255, 80, 0)
LAVA_GLOW_COLOR = (255, 150, 0)

# --- NOVAS CORES PARA O BOSS ---
ENEMY_BULLET_COLOR = (255, 0, 50) # Vermelho Neon

# Stats
PLAYER_SPEED = 5
ENEMY_SPEED = 3

# Mapa
MAP_WIDTH = 80
MAP_HEIGHT = 80
WALK_STEPS = 15000

# --- HORDA (OTIMIZADO) ---
MAX_ENEMIES = 15        
ENEMY_SPAWN_RATE = 1000 
SPAWN_RADIUS_MIN = 1000 
SPAWN_RADIUS_MAX = 2500

# HUD
RELOAD_ICON_SIZE = 64
RELOAD_ICON_POS = (WIDTH // 2, HEIGHT - 100)

# --- BOSS SETTINGS ---
BOSS_TRIGGER_SCORE = 10

# --- ARSENAL ---
WEAPONS_DATA = {
    'pistol': {
        'bullet_speed': 20, 'bullet_lifetime': 1000, 'rate': 400, 'spam_rate': 100,
        'bullet_count': 1, 'spread': 0, 'damage': 10, 'ammo': 12, 'reload_time': 1500, 'color': (0, 255, 255),
        'sfx_shoot': 'audio/tiro de pistol.ogg',
        'sfx_reload': 'audio/pegando pistola na mao.ogg',
        'sfx_equip': 'audio/pegando pistola na mao.ogg'
    },
    'machinegun': {
        'bullet_speed': 25, 'bullet_lifetime': 900, 'rate': 100, 'spam_rate': 100,
        'bullet_count': 1, 'spread': 10, 'damage': 5, 'ammo': 30, 'reload_time': 2500, 'color': (0, 150, 255),
        'sfx_shoot': 'audio/tiro de pistol.ogg',
        'sfx_reload': 'audio/ak47 reload.ogg',
        'sfx_equip': 'audio/pegando pistola na mao.ogg'
    },
    'shotgun': {
        'bullet_speed': 18, 'bullet_lifetime': 400, 'rate': 900, 'spam_rate': 900,
        'bullet_count': 5, 'spread': 25, 'damage': 15, 'ammo': 6, 'reload_time': 2000, 'color': (200, 255, 255),
        'sfx_shoot': 'audio/balote de doze.ogg',
        'sfx_reload': 'audio/shotgun reload.ogg',
        'sfx_equip': 'audio/pegando doze na mao.ogg'
    }
}

MUSIC_VOLUME = 0.5
SFX_VOLUME = 0.5

# --- DADOS DOS INIMIGOS ---
ENEMIES_DATA = {
    'wrath':    {'health': 40, 'speed': 2.0, 'size': 32, 'color': (255, 50, 50),  'points': 20, 'weight': 25},
    'gluttony': {'health': 150, 'speed': 0.5, 'size': 64, 'color': (150, 80, 0),   'points': 50, 'weight': 15},
    'greed':    {'health': 300, 'speed': 0.8, 'size': 48, 'color': (255, 215, 0),  'points': 500, 'weight': 5},
    'lust':     {'health': 30, 'speed': 2.5, 'size': 36, 'color': (255, 100, 200), 'points': 25, 'weight': 15},
    'sloth':    {'health': 200, 'speed': 0.2, 'size': 80, 'color': (100, 150, 255), 'points': 40, 'weight': 10},
    'envy':     {'health': 80, 'speed': 1.8, 'size': 40, 'color': (50, 200, 50),   'points': 100, 'weight': 15},
    'pride':    {'health': 250, 'speed': 1.2, 'size': 100, 'color': (200, 50, 255), 'points': 150, 'weight': 10},
    'minion':   {'health': 10, 'speed': 3.0, 'size': 24, 'color': (100, 100, 100), 'points': 5, 'weight': 0},
    
    # --- DADOS DO BOSS ---
    'lucifer': {
        'health': 500, # Aumentei um pouco a vida para que ele dure mais e o jogador veja as fases
        'speed': 1.0,   # Reduzi a velocidade um pouco para não ser um torpedo constante
        'size': 120,    
        'color': (50, 0, 0), 
        'points': 10000,
        'attack_cooldown': 4000, # Aumentei o cooldown geral para ter mais pausas entre ataques
        'phase_2_threshold': 250, # Metade da vida total
        'minion_spawn_cooldown': 10000, # NOVO: Cooldown para invocar minions
        'dash_cooldown': 7000,         # NOVO: Cooldown para o ataque de Dash
        'weight': 0 
    }
}