# menu.py
import pygame
import math
from settings import *

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        
        # Fontes
        try:
            self.title_font = pygame.font.Font('8bit.ttf', 80)
            self.sub_font = pygame.font.Font('8bit.ttf', 30)
            self.option_font = pygame.font.Font('8bit.ttf', 40)
        except FileNotFoundError:
            self.title_font = pygame.font.SysFont('Arial', 80, bold=True)
            self.sub_font = pygame.font.SysFont('Arial', 30, bold=True)
            self.option_font = pygame.font.SysFont('Arial', 40, bold=True)

        # --- OPÇÕES DOS MENUS ---
        self.main_options = ['PLAY', 'SETTINGS', 'QUIT']
        self.settings_options = ['MUSIC', 'SFX', 'BACK']
        
        # Índices de seleção
        self.main_index = 0
        self.settings_index = 0
        
        # Opções de Dificuldade
        self.difficulties = ['EASY', 'MEDIUM', 'HARD']
        self.diff_index = 1

    def draw_text_wobble(self, text, font, color, center_pos, wobble_intensity=0, rotate_speed=0):
        current_time = pygame.time.get_ticks()
        y_offset = math.sin(current_time * 0.005) * wobble_intensity
        rotation = math.cos(current_time * 0.003) * rotate_speed
        
        shadow = font.render(text, True, (0, 0, 0))
        text_surf = font.render(text, True, color)
        
        shadow_rot = pygame.transform.rotate(shadow, rotation)
        text_rot = pygame.transform.rotate(text_surf, rotation)
        
        shadow_rect = shadow_rot.get_rect(center=(center_pos[0] + 4, center_pos[1] + y_offset + 4))
        text_rect = text_rot.get_rect(center=(center_pos[0], center_pos[1] + y_offset))
        
        self.screen.blit(shadow_rot, shadow_rect)
        self.screen.blit(text_rot, text_rect)

    def draw_list(self, options, selected_index, title_text, is_main_menu=False):
        self.screen.fill(FLOOR_BG_COLOR)
        current_time = pygame.time.get_ticks()
        
        # --- LÓGICA DA LOGO (RESTAURADA) ---
        if is_main_menu:
            # Cor pulsante entre Vermelho e Laranja
            r = int(200 + math.sin(current_time * 0.005) * 55)
            color_title = (r, 50, 0)
            # Desenha título grande e trêmulo
            self.draw_text_wobble(title_text, self.title_font, color_title, (self.width // 2, 150), 10, 2)
            # Subtítulo
            self.draw_text_wobble("ANGEL VS SINS", self.sub_font, (150, 150, 150), (self.width // 2, 220), 2)
            start_y = 350 # Empurra as opções mais para baixo
        else:
            # Título padrão (branco) para outros menus
            self.draw_text_wobble(title_text, self.title_font, (255, 255, 255), (self.width // 2, 150), 5)
            start_y = self.height // 2
        
        # Opções
        for index, option in enumerate(options):
            base_y = start_y + (index * 60)
            if index == selected_index:
                color = (255, 50, 50)
                text = f"> {option} <"
                wobble = 3
            else:
                color = (100, 100, 100)
                text = option
                wobble = 0
            self.draw_text_wobble(text, self.option_font, color, (self.width // 2, base_y), wobble)

    def draw_settings(self, music_vol, sfx_vol):
        self.screen.fill(FLOOR_BG_COLOR)
        self.draw_text_wobble("SETTINGS", self.title_font, (255, 255, 255), (self.width // 2, 150), 5)
        
        for index, option in enumerate(self.settings_options):
            base_y = self.height // 2 + (index * 70)
            color = (100, 100, 100)
            prefix = ""
            suffix = ""
            
            if index == self.settings_index:
                color = (255, 50, 50)
                prefix = "> "
                suffix = " <"
            
            if option == 'MUSIC':
                display_text = f"{prefix}MUSIC: {int(music_vol * 100)}%{suffix}"
            elif option == 'SFX':
                display_text = f"{prefix}SFX: {int(sfx_vol * 100)}%{suffix}"
            else:
                display_text = f"{prefix}BACK{suffix}"
                
            self.draw_text_wobble(display_text, self.option_font, color, (self.width // 2, base_y), 0)
            
        self.draw_text_wobble("ARROWS TO CHANGE / ENTER TO BACK", self.sub_font, (100, 100, 100), (self.width // 2, self.height - 50), 0)

    def run(self, state, music_vol=0, sfx_vol=0):
        if state == 'menu':
            # Passamos True para ativar a logo estilosa
            self.draw_list(self.main_options, self.main_index, "HELL ROGUELIKE", is_main_menu=True)
            
        elif state == 'difficulty_select':
            self.draw_list(self.difficulties, self.diff_index, "SELECT DIFFICULTY")
            
        elif state == 'settings':
            self.draw_settings(music_vol, sfx_vol)

        mx, my = pygame.mouse.get_pos()
        self.draw_cursor(mx, my)

    def draw_cursor(self, x, y):
        s = 20
        # Desenha a mira do menu
        pygame.draw.line(self.screen, (255,0,0), (x, y-s), (x, y+s), 3)
        pygame.draw.line(self.screen, (255,0,0), (x-s, y), (x+s, y), 3)