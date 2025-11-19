# main.py
import pygame
import sys
import random
import math 
import copy 
import os
import logging
from settings import *
from player import Player
from projectile import Bullet, EnemyBullet
from enemy import Enemy, Boss
from tile import Tile, Lava
from map_data import MapGenerator
from hud import HUD
from menu import Menu
from database import Database

# CONFIG DO LOGGING
logging.basicConfig(
    filename='error.log', 
    level=logging.ERROR, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# -------------------------------------------------------------
# FUNÇÃO DE COLISÃO
# -------------------------------------------------------------
def collide_hitbox(sprite1, sprite2):
    r1 = sprite1.hitbox if hasattr(sprite1, 'hitbox') else sprite1.rect
    r2 = sprite2.hitbox if hasattr(sprite2, 'hitbox') else sprite2.rect
    return r1.colliderect(r2)

# -------------------------------------------------------------
# CÂMERA
# -------------------------------------------------------------
class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.grid_map = {} 

    def add_static(self, sprite, col, row):
        self.grid_map[(col, row)] = sprite

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height
        self.display_surface.fill(FLOOR_BG_COLOR)
        
        padding = 6
        start_col = int(self.offset.x // TILE_SIZE) - padding
        end_col = int((self.offset.x + WIDTH) // TILE_SIZE) + padding
        start_row = int(self.offset.y // TILE_SIZE) - padding
        end_row = int((self.offset.y + HEIGHT) // TILE_SIZE) + padding
        
        sprites_to_draw = []
        margin = 1500 
        # Adiciona sprites dinâmicos (inimigos, player, balas)
        for sprite in self.sprites():
            if -margin < sprite.rect.centerx - player.rect.centerx < WIDTH + margin and \
               -margin < sprite.rect.centery - player.rect.centery < HEIGHT + margin:
                sprites_to_draw.append(sprite)

        # Adiciona sprites estáticos (paredes, lava) baseados na grade visível
        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                sprite = self.grid_map.get((col, row))
                if sprite:
                    sprites_to_draw.append(sprite)

        # Desenha ordenado pelo Y (efeito de profundidade)
        for sprite in sorted(sprites_to_draw, key=lambda s: s.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

# -------------------------------------------------------------
# CLASSE DO JOGO
# -------------------------------------------------------------
class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Angel vs Sins')
        self.clock = pygame.time.Clock()
        pygame.mouse.set_visible(False) 
        
        self.game_state = 'menu' 
        self.menu = Menu(self.screen)
        
        # --- DATABASE SETUP ---
        self.db = Database() # Inicializa banco de dados
        self.player_name = "" # Armazena o nome digitado
        
        # --- AUDIO SETUP ---
        self.current_music_vol = MUSIC_VOLUME 
        self.current_sfx_vol = SFX_VOLUME
        pygame.mixer.music.set_volume(self.current_music_vol)
        
        self.music_tracks = {
            'menu': 'audio/menu.mp3', 
            'game': ['audio/game2.mp3', 'audio/game1.mp3'],
            'boss': 'audio/boss.ogg'
        }
        self.play_music('menu', force_start=True)
        self.base_enemy_data = copy.deepcopy(ENEMIES_DATA)
        self.max_enemies = MAX_ENEMIES
        self.spawn_rate = ENEMY_SPAWN_RATE

        self.visible_sprites = CameraGroup()        
        self.obstacle_sprites = pygame.sprite.Group() 
        self.lava_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()   
        self.enemy_sprites = pygame.sprite.Group()    
        self.movement_obstacles = pygame.sprite.Group()
        self.enemy_bullet_sprites = pygame.sprite.Group() 

        self.hud = HUD(self.screen)
        self.last_spawn_time = 0
        self.valid_tiles = [] 
        self.crosshair_angle = 0
        
        self.boss_fight_active = False
        self.warning_timer = 0

    def play_music(self, track_type, force_start=False):
        try:
            if track_type == 'menu':
                if force_start or not pygame.mixer.music.get_busy():
                    pygame.mixer.music.load(self.music_tracks['menu'])
                    pygame.mixer.music.set_volume(self.current_music_vol)
                    pygame.mixer.music.play(-1, fade_ms=1000)
            
            elif track_type == 'game':
                chosen = random.choice(self.music_tracks['game'])
                pygame.mixer.music.load(chosen)
                pygame.mixer.music.set_volume(self.current_music_vol)
                pygame.mixer.music.play(-1, fade_ms=500)
            
            elif track_type == 'boss':
                # Toca a música do boss
                if os.path.exists(self.music_tracks['boss']):
                    pygame.mixer.music.load(self.music_tracks['boss'])
                    pygame.mixer.music.set_volume(self.current_music_vol)
                    pygame.mixer.music.play(-1, fade_ms=100)
                else:
                    print("AVISO: Arquivo audio/boss.mp3 não encontrado.")
                
        except pygame.error as e:
            print(f"Erro no mixer: {e}")

    def apply_difficulty(self, difficulty):
        global ENEMIES_DATA
        ENEMIES_DATA = copy.deepcopy(self.base_enemy_data)
        
        if difficulty == 'EASY':
            print("Dificuldade: FÁCIL")
            for enemy in ENEMIES_DATA:
                ENEMIES_DATA[enemy]['health'] *= 0.6
                ENEMIES_DATA[enemy]['speed'] *= 0.8
        elif difficulty == 'HARD':
            print("Dificuldade: DIFÍCIL")
            for enemy in ENEMIES_DATA:
                ENEMIES_DATA[enemy]['health'] *= 1.8
                ENEMIES_DATA[enemy]['speed'] *= 1.3

    def setup_map(self):
        self.boss_fight_active = False
        self.visible_sprites.empty()
        self.obstacle_sprites.empty()
        self.lava_sprites.empty()
        self.bullet_sprites.empty()
        self.enemy_sprites.empty()
        self.movement_obstacles.empty()
        self.enemy_bullet_sprites.empty()
        self.visible_sprites.grid_map = {}

        generator = MapGenerator()
        generated_map, self.valid_tiles = generator.get_map() 

        player_x, player_y = 0, 0
        
        for row_index, row_list in enumerate(generated_map): 
            for col_index, tile_type in enumerate(row_list): 
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                
                if tile_type == 'W':
                    wall = Tile((x, y), [self.obstacle_sprites], generated_map, row_index, col_index)
                    self.visible_sprites.add_static(wall, col_index, row_index)
                elif tile_type == 'L':
                    lava = Lava((x, y), [self.lava_sprites], generated_map, row_index, col_index)
                    self.visible_sprites.add_static(lava, col_index, row_index)
                elif tile_type == 'P':
                    player_x, player_y = x, y
        
        self.movement_obstacles.add(self.obstacle_sprites)
        self.movement_obstacles.add(self.lava_sprites)

        self.player = Player(
            (player_x, player_y), 
            [self.visible_sprites], 
            self.movement_obstacles, 
            self.create_bullet, 
            self.visible_sprites
        )
        
        self.spawn_horde(5)
        self.hud.score = 0

    def start_boss_fight(self):
        print("--- ATENÇÃO: LÚCIFER DESPERTOU ---")
        self.boss_fight_active = True
        self.warning_timer = pygame.time.get_ticks()
        
        self.enemy_sprites.empty()
        self.bullet_sprites.empty()
        self.enemy_bullet_sprites.empty()
        
        self.visible_sprites.empty()
        self.obstacle_sprites.empty()
        self.lava_sprites.empty()
        self.movement_obstacles.empty()
        self.visible_sprites.grid_map = {}
        
        generator = MapGenerator()
        generated_map, self.valid_tiles, boss_pos_tile = generator.generate_arena()
        
        player_pos_pixel = (0,0)
        boss_pos_pixel = (boss_pos_tile[0] * TILE_SIZE, boss_pos_tile[1] * TILE_SIZE)

        for row_index, row_list in enumerate(generated_map): 
            for col_index, tile_type in enumerate(row_list): 
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                if tile_type == 'W':
                    wall = Tile((x, y), [self.obstacle_sprites], generated_map, row_index, col_index)
                    self.visible_sprites.add_static(wall, col_index, row_index)
                elif tile_type == 'P':
                    player_pos_pixel = (x, y)

        self.movement_obstacles.add(self.obstacle_sprites)
        
        self.player.rect.topleft = player_pos_pixel
        self.player.hitbox.center = self.player.rect.center
        self.player.pos = pygame.math.Vector2(self.player.rect.center)
        self.visible_sprites.add(self.player)

        Boss(boss_pos_pixel, 
             [self.visible_sprites, self.enemy_sprites], 
             self.player, 
             self.enemy_sprites, 
             self.movement_obstacles, 
             self.spawn_specific_enemy, 
             self.hud,
             self.create_enemy_bullet)

    def create_bullet(self, pos, angle, speed, lifetime, color, damage):
        Bullet(pos, angle, [self.visible_sprites, self.bullet_sprites], self.obstacle_sprites, speed, lifetime, color, damage) 

    def create_enemy_bullet(self, pos, angle, speed, damage):
        EnemyBullet(pos, angle, [self.visible_sprites, self.enemy_bullet_sprites], self.obstacle_sprites, speed, damage)

    def spawn_specific_enemy(self, pos, enemy_name):
        if len(self.enemy_sprites) < self.max_enemies + 10: 
            Enemy(pos, [self.visible_sprites, self.enemy_sprites], self.player, self.enemy_sprites, self.movement_obstacles, enemy_name, self.spawn_specific_enemy, self.hud)

    def enemy_spawner(self):
        current_time = pygame.time.get_ticks()
        if len(self.enemy_sprites) < self.max_enemies and current_time - self.last_spawn_time > self.spawn_rate:
            self.last_spawn_time = current_time
            self.spawn_horde(1)

    def spawn_horde(self, amount):
        spawned_count = 0
        attempts = 0 
        camera_x = self.visible_sprites.offset.x
        camera_y = self.visible_sprites.offset.y
        screen_rect = pygame.Rect(camera_x, camera_y, WIDTH, HEIGHT)
        safe_rect = screen_rect.inflate(1000, 1000)
        
        enemy_types = [e for e in ENEMIES_DATA.keys() if e != 'minion' and e != 'lucifer']
        enemy_weights = [ENEMIES_DATA[e]['weight'] for e in enemy_types]
        
        while spawned_count < amount and attempts < 100:
            attempts += 1
            if not self.valid_tiles: break
            tile_pos = random.choice(self.valid_tiles)
            pixel_x = tile_pos[0] * TILE_SIZE + TILE_SIZE // 2
            pixel_y = tile_pos[1] * TILE_SIZE + TILE_SIZE // 2
            pixel_pos = (pixel_x, pixel_y)
            
            if safe_rect.collidepoint(pixel_pos): continue 
            dist_vec = pygame.math.Vector2(pixel_pos) - pygame.math.Vector2(self.player.rect.center)
            
            if dist_vec.magnitude() < SPAWN_RADIUS_MAX:
                chosen_enemy = random.choices(enemy_types, weights=enemy_weights, k=1)[0]
                Enemy(pixel_pos, [self.visible_sprites, self.enemy_sprites], self.player, self.enemy_sprites, self.movement_obstacles, chosen_enemy, self.spawn_specific_enemy, self.hud)
                spawned_count += 1

    def draw_crosshair(self):
        mx, my = pygame.mouse.get_pos()
        self.crosshair_angle += 2 
        if self.crosshair_angle >= 360: self.crosshair_angle -= 360
        size = 15
        color = (255, 50, 50)
        thickness = 3
        surf = pygame.Surface((size * 2 + 10, size * 2 + 10), pygame.SRCALPHA)
        center = (surf.get_width() // 2, surf.get_height() // 2)
        pygame.draw.line(surf, color, (center[0], center[1] - size), (center[0], center[1] + size), thickness)
        pygame.draw.line(surf, color, (center[0] - size, center[1]), (center[0] + size, center[1]), thickness)
        pygame.draw.circle(surf, (255, 255, 255), center, 2)
        rotated_surf = pygame.transform.rotate(surf, self.crosshair_angle)
        rect = rotated_surf.get_rect(center=(mx, my))
        self.screen.blit(rotated_surf, rect)

    def run(self):
        while True:
            import settings
            settings.MUSIC_VOLUME = self.current_music_vol
            settings.SFX_VOLUME = self.current_sfx_vol
            pygame.mixer.music.set_volume(self.current_music_vol)

            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                
                # --- LÓGICA DE DIGITAÇÃO DE NOME ---
                if self.game_state == 'name_input':
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            # Salva score e vai pro leaderboard
                            final_name = self.player_name if self.player_name else "UNKNOWN"
                            self.db.add_score(final_name, self.hud.score)
                            self.player_name = "" # Reseta
                            self.game_state = 'leaderboard' # Mostra o placar
                        elif event.key == pygame.K_BACKSPACE:
                            self.player_name = self.player_name[:-1]
                        else:
                            # Limita tamanho do nome a 10 caracteres
                            if len(self.player_name) < 10 and event.unicode.isprintable():
                                self.player_name += event.unicode

                elif event.type == pygame.KEYDOWN:
                    # MENU PRINCIPAL
                    if self.game_state == 'menu':
                        if event.key == pygame.K_UP:
                            self.menu.main_index = (self.menu.main_index - 1) % len(self.menu.main_options)
                        elif event.key == pygame.K_DOWN:
                            self.menu.main_index = (self.menu.main_index + 1) % len(self.menu.main_options)
                        elif event.key == pygame.K_RETURN:
                            choice = self.menu.main_options[self.menu.main_index]
                            if choice == 'PLAY': self.game_state = 'difficulty_select'
                            elif choice == 'LEADERBOARD': self.game_state = 'leaderboard' # <--- Novo
                            elif choice == 'SETTINGS': self.game_state = 'settings'
                            elif choice == 'QUIT': pygame.quit(); sys.exit()

                    # LEADERBOARD (Botão para voltar)
                    elif self.game_state == 'leaderboard':
                         if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                             self.game_state = 'menu'

                    # SETTINGS
                    elif self.game_state == 'settings':
                        if event.key == pygame.K_UP:
                            self.menu.settings_index = (self.menu.settings_index - 1) % len(self.menu.settings_options)
                        elif event.key == pygame.K_DOWN:
                            self.menu.settings_index = (self.menu.settings_index + 1) % len(self.menu.settings_options)
                        elif event.key == pygame.K_LEFT:
                            option = self.menu.settings_options[self.menu.settings_index]
                            if option == 'MUSIC': self.current_music_vol = max(0.0, round(self.current_music_vol - 0.1, 1))
                            elif option == 'SFX': self.current_sfx_vol = max(0.0, round(self.current_sfx_vol - 0.1, 1))
                        elif event.key == pygame.K_RIGHT:
                            option = self.menu.settings_options[self.menu.settings_index]
                            if option == 'MUSIC': self.current_music_vol = min(1.0, round(self.current_music_vol + 0.1, 1))
                            elif option == 'SFX': self.current_sfx_vol = min(1.0, round(self.current_sfx_vol + 0.1, 1))
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                            self.game_state = 'menu'

                    # DIFFICULTY
                    elif self.game_state == 'difficulty_select':
                        # ... (Lógica igual) ...
                        if event.key == pygame.K_UP:
                            self.menu.diff_index = (self.menu.diff_index - 1) % len(self.menu.difficulties)
                        elif event.key == pygame.K_DOWN:
                            self.menu.diff_index = (self.menu.diff_index + 1) % len(self.menu.difficulties)
                        elif event.key == pygame.K_RETURN:
                            chosen_diff = self.menu.difficulties[self.menu.diff_index]
                            self.apply_difficulty(chosen_diff)
                            self.setup_map() 
                            self.game_state = 'playing'
                            self.play_music('game')
                        elif event.key == pygame.K_ESCAPE:
                            self.game_state = 'menu'

                    # PLAYING
                    elif self.game_state == 'playing':
                        if event.key == pygame.K_RETURN: 
                            if not self.player.alive: 
                                # MUDANÇA: Se morreu e apertou Enter, vai para digitar nome
                                self.player_name = ""
                                self.game_state = 'name_input' 
                                self.play_music('menu') # Música volta pro menu
                        if event.key == pygame.K_ESCAPE: 
                            self.game_state = 'menu'
                            self.play_music('menu')
                    
                    # VICTORY
                    elif self.game_state == 'victory':
                        if event.key == pygame.K_RETURN:
                            # MUDANÇA: Se venceu e apertou Enter, vai para digitar nome
                            self.player_name = ""
                            self.game_state = 'name_input'
                            self.play_music('menu')

            # DRAW & UPDATE
            if self.game_state == 'menu':
                self.menu.run('menu')
            elif self.game_state == 'settings':
                self.menu.run('settings', self.current_music_vol, self.current_sfx_vol)
            elif self.game_state == 'difficulty_select':
                self.menu.run('difficulty_select')
            elif self.game_state == 'leaderboard':
                # Busca scores atualizados
                top_scores = self.db.get_top_scores()
                self.menu.run('leaderboard', scores=top_scores)
            elif self.game_state == 'name_input':
                self.menu.run('name_input', current_name=self.player_name)
            elif self.game_state == 'playing':
                self.visible_sprites.update()
                self.enemy_bullet_sprites.update()

                # TRIGGER DA BOSS FIGHT
                if self.hud.score >= BOSS_TRIGGER_SCORE and not self.boss_fight_active:
                    self.start_boss_fight()
                    self.play_music('boss')

                if self.player.alive:
                    if not self.boss_fight_active:
                        self.enemy_spawner()
                    
                    # Colisões
                    hits = pygame.sprite.groupcollide(self.bullet_sprites, self.enemy_sprites, True, False, collided=collide_hitbox)
                    for bullet, hit_enemies in hits.items():
                        for enemy in hit_enemies:
                            enemy.take_damage(bullet.damage)
                            if enemy.health <= 0:
                                enemy.kill()
                                self.hud.add_score(enemy.stats['points'])
                                if enemy.enemy_name == 'lucifer':
                                    print("LÚCIFER DERROTADO!")
                                    self.game_state = 'victory' 
                                    self.boss_fight_active = False

                    if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, collided=collide_hitbox):
                        self.player.die()

                    if pygame.sprite.spritecollide(self.player, self.enemy_bullet_sprites, True, collided=collide_hitbox):
                        self.player.die()

                self.visible_sprites.custom_draw(self.player)
                
                if self.boss_fight_active and pygame.time.get_ticks() - self.warning_timer < 4000:
                    alpha = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 255
                    warn_surf = self.hud.font.render("WARNING: LUCIFER HAS AWOKEN", True, (255, 0, 0))
                    warn_surf.set_alpha(alpha)
                    warn_rect = warn_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 200))
                    self.screen.blit(warn_surf, warn_rect)

                self.hud.draw(self.player.current_ammo, self.player.is_reloading, self.player.weapon_index, self.player.alive) 
                if self.player.alive: self.draw_crosshair()
            
            elif self.game_state == 'victory':
                self.visible_sprites.custom_draw(self.player)
                self.hud.draw_victory_screen()

            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':
    try:
        # Tenta rodar o jogo
        game = Game()
        game.run()
    except Exception as e: # Pega o crash se acontecer
        logging.critical("CRASH FATAL: Ocorreu um erro inesperado que fechou o jogo.", exc_info=True)
        print("O jogo encontrou um erro fatal. Verifique error.log.")
        pygame.quit()
        sys.exit()