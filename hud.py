import pygame
import math 
from settings import *

class HUD:
    def __init__(self, screen):
        self.screen = screen
        self.score = 0
        try:
            self.font = pygame.font.Font('8bit.ttf', 24)
        except FileNotFoundError:
            self.font = pygame.font.SysFont('Arial', 24, bold=True)
            
        self.wave_speed = 0.002 
        self.wave_height = 5    
        self.tilt_amount = 3

        self.spinner_size = 64
        self.spinner_surf = pygame.Surface((self.spinner_size, self.spinner_size), pygame.SRCALPHA)
        color = BULLET_COLOR 
        rect = (2, 2, self.spinner_size-4, self.spinner_size-4)
        for i in range(0, 360, 90):
            pygame.draw.arc(self.spinner_surf, color, rect, math.radians(i), math.radians(i+60), 4)
        self.reload_angle = 0 
        self.reload_rotation_speed = -5 

    def add_score(self, amount):
        self.score += amount

    def draw_text_wobble(self, text, color, anchor_point, anchor_type, y_offset, rotation_angle):
        surf = self.font.render(text, True, color)
        shadow = self.font.render(text, True, (0, 0, 0))
        rotated_surf = pygame.transform.rotate(surf, rotation_angle)
        rotated_shadow = pygame.transform.rotate(shadow, rotation_angle)
        pos_x, pos_y = anchor_point
        rect_kwargs = {anchor_type: (pos_x, pos_y + y_offset)}
        rect = rotated_surf.get_rect(**rect_kwargs)
        shadow_rect = rotated_shadow.get_rect(**rect_kwargs)
        shadow_rect.x += 2
        shadow_rect.y += 2
        self.screen.blit(rotated_shadow, shadow_rect)
        self.screen.blit(rotated_surf, rect)

    def draw(self, current_ammo, is_reloading, weapon_name, is_alive): 
        current_time = pygame.time.get_ticks()
        y_offset = math.sin(current_time * self.wave_speed) * self.wave_height
        rotation = math.cos(current_time * self.wave_speed) * self.tilt_amount

        if not is_alive:
            self.draw_text_wobble("YOU ARE DEAD", (200, 0, 0), (WIDTH // 2, HEIGHT - 150), "center", y_offset * 2, rotation)
            self.draw_text_wobble("PRESS ENTER", (255, 255, 255), (WIDTH // 2, HEIGHT - 100), "center", y_offset, rotation)
            return 

        self.draw_text_wobble(f"WEAPON: {weapon_name.upper()}", (255, 255, 255), (WIDTH // 2, 20), "midtop", y_offset, rotation)
        self.draw_text_wobble(f"AMMO: {current_ammo}", PLAYER_COLOR, (30, HEIGHT - 30), "bottomleft", y_offset, rotation)
        self.draw_text_wobble(f"SCORE: {self.score}", BULLET_COLOR, (WIDTH - 20, 20), "topright", y_offset, rotation)

        if is_reloading:
            center_x, center_y = RELOAD_ICON_POS
            pygame.draw.rect(self.screen, (150, 50, 50), (center_x - 12, center_y - 10, 6, 20))
            pygame.draw.rect(self.screen, (150, 50, 50), (center_x - 3, center_y - 10, 6, 20))
            pygame.draw.rect(self.screen, (150, 50, 50), (center_x + 6, center_y - 10, 6, 20))
            pygame.draw.rect(self.screen, (255, 200, 50), (center_x - 12, center_y - 10, 6, 5))
            pygame.draw.rect(self.screen, (255, 200, 50), (center_x - 3, center_y - 10, 6, 5))
            pygame.draw.rect(self.screen, (255, 200, 50), (center_x + 6, center_y - 10, 6, 5))
            self.reload_angle += self.reload_rotation_speed
            if self.reload_angle >= 360: self.reload_angle -= 360
            rotated_spinner = pygame.transform.rotate(self.spinner_surf, self.reload_angle)
            spinner_rect = rotated_spinner.get_rect(center=(center_x, center_y))
            self.screen.blit(rotated_spinner, spinner_rect)

    def draw_victory_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        current_time = pygame.time.get_ticks()
        scale = 1.0 + math.sin(current_time * 0.005) * 0.1
        
        title_text = "HELL CONQUERED"
        title_surf = self.font.render(title_text, True, (255, 215, 0))
        w = int(title_surf.get_width() * 2 * scale)
        h = int(title_surf.get_height() * 2 * scale)
        scaled_surf = pygame.transform.scale(title_surf, (w, h))
        title_rect = scaled_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        
        shadow_surf = self.font.render(title_text, True, (100, 50, 0))
        scaled_shadow = pygame.transform.scale(shadow_surf, (w, h))
        shadow_rect = scaled_shadow.get_rect(center=(WIDTH // 2 + 4, HEIGHT // 2 - 46))
        
        self.screen.blit(scaled_shadow, shadow_rect)
        self.screen.blit(scaled_surf, title_rect)
        
        score_text = f"FINAL SCORE: {self.score}"
        score_surf = self.font.render(score_text, True, (255, 255, 255))
        score_rect = score_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        self.screen.blit(score_surf, score_rect)
        
        if current_time % 1000 < 500: 
            press_text = "PRESS ENTER TO RETURN"
            press_surf = self.font.render(press_text, True, (150, 150, 150))
            press_rect = press_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
            self.screen.blit(press_surf, press_rect)