import pygame
import random
import math
import sys
import numpy as np
from pygame import gfxdraw

# Pygame başlat
pygame.init()
pygame.mixer.init()
pygame.mixer.pre_init(44100, -16, 2, 512)

# Ekran ayarları - 800x480 çözünürlük (155mm x 86mm)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("🎮 AKENA")

# Rahatlatıcı soft renk paleti
BACKGROUND = (15, 25, 40)
GRID_COLOR = (70, 90, 130, 30)
SOFT_GREEN = (160, 220, 180)
SOFT_BLUE = (140, 180, 220)
SOFT_PINK = (210, 160, 180)
SOFT_PURPLE = (180, 160, 200)
SOFT_YELLOW = (220, 200, 140)
SOFT_ORANGE = (220, 180, 150)
PURE_WHITE = (250, 250, 255)
BUTTON_COLOR = (50, 65, 95, 180)
BUTTON_HOVER = (75, 95, 130, 210)
STAR_COLORS = [
    (255, 255, 255, 120), 
    (220, 230, 240, 100), 
    (240, 240, 220, 110),
]

# Oyun ayarları
CELL_SIZE = 18
GRID_WIDTH = 10
GRID_HEIGHT = 20
GRID_X = SCREEN_WIDTH // 2 - (GRID_WIDTH * CELL_SIZE) // 2
GRID_Y = SCREEN_HEIGHT // 2 - (GRID_HEIGHT * CELL_SIZE) // 2 + 10

# Soft tek renk bloklar ve koyu çizgi renkleri
BLOCK_COLORS = {
    'I': [(120, 190, 220), (90, 150, 190)],
    'J': [(110, 150, 200), (80, 110, 160)],
    'L': [(220, 170, 110), (190, 130, 80)],
    'O': [(220, 200, 120), (190, 170, 90)],
    'S': [(130, 190, 140), (100, 150, 110)],
    'T': [(190, 140, 200), (160, 110, 170)],
    'Z': [(210, 140, 140), (180, 110, 110)]
}

# Tetris parçaları
SHAPES = {
    'I': [
        [[0, 0, 0, 0],
         [1, 1, 1, 1],
         [0, 0, 0, 0],
         [0, 0, 0, 0]],
        [[0, 0, 1, 0],
         [0, 0, 1, 0],
         [0, 0, 1, 0],
         [0, 0, 1, 0]]
    ],
    'J': [
        [[1, 0, 0],
         [1, 1, 1],
         [0, 0, 0]],
        [[0, 1, 1],
         [0, 1, 0],
         [0, 1, 0]],
        [[0, 0, 0],
         [1, 1, 1],
         [0, 0, 1]],
        [[0, 1, 0],
         [0, 1, 0],
         [1, 1, 0]]
    ],
    'L': [
        [[0, 0, 1],
         [1, 1, 1],
         [0, 0, 0]],
        [[0, 1, 0],
         [0, 1, 0],
         [0, 1, 1]],
        [[0, 0, 0],
         [1, 1, 1],
         [1, 0, 0]],
        [[1, 1, 0],
         [0, 1, 0],
         [0, 1, 0]]
    ],
    'O': [
        [[1, 1],
         [1, 1]]
    ],
    'S': [
        [[0, 1, 1],
         [1, 1, 0],
         [0, 0, 0]],
        [[0, 1, 0],
         [0, 1, 1],
         [0, 0, 1]]
    ],
    'T': [
        [[0, 1, 0],
         [1, 1, 1],
         [0, 0, 0]],
        [[0, 1, 0],
         [0, 1, 1],
         [0, 1, 0]],
        [[0, 0, 0],
         [1, 1, 1],
         [0, 1, 0]],
        [[0, 1, 0],
         [1, 1, 0],
         [0, 1, 0]]
    ],
    'Z': [
        [[1, 1, 0],
         [0, 1, 1],
         [0, 0, 0]],
        [[0, 0, 1],
         [0, 1, 1],
         [0, 1, 0]]
    ]
}

# SES FONKSİYONLARI
current_8d_sound = None

def generate_binaural_8d(base=330, beat=4, duration=8, volume=0.45, spin_speed=0.05):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    pan = (np.cos(2 * np.pi * spin_speed * t + random.uniform(0, 2 * np.pi)) + 1) / 2
    fade = np.ones_like(t)
    fade_len = int(0.15 * sample_rate)
    fade[:fade_len] = np.linspace(0, 1, fade_len)
    fade[-fade_len:] = np.linspace(1, 0, fade_len)
    left = np.sin(2 * np.pi * base * t) * (1 - pan)
    right = np.sin(2 * np.pi * (base + beat) * t) * pan
    stereo = np.vstack((left, right)).T * fade[:, None]
    stereo = (stereo * 32767).astype(np.int16)
    sound = pygame.sndarray.make_sound(stereo.copy())
    sound.set_volume(volume)
    return sound

def play_random_binaural_8d():
    global current_8d_sound
    base = random.choice([220, 330, 440, 520])
    beat = random.uniform(13.5, 14.6)
    spin = random.uniform(0.15, 0.35)
    s = generate_binaural_8d(base, beat, 12, 0.45, spin)
    current_8d_sound = s
    s.play(-1)
    return s

