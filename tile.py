# tile.py
import pygame
import random 
from settings import *

# --- CLASSE DA PAREDE (MANTENHA IGUAL) ---
class Tile(pygame.sprite.Sprite):
    _wall_base_image = None
    
    def __init__(self, pos, groups, map_data, row, col): 
        super().__init__(groups)
        
        # (Mantenha todo o código da classe Tile exatamente como estava no passo anterior...)
        # ...
        # Se você não mudou nada na parede, basta manter o código dela aqui.
        # Vou focar na classe LAVA abaixo.
        
        # ... (CÓDIGO DA CLASSE TILE OMITIDO PARA ECONOMIZAR ESPAÇO, MANTENHA O SEU) ...
        # Se precisar do Tile completo de novo, me avise, mas o foco é a Lava.
        
        # --- REPETINDO O INICIO DO TILE SÓ PRA CONTEXTO ---
        self.depth = 20 
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE + self.depth), pygame.SRCALPHA)
        front_rect = pygame.Rect(0, self.depth, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(self.image, WALL_FRONT_COLOR, front_rect)
        top_rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(self.image, WALL_TOP_COLOR, top_rect)
        pygame.draw.rect(self.image, (130, 40, 40), top_rect, 2) 
        pygame.draw.rect(self.image, WALL_OUTLINE_COLOR, top_rect, 1)
        pygame.draw.line(self.image, (30, 5, 5), (0, TILE_SIZE), (TILE_SIZE, TILE_SIZE), 4)
        self.rect = self.image.get_rect(topleft=(pos[0], pos[1] - self.depth))
        self.hitbox = pygame.Rect(pos[0], pos[1], TILE_SIZE, TILE_SIZE)


# --- CLASSE DA LAVA (ATUALIZADA COM FUSÃO) ---
class Lava(pygame.sprite.Sprite):
    def __init__(self, pos, groups, map_data, row, col): # <--- NOVOS ARGUMENTOS
        super().__init__(groups)
        
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        
        # 1. Base: Magma Líquido
        BASE_MAGMA = (255, 80, 0)
        self.image.fill(BASE_MAGMA)
        
        # Seed fixa para textura
        random.seed(pos[0] * 342 + pos[1] * 523)
        
        # 2. Textura: "Crosta" (Magma esfriando)
        CRUST_COLOR = (180, 40, 0) 
        for _ in range(6):
            w = random.randint(15, 40)
            h = random.randint(8, 20)
            x = random.randint(-10, TILE_SIZE)
            y = random.randint(-10, TILE_SIZE)
            pygame.draw.ellipse(self.image, CRUST_COLOR, (x, y, w, h))
            
        # 3. Detalhes: Bolhas de Calor
        BUBBLE_COLOR = (255, 220, 100) 
        for _ in range(4):
            bx = random.randint(4, TILE_SIZE - 4)
            by = random.randint(4, TILE_SIZE - 4)
            radius = random.randint(1, 3)
            pygame.draw.circle(self.image, BUBBLE_COLOR, (bx, by), radius)

        # 4. Profundidade Inteligente (Fusão)
        # Só desenha a borda se o vizinho NÃO for lava
        
        MAP_MAX_ROW = len(map_data) - 1
        MAP_MAX_COL = len(map_data[0]) - 1
        
        neighbors = {
            "N": row > 0 and map_data[row - 1][col] == 'L',
            "S": row < MAP_MAX_ROW and map_data[row + 1][col] == 'L',
            "E": col < MAP_MAX_COL and map_data[row][col + 1] == 'L',
            "W": col > 0 and map_data[row][col - 1] == 'L',
        }

        SHADOW_COLOR = (40, 0, 0) 
        BORDER_WIDTH = 3 # Largura da borda
        
        # Borda Norte (Topo)
        if not neighbors['N']:
            pygame.draw.rect(self.image, SHADOW_COLOR, (0, 0, TILE_SIZE, BORDER_WIDTH))
            
        # Borda Sul (Baixo)
        if not neighbors['S']:
            pygame.draw.rect(self.image, SHADOW_COLOR, (0, TILE_SIZE - BORDER_WIDTH, TILE_SIZE, BORDER_WIDTH))
            
        # Borda Oeste (Esquerda)
        if not neighbors['W']:
            pygame.draw.rect(self.image, SHADOW_COLOR, (0, 0, BORDER_WIDTH, TILE_SIZE))
            
        # Borda Leste (Direita)
        if not neighbors['E']:
            pygame.draw.rect(self.image, SHADOW_COLOR, (TILE_SIZE - BORDER_WIDTH, 0, BORDER_WIDTH, TILE_SIZE))
        
        random.seed()
        
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-20, -20)