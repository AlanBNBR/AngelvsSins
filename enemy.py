# enemy.py
import pygame
import math
import random 
from settings import *
from particles import Particle

class Enemy(pygame.sprite.Sprite):
    # Novos argumentos: spawn_callback e hud
    def __init__(self, pos, groups, player, all_enemies, obstacle_sprites, enemy_name, spawn_callback, hud): 
        super().__init__(groups)
        
        self.enemy_name = enemy_name
        self.stats = ENEMIES_DATA[enemy_name]
        
        # Callbacks e Referências
        self.spawn_callback = spawn_callback
        self.hud = hud
        
        # --- FÍSICA ---
        self.size = self.stats['size']
        self.speed = self.stats['speed']
        self.health = self.stats['health']
        self.color = self.stats['color']
        
        # --- VISUAL ---
        visual_padding = 50
        self.image_size = self.size + visual_padding
        self.image = pygame.Surface((self.image_size, self.image_size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)
        
        # --- COLISÃO ---
        self.hitbox = pygame.Rect(0, 0, self.size, self.size)
        self.hitbox.center = self.rect.center
        
        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = pygame.math.Vector2()
        
        self.player = player
        self.all_enemies = all_enemies
        self.obstacle_sprites = obstacle_sprites
        
        # Variáveis de IA
        self.stuck_timer = 0
        self.stuck_direction = pygame.math.Vector2()
        self.in_corner = False
        self.wander_timer = 0
        self.wander_interval = 1000
        
        # Variáveis Visuais
        self.animation_timer = random.randint(0, 1000)
        self.hit_time = 0
        self.is_hit = False
        self.particle_timer = 0
        self.rotation_angle = 0
        
        # --- VARIÁVEIS DE PERSONALIDADE ---
        # Gula (Spawn Timer)
        self.spawn_cooldown = 5000 # Gospe a cada 5s
        self.last_spawn_action = pygame.time.get_ticks()
        
        # Preguiça (Rage Mode)
        self.is_enraged = False
        self.rage_end_time = 0
        
        # Inveja (Roubo de Pontos)
        self.steal_timer = pygame.time.get_ticks()

    def take_damage(self, amount):
        self.health -= amount
        self.is_hit = True
        self.hit_time = pygame.time.get_ticks()
        
        # --- PREGUIÇA: Fica furiosa ao levar dano ---
        if self.enemy_name == 'sloth':
            self.is_enraged = True
            self.rage_end_time = pygame.time.get_ticks() + 5000 # Dura 5 segundos
            
            # Efeito visual de "acordar"
            visual_groups = [g for g in self.groups() if hasattr(g, 'custom_draw')]
            if visual_groups:
                Particle(self.rect.center, visual_groups, self.obstacle_sprites, 
                         size_range=(5,10), color_base=(255, 0, 0), speed_range=(2,4))

        # Knockback
        player_pos_vec = pygame.math.Vector2(self.player.rect.center)
        direction_vec = (self.pos - player_pos_vec)
        if direction_vec.magnitude() > 0:
            knockback_dir = direction_vec.normalize()
            self.pos += knockback_dir * 12 

    def get_pursuit_vector(self):
        enemy_vec = self.pos
        player_vec = pygame.math.Vector2(self.player.rect.center) 
        distance_vec = player_vec - enemy_vec
        if distance_vec.magnitude() > 0:
            return distance_vec.normalize()
        return pygame.math.Vector2(0, 0)

    def specific_behavior(self):
        current_time = pygame.time.get_ticks()
        
        # --- GULA: GOSPE INIMIGOS (MINIONS) ---
        if self.enemy_name == 'gluttony' and self.player.alive:
            if current_time - self.last_spawn_action > self.spawn_cooldown:
                self.last_spawn_action = current_time
                # Spawn na frente da Gula
                offset = pygame.math.Vector2(random.randint(-20, 20), random.randint(-20, 20))
                spawn_pos = self.rect.center + offset
                self.spawn_callback(spawn_pos, 'minion') # Chama a função do Game
        
        # --- INVEJA: ROUBA PONTOS ---
        if self.enemy_name == 'envy' and self.player.alive:
            if current_time - self.steal_timer > 3000: # Rouba a cada 1s
                self.steal_timer = current_time
                if self.hud.score > 0:
                    self.hud.score = max(0, self.hud.score - 2)
                    # Efeito visual negativo no HUD poderia ser adicionado aqui
                    
        # --- PREGUIÇA: CONTROLE DE RAGE ---
        if self.enemy_name == 'sloth':
            if self.is_enraged and current_time > self.rage_end_time:
                self.is_enraged = False # Volta a dormir

    def hunt_player(self):
        self.specific_behavior()

        # Greed: Passivo
        if self.enemy_name == 'greed':
            self.wander_logic()
            return
        
        # Sloth: Só persegue se estiver furiosa
        if self.enemy_name == 'sloth':
            if self.is_enraged:
                 self.direction = self.get_pursuit_vector()
            else:
                 self.wander_logic() # Dormindo/Vagando
            return
        
        # Lust: Zigue-zague
        if self.enemy_name == 'lust':
            if self.player.alive:
                base_dir = self.get_pursuit_vector()
                current_time = pygame.time.get_ticks()
                sway_amount = math.sin(current_time * 0.008) * 0.6 
                self.direction.x = base_dir.x + (base_dir.y * sway_amount)
                self.direction.y = base_dir.y - (base_dir.x * sway_amount)
                if self.direction.magnitude() > 0:
                    self.direction.normalize_ip()
            else:
                self.wander_logic()
            return
        
        # Pride: Para para se exibir
        if self.enemy_name == 'pride':
            if self.player.alive:
                current_time = pygame.time.get_ticks()
                if (current_time // 1000) % 4 == 0: 
                    self.direction = pygame.math.Vector2(0,0)
                else:
                    self.direction = self.get_pursuit_vector()
            else:
                self.wander_logic()
            return

        # Padrão (Wrath, Gluttony, Envy, Minion)
        if self.player.alive:
            if self.in_corner:
                self.stuck_timer = 60 
                random_angle = random.uniform(0, 2 * math.pi)
                self.stuck_direction.x = math.cos(random_angle)
                self.stuck_direction.y = math.sin(random_angle)
                self.in_corner = False 
            
            if self.stuck_timer > 0:
                self.direction = self.stuck_direction.copy() 
                self.stuck_timer -= 1
            else:
                self.direction = self.get_pursuit_vector()
        else:
            self.wander_logic()

    def wander_logic(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.wander_timer > self.wander_interval:
            self.wander_timer = current_time
            self.wander_interval = random.randint(1000, 3000)
            rand_x = random.uniform(-1, 1)
            rand_y = random.uniform(-1, 1)
            self.direction = pygame.math.Vector2(rand_x, rand_y)
            if self.direction.magnitude() != 0:
                self.direction = self.direction.normalize()

    def collision(self, direction):
        blocked = False 
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.rect.colliderect(self.hitbox):
                    blocked = True
                    if abs(self.direction.x) > 0.1: 
                        self.stuck_timer = 30 
                        self.stuck_direction.x = 0 
                        self.stuck_direction.y = random.choice([-1, 1]) 
                    if self.direction.x > 0: self.hitbox.right = sprite.rect.left
                    if self.direction.x < 0: self.hitbox.left = sprite.rect.right
                    self.pos.x = self.hitbox.centerx 
            return blocked
        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.rect.colliderect(self.hitbox):
                    blocked = True
                    if abs(self.direction.y) > 0.1:
                         self.stuck_timer = 30
                         self.stuck_direction.y = 0 
                         self.stuck_direction.x = random.choice([-1, 1])
                    if self.direction.y > 0: self.hitbox.bottom = sprite.rect.top
                    if self.direction.y < 0: self.hitbox.top = sprite.rect.bottom
                    self.pos.y = self.hitbox.centery
            return blocked

    def move(self):
        x_blocked = False
        y_blocked = False
        
        move_speed = self.speed
        
        # --- VELOCIDADE DINÂMICA DA PREGUIÇA ---
        if self.enemy_name == 'sloth':
            if self.is_enraged:
                move_speed = self.speed * 6.0 # Corre MUITO rápido (Speed 0.2 * 6 = 1.2, ainda lento? Ajuste settings)
                # Ajuste: No settings Sloth speed é 0.2. Vamos aumentar no rage.
                move_speed = 4.0 
            else:
                move_speed = 0.5 # Quase parado

        self.hitbox.x += self.direction.x * move_speed
        if self.collision('horizontal'): x_blocked = True
        self.hitbox.y += self.direction.y * move_speed
        if self.collision('vertical'): y_blocked = True
        
        if x_blocked and y_blocked and self.stuck_timer < 5: 
            self.in_corner = True
        
        self.rect.center = self.hitbox.center
        self.pos.x, self.pos.y = self.hitbox.center

    def check_separation(self):
        for enemy in self.all_enemies:
            if enemy != self:
                if self.hitbox.colliderect(enemy.hitbox):
                    push_direction = pygame.math.Vector2(self.hitbox.center) - pygame.math.Vector2(enemy.hitbox.center)
                    if push_direction.magnitude() > 0:
                        push_direction = push_direction.normalize()
                        self.pos += push_direction * 0.5 
                        self.hitbox.center = round(self.pos.x), round(self.pos.y)
                        self.rect.center = self.hitbox.center

    def draw_visuals(self):
        self.image.fill((0,0,0,0)) 
        
        draw_color = self.color
        if self.is_hit:
            current_time = pygame.time.get_ticks()
            if current_time - self.hit_time < 100: 
                draw_color = (255, 255, 255) 
            else:
                self.is_hit = False
        
        # Sloth Furiosa fica vermelha
        if self.enemy_name == 'sloth' and self.is_enraged:
             draw_color = (255, 50, 50)

        self.animation_timer += 1
        cx, cy = self.image_size // 2, self.image_size // 2
        center = (cx, cy)
        
        def draw_glow(radius, color, alpha):
            s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*color, alpha), (radius, radius), radius)
            self.image.blit(s, (cx - radius, cy - radius), special_flags=pygame.BLEND_RGBA_ADD)

        # 1. IRA (WRATH)
        if self.enemy_name == 'wrath':
            shake_x = random.randint(-1, 1); shake_y = random.randint(-1, 1)
            cx += shake_x; cy += shake_y
            base_size = self.size // 2
            draw_glow(base_size + 15, (255, 0, 0), 50)
            points = [(cx, cy - base_size - 5), (cx + base_size, cy), (cx, cy + base_size + 5), (cx - base_size, cy)]
            pygame.draw.polygon(self.image, draw_color, points)
            if not self.is_hit:
                pygame.draw.polygon(self.image, (50, 0, 0), points, 0) 
                pygame.draw.polygon(self.image, (255, 50, 50), points, 2) 
                pygame.draw.line(self.image, (255, 255, 255), (cx - 8, cy - 2), (cx - 2, cy + 4), 2)
                pygame.draw.line(self.image, (255, 255, 255), (cx + 8, cy - 2), (cx + 2, cy + 4), 2)

        # 2. GULA (GLUTTONY)
        elif self.enemy_name == 'gluttony':
            pulse = math.sin(self.animation_timer * 0.05) * 4
            radius = (self.size // 2) + pulse
            draw_glow(int(radius + 10), (150, 80, 0), 40)
            rect_blob = pygame.Rect(0, 0, radius*2, radius*1.8)
            rect_blob.center = (cx, cy)
            pygame.draw.ellipse(self.image, draw_color, rect_blob)
            if not self.is_hit:
                pygame.draw.ellipse(self.image, (100, 50, 20), rect_blob, 4)
                mouth_rect = pygame.Rect(0, 0, radius * 1.2, radius * 0.8)
                mouth_rect.center = (cx, cy + 5)
                pygame.draw.ellipse(self.image, (20, 0, 0), mouth_rect) 
                pygame.draw.polygon(self.image, (200, 200, 180), [(cx-10, cy-10), (cx-5, cy+5), (cx, cy-10)])
                pygame.draw.polygon(self.image, (200, 200, 180), [(cx+10, cy-10), (cx+5, cy+5), (cx, cy-10)])

        # 3. AVAREZA (GREED)
        elif self.enemy_name == 'greed':
            self.rotation_angle += 2
            diamond_size = self.size
            surf_d = pygame.Surface((diamond_size, diamond_size), pygame.SRCALPHA)
            rect_d = pygame.Rect(0, 0, diamond_size, diamond_size)
            mid = diamond_size // 2
            pts = [(mid, 0), (diamond_size, mid), (mid, diamond_size), (0, mid)]
            pygame.draw.polygon(surf_d, draw_color, pts) 
            if not self.is_hit:
                pygame.draw.polygon(surf_d, (255, 255, 200), pts, 4) 
                pygame.draw.circle(surf_d, (180, 150, 0), (mid, mid), 6)
            rotated_d = pygame.transform.rotate(surf_d, self.rotation_angle)
            r_rect = rotated_d.get_rect(center=(cx, cy))
            draw_glow(int(self.size * 0.7), (255, 215, 0), 60)
            self.image.blit(rotated_d, r_rect)

        # 4. LUXÚRIA (LUST)
        elif self.enemy_name == 'lust':
            pulse_amp = math.sin(self.animation_timer * 0.08) * 3
            base_size = self.size // 2
            draw_glow(base_size + 15, (255, 50, 200), 60)
            heart_points = [(cx, cy - base_size - pulse_amp), (cx + base_size + pulse_amp, cy - base_size // 2),
                            (cx + base_size, cy + base_size), (cx, cy + base_size + pulse_amp + 10),
                            (cx - base_size, cy + base_size), (cx - base_size - pulse_amp, cy - base_size // 2)]
            pygame.draw.polygon(self.image, draw_color, heart_points)
            if not self.is_hit:
                pygame.draw.polygon(self.image, (150, 0, 100), heart_points, 0)
                pygame.draw.polygon(self.image, (255, 150, 255), heart_points, 2) 

        # 5. PREGUIÇA (SLOTH)
        elif self.enemy_name == 'sloth':
            deform_x = math.sin(self.animation_timer * 0.02) * 5
            deform_y = math.cos(self.animation_timer * 0.015) * 5
            base_size = self.size // 2
            draw_glow(base_size + 20, (50, 100, 200), 70)
            blob_points = [(cx, cy - base_size - 10), (cx + base_size + deform_x, cy - base_size // 2),
                           (cx + base_size + deform_x, cy + base_size + deform_y), (cx, cy + base_size + 15),
                           (cx - base_size - deform_x, cy + base_size + deform_y), (cx - base_size - deform_x, cy - base_size // 2)]
            pygame.draw.polygon(self.image, draw_color, blob_points)
            if not self.is_hit:
                pygame.draw.polygon(self.image, (0, 50, 100), blob_points, 0) 
                pygame.draw.polygon(self.image, (150, 200, 255), blob_points, 3) 
                # Olhos
                eye_color = (255, 50, 50) if self.is_enraged else (200, 200, 255)
                pygame.draw.line(self.image, eye_color, (cx - 10, cy - 5 + deform_y), (cx - 2, cy - 5 + deform_y), 2)
                pygame.draw.line(self.image, eye_color, (cx + 10, cy - 5 + deform_y), (cx + 2, cy - 5 + deform_y), 2)

        # 6. INVEJA (ENVY)
        elif self.enemy_name == 'envy':
            base_size = self.size // 2
            draw_glow(base_size + 15, (0, 150, 0), 60)
            eye_radius_x = base_size + 5; eye_radius_y = base_size - 5
            pygame.draw.ellipse(self.image, draw_color, (cx - eye_radius_x, cy - eye_radius_y, eye_radius_x*2, eye_radius_y*2))
            if not self.is_hit:
                pygame.draw.ellipse(self.image, (0, 80, 0), (cx - eye_radius_x, cy - eye_radius_y, eye_radius_x*2, eye_radius_y*2), 0)
                pygame.draw.ellipse(self.image, (100, 255, 100), (cx - eye_radius_x, cy - eye_radius_y, eye_radius_x*2, eye_radius_y*2), 2)
                pupil_radius = int(base_size * 0.4)
                pygame.draw.circle(self.image, (0, 0, 0), (cx, cy), pupil_radius)

        # 7. SOBERBA (PRIDE)
        elif self.enemy_name == 'pride':
            self.rotation_angle += 1.5 
            base_size = self.size // 2
            pride_surf_size = base_size * 2 + 20
            pride_surf = pygame.Surface((pride_surf_size, pride_surf_size), pygame.SRCALPHA)
            pride_center = pride_surf_size // 2
            num_points = 6; outer_radius = base_size + 5; inner_radius = base_size - 10
            points = []
            for i in range(num_points):
                angle_outer = math.radians(i * (360 / num_points) + self.animation_timer * 0.5)
                angle_inner = math.radians(i * (360 / num_points) + (360 / (num_points * 2)) + self.animation_timer * 0.5)
                points.append((pride_center + outer_radius * math.cos(angle_outer), pride_center + outer_radius * math.sin(angle_outer)))
                points.append((pride_center + inner_radius * math.cos(angle_inner), pride_center + inner_radius * math.sin(angle_inner)))
            pygame.draw.polygon(pride_surf, draw_color, points) 
            if not self.is_hit:
                pygame.draw.polygon(pride_surf, (255, 255, 0), points, 2) 
            rotated_pride = pygame.transform.rotate(pride_surf, self.rotation_angle)
            r_rect = rotated_pride.get_rect(center=(cx, cy))
            draw_glow(base_size + 20, (180, 0, 255), 70)
            self.image.blit(rotated_pride, r_rect)

        # 8. MINION (Spawnado pela Gula)
        elif self.enemy_name == 'minion':
            radius = self.size // 2
            pygame.draw.circle(self.image, draw_color, (cx, cy), radius)
            draw_glow(radius + 5, (150, 150, 150), 50)

    def emit_particles(self):
        visual_groups = [g for g in self.groups() if hasattr(g, 'custom_draw')]
        if not visual_groups: return
        current_time = pygame.time.get_ticks()

        if self.enemy_name == 'greed':
            if current_time - self.particle_timer > 200: 
                self.particle_timer = current_time
                Particle(self.rect.center, visual_groups, self.obstacle_sprites, size_range=(2, 4), color_base=(255, 215, 0), speed_range=(0.5, 1.5))
        elif self.enemy_name == 'lust':
            if random.randint(0, 100) < 5: 
                Particle(self.rect.center, visual_groups, self.obstacle_sprites, size_range=(3, 6), color_base=(255, 100, 200), speed_range=(0.8, 1.8))
        elif self.enemy_name == 'sloth' and self.is_enraged: # Fumaça de raiva
            if random.randint(0, 100) < 10: 
                Particle(self.rect.center, visual_groups, self.obstacle_sprites, size_range=(4, 8), color_base=(100, 0, 0), speed_range=(1.0, 2.0))

    def update(self):
        self.hunt_player()
        self.check_separation()
        self.move()
        self.draw_visuals()
        self.emit_particles()

    class EnemyBullet(pygame.sprite.Sprite):
        def __init__(self, pos, angle, groups, obstacle_sprites, speed=6, damage=1):
            super().__init__(groups)
            self.image = pygame.Surface((12, 12))
            self.image.fill(ENEMY_BULLET_COLOR) # Cor definida no settings
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

# No arquivo enemy.py, substitua a classe Boss por esta versão:

class Boss(Enemy):
    def __init__(self, pos, groups, player, all_enemies, obstacle_sprites, spawn_callback, hud, create_bullet_callback):
        super().__init__(pos, groups, player, all_enemies, obstacle_sprites, 'lucifer', spawn_callback, hud)
        
        self.max_health = self.stats['health']
        self.create_bullet_callback = create_bullet_callback
        
        self.phase = 1
        self.attack_timer = 0
        self.minion_timer = 0
        self.dash_timer = 0
        
        # --- VARIÁVEIS VISUAIS AVANÇADAS ---
        self.image_size = 240 # Aumentei a área de desenho para caber asas e espada
        self.image = pygame.Surface((self.image_size, self.image_size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(0, 0, 60, 80) # Hitbox mais justa ao corpo
        self.hitbox.center = self.rect.center

        self.float_timer = 0
        self.wing_frame = 0
        self.cape_wave = 0
        self.halo_rotation = 0
        
        # Lógica de estado
        self.dash_direction = pygame.math.Vector2()

    def specific_behavior(self):
        current_time = pygame.time.get_ticks()
        
        # --- CHECAGEM DE FASE ---
        if self.health < self.stats['phase_2_threshold'] and self.phase == 1:
            self.phase = 2
            self.speed *= 1.3
            # Explosão visual de troca de fase
            visual_groups = [g for g in self.groups() if hasattr(g, 'custom_draw')]
            for _ in range(50):
                Particle(self.rect.center, visual_groups, self.obstacle_sprites, size_range=(10,25), color_base=(255, 50, 0), speed_range=(4,8))

        # --- MÁQUINA DE ESTADOS (Mantida a lógica original) ---
        if current_time - self.attack_timer > self.stats['attack_cooldown']:
            self.attack_timer = current_time
            if self.phase == 1: 
                self.shoot_at_player()
            elif self.phase == 2: 
                if random.choice([True, False]):
                    self.shoot_at_player() 
                else:
                    self.shoot_circle()

        if current_time - self.minion_timer > self.stats['minion_spawn_cooldown']:
            self.minion_timer = current_time
            amount = 1 if self.phase == 1 else random.randint(2, 3)
            self.summon_minion(amount)

        if current_time - self.dash_timer > self.stats['dash_cooldown']:
            self.dash_timer = current_time
            self.is_enraged = True 
            self.rage_end_time = current_time + 800
            self.dash_direction = self.get_pursuit_vector()

        # Movimento
        self.direction = self.get_pursuit_vector()
        move_speed = self.speed
        
        if self.is_enraged:
             move_speed = self.speed * 4
             self.direction = self.dash_direction 
             if current_time > self.rage_end_time:
                 self.is_enraged = False
                 self.direction = self.get_pursuit_vector()

        # Física
        self.hitbox.x += self.direction.x * move_speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * move_speed
        self.collision('vertical')
        self.rect.center = self.hitbox.center
        self.pos.x, self.pos.y = self.hitbox.center

    def shoot_at_player(self):
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        angle = math.degrees(math.atan2(-dy, dx))
        for offset in [-15, -5, 5, 15]: 
            self.create_bullet_callback(self.rect.center, angle + offset, speed=4, damage=1)

    def shoot_circle(self):
        for angle in range(0, 360, 20):
            self.create_bullet_callback(self.rect.center, angle, speed=3, damage=1)

    def summon_minion(self, amount):
        for _ in range(amount):
            spawn_pos = self.rect.center + pygame.math.Vector2(random.randint(-150, 150), random.randint(-150, 150))
            minion_type = random.choice([e for e in ENEMIES_DATA.keys() if e != 'lucifer' and e != 'minion'])
            self.spawn_callback(spawn_pos, minion_type)

    def draw_visuals(self):
        self.image.fill((0,0,0,0)) # Limpa o frame
        cx, cy = self.image_size // 2, self.image_size // 2
        
        # Atualiza timers de animação
        self.float_timer += 0.05
        self.wing_frame += 0.1
        self.cape_wave += 0.2
        self.halo_rotation += 2
        
        # Efeito de levitação (Senoide vertical)
        float_offset = math.sin(self.float_timer) * 5
        cy += float_offset

        # --- PALETA DE CORES ---
        COLOR_SKIN = (220, 220, 255) # Pálido quase branco (angelical corrompido)
        COLOR_ARMOR = (20, 20, 25)   # Obsidiana
        COLOR_GOLD = (180, 140, 50)  # Ouro velho
        COLOR_CLOTH = (40, 0, 10) if self.phase == 1 else (20, 0, 0) # Vermelho sangue escuro
        COLOR_WING_BONE = (10, 10, 10)
        COLOR_WING_FEATHER = (30, 5, 5)
        COLOR_GLOW = (255, 100, 0) if self.phase == 1 else (255, 0, 0) # Laranja -> Vermelho Puro

        # --- 1. AURÉOLA CORROMPIDA (Trás) ---
        halo_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        halo_radius = 40
        # Desenha espinhos rotacionando
        for i in range(0, 360, 45):
            rad = math.radians(i + self.halo_rotation)
            start = (50 + math.cos(rad) * (halo_radius - 5), 50 + math.sin(rad) * (halo_radius - 5))
            end = (50 + math.cos(rad) * (halo_radius + 10), 50 + math.sin(rad) * (halo_radius + 10))
            pygame.draw.line(halo_surf, COLOR_GOLD, start, end, 3)
        pygame.draw.circle(halo_surf, COLOR_GOLD, (50, 50), halo_radius, 2)
        
        self.image.blit(halo_surf, (cx - 50, cy - 90))

        # --- 2. ASAS DETALHADAS (Procedural) ---
        # Ângulo da asa oscila lentamente
        wing_angle = math.sin(self.wing_frame) * 10
        
        def draw_wing(is_right):
            direction = 1 if is_right else -1
            base_x = cx + (10 * direction)
            base_y = cy - 20
            
            # Estrutura óssea da asa
            bone_end_x = base_x + (120 * direction)
            bone_end_y = base_y - 60 + wing_angle
            mid_bone_x = base_x + (60 * direction)
            mid_bone_y = base_y - 80 + (wing_angle * 0.5)

            points = [(base_x, base_y), (mid_bone_x, mid_bone_y), (bone_end_x, bone_end_y)]
            pygame.draw.lines(self.image, COLOR_WING_BONE, False, points, 4)
            
            # Penas (Várias camadas de polígonos)
            num_feathers = 8
            for i in range(num_feathers):
                t = i / num_feathers
                # Interpolação ao longo do osso para a base das penas
                fx = mid_bone_x + (bone_end_x - mid_bone_x) * t
                fy = mid_bone_y + (bone_end_y - mid_bone_y) * t
                
                # Comprimento da pena
                flen = 60 + math.sin(i) * 20
                
                # Desenha pena
                feather_points = [
                    (fx, fy),
                    (fx + (10 * direction), fy + flen),
                    (fx - (5 * direction), fy + flen - 10)
                ]
                pygame.draw.polygon(self.image, COLOR_WING_FEATHER, feather_points)
                
        draw_wing(False) # Esquerda
        draw_wing(True)  # Direita

        # --- 3. CAPA/MANTO (Ondulação Senoidal) ---
        cape_points = []
        # Topo da capa (ombros)
        cape_points.append((cx - 20, cy - 10))
        cape_points.append((cx + 20, cy - 10))
        
        # Base da capa (com ondas)
        segments = 10
        cape_width = 60
        cape_height = 90
        start_x = cx + (cape_width // 2)
        
        # Desenha a borda inferior ondulada
        for i in range(segments + 1):
            px = start_x - (i * (cape_width / segments))
            # Onda senoidal baseada no tempo e posição X
            py = cy + cape_height + math.sin(self.cape_wave + i * 0.5) * 5
            cape_points.append((px, py))
            
        pygame.draw.polygon(self.image, COLOR_CLOTH, cape_points)
        pygame.draw.lines(self.image, (0,0,0), True, cape_points, 2)

        # --- 4. CORPO/ARMADURA ---
        # Tronco
        body_rect = pygame.Rect(0, 0, 30, 50)
        body_rect.center = (cx, cy + 10)
        pygame.draw.rect(self.image, COLOR_ARMOR, body_rect)
        
        # Detalhes Dourados na Armadura (Peitoral)
        pygame.draw.line(self.image, COLOR_GOLD, (cx - 15, cy - 15), (cx + 15, cy - 15), 2)
        pygame.draw.line(self.image, COLOR_GOLD, (cx, cy - 15), (cx, cy + 30), 2)

        # --- 5. ESPADA FLAMEJANTE (Lightbringer) ---
        # A espada flutua e gira levemente ao lado dele
        sword_angle = math.sin(self.float_timer * 2) * 5
        sword_surf = pygame.Surface((20, 100), pygame.SRCALPHA)
        
        # Lâmina Brilhante (Gradiente Simulado)
        blade_color_core = (255, 255, 200) # Branco quente
        blade_color_outer = (255, 100, 0)  # Laranja
        
        pygame.draw.rect(sword_surf, blade_color_outer, (5, 0, 10, 80)) # Borda
        pygame.draw.rect(sword_surf, blade_color_core, (8, 0, 4, 75))   # Núcleo
        
        # Punho
        pygame.draw.line(sword_surf, COLOR_GOLD, (0, 80), (20, 80), 4) # Guarda
        pygame.draw.line(sword_surf, (50, 50, 50), (10, 80), (10, 100), 3) # Cabo

        rotated_sword = pygame.transform.rotate(sword_surf, -45 + sword_angle)
        
        # Brilho da Espada (Blend Additive)
        glow_circle = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(glow_circle, (100, 50, 0, 100), (30,30), 25)
        self.image.blit(glow_circle, (cx + 30, cy - 20), special_flags=pygame.BLEND_RGBA_ADD)
        self.image.blit(rotated_sword, (cx + 35, cy - 40))

        # --- 6. CABEÇA E ROSTO ---
        head_pos = (cx, cy - 25)
        pygame.draw.circle(self.image, COLOR_SKIN, head_pos, 12) # Rosto pálido
        
        # Cabelo/Elmo Escuro
        pygame.draw.arc(self.image, (10, 10, 10), (cx - 14, cy - 40, 28, 30), math.pi, 0, 10)
        
        # Chifres Magníficos
        horn_pts_l = [(cx - 5, cy - 35), (cx - 20, cy - 55), (cx - 10, cy - 30)]
        horn_pts_r = [(cx + 5, cy - 35), (cx + 20, cy - 55), (cx + 10, cy - 30)]
        pygame.draw.polygon(self.image, (30, 30, 30), horn_pts_l)
        pygame.draw.polygon(self.image, (30, 30, 30), horn_pts_r)

        # Olhos Brilhantes (Sem pupilas, apenas luz)
        eye_color = (255, 200, 0) if self.phase == 1 else (255, 0, 0)
        pygame.draw.circle(self.image, eye_color, (cx - 4, cy - 24), 2)
        pygame.draw.circle(self.image, eye_color, (cx + 4, cy - 24), 2)
        
        # Brilho dos olhos
        eye_glow = pygame.Surface((40, 20), pygame.SRCALPHA)
        pygame.draw.circle(eye_glow, (*eye_color, 50), (20, 10), 8)
        self.image.blit(eye_glow, (cx - 20, cy - 34), special_flags=pygame.BLEND_RGBA_ADD)

        # --- 7. BARRA DE VIDA ---
        hp_perc = self.health / self.max_health
        bar_w = 100
        bar_h = 6
        bar_x = cx - bar_w // 2
        bar_y = cy - 100
        
        pygame.draw.rect(self.image, (50, 0, 0), (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(self.image, (255, 0, 0), (bar_x, bar_y, bar_w * hp_perc, bar_h))
        
        # --- 8. EFEITO DE HIT (Flash Branco) ---
        if self.is_hit:
             if pygame.time.get_ticks() - self.hit_time < 50:
                 mask = pygame.mask.from_surface(self.image)
                 white_surf = mask.to_surface(setcolor=(255,255,255,255), unsetcolor=(0,0,0,0))
                 self.image.blit(white_surf, (0,0))
             else:
                 self.is_hit = False