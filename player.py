import pygame
import math
import random
import os
import logging
from settings import * 
import settings
from particles import Particle

def draw_pixel_circle(surface, color, center, radius, alpha=255):
    if radius <= 0: return 
    temp_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(temp_surf, color, (radius, radius), radius)
    temp_surf.set_alpha(alpha)
    surface.blit(temp_surf, (center[0] - radius, center[1] - radius))

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, create_bullet_callback, camera_group):
        super().__init__(groups)
        
        self.surface_size = 96 
        self.original_image = pygame.Surface((self.surface_size, self.surface_size), pygame.SRCALPHA)
        self.image = self.original_image
        self.rect = self.image.get_rect(topleft=pos)
        
        self.hitbox = self.rect.inflate(-66, -66) 
        
        self.direction = pygame.math.Vector2()
        self.speed = PLAYER_SPEED
        self.obstacle_sprites = obstacle_sprites
        
        self.create_bullet = create_bullet_callback
        self.last_shot_time = 0
        self.angle = 0
        
        self.weapon_index = 'pistol'
        self.stats = WEAPONS_DATA[self.weapon_index]
        self.weapon_ammo = {name: data['ammo'] for name, data in WEAPONS_DATA.items()}
        
        self.is_reloading = False
        self.reload_start_time = 0
        
        self.mouse_prev = False 
        self.groups = groups 
        self.camera_group = camera_group
        self.alive = True

        # Partículas
        self.particle_emit_interval = 5 
        self.particle_emit_timer = 0
        self.trail_emit_timer = 0 
        self.trail_emit_interval = 50 
        self.core_color = (0, 255, 255) 
        self.trail_color = (0, 150, 255)

        self.pulse_value = 0
        self.visual_offset = pygame.math.Vector2(0, 0)
        self.weapon_pulse_value = 0

        # --- CARREGAMENTO DE ÁUDIOS ---
        # Estrutura: self.sounds['pistol']['shoot'] -> Sound Object
        self.sounds = {}
        self.load_weapon_sounds()

    def load_weapon_sounds(self):
        
        for weapon_name, data in WEAPONS_DATA.items():
            self.sounds[weapon_name] = {}
            actions = {
                'shoot': data.get('sfx_shoot'),
                'reload': data.get('sfx_reload'),
                'equip': data.get('sfx_equip')
            }
            
            for action, filename in actions.items():
                sound_obj = None
                if filename: 
                    if os.path.exists(filename):
                        try:
                            sound_obj = pygame.mixer.Sound(filename)
                            sound_obj.set_volume(settings.SFX_VOLUME)
                        except pygame.error as e:
                            # LOG DE ERRO DE CARREGAMENTO (Arquivo corrompido ou formato inválido)
                            logging.error(f"ASSET ERROR - Erro ao decodificar som '{filename}': {e}")
                    else:
                        # LOG DE ARQUIVO NÃO ENCONTRADO
                        logging.warning(f"ASSET MISSING - Arquivo de som não encontrado: {filename}")
                
                self.sounds[weapon_name][action] = sound_obj

    def play_weapon_sound(self, action):
        """Toca o som da arma atual com o volume global atualizado"""
        sfx = self.sounds[self.weapon_index].get(action)
        if sfx:
            sfx.set_volume(settings.SFX_VOLUME) 
            sfx.play()

    @property
    def current_ammo(self):
        return self.weapon_ammo[self.weapon_index]

    @current_ammo.setter
    def current_ammo(self, value):
        self.weapon_ammo[self.weapon_index] = value

    def input(self):
        if not self.alive: 
            self.direction = pygame.math.Vector2(0,0)
            return

        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        left_click_holding = mouse_buttons[0] 
        just_clicked = left_click_holding and not self.mouse_prev

        if not self.is_reloading:
            if keys[pygame.K_1]: self.switch_weapon('pistol')
            if keys[pygame.K_2]: self.switch_weapon('machinegun')
            if keys[pygame.K_3]: self.switch_weapon('shotgun')

        self.direction.x = 0; self.direction.y = 0
        if keys[pygame.K_w]: self.direction.y = -1
        elif keys[pygame.K_s]: self.direction.y = 1
        if keys[pygame.K_a]: self.direction.x = -1
        elif keys[pygame.K_d]: self.direction.x = 1
        
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        if keys[pygame.K_r] and not self.is_reloading and self.current_ammo < self.stats['ammo']:
            self.start_reload()

        if not self.is_reloading and self.current_ammo > 0:
            if just_clicked: self.shoot(self.stats['spam_rate'])
            elif left_click_holding: self.shoot(self.stats['rate'])

        self.mouse_prev = left_click_holding

    def switch_weapon(self, new_weapon):
        if self.weapon_index != new_weapon:
            self.weapon_index = new_weapon
            self.stats = WEAPONS_DATA[self.weapon_index]
            self.play_weapon_sound('equip') # <--- SOM DE EQUIPAR

    def start_reload(self):
        self.is_reloading = True
        self.reload_start_time = pygame.time.get_ticks()
        self.play_weapon_sound('reload') # <--- SOM DE RECARREGAR

    def update_reload(self):
        if self.is_reloading:
            current_time = pygame.time.get_ticks()
            if current_time - self.reload_start_time >= self.stats['reload_time']:
                self.current_ammo = self.stats['ammo'] 
                self.is_reloading = False

    def shoot(self, cooldown_override):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= cooldown_override:
            self.last_shot_time = current_time
            
            # <--- SOM DE TIRO
            self.play_weapon_sound('shoot')

            # Muzzle Flash
            rad_angle = math.radians(self.angle)
            barrel_offset = 50
            muzzle_x = self.hitbox.centerx + math.cos(rad_angle) * barrel_offset
            muzzle_y = self.hitbox.centery - math.sin(rad_angle) * barrel_offset
            
            for _ in range(random.randint(3, 5)):
                Particle((muzzle_x, muzzle_y), self.groups, self.obstacle_sprites,
                         size_range=(3, 6), color_base=self.stats['color'], 
                         lifetime_range=(100, 200), speed_range=(1.0, 3.0))

            for _ in range(self.stats['bullet_count']):
                spread_val = self.stats['spread']
                offset = random.uniform(-spread_val, spread_val)
                final_angle = self.angle + offset
                
                self.create_bullet(
                    self.hitbox.center, 
                    final_angle, 
                    self.stats['bullet_speed'], 
                    self.stats['bullet_lifetime'], 
                    self.stats['color'],
                    self.stats['damage']
                )
            self.current_ammo -= 1

    def rotate(self):
        if not self.alive: return
        mouse_x, mouse_y = pygame.mouse.get_pos()
        world_mouse_x = mouse_x + self.camera_group.offset.x
        world_mouse_y = mouse_y + self.camera_group.offset.y
        rel_x = world_mouse_x - self.rect.centerx
        rel_y = world_mouse_y - self.rect.centery
        self.angle = math.degrees(math.atan2(-rel_y, rel_x))

    def draw_visuals(self):
        self.image.fill((0,0,0,0)) 

        if not self.alive:
            if random.randint(0, 3) == 0:
                Particle(self.hitbox.center, self.groups, self.obstacle_sprites, size_range=(3,7), 
                         color_base=(100,100,100), lifetime_range=(300, 600), speed_range=(0.5, 1.0))
            return 

        current_time = pygame.time.get_ticks()
        float_x = math.cos(current_time * 0.003) * 3 
        float_y = math.sin(current_time * 0.005) * 4 
        self.visual_offset = pygame.math.Vector2(float_x, float_y)
        center_offset = ((self.surface_size // 2) + float_x, (self.surface_size // 2) + float_y)
        
        # Alma Pulsante
        self.pulse_value += 0.05
        base_r = int(8 + math.sin(self.pulse_value) * 1.5)

        draw_pixel_circle(self.image, (0, 200, 255), center_offset, base_r + 6, alpha=50)
        draw_pixel_circle(self.image, (100, 230, 255), center_offset, base_r + 4, alpha=100)
        draw_pixel_circle(self.image, (200, 250, 255), center_offset, base_r + 2, alpha=200)
        draw_pixel_circle(self.image, (255, 255, 255), center_offset, base_r, alpha=255)

        # Arma Holográfica
        self.weapon_pulse_value += 0.1 
        dynamic_alpha = int(185 + math.sin(self.weapon_pulse_value) * 35)
        dynamic_alpha = max(150, min(220, dynamic_alpha)) 
        c = self.stats['color']
        weapon_color = (c[0], c[1], c[2], dynamic_alpha) 
        
        if self.weapon_index == 'pistol':
            surf_w, surf_h = 20, 6
            offset_dist = 35
            weapon_surf = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
            pygame.draw.rect(weapon_surf, weapon_color, (0, 0, surf_w, surf_h), border_radius=2)
        elif self.weapon_index == 'machinegun':
            surf_w, surf_h = 32, 8
            offset_dist = 40 
            weapon_surf = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
            pygame.draw.rect(weapon_surf, weapon_color, (8, 2, 24, 4)) 
            pygame.draw.rect(weapon_surf, weapon_color, (0, 0, 10, 8), border_radius=1) 
        elif self.weapon_index == 'shotgun':
            surf_w, surf_h = 24, 12
            offset_dist = 35
            weapon_surf = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
            pygame.draw.rect(weapon_surf, weapon_color, (0, 0, 24, 4), border_radius=1) 
            pygame.draw.rect(weapon_surf, weapon_color, (0, 8, 24, 4), border_radius=1) 
            pygame.draw.rect(weapon_surf, weapon_color, (0, 2, 8, 8)) 

        rotated_weapon = pygame.transform.rotate(weapon_surf, self.angle)
        rad_angle = math.radians(self.angle)
        w_x = center_offset[0] + math.cos(rad_angle) * offset_dist - rotated_weapon.get_width() // 2
        w_y = center_offset[1] - math.sin(rad_angle) * offset_dist - rotated_weapon.get_height() // 2 
        self.image.blit(rotated_weapon, (w_x, w_y))

    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.rect.colliderect(self.hitbox):
                    if self.direction.x > 0: self.hitbox.right = sprite.rect.left
                    if self.direction.x < 0: self.hitbox.left = sprite.rect.right
        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.rect.colliderect(self.hitbox):
                    if self.direction.y > 0: self.hitbox.bottom = sprite.rect.top
                    if self.direction.y < 0: self.hitbox.top = sprite.rect.bottom

    def move(self, speed):
        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')
        self.rect.center = self.hitbox.center

    def die(self):
        self.alive = False

    def emit_particles(self):
        current_time = pygame.time.get_ticks()
        if self.alive:
            if current_time - self.particle_emit_timer > self.particle_emit_interval:
                self.particle_emit_timer = current_time
                offset_x = random.uniform(-12, 12)
                offset_y = random.uniform(-12, 12)
                spawn_x = self.hitbox.centerx + self.visual_offset.x + offset_x
                spawn_y = self.hitbox.centery + self.visual_offset.y + offset_y
                Particle((spawn_x, spawn_y), self.groups, self.obstacle_sprites, 
                         size_range=(4, 9), color_base=self.core_color, lifetime_range=(200, 400), speed_range=(0.3, 1.2))
            
            if self.direction.magnitude() > 0 and current_time - self.trail_emit_timer > self.trail_emit_interval:
                self.trail_emit_timer = current_time
                spawn_x = self.hitbox.centerx + self.visual_offset.x
                spawn_y = self.hitbox.centery + self.visual_offset.y
                Particle((spawn_x, spawn_y), self.groups, self.obstacle_sprites,
                         size_range=(3, 8), color_base=self.trail_color, lifetime_range=(300, 500), speed_range=(1.0, 2.5))

    def update(self):
        self.input()
        self.update_reload()
        self.rotate()
        self.move(self.speed)
        self.draw_visuals() 
        self.emit_particles()