def generate_ding(volume=0.5):
    sample_rate = 44100
    duration = 0.65
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    freq = 380
    wave = np.sin(2 * np.pi * freq * t) * np.exp(-t * 6)
    stereo = np.vstack((wave, wave)).T
    stereo = (stereo * 32767).astype(np.int16)
    s = pygame.sndarray.make_sound(stereo.copy())
    s.set_volume(volume)
    return s

ding_fx = generate_ding()

def generate_fall_ding(volume=0.5):
    sample_rate = 44100
    duration = 0.45
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    freq = 540
    wave = np.sin(2 * np.pi * freq * t) * np.exp(-t * 6)
    stereo = np.vstack((wave, wave)).T
    stereo = (stereo * 32767).astype(np.int16)
    s = pygame.sndarray.make_sound(stereo.copy())
    s.set_volume(volume)
    return s

fall_ding_fx = generate_fall_ding()

def generate_galactic_echo(duration=12, base_freq=48, echo_delay=0.18, echo_decay=0.5, volume=0.25):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    base_wave = np.sin(2 * np.pi * base_freq * t + 0.7 * np.sin(2 * np.pi * 0.09 * t))
    echo_samples = int(sample_rate * echo_delay)
    echo_wave = np.zeros_like(base_wave)
    if echo_samples < len(base_wave):
        echo_wave[echo_samples:] = base_wave[:-echo_samples] * echo_decay
    final_wave = base_wave + echo_wave
    final_wave = final_wave / np.max(np.abs(final_wave))
    stereo = np.vstack((final_wave, final_wave)).T
    stereo = (stereo * 32767).astype(np.int16)
    sound = pygame.sndarray.make_sound(stereo.copy())
    sound.set_volume(volume)
    return sound

def play_galactic_echo():
    echo_sound = generate_galactic_echo()
    echo_sound.play(-1)
    return echo_sound

