# map_data.py
import random
from settings import *

class MapGenerator:
    def __init__(self):
        self.map_array = [['W' for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
        self.valid_spawn_tiles = [] 

    def generate_random_walk(self):
        x, y = MAP_WIDTH // 2, MAP_HEIGHT // 2
        self.map_array[y][x] = 'P' 
        player_spawn_index = (x, y)

        # 1. GERA O CAMINHO (Escavação)
        for _ in range(WALK_STEPS):
            direction = random.randint(0, 3)
            if direction == 0: y -= 1
            elif direction == 1: y += 1
            elif direction == 2: x -= 1
            elif direction == 3: x += 1
            
            x = max(1, min(x, MAP_WIDTH - 2))
            y = max(1, min(y, MAP_HEIGHT - 2))
            
            if self.map_array[y][x] == 'W':
                self.map_array[y][x] = ' '
                # Nota: Não adicionamos a valid_spawn_tiles aqui ainda, faremos no final
                # para garantir que não spawne inimigo na lava.

        # 2. GERA A LAVA (Poças Agrupadas Longe de Paredes)
        
        # A. Encontrar candidatos seguros (Chão que não toca em parede)
        safe_spots = []
        for row in range(1, MAP_HEIGHT - 1):
            for col in range(1, MAP_WIDTH - 1):
                if self.map_array[row][col] == ' ':
                    # Verifica os 8 vizinhos
                    is_safe = True
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if self.map_array[row+dy][col+dx] == 'W':
                                is_safe = False
                                break
                        if not is_safe: break
                    
                    # Se for seguro e não for o spawn do player, adiciona
                    if is_safe and (col, row) != player_spawn_index:
                        safe_spots.append((col, row))

        # B. Criar Poças (Blobs)
        num_lava_pools = random.randint(3, 6) # Quantidade de poças no mapa inteiro (Raro)
        
        if safe_spots:
            for _ in range(num_lava_pools):
                if not safe_spots: break
                
                # Escolhe um centro aleatório
                center = random.choice(safe_spots)
                pool_size = random.randint(4, 10) # Tamanho da poça em tiles
                
                # Algoritmo de crescimento simples
                tiles_to_turn = [center]
                current_pool_size = 0
                
                while tiles_to_turn and current_pool_size < pool_size:
                    cx, cy = tiles_to_turn.pop(0)
                    
                    # Transforma em lava se ainda for chão
                    if self.map_array[cy][cx] == ' ':
                        self.map_array[cy][cx] = 'L'
                        current_pool_size += 1
                        
                        # Tenta expandir para os vizinhos (Cima, Baixo, Esq, Dir)
                        neighbors = [(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)]
                        random.shuffle(neighbors) # Embaralha para crescer organicamente
                        
                        for nx, ny in neighbors:
                            # Só expande se o vizinho TAMBÉM for um "safe_spot" 
                            # (Isso garante que a poça não encoste na parede ao crescer)
                            if (nx, ny) in safe_spots and self.map_array[ny][nx] == ' ':
                                tiles_to_turn.append((nx, ny))

        # 3. FINALIZAÇÃO (Recalcula onde inimigos podem nascer)
        # Agora que a lava está pronta, varremos o mapa para achar onde é chão ' '
        self.valid_spawn_tiles = []
        for row in range(MAP_HEIGHT):
            for col in range(MAP_WIDTH):
                if self.map_array[row][col] == ' ' and (col, row) != player_spawn_index:
                    self.valid_spawn_tiles.append((col, row))

        self.map_array[player_spawn_index[1]][player_spawn_index[0]] = 'P'
        return self.map_array, self.valid_spawn_tiles

    def get_map(self):
        return self.generate_random_walk()
    
    def generate_arena(self):
        # Reseta o mapa para vazio
        self.map_array = [[' ' for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
        self.valid_spawn_tiles = []
        
        # Define o tamanho da Arena
        arena_size = 30
        offset_x = (MAP_WIDTH - arena_size) // 2
        offset_y = (MAP_HEIGHT - arena_size) // 2

        for row in range(MAP_HEIGHT):
            for col in range(MAP_WIDTH):
                # Cria paredes em tudo que for fora da arena
                if row < offset_y or row >= offset_y + arena_size or \
                   col < offset_x or col >= offset_x + arena_size:
                    self.map_array[row][col] = 'W'
                # Cria bordas da arena
                elif row == offset_y or row == offset_y + arena_size - 1 or \
                     col == offset_x or col == offset_x + arena_size - 1:
                    self.map_array[row][col] = 'W'
                else:
                    self.map_array[row][col] = ' ' # Chão limpo
                    self.valid_spawn_tiles.append((col, row))

        # --- MUDANÇAS AQUI ---
        
        # Player spawna no CENTRO INFERIOR da arena
        # X = Offset + Metade da arena
        # Y = Offset + Arena inteira - margem pequena
        player_pos = (offset_x + arena_size // 2, offset_y + arena_size - 6)
        self.map_array[player_pos[1]][player_pos[0]] = 'P'
        
        # Boss spawna no CENTRO SUPERIOR da arena
        # X = Offset + Metade da arena
        # Y = Offset + margem pequena (para não nascer na parede)
        boss_pos = (offset_x + arena_size // 2, offset_y + 6)
        
        return self.map_array, self.valid_spawn_tiles, boss_pos