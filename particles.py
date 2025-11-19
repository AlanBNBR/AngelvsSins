import pygame
import random

class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, size_range=(4, 8), color_base=(0, 255, 255), lifetime_range=(200, 400), speed_range=(0.5, 1.5)):
        super().__init__(groups)
        
        self.obstacle_sprites = obstacle_sprites
        
        size = random.randint(size_range[0], size_range[1])
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        
        r = color_base[0]
        g = color_base[1]
        b = color_base[2]
        
        initial_alpha = random.randint(200, 255)
        self.color = pygame.Color(r, g, b, initial_alpha)
        
        self.image.fill(self.color)
        self.rect = self.image.get_rect(center=pos)
        
        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        self.speed = random.uniform(speed_range[0], speed_range[1])
        
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = random.randint(lifetime_range[0], lifetime_range[1])
        
    def update(self):
        self.pos += self.direction * self.speed
        self.rect.center = round(self.pos.x), round(self.pos.y)
        
        # Colisão com paredes (Partícula morre se bater)
        if pygame.sprite.spritecollide(self, self.obstacle_sprites, False):
            self.kill()
            return
        
        current_time = pygame.time.get_ticks()
        time_elapsed = current_time - self.spawn_time
        
        if time_elapsed > self.lifetime:
            self.kill()
        else:
            alpha = max(0, self.color.a - (time_elapsed * self.color.a // self.lifetime))
            new_image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            new_image.fill((self.color.r, self.color.g, self.color.b, alpha))
            self.image = new_image