# ...existing code...
# ...existing code...
class Starfield:
    def __init__(self):
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT // 2
        self.stars = []
        self.shooting_stars = []
        self.num_arms = 6
        self.star_count = 420
        # allow stars to fill entire screen area (use hypotenuse/2 to reach corners)
        self.radius_min = 0
        self.radius_max = max(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.65
        self.spiral_tightness = 0.5
        self.rotation_speed = 0.0025
        self.rotation_angle = 0
        self.generate_galaxy_stars(self.star_count)

    def generate_galaxy_stars(self, count):
        self.stars = []
        for i in range(count):
            arm = i % self.num_arms
            arm_angle = (2 * math.pi / self.num_arms) * arm
            # uniform distribution across disk: radius ~ sqrt(u) for area-uniform
            u = random.random()
            radius = math.sqrt(u) * (self.radius_max - self.radius_min) + self.radius_min
            # give a small arm spread so stars are "in" arms but cover whole screen
            spiral_angle = self.spiral_tightness * (radius / (self.radius_max + 1e-6)) * math.pi * 2
            spiral_angle += arm_angle + random.uniform(-0.8, 0.8)
            color = random.choice([
                (255, 255, 255, 200),
                (220, 230, 240, 180),
                (240, 240, 220, 190),
                (180, 200, 255, 170),
                (255, 210, 230, 180),
                (200, 255, 220, 170)
            ])
            size = random.uniform(0.7, 2.8)
            speed = random.uniform(0.6, 1.6)
            initial_brightness = random.uniform(0.3, 0.8)
            init_x = self.center_x + radius * math.cos(spiral_angle)
            init_y = self.center_y + radius * math.sin(spiral_angle)
            self.stars.append({
                'initial_radius': radius,
                'initial_angle': spiral_angle,
                'color': color,
                'size': size,
                'speed': speed,
                'wobble_phase': random.uniform(0, 2 * math.pi),
                'wobble_speed': random.uniform(0.006, 0.018),
                'wobble_amount': random.uniform(1.0, 8.0),
                'phase_offset': random.uniform(0, 2 * math.pi),
                'brightness': initial_brightness,
                'x': init_x,
                'y': init_y
            })

    def maybe_spawn_shooting_star(self):
        if random.random() < 0.006:
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(12, 20)
            start_distance = max(SCREEN_WIDTH, SCREEN_HEIGHT) + 150
            x = self.center_x + math.cos(angle) * start_distance
            y = self.center_y + math.sin(angle) * start_distance
            self.shooting_stars.append({
                'x': x,
                'y': y,
                'vx': -math.cos(angle) * speed,
                'vy': -math.sin(angle) * speed,
                'life': 1.0,
                'color': (255, 255, 255, 250),
                'trail_length': random.randint(8, 16)
            })

    def update(self):
        # advance shared rotation so motion is synchronized
        self.rotation_angle += self.rotation_speed
        t = pygame.time.get_ticks() * 0.001
        for idx, star in enumerate(self.stars):
            # synchronized spiral motion: shared rotation + per-star offsets
            angle = star['initial_angle'] + self.rotation_angle * star['speed'] + star['phase_offset']
            # gentle radius oscillation around initial radius, clamped to screen bounds
            bob = math.sin(t * 0.6 * star['speed'] + idx) * (star['wobble_amount'])
            radius = star['initial_radius'] + bob * 0.45
            radius = max(self.radius_min, min(self.radius_max, radius))
            wobble = star['wobble_amount'] * math.sin(t * star['wobble_speed'] + star['wobble_phase'])
            x = self.center_x + (radius + wobble) * math.cos(angle)
            y = self.center_y + (radius + wobble) * math.sin(angle)
            star['x'] = x
            star['y'] = y
            # brightness for twinkle
            star['brightness'] = 0.45 + 0.35 * math.sin(t * (0.8 + star['wobble_speed'] * 40) + star['wobble_phase'])

        # shooting stars
        for s in self.shooting_stars[:]:
            s['x'] += s['vx']
            s['y'] += s['vy']
            s['life'] -= 0.03
            if s['life'] <= 0 or not (-200 <= s['x'] < SCREEN_WIDTH + 200 and -200 <= s['y'] < SCREEN_HEIGHT + 200):
                self.shooting_stars.remove(s)
        self.maybe_spawn_shooting_star()

    def draw(self, surface):
        for star in self.stars:
            b = star.get('brightness', 0.5)
            alpha_base = star['color'][3] if len(star['color']) > 3 else 180
            alpha = int(b * alpha_base)
            color = (*star['color'][:3], max(24, min(255, alpha)))
            x, y = int(star.get('x', self.center_x)), int(star.get('y', self.center_y))
            if -60 <= x < SCREEN_WIDTH + 60 and -60 <= y < SCREEN_HEIGHT + 60:
                if star['size'] < 1.6:
                    surface.set_at((x, y), color)
                else:
                    glow_radius = int(star['size'] * 1.8)
                    glow_color = (*color[:3], int(alpha * 0.25))
                    if glow_radius > 1:
                        gfxdraw.filled_circle(surface, x, y, glow_radius, glow_color)
                    gfxdraw.filled_circle(surface, x, y, int(star['size']), color)
        for s in self.shooting_stars:
            alpha = int(s['life'] * s['color'][3])
            if alpha > 0:
                color = (*s['color'][:3], alpha)
                for i in range(s['trail_length']):
                    trail_alpha = alpha * (1 - i / s['trail_length']) * 0.45
                    trail_color = (*s['color'][:3], int(trail_alpha))
                    trail_x = s['x'] - s['vx'] * i * 0.14
                    trail_y = s['y'] - s['vy'] * i * 0.14
                    if 0 <= trail_x < SCREEN_WIDTH and 0 <= trail_y < SCREEN_HEIGHT:
                        pygame.draw.circle(surface, trail_color, (int(trail_x), int(trail_y)), 
                                          max(1, int(2.0 * (1 - i / s['trail_length']))))
                if 0 <= s['x'] < SCREEN_WIDTH and 0 <= s['y'] < SCREEN_HEIGHT:
                    gfxdraw.filled_circle(surface, int(s['x']), int(s['y']), 2, color)
# ...existing code...


class Nebula:
    def __init__(self):
        self.reset()
        self.size = random.randint(250, 400)
        
    def reset(self):
        self.x = random.randint(-100, SCREEN_WIDTH + 100)
        self.y = random.randint(-100, SCREEN_HEIGHT + 100)
        self.color = random.choice([
            (60, 50, 90, 4), 
            (50, 60, 100, 3), 
            (70, 40, 80, 5)
        ])
        self.speed = random.uniform(0.005, 0.02)
        self.pulse_timer = random.uniform(0, math.pi * 2)
        self.pulse_speed = random.uniform(0.0003, 0.001)
        
    def update(self):
        self.x -= self.speed
        self.pulse_timer += self.pulse_speed
        if self.x < -self.size * 2:
            self.reset()
        
    def draw(self, surface):
        pulse_boost = 1 + 0.15 * math.sin(self.pulse_timer * 2)
        pulse_factor = 0.5 + 0.3 * math.sin(self.pulse_timer)
        nebula_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        for i in range(3):
            radius = int((self.size - i * 50) * pulse_factor * pulse_boost)
            if radius > 0:
                alpha = self.color[3] - i * 1
                color = (*self.color[:3], max(1, alpha))
                pygame.draw.circle(nebula_surface, color, (self.size, self.size), radius)
        surface.blit(nebula_surface, (self.x - self.size, self.y - self.size))

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.uniform(0.8, 1.5)
        self.speed_x = random.uniform(-1.0, 1.0)
        self.speed_y = random.uniform(-1.5, -0.3)
        self.life = 1.0
        self.decay = random.uniform(0.008, 0.02)
        
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += 0.02
        self.life -= self.decay
        return self.life > 0
        
    def draw(self, surface):
        alpha = int(self.life * 120)
        color = (*self.color, alpha)
        gfxdraw.filled_circle(surface, int(self.x), int(self.y), int(self.size), color)

class DropTrail:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.life = 1.0
        self.decay = 0.55
        self.size = CELL_SIZE - 4
        
    def update(self):
        self.life -= self.decay
        return self.life > 0
        
    def draw(self, surface):
        alpha = int(self.life * 400)
        trail_color = (255, 255, 255, alpha)
        rect = pygame.Rect(
            GRID_X + self.x * CELL_SIZE + 2,
            GRID_Y + self.y * CELL_SIZE + 2,
            self.size, self.size
        )
        pygame.draw.rect(surface, trail_color, rect, border_radius=2)

class SoftGlowBlock:
    def __init__(self, x, y, block_type):
        self.x = x
        self.y = y
        self.block_type = block_type
        self.life = 1.0
        self.decay = 0.05
        self.size = CELL_SIZE
        
    def update(self):
        self.life -= self.decay
        return self.life > 0
        
    def draw(self, surface):
        alpha = int(self.life * 150)
        color = (*BLOCK_COLORS[self.block_type][0], alpha)
        rect = pygame.Rect(
            GRID_X + self.x * CELL_SIZE,
            GRID_Y + self.y * CELL_SIZE,
            self.size, self.size
        )
        glow_surface = pygame.Surface((self.size + 6, self.size + 6), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*color[:3], alpha // 2), 
                        (0, 0, self.size + 6, self.size + 6), 
                        border_radius=5)
        surface.blit(glow_surface, (rect.x - 3, rect.y - 3))
        pygame.draw.rect(surface, color, rect, border_radius=3)

class MenuButton:
    def __init__(self, x, y, width, height, text, font, color=SOFT_GREEN, hover_color=SOFT_BLUE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.hovered else self.color
        
        # Buton gövdesi - BUTTON_COLOR zaten RGBA formatında
        pygame.draw.rect(surface, BUTTON_COLOR, self.rect, border_radius=12)
        
        # Glow efekti - hover durumunda
        if self.hovered:
            glow_rect = self.rect.inflate(8, 8)
            # RGB renk + alpha değeri
            glow_color = (color[0], color[1], color[2], 80)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, glow_color, (0, 0, glow_rect.width, glow_rect.height), 3, border_radius=16)
            surface.blit(glow_surface, glow_rect)
        
        # Buton kenarı - RGB renk kullan
        pygame.draw.rect(surface, (color[0], color[1], color[2]), self.rect, 3, border_radius=12)
        
        # Buton metni
        text_color = PURE_WHITE
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered
        
    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click

class ComfortButton:
    def __init__(self, x, y, width, height, text, font, color=SOFT_GREEN, hover_color=SOFT_BLUE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, BUTTON_COLOR, self.rect, border_radius=10)
        if self.hovered:
            glow_color = (*color[:3], 30)
            glow_rect = self.rect.inflate(6, 6)
            pygame.draw.rect(surface, glow_color, glow_rect, border_radius=12, width=2)
        pygame.draw.rect(surface, color, self.rect, 2, border_radius=10)
        text_color = PURE_WHITE
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered
        
    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click

class TetrisGame:
    # ...existing code...
    def draw_shade_overlay(self, surface, alpha=160, hole_radius=160, hole_softness=36):
        """Draw a dark vignette with a soft transparent hole at screen center."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        # soft edge: multiple concentric circles reducing alpha
        for i in range(hole_softness, -1, -1):
            a = int((i / (hole_softness + 1)) * alpha)
            pygame.draw.circle(overlay, (0, 0, 0, a), (cx, cy), hole_radius + i)
        # fully transparent center
        pygame.draw.circle(overlay, (0, 0, 0, 0), (cx, cy), max(0, hole_radius - 6))
        surface.blit(overlay, (0, 0))
# ...existing code...
    def draw_soft_gradient(self, surface, opacity=180):
        grad = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for i in range(SCREEN_HEIGHT):
            a = opacity * (i / SCREEN_HEIGHT)
            color = (20, 30, 50, int(a))
            pygame.draw.line(grad, color, (0, i), (SCREEN_WIDTH, i))
        surface.blit(grad, (0, 0))

    def glow_text(self, text, font, color, glow_color, pos):
        for r in range(1, 6):
            glow = font.render(text, True, (*glow_color, max(10, 40-r*6)))
            screen.blit(glow, (pos[0]-r, pos[1]))
            screen.blit(glow, (pos[0]+r, pos[1]))
            screen.blit(glow, (pos[0], pos[1]-r))
            screen.blit(glow, (pos[0], pos[1]+r))
        real = font.render(text, True, color)
        screen.blit(real, pos)

    def __init__(self):
        self.reset_game()
        self.particles = []
        self.drop_trails = []
        self.glow_blocks = []
        self.starfield = Starfield()
        self.nebulae = [Nebula() for _ in range(2)]
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.font_xsmall = pygame.font.Font(None, 18)
        
        # Oyun butonları
        big_button_size = 65
        small_button_width = 80
        small_button_height = 50
        right_panel_x = SCREEN_WIDTH - 250
        button_center_y = SCREEN_HEIGHT // 2 - 50
        
        self.buttons = {
            'up': ComfortButton(right_panel_x + big_button_size, button_center_y - big_button_size - 10, 
                              big_button_size, big_button_size, "W", self.font_medium, SOFT_BLUE),
            'left': ComfortButton(right_panel_x, button_center_y + 10, 
                                big_button_size, big_button_size, "A", self.font_medium, SOFT_GREEN),
            'right': ComfortButton(right_panel_x + big_button_size * 2, button_center_y + 10, 
                                 big_button_size, big_button_size, "D", self.font_medium, SOFT_GREEN),
            'down': ComfortButton(right_panel_x + big_button_size, button_center_y + big_button_size + 20, 
                                big_button_size, big_button_size, "S", self.font_medium, SOFT_PINK),
            'rotate': ComfortButton(right_panel_x, SCREEN_HEIGHT - 70, 
                                  small_button_width, small_button_height, "DÖNDÜR", self.font_xsmall, SOFT_PURPLE),
            'drop': ComfortButton(right_panel_x + small_button_width + 10, SCREEN_HEIGHT - 70, 
                                small_button_width, small_button_height, "BIRAK", self.font_xsmall, SOFT_ORANGE),
            'pause': ComfortButton(SCREEN_WIDTH - 60, 20, 50, 35, "M", self.font_xsmall, SOFT_YELLOW)
        }
        
        # Menü butonları
        menu_button_width = 200
        menu_button_height = 50
        center_x = SCREEN_WIDTH // 2 - menu_button_width // 2
        
        self.menu_buttons = {
            'start': MenuButton(center_x, SCREEN_HEIGHT // 2 + 20, menu_button_width, menu_button_height, 
                              "OYUNA BAŞLA", self.font_medium, SOFT_GREEN),
            'restart': MenuButton(center_x, SCREEN_HEIGHT // 2 + 30, menu_button_width, menu_button_height, 
                               "TEKRAR DENE", self.font_medium, SOFT_GREEN),
            'continue': MenuButton(center_x, SCREEN_HEIGHT // 2 - 20, menu_button_width, menu_button_height, 
                                 "DEVAM ET", self.font_medium, SOFT_BLUE),
            'quit': MenuButton(center_x, SCREEN_HEIGHT // 2 + 90, menu_button_width, menu_button_height, 
                             "ÇIKIŞ", self.font_medium, SOFT_PINK)
        }
        
        self.fast_drop_button_pressed = False
        
    def reset_game(self):
        self.board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.paused = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.started = False
        self.base_drop_speed = 600
        self.fast_drop_speed = 80
        self.current_drop_speed = self.base_drop_speed
        self.last_drop_time = pygame.time.get_ticks()
        self.combo_count = 0
        self.fall_progress = 0
        self.fast_falling = False
        self.fast_drop_button_pressed = False
        
    def new_piece(self):
        shape_type = random.choice(list(SHAPES.keys()))
        return {
            'shape': SHAPES[shape_type][0],
            'type': shape_type,
            'x': GRID_WIDTH // 2 - len(SHAPES[shape_type][0][0]) // 2,
            'y': 0,
            'rotation': 0
        }
        
    def valid_position(self, piece, x, y, rotation):
        shape = SHAPES[piece['type']][rotation % len(SHAPES[piece['type']])]
        for row in range(len(shape)):
            for col in range(len(shape[0])):
                if shape[row][col]:
                    board_x = x + col
                    board_y = y + row
                    if (board_x < 0 or board_x >= GRID_WIDTH or 
                        board_y >= GRID_HEIGHT or 
                        (board_y >= 0 and self.board[board_y][board_x])):
                        return False
        return True
        
    def rotate_piece(self):
        new_rotation = (self.current_piece['rotation'] + 1) % len(SHAPES[self.current_piece['type']])
        if self.valid_position(self.current_piece, self.current_piece['x'], self.current_piece['y'], new_rotation):
            self.current_piece['rotation'] = new_rotation
            self.current_piece['shape'] = SHAPES[self.current_piece['type']][new_rotation]
            
    def move_piece(self, dx, dy):
        if self.valid_position(self.current_piece, self.current_piece['x'] + dx, 
                             self.current_piece['y'] + dy, self.current_piece['rotation']):
            self.current_piece['x'] += dx
            self.current_piece['y'] += dy
            return True
        return False
        
    def hard_drop(self):
        drop_distance = 0
        current_y = self.current_piece['y']
        while self.valid_position(self.current_piece, self.current_piece['x'], 
                                current_y + drop_distance + 1, 
                                self.current_piece['rotation']):
            drop_distance += 1
        trail_count = min(3, drop_distance)
        for i in range(drop_distance - trail_count, drop_distance):
            y_pos = current_y + i
            shape = self.current_piece['shape']
            for row in range(len(shape)):
                for col in range(len(shape[0])):
                    if shape[row][col]:
                        x = self.current_piece['x'] + col
                        y = y_pos + row
                        if 0 <= y < GRID_HEIGHT:
                            self.drop_trails.append(DropTrail(x, y))
        self.current_piece['y'] += drop_distance
        self.lock_piece()
        
    def lock_piece(self):
        shape = self.current_piece['shape']
        for row in range(len(shape)):
            for col in range(len(shape[0])):
                if shape[row][col]:
                    board_y = self.current_piece['y'] + row
                    board_x = self.current_piece['x'] + col
                    if 0 <= board_y < GRID_HEIGHT and 0 <= board_x < GRID_WIDTH:
                        self.board[board_y][board_x] = self.current_piece['type']
                        self.glow_blocks.append(SoftGlowBlock(board_x, board_y, self.current_piece['type']))
                    x = GRID_X + (self.current_piece['x'] + col) * CELL_SIZE + CELL_SIZE // 2
                    y = GRID_Y + (self.current_piece['y'] + row) * CELL_SIZE + CELL_SIZE // 2
                    for _ in range(2):
                        color = random.choice([SOFT_GREEN, SOFT_BLUE, SOFT_PINK, SOFT_PURPLE])
                        self.particles.append(Particle(x, y, color))
        self.check_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        self.fall_progress = 0
        self.fast_falling = False
        self.fast_drop_button_pressed = False
        if not self.valid_position(self.current_piece, self.current_piece['x'], 
                                 self.current_piece['y'], self.current_piece['rotation']):
            self.game_over = True
            
    def check_lines(self):
        lines_to_clear = []
        for row in range(GRID_HEIGHT):
            if all(self.board[row]):
                lines_to_clear.append(row)
        if lines_to_clear:
            ding_fx.play()
            for row in lines_to_clear:
                for col in range(GRID_WIDTH):
                    x = GRID_X + col * CELL_SIZE + CELL_SIZE // 2
                    y = GRID_Y + row * CELL_SIZE + CELL_SIZE // 2
                    for _ in range(1):
                        color = random.choice([SOFT_GREEN, SOFT_BLUE, SOFT_PINK])
                        self.particles.append(Particle(x, y, color))
            for row in sorted(lines_to_clear):
                del self.board[row]
                self.board.insert(0, [0 for _ in range(GRID_WIDTH)])
            self.lines_cleared += len(lines_to_clear)
            self.level = self.lines_cleared // 5 + 1
            line_scores = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += line_scores.get(len(lines_to_clear), 0) * self.level
            if len(lines_to_clear) > 1:
                self.combo_count += 1
                self.score += self.combo_count * 50
            else:
                self.combo_count = 0
            self.base_drop_speed = max(150, 600 - (self.level - 1) * 40)
            
    # ...existing code...
    def draw_board(self):
        screen.fill(BACKGROUND)
        # update starfield & nebulae only during active gameplay
        if self.started and not self.paused and not self.game_over:
            self.starfield.update()
            for nebula in self.nebulae:
                nebula.update()
        # always draw (will be frozen when not updating)
        self.starfield.draw(screen)
        for nebula in self.nebulae:
            nebula.draw(screen)

        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(screen, GRID_COLOR, 
                           (GRID_X + x * CELL_SIZE, GRID_Y),
                           (GRID_X + x * CELL_SIZE, GRID_Y + GRID_HEIGHT * CELL_SIZE), 1)
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(screen, GRID_COLOR,
                           (GRID_X, GRID_Y + y * CELL_SIZE),
                           (GRID_X + GRID_WIDTH * CELL_SIZE, GRID_Y + y * CELL_SIZE), 1)
        for glow_block in self.glow_blocks[:]:
            if not glow_block.update():
                self.glow_blocks.remove(glow_block)
            else:
                glow_block.draw(screen)
        for trail in self.drop_trails[:]:
            if not trail.update():
                self.drop_trails.remove(trail)
            else:
                trail.draw(screen)
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                if self.board[row][col]:
                    self.draw_block(col, row, self.board[row][col])
        if not self.game_over and self.started and not self.paused:
            shape = self.current_piece['shape']
            for row in range(len(shape)):
                for col in range(len(shape[0])):
                    if shape[row][col]:
                        x = self.current_piece['x'] + col
                        y = self.current_piece['y'] + row
                        if y >= 0:
                            self.draw_block(x, y, self.current_piece['type'])
        for particle in self.particles[:]:
            if not particle.update():
                self.particles.remove(particle)
            else:
                particle.draw(screen)
        self.draw_ui()
# ...existing code...
        
    def draw_block(self, x, y, block_type, fall_offset=0):
        rect = pygame.Rect(
            GRID_X + x * CELL_SIZE, 
            GRID_Y + y * CELL_SIZE, 
            CELL_SIZE, 
            CELL_SIZE
        )
        block_color = BLOCK_COLORS[block_type][0]
        line_color = BLOCK_COLORS[block_type][1]
        pygame.draw.rect(screen, block_color, rect, border_radius=3)
        pygame.draw.line(screen, line_color, 
                        (rect.left, rect.top), (rect.right, rect.top), 1)
        pygame.draw.line(screen, line_color, 
                        (rect.left, rect.top), (rect.left, rect.bottom), 1)
        pygame.draw.line(screen, (*line_color, 150), 
                        (rect.left, rect.bottom-1), (rect.right, rect.bottom-1), 1)
        pygame.draw.line(screen, (*line_color, 150), 
                        (rect.right-1, rect.top), (rect.right-1, rect.bottom), 1)
        
    def draw_ui(self):
        title = self.font_medium.render("AKENA", True, SOFT_PURPLE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 15))
        panel_x = 30
        panel_y = 80
        panel_width = 110
        panel_height = 120
        panel_bg = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_bg.fill((40, 55, 80, 80))
        screen.blit(panel_bg, (panel_x, panel_y))
        pygame.draw.rect(screen, (*SOFT_BLUE, 100), (panel_x, panel_y, panel_width, panel_height), 1, border_radius=8)
        score_text = self.font_xsmall.render("* SKOR", True, (*SOFT_YELLOW, 180))
        screen.blit(score_text, (panel_x + panel_width//2 - score_text.get_width()//2, panel_y + 10))
        score_value = self.font_small.render(str(self.score), True, PURE_WHITE)
        screen.blit(score_value, (panel_x + panel_width//2 - score_value.get_width()//2, panel_y + 35))
        level_text = self.font_xsmall.render(f"SEVİYE: {self.level}", True, (*SOFT_GREEN, 180))
        screen.blit(level_text, (panel_x + 29, panel_y + 90))
        lines_text = self.font_xsmall.render(f"SATIR: {self.lines_cleared}", True, (*SOFT_PINK, 180))
        screen.blit(lines_text, (panel_x + 32, panel_y + 65))
        next_panel_y = panel_y + panel_height + 15
        next_panel_height = 90
        next_bg = pygame.Surface((panel_width, next_panel_height), pygame.SRCALPHA)
        next_bg.fill((40, 55, 80, 80))
        screen.blit(next_bg, (panel_x, next_panel_y))
        pygame.draw.rect(screen, (*SOFT_PURPLE, 100), (panel_x, next_panel_y, panel_width, next_panel_height), 1, border_radius=8)
        next_text = self.font_xsmall.render("SONRAKİ", True, (*SOFT_PURPLE, 180))
        screen.blit(next_text, (panel_x + panel_width//2 - next_text.get_width()//2, next_panel_y + 8))
        if hasattr(self, 'next_piece'):
            shape = self.next_piece['shape']
            start_x = panel_x + panel_width//2 - (len(shape[0]) * CELL_SIZE)//2
            start_y = next_panel_y + 30
            for row in range(len(shape)):
                for col in range(len(shape[0])):
                    if shape[row][col]:
                        block_rect = pygame.Rect(
                            start_x + col * CELL_SIZE, 
                            start_y + row * CELL_SIZE, 
                            CELL_SIZE, CELL_SIZE
                        )
                        color = BLOCK_COLORS[self.next_piece['type']][0]
                        pygame.draw.rect(screen, color, block_rect, border_radius=3)
        for button in self.buttons.values():
            button.draw(screen)
        if not self.started:
            self.draw_start_screen()
        elif self.game_over:
            self.draw_game_over()
        elif self.paused:
            self.draw_pause_screen()
            
    def draw_start_screen(self):
        self.draw_soft_gradient(screen, 220)
        self.starfield.draw(screen)
        for nebula in self.nebulae:
            nebula.draw(screen)

        # soft shade for focus
        self.draw_shade_overlay(screen, alpha=170, hole_radius=180, hole_softness=44)

        # Title
        title_font = pygame.font.Font(None, 64)
        title_text = "AKENA"
        title_surf = title_font.render(title_text, True, PURE_WHITE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
        for i in range(10, 0, -2):
            glow_surf = title_font.render(title_text, True, (*SOFT_PURPLE, max(6, i*8)))
            glow_rect = glow_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
            screen.blit(glow_surf, glow_rect)
        screen.blit(title_surf, title_rect)

        # Subtitle
        subtitle = self.font_medium.render("Rahatla ve Akışa Bırak", True, (*PURE_WHITE, 200))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
        screen.blit(subtitle, subtitle_rect)

        # Draw START menu button so the game can actually begin
        if 'start' in self.menu_buttons:
            self.menu_buttons['start'].draw(screen)

        # Hint text
        hint = self.font_small.render("Tıkla veya SPACE ile başla", True, (*SOFT_BLUE, 160))
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))
        screen.blit(hint, hint_rect)
    def draw_pause_screen(self):
        self.draw_soft_gradient(screen, 180)
        self.starfield.draw(screen)
        for nebula in self.nebulae:
            nebula.draw(screen)
    def draw_game_over(self):
        self.draw_soft_gradient(screen, 220)
        self.starfield.draw(screen)
        for nebula in self.nebulae:
            nebula.draw(screen)

        # shade for focus
        self.draw_shade_overlay(screen, alpha=180, hole_radius=160, hole_softness=40)

        # darker vignette when paused
        self.draw_shade_overlay(screen, alpha=200, hole_radius=140, hole_softness=36)
        # Ana başlık
        title_font = pygame.font.Font(None, 64)
        title_text = "AKENA"
        title_surf = title_font.render(title_text, True, PURE_WHITE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
        
        # Glow efekti
        for i in range(10, 0, -2):
            glow_surf = title_font.render(title_text, True, (*SOFT_PURPLE, i*10))
            glow_rect = glow_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
            screen.blit(glow_surf, glow_rect)
        
        screen.blit(title_surf, title_rect)
        
        # Alt başlık
        subtitle = self.font_medium.render("Rahatla ve Akışa Bırak", True, (*PURE_WHITE, 200))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
        screen.blit(subtitle, subtitle_rect)
        
        # Buton
        self.menu_buttons['start'].draw(screen)
        
        # Alt yazı
        hint = self.font_small.render("Müzikle rahatla, bloklarla ak", True, (*SOFT_BLUE, 150))
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))
        screen.blit(hint, hint_rect)

    def draw_game_over(self):
        self.draw_soft_gradient(screen, 220)
        self.starfield.draw(screen)
        for nebula in self.nebulae:
            nebula.draw(screen)
        
        # Başlık
        title_font = pygame.font.Font(None, 56)
        title_text = "X Oyun Bitti"
        title_surf = title_font.render(title_text, True, SOFT_PINK)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
        
        # Glow efekti
        for i in range(8, 0, -2):
            glow_surf = title_font.render(title_text, True, (*SOFT_PINK, i*15))
            glow_rect = glow_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
            screen.blit(glow_surf, glow_rect)
        
        screen.blit(title_surf, title_rect)
        
        # Skor
        score_text = self.font_large.render(f"Skor: {self.score}", True, SOFT_YELLOW)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
        screen.blit(score_text, score_rect)
        
        # Seviye ve satırlar
        stats_text = self.font_medium.render(f"Seviye: {self.level}  |  Satır: {self.lines_cleared}", True, (*PURE_WHITE, 180))
        stats_rect = stats_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10))
        screen.blit(stats_text, stats_rect)
        
        # Butonlar
        self.menu_buttons['restart'].draw(screen)
        self.menu_buttons['quit'].draw(screen)

    def draw_pause_screen(self):
        self.draw_soft_gradient(screen, 180)
        self.starfield.draw(screen)
        for nebula in self.nebulae:
            nebula.draw(screen)
        
        # Başlık
        title_font = pygame.font.Font(None, 58)
        title_text = "Duraklatıldı"
        title_surf = title_font.render(title_text, True, SOFT_YELLOW)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 140))
        
        # Glow efekti
        for i in range(8, 0, -2):
            glow_surf = title_font.render(title_text, True, (*SOFT_YELLOW, i*15))
            glow_rect = glow_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 140))
            screen.blit(glow_surf, glow_rect)
        
        screen.blit(title_surf, title_rect)
        
        # Mesaj
        message = self.font_medium.render("Mola ver ve nefes al", True, (*PURE_WHITE, 200))
        message_rect = message.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
        screen.blit(message, message_rect)
        
        # Butonlar
        self.menu_buttons['continue'].draw(screen)
        self.menu_buttons['quit'].draw(screen)

    def update(self):
        if self.started and not self.game_over and not self.paused:
            current_time = pygame.time.get_ticks()
            time_since_last_drop = current_time - self.last_drop_time
            self.fast_falling = pygame.key.get_pressed()[pygame.K_DOWN] or self.fast_drop_button_pressed
            self.current_drop_speed = self.fast_drop_speed if self.fast_falling else self.base_drop_speed
            if time_since_last_drop > self.current_drop_speed:
                if not self.move_piece(0, 1):
                    self.lock_piece()
                self.last_drop_time = current_time

def main():
    game = TetrisGame()
    play_random_binaural_8d()
    play_galactic_echo()
    clock = pygame.time.Clock()
    running = True
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_click = True
                # Menü buton kontrolleri
                if not game.started:
                    if game.menu_buttons['start'].is_clicked(mouse_pos, mouse_click):
                        game.started = True
                elif game.game_over:
                    if game.menu_buttons['restart'].is_clicked(mouse_pos, mouse_click):
                        game.reset_game()
                        game.started = True
                    elif game.menu_buttons['quit'].is_clicked(mouse_pos, mouse_click):
                        running = False
                elif game.paused:
                    if game.menu_buttons['continue'].is_clicked(mouse_pos, mouse_click):
                        game.paused = False
                    elif game.menu_buttons['quit'].is_clicked(mouse_pos, mouse_click):
                        running = False
                else:
                    # Normal oyun içi tıklama
                    if not game.game_over:
                        game.started = True
                    
            elif event.type == pygame.KEYDOWN:
                if game.started and not game.game_over and not game.paused:
                    if event.key == pygame.K_LEFT:
                        game.move_piece(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        game.move_piece(1, 0)
                    elif event.key == pygame.K_UP:
                        game.rotate_piece()
                    elif event.key == pygame.K_SPACE:
                        game.hard_drop()
                        fall_ding_fx.play()
                    elif event.key == pygame.K_p:
                        game.paused = not game.paused
                elif event.key == pygame.K_r and game.game_over:
                    game.reset_game()
                    game.started = True
        
        # Buton hover kontrolleri
        if not game.started:
            game.menu_buttons['start'].check_hover(mouse_pos)
        elif game.game_over:
            game.menu_buttons['restart'].check_hover(mouse_pos)
            game.menu_buttons['quit'].check_hover(mouse_pos)
        elif game.paused:
            game.menu_buttons['continue'].check_hover(mouse_pos)
            game.menu_buttons['quit'].check_hover(mouse_pos)
        
        # Oyun buton kontrolü
        if game.started and not game.game_over:
            for button_name, button in game.buttons.items():
                button.check_hover(mouse_pos)
                if button_name == 'down':
                    if button.rect.collidepoint(mouse_pos) and mouse_pressed:
                        game.fast_drop_button_pressed = True
                        fall_ding_fx.play()
                    elif not mouse_pressed:
                        game.fast_drop_button_pressed = False
                if button.is_clicked(mouse_pos, mouse_click):
                    if button_name == 'left':
                        game.move_piece(-1, 0)
                    elif button_name == 'right':
                        game.move_piece(1, 0)
                    elif button_name == 'up':
                        game.rotate_piece()
                    elif button_name == 'down':
                        game.fast_drop_button_pressed = True
                    elif button_name == 'rotate':
                        game.rotate_piece()
                    elif button_name == 'drop':
                        game.hard_drop()
                        fall_ding_fx.play()
                    elif button_name == 'pause':
                        game.paused = not game.paused
        
        game.update()
        game.draw_board()
        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()