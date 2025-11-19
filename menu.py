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
            self.input_font = pygame.font.Font('8bit.ttf', 50) # Fonte para o input
        except FileNotFoundError:
            self.title_font = pygame.font.SysFont('Arial', 80, bold=True)
            self.sub_font = pygame.font.SysFont('Arial', 30, bold=True)
            self.option_font = pygame.font.SysFont('Arial', 40, bold=True)
            self.input_font = pygame.font.SysFont('Arial', 50, bold=True)

        # --- OPÇÕES DOS MENUS ---
        # Adicionei LEADERBOARD aqui
        self.main_options = ['PLAY', 'LEADERBOARD', 'SETTINGS', 'QUIT']
        self.settings_options = ['MUSIC', 'SFX', 'BACK']
        
        # Índices de seleção
        self.main_index = 0
        self.settings_index = 0
        
        # Opções de Dificuldade
        self.difficulties = ['EASY', 'MEDIUM', 'HARD']
        self.diff_index = 1

    def draw_text_wobble(self, text, font, color, center_pos, wobble_intensity=0, rotate_speed=0, align="center"):
        current_time = pygame.time.get_ticks()
        y_offset = math.sin(current_time * 0.005) * wobble_intensity
        rotation = math.cos(current_time * 0.003) * rotate_speed
        
        shadow = font.render(text, True, (0, 0, 0))
        text_surf = font.render(text, True, color)
        
        shadow_rot = pygame.transform.rotate(shadow, rotation)
        text_rot = pygame.transform.rotate(text_surf, rotation)
        
        if align == "center":
            shadow_rect = shadow_rot.get_rect(center=(center_pos[0] + 4, center_pos[1] + y_offset + 4))
            text_rect = text_rot.get_rect(center=(center_pos[0], center_pos[1] + y_offset))
        elif align == "left":
            shadow_rect = shadow_rot.get_rect(midleft=(center_pos[0] + 4, center_pos[1] + y_offset + 4))
            text_rect = text_rot.get_rect(midleft=(center_pos[0], center_pos[1] + y_offset))
        elif align == "right":
            shadow_rect = shadow_rot.get_rect(midright=(center_pos[0] + 4, center_pos[1] + y_offset + 4))
            text_rect = text_rot.get_rect(midright=(center_pos[0], center_pos[1] + y_offset))

        self.screen.blit(shadow_rot, shadow_rect)
        self.screen.blit(text_rot, text_rect)

    def draw_list(self, options, selected_index, title_text, is_main_menu=False):
        self.screen.fill(FLOOR_BG_COLOR)
        current_time = pygame.time.get_ticks()
        
        if is_main_menu:
            r = int(200 + math.sin(current_time * 0.005) * 55)
            color_title = (r, 50, 0)
            self.draw_text_wobble(title_text, self.title_font, color_title, (self.width // 2, 150), 10, 2)
            self.draw_text_wobble("ANGEL VS SINS", self.sub_font, (150, 150, 150), (self.width // 2, 220), 2)
            start_y = 350
        else:
            self.draw_text_wobble(title_text, self.title_font, (255, 255, 255), (self.width // 2, 150), 5)
            start_y = self.height // 2
        
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

    def draw_input_name(self, current_name):
        """Tela para digitar o nome do jogador"""
        self.screen.fill(FLOOR_BG_COLOR)
        
        # Título
        self.draw_text_wobble("NEW HIGHSCORE!", self.title_font, (255, 215, 0), (self.width // 2, 150), 5)
        self.draw_text_wobble("ENTER YOUR NAME", self.sub_font, (200, 200, 200), (self.width // 2, 220), 2)
        
        # Caixa de Input
        input_box_rect = pygame.Rect(self.width // 2 - 200, self.height // 2 - 30, 400, 60)
        pygame.draw.rect(self.screen, (30, 10, 10), input_box_rect)
        pygame.draw.rect(self.screen, (255, 50, 50), input_box_rect, 3)
        
        # Nome digitado
        text_surf = self.input_font.render(current_name + "_", True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=input_box_rect.center)
        self.screen.blit(text_surf, text_rect)
        
        self.draw_text_wobble("PRESS ENTER TO SAVE", self.sub_font, (100, 100, 100), (self.width // 2, self.height - 100), 0)

    def draw_leaderboard(self, scores):
        """Desenha a lista de top scores"""
        self.screen.fill(FLOOR_BG_COLOR)
        self.draw_text_wobble("LEADERBOARD", self.title_font, (255, 215, 0), (self.width // 2, 100), 5)
        
        # Cabeçalho da tabela
        header_y = 180
        pygame.draw.line(self.screen, (100, 50, 50), (200, header_y+30), (self.width-200, header_y+30), 2)
        self.draw_text_wobble("RANK", self.sub_font, (150, 150, 150), (self.width // 2 - 300, header_y), 0, align="left")
        self.draw_text_wobble("NAME", self.sub_font, (150, 150, 150), (self.width // 2 - 50, header_y), 0, align="center")
        self.draw_text_wobble("SCORE", self.sub_font, (150, 150, 150), (self.width // 2 + 300, header_y), 0, align="right")
        
        start_y = 240
        for i, (name, score) in enumerate(scores):
            y_pos = start_y + (i * 40)
            
            # Cores para os top 3
            if i == 0: color = (255, 215, 0) # Ouro
            elif i == 1: color = (192, 192, 192) # Prata
            elif i == 2: color = (205, 127, 50) # Bronze
            else: color = (200, 200, 200) # Normal
            
            self.draw_text_wobble(f"#{i+1}", self.sub_font, color, (self.width // 2 - 300, y_pos), 0, align="left")
            self.draw_text_wobble(name, self.sub_font, color, (self.width // 2 - 50, y_pos), 0, align="center")
            self.draw_text_wobble(str(score), self.sub_font, color, (self.width // 2 + 300, y_pos), 0, align="right")
            
        self.draw_text_wobble("PRESS ESC TO BACK", self.sub_font, (100, 100, 100), (self.width // 2, self.height - 50), 0)

    def run(self, state, music_vol=0, sfx_vol=0, current_name="", scores=[]):
        if state == 'menu':
            self.draw_list(self.main_options, self.main_index, "HELL ROGUELIKE", is_main_menu=True)
        elif state == 'difficulty_select':
            self.draw_list(self.difficulties, self.diff_index, "SELECT DIFFICULTY")
        elif state == 'settings':
            self.draw_settings(music_vol, sfx_vol)
        elif state == 'name_input':
            self.draw_input_name(current_name)
        elif state == 'leaderboard':
            self.draw_leaderboard(scores)

        mx, my = pygame.mouse.get_pos()
        if state != 'name_input' and state != 'leaderboard':
            self.draw_cursor(mx, my)

    def draw_cursor(self, x, y):
        s = 20
        pygame.draw.line(self.screen, (255,0,0), (x, y-s), (x, y+s), 3)
        pygame.draw.line(self.screen, (255,0,0), (x-s, y), (x+s, y), 3)