import pygame
import math
import random
from settings import *
from particles import Particle

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, angle, groups, obstacle_sprites, speed, lifetime, color, damage): 
        super().__init__(groups)
        
        self.original_image = pygame.Surface((10, 5))
        self.original_image.fill(color)
        self.color = color
        
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=pos)
        
        self.hitbox = self.rect.copy() 
        
        self.obstacle_sprites = obstacle_sprites 
        self.damage = damage
        
        rad_angle = math.radians(angle)
        self.direction = pygame.math.Vector2(math.cos(rad_angle), -math.sin(rad_angle))
        
        self.speed = speed
        self.lifetime = lifetime
        self.pos = pygame.math.Vector2(self.rect.center)
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        self.pos += self.direction * self.speed
        self.rect.center = round(self.pos.x), round(self.pos.y)
        self.hitbox.center = self.rect.center 
        
        # Rastro da bala
        if random.randint(0, 2) == 0:
            visual_groups = [g for g in self.groups() if hasattr(g, 'custom_draw')]
            if visual_groups:
                Particle(self.rect.center, visual_groups, self.obstacle_sprites,
                         size_range=(2, 4), color_base=self.color, 
                         lifetime_range=(100, 250), speed_range=(0, 0.5))

        # Colisão com paredes
        if pygame.sprite.spritecollideany(self, self.obstacle_sprites):
            self.kill() 
        
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill() 
        
        if self.rect.centerx < 0 or self.rect.centerx > MAP_WIDTH * TILE_SIZE or \
           self.rect.centery < 0 or self.rect.centery > MAP_HEIGHT * TILE_SIZE:
           self.kill()

# --- NOVA CLASSE QUE ESTAVA FALTANDO ---
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, pos, angle, groups, obstacle_sprites, speed=6, damage=1):
        super().__init__(groups)
        self.image = pygame.Surface((12, 12))
        self.image.fill(ENEMY_BULLET_COLOR) # Pega a cor do settings
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(-2, -2)
        
        self.obstacle_sprites = obstacle_sprites
        self.speed = speed
        self.damage = damage
        
        rad_angle = math.radians(angle)
        self.direction = pygame.math.Vector2(math.cos(rad_angle), -math.sin(rad_angle))
        self.pos = pygame.math.Vector2(self.rect.center)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 3000 # 3 segundos

    def update(self):
        self.pos += self.direction * self.speed
        self.rect.center = round(self.pos.x), round(self.pos.y)
        self.hitbox.center = self.rect.center

        # Colisão com paredes
        if pygame.sprite.spritecollideany(self, self.obstacle_sprites):
            self.kill()
            
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()