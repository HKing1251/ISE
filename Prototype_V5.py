import pygame
import random
import time
import sys
import os
import json
import pygame.mixer
import math
from pathlib import Path

from BackgroundTest.BackgroundScreen import draw_dynamic_background as draw_bg_1
from BackgroundTest.BackgroundScreen2 import draw_dynamic_background as draw_bg_2
from BackgroundTest.BackgroundScreen3 import draw_dynamic_background as draw_bg_3

pygame.init()

clock = pygame.time.Clock()


# === Constants ===
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

ARROW_SIZE = 80
ARROW_SPACING = 100
TARGET_Y = 100
GLOW_DURATION = 15
RATING_DISPLAY_TIME = 30

MAX_HEALTH = 200
INITIAL_HEALTH = 100
SHAKE_INTENSITY = 3
HEALTH_BAR_WIDTH = 300
HEALTH_BAR_HEIGHT = 30
BLOOD_SPLASH_DURATION = 500

PROGRESS_BAR_X = 100
PROGRESS_BAR_Y = 140  # just under the health bar
PROGRESS_BAR_LENGTH = SCREEN_WIDTH - 200
SAVE_FILE = "game_progress.json"

max_score = 1000


# Set the working directory to the script's location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

BASE_PATH = os.path.dirname(__file__)
SPRITE_FOLDER = os.path.join(BASE_PATH, "ChoosingCharacter", "Player")  # New correct path

def resizeObject(originObject, scaledFactor):
    return pygame.transform.scale_by(originObject, scaledFactor)

def load_font(path, size):
    return pygame.font.Font(path, size)

atlantaFont = load_font("assets/Atlanta-College.ttf", 30)
atlantaFontLarge = load_font("assets/Atlanta-College.ttf", 60)
gladoliaFont = load_font("assets/Gladolia-Regular.otf", 30)
gladoliaFontLarge = load_font("assets/Gladolia-Regular.otf", 60)
moldieFont = load_font("assets/Moldie.otf", 30)
moldieFontLarge = load_font("assets/Moldie.otf", 60)
pixelGameFont = load_font("assets/PixelGame.otf", 30)
pixelGameFontLarge = load_font("assets/PixelGame.otf", 60)
pixelGameFontHuge = load_font("assets/PixelGame.otf", 85)


class Character:
    def __init__(self, x, y, screen_width, screen_height,speed):
        self.x = x
        self.y = y
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.direction = "idle"
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_delay = speed  # Animation speed (higher = slower)
        self.speed = 5
        self.scale = 1
        self.last_direction = None  # Track previous direction

        # Load animations
        self.animations = {
            "idle": self.load_frames("BoyfriendIdle", 4),
            "down": self.load_frames("BoyfriendDown", 2),
            "up": self.load_frames("BoyfriendUp", 2),
            "left": self.load_frames("BoyfriendLeft", 2),
            "right": self.load_frames("BoyfriendRight", 2),
        }
        
        # Set initial image
        self.image = self.animations["idle"][0]

    def load_frames(self, base_name, frame_count):
        """Load animation frames with error handling"""
        frames = []
        for i in range(1, frame_count + 1):
            try:
                path = os.path.join(SPRITE_FOLDER, f"{base_name}({i}).png")
                img = pygame.image.load(path).convert_alpha()
                frames.append(pygame.transform.scale_by(img, self.scale))
            except:
                try:
                    path = os.path.join(SPRITE_FOLDER, f"{base_name}({i}).PNG")
                    img = pygame.image.load(path).convert_alpha()
                    frames.append(pygame.transform.scale_by(img, self.scale))
                except:
                    # Create placeholder if image fails to load
                    placeholder = pygame.Surface((50, 50), pygame.SRCALPHA)
                    pygame.draw.rect(placeholder, (255, 0, 0), (0, 0, 50, 50))
                    frames.append(placeholder)
        return frames

    def update(self, keys):
        # Store previous direction
        prev_direction = self.direction
        self.direction = "idle"
        
        # Direction change based on key input (but no movement)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction = "left"
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction = "right"
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction = "up"
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction = "down"

        # Reset animation if direction changed
        if prev_direction != self.direction:
            self.current_frame = 0
            self.frame_timer = 0

        # Animation update - only advance frames after delay
        self.frame_timer += 1
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0
            if self.animations[self.direction]:  # Check if frames exist
                self.current_frame = (self.current_frame + 1) % len(self.animations[self.direction])
                self.image = self.animations[self.direction][self.current_frame]


    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

# === Particle System ===
class Particle:
    def __init__(self, x, y, color, velocity_x=0, velocity_y=0, life=60, size=3):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.life = life
        self.max_life = life
        self.size = size
        self.gravity = 0.1

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += self.gravity
        self.life -= 1
        
        # Fade out effect
        alpha = int(255 * (self.life / self.max_life))
        self.color = (*self.color[:3], max(0, alpha))

    def draw(self, screen):
        if self.life > 0:
            # Create surface with per-pixel alpha
            surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, self.color, (self.size, self.size), self.size)
            screen.blit(surf, (self.x - self.size, self.y - self.size))

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def add_explosion(self, x, y, color, count=15):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            life = random.randint(30, 60)
            size = random.randint(2, 5)
            self.particles.append(Particle(x, y, color, vel_x, vel_y, life, size))

    def add_trail(self, x, y, color, count=5):
        for _ in range(count):
            vel_x = random.uniform(-1, 1)
            vel_y = random.uniform(-3, -1)
            life = random.randint(20, 40)
            size = random.randint(1, 3)
            self.particles.append(Particle(x, y, color, vel_x, vel_y, life, size))

    def update(self):
        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.update()

    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)

# === Enhanced Rain Effect ===
class RainDrop:
    def __init__(self, screen_width, screen_height):
        self.x = random.randint(0, screen_width)
        self.y = random.randint(-screen_height, 0)
        self.length = random.randint(15, 25)
        self.speed = random.uniform(6, 12)
        self.thickness = random.randint(2, 4)
        # Varying shades of blue for depth
        blue_intensity = random.randint(100, 200)
        self.color = (blue_intensity//3, blue_intensity//2, blue_intensity)
        self.angle = random.uniform(-0.2, 0.2)  # Slight angle for realism

    def fall(self):
        self.y += self.speed
        self.x += self.angle * self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = random.randint(-100, -10)
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self, screen):
        end_x = self.x + self.angle * self.length
        end_y = self.y + self.length
        pygame.draw.line(screen, self.color, (self.x, self.y), (end_x, end_y), self.thickness)

# === Background Effects ===
class BackgroundEffect:
    def __init__(self):
        self.time = 0
        self.pulse_intensity = 0
        
    def update(self, beat_detected=False):
        self.time += 1
        if beat_detected:
            self.pulse_intensity = 20
        if self.pulse_intensity > 0:
            self.pulse_intensity -= 1
    
    def draw_gradient_background(self, screen):
        # Create animated gradient background
        base_color1 = (20 + self.pulse_intensity, 10 + self.pulse_intensity//2, 40 + self.pulse_intensity)
        base_color2 = (10 + self.pulse_intensity//2, 20 + self.pulse_intensity, 60 + self.pulse_intensity)
        
        # Simple gradient effect
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(base_color1[0] * (1 - ratio) + base_color2[0] * ratio)
            g = int(base_color1[1] * (1 - ratio) + base_color2[1] * ratio)
            b = int(base_color1[2] * (1 - ratio) + base_color2[2] * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

# === Enhanced Title Rendering ===
def render_neon_title_scaled(screen, font, screen_width, y_offset, scale, time_offset=0):
    title_texts = [
        ("F", NEON_RED),
        ("unky ", WHITE),
        ("F", NEON_CYAN), 
        ("low ", WHITE),
        ("F", NEON_VIOLET),
        ("riday", WHITE),
    ]

    total_width = sum(font.render(text, True, color).get_width() for text, color in title_texts)
    height = font.get_height()
    title_surface = pygame.Surface((total_width, height), pygame.SRCALPHA)

    x_offset = 0
    for i, (text, color) in enumerate(title_texts):
        # Add subtle wave motion to letters
        wave_y = math.sin(time_offset + i * 0.5) * 2
        
        # Enhanced glow effect
        for glow_size in range(5, 0, -1):
            glow_color = (*color[:3], 50)
            glow_surf = font.render(text, True, glow_color)
            for dx in range(-glow_size, glow_size + 1):
                for dy in range(-glow_size, glow_size + 1):
                    if dx*dx + dy*dy <= glow_size*glow_size:
                        title_surface.blit(glow_surf, (x_offset + dx, wave_y + dy))
        
        # Main text
        surf = font.render(text, True, color)
        shadow = font.render(text, True, DARK_SHADOW)
        title_surface.blit(shadow, (x_offset + 3, wave_y + 3))
        title_surface.blit(surf, (x_offset, wave_y))
        x_offset += surf.get_width()

    scaled_title = resizeObject(title_surface, scale)
    screen.blit(scaled_title, ((screen_width - scaled_title.get_width()) // 2, y_offset))

# === Enhanced Intro Screen ===
def show_intro_screen(screen):
    pygame.mixer.music.load('BackgroundTest/SoulChef.mp3')
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    screen_width, screen_height = screen.get_size()

    bg_back = pygame.transform.scale(pygame.image.load('assets/MainMenuSky.png').convert(), (screen_width, screen_height))
    bg_front = pygame.transform.scale(pygame.image.load('assets/MainMenuScreen.png').convert_alpha(), (screen_width, screen_height))

    font = atlantaFontLarge
    small_font = atlantaFont
    
    bg_x = 0
    scroll_speed = 1.5
    rain_drops = [RainDrop(screen_width, screen_height) for _ in range(200)]
    particles = ParticleSystem()
    bg_effect = BackgroundEffect()
    
    # Animation variables
    title_glow = 0
    title_pulse = 0
    prompt_fade = 0
    
    clock = pygame.time.Clock()
    running = True
    start_time = time.time()

    while running:
        current_time = time.time() - start_time
        
        # Background scroll
        bg_x = (bg_x + scroll_speed) % screen_width
        bg_effect.update()
        bg_effect.draw_gradient_background(screen)
        
        screen.blit(bg_back, (-bg_x, 0))
        screen.blit(bg_back, (screen_width - bg_x, 0))
        screen.blit(bg_front, (0, 50))

        # Enhanced rain with occasional lightning flash
        if random.randint(1, 300) == 1:  # Lightning chance
            flash_overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            flash_overlay.fill((255, 255, 255, 100))
            screen.blit(flash_overlay, (0, 0))
            
        for drop in rain_drops:
            drop.fall()
            drop.draw(screen)

        # Add some sparkle particles
        if random.randint(1, 10) == 1:
            particles.add_trail(random.randint(0, screen_width), 
                              random.randint(0, screen_height//3), 
                              (255, 255, 255, 200))

        particles.update()
        particles.draw(screen)

        # Animated title with time-based effects
        title_glow = math.sin(current_time * 2) * 0.5 + 1.5
        render_neon_title_scaled(screen, font, screen_width, y_offset=80, 
                                scale=title_glow, time_offset=current_time)

        # Pulsing prompt text
        prompt_fade = int(abs(math.sin(current_time * 3)) * 255)
        prompt_color = (prompt_fade, prompt_fade, prompt_fade)
        prompt = font.render("Press any key to continue...", True, prompt_color)
        screen.blit(prompt, ((screen_width - prompt.get_width()) // 2, 225))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # Add exit effect
                for _ in range(30):
                    particles.add_explosion(screen_width//2, screen_height//2, 
                                          (255, 255, 255, 255))
                running = False

        pygame.display.flip()
        clock.tick(60)

# HEALTH BAR
class HealthBar:
    def __init__(self, x, y, width, height, max_health):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_health = max_health
        
        # Load images once during initialization
        self.bg_img = self.load_health_image("assets/HealthBar.png")
        self.fg_img = self.load_health_image("assets/Health.png")
        self.splash_img = self.load_health_image("assets/BloodSplashClose.png")
        
        # Animation variables
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.pulse_scale = 1.0
    
    def load_health_image(self, path):
        """Safely load health bar images with fallback"""
        try:
            return pygame.image.load(path).convert_alpha()
        except pygame.error as e:
            print(f"Warning: Could not load {path}: {e}")
            return None
    
    def update(self, health, game_time):
        """Update health bar animations"""
        # Shake effect when health is low
        if health < self.max_health * 0.25:  # Shake when below 25% health
            self.shake_offset_x = random.randint(-SHAKE_INTENSITY, SHAKE_INTENSITY)
            self.shake_offset_y = random.randint(-SHAKE_INTENSITY, SHAKE_INTENSITY)
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0
        
        # Pulse effect when health is critical
        if health < self.max_health * 0.15:  # Pulse when below 15% health
            self.pulse_scale = 1.0 + 0.1 * math.sin(game_time * 0.01)
        else:
            self.pulse_scale = 1.0
    
    def draw(self, screen, health, splash_timer):
        """Draw the health bar with all effects"""
        # Calculate positions with shake effect
        draw_x = self.x + self.shake_offset_x
        draw_y = self.y + self.shake_offset_y
        
        # Apply pulse scaling
        scaled_width = int(self.width * self.pulse_scale)
        scaled_height = int(self.height * self.pulse_scale)
        
        # Adjust position to keep bar centered when scaling
        scaled_x = draw_x - (scaled_width - self.width) // 2
        scaled_y = draw_y - (scaled_height - self.height) // 2
        
        # Draw background
        self.draw_background(screen, scaled_x, scaled_y, scaled_width, scaled_height)
        
        # Draw health fill
        self.draw_health_fill(screen, scaled_x, scaled_y, scaled_width, scaled_height, health)
        
        # Draw border
        self.draw_border(screen, scaled_x, scaled_y, scaled_width, scaled_height, health)
        
        # Draw blood splash effect
        if pygame.time.get_ticks() - splash_timer < BLOOD_SPLASH_DURATION:
            self.draw_blood_splash(screen, scaled_x, scaled_y, scaled_width, scaled_height)
    
    def draw_background(self, screen, x, y, width, height):
        """Draw the health bar background"""
        if self.bg_img:
            try:
                bg_scaled = pygame.transform.scale(self.bg_img, (width, height))
                screen.blit(bg_scaled, (x, y))
            except pygame.error:
                # Fallback to simple rectangle
                pygame.draw.rect(screen, GRAY, (x, y, width, height))
                pygame.draw.rect(screen, BLACK, (x, y, width, height), 2)
        else:
            # Simple background fallback
            pygame.draw.rect(screen, GRAY, (x, y, width, height))
            pygame.draw.rect(screen, BLACK, (x, y, width, height), 2)
    
    def draw_health_fill(self, screen, x, y, width, height, health):
        """Draw the health fill portion"""
        health_ratio = max(0, min(1, health / self.max_health))
        fill_width = int(width * health_ratio)
        
        if fill_width <= 0:
            return
        
        if self.fg_img:
            try:
                # Create a surface for the health fill
                fill_surface = pygame.Surface((fill_width, height), pygame.SRCALPHA)
                
                # Scale the foreground image to match the full bar size
                scaled_fg = pygame.transform.scale(self.fg_img, (width, height))
                
                # Blit only the portion we need
                fill_surface.blit(scaled_fg, (0, 0), (0, 0, fill_width, height))
                
                screen.blit(fill_surface, (x, y))
            except pygame.error:
                # Fallback to colored rectangle
                self.draw_colored_health_fill(screen, x, y, fill_width, height, health)
        else:
            # Simple colored fill fallback
            self.draw_colored_health_fill(screen, x, y, fill_width, height, health)
    
    def draw_colored_health_fill(self, screen, x, y, width, height, health):
        """Draw a simple colored health fill as fallback"""
        health_ratio = health / self.max_health
        
        # Color based on health level
        if health_ratio > 0.6:
            color = GREEN
        elif health_ratio > 0.3:
            color = YELLOW
        else:
            color = RED
        
        pygame.draw.rect(screen, color, (x, y, width, height))
    
    def draw_border(self, screen, x, y, width, height, health):
        """Draw border and health text"""
        # Draw border
        border_color = WHITE if health > self.max_health * 0.25 else RED
        pygame.draw.rect(screen, border_color, (x - 2, y - 2, width + 4, height + 4), 2)
        
        # Draw health text
        health_text = f"{int(health)}/{int(self.max_health)}"
        text_surface = atlantaFont.render(health_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        
        # Add text shadow for better readability
        shadow_surface = atlantaFont.render(health_text, True, BLACK)
        shadow_rect = text_rect.copy()
        shadow_rect.x += 1
        shadow_rect.y += 1
        screen.blit(shadow_surface, shadow_rect)
        screen.blit(text_surface, text_rect)
    
    def draw_blood_splash(self, screen, x, y, width, height):
        """Draw blood splash effect"""
        if self.splash_img:
            try:
                splash_width = width + 40
                splash_height = height + 40
                splash_scaled = pygame.transform.scale(self.splash_img, (splash_width, splash_height))
                
                # Center the splash on the health bar
                splash_x = x - 55
                splash_y = y - 20
                
                screen.blit(splash_scaled, (splash_x, splash_y))
            except pygame.error:
                # Simple red flash fallback
                flash_surface = pygame.Surface((width + 20, height + 20), pygame.SRCALPHA)
                flash_surface.fill((255, 0, 0, 100))
                screen.blit(flash_surface, (x - 10, y - 10))

class Result:
    def __init__(self, final_score, max_score, font_path, pulse_rate=2.0):
        self.score = final_score
        self.max_score = max_score
        self.font_path = font_path
        self.pulse_rate = pulse_rate
        self.values = self.calculate_score_chunks()

    def calculate_score_chunks(self):
        third = self.max_score // 3
        return [
            min(10, int((self.score / third))) if self.score >= i * third else 0
            for i in range(1, 4)
        ]

    def draw(self, screen):
        spacing = 150
        card_width = 100
        card_height = 150
        total_width = spacing * (len(self.values) - 1)
        start_x = SCREEN_WIDTH // 2 - total_width // 2
        top_margin = 80  # Adjust this to move it up/down

        # Pulse effect
        tick = pygame.time.get_ticks() / 1000
        pulse_scale = 1 + 0.05 * math.sin(tick * self.pulse_rate)

        for i, value in enumerate(self.values):
            # Scaled dimensions
            scaled_width = int(card_width * pulse_scale)
            scaled_height = int(card_height * pulse_scale)
            scaled_font_size = int(60 * pulse_scale)
            result_font = load_font(self.font_path, scaled_font_size)

            # Position
            x = start_x + i * spacing
            rect_x = x - scaled_width // 2
            rect_y = top_margin
            center_x = x
            center_y = rect_y + scaled_height // 2

            # Draw card
            card_rect = pygame.Rect(rect_x, rect_y, scaled_width, scaled_height)
            pygame.draw.rect(screen, WHITE, card_rect, border_radius=15)
            pygame.draw.rect(screen, BLACK, card_rect, 3, border_radius=15)

            # Draw number centered inside card
            text_surface = result_font.render(str(value), True, BLACK)
            text_rect = text_surface.get_rect(center=(center_x, center_y))
            screen.blit(text_surface, text_rect)

def get_performance_rank(score, max_score):
    ratio = score / max_score
    if ratio >= 0.95:
        return "SSS", GOLD
    elif ratio >= 0.85:
        return "SS", YELLOW
    elif ratio >= 0.70:
        return "S", LIGHT_BLUE
    elif ratio >= 0.55:
        return "A", GREEN
    elif ratio >= 0.40:
        return "B", ORANGE
    elif ratio >= 0.20:
        return "C", RED
    else:
        return "", WHITE  


class RedFlag:
    def __init__(self, x, y, size=48, pole_height=64, pole_width=6):
        self.x = x
        self.y = y
        self.size = size
        self.pole_height = pole_height
        self.pole_width = pole_width

    def draw(self, surface):
        # Draw golden pole
        pole = pygame.Rect(self.x, self.y, self.pole_width, self.pole_height)
        pygame.draw.rect(surface, GOLD, pole)
        pygame.draw.rect(surface, BLACK, pole, 2)  # outline

        # Draw blocky red triangle (right pointing)
        p1 = (self.x + self.pole_width, self.y + 0)
        p2 = (self.x + self.pole_width + self.size, self.y + self.size // 2)
        p3 = (self.x + self.pole_width, self.y + self.size)
        pygame.draw.polygon(surface, RED, [p1, p2, p3])
        pygame.draw.polygon(surface, BLACK, [p1, p2, p3], 2)  # outline

class FinishLineFlag:
    def __init__(self, x, y, cols=6, rows=4, square_size=12, pole_height=64, pole_width=6):
        self.x = x
        self.y = y
        self.cols = cols
        self.rows = rows
        self.square_size = square_size
        self.pole_height = pole_height
        self.pole_width = pole_width

    def draw(self, surface):
        # Draw golden pole
        pole = pygame.Rect(self.x, self.y, self.pole_width, self.pole_height)
        pygame.draw.rect(surface, GOLD, pole)
        pygame.draw.rect(surface, BLACK, pole, 2)

        # Draw checkered pattern
        for row in range(self.rows):
            for col in range(self.cols):
                color = BLACK if (row + col) % 2 == 0 else WHITE
                rect = pygame.Rect(
                    self.x + self.pole_width + col * self.square_size,
                    self.y + row * self.square_size,
                    self.square_size,
                    self.square_size
                )
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, BLACK, rect, 1)  # outline


# === Level Configuration ===
LEVELS = {
    1: {"name": "Level 1", "win_threshold": 2000, "arrow_speed": 5, "note_interval_start": 1.5, "note_interval_min": 0.35, "unlocked": True, "background_func": draw_bg_1},
    2: {"name": "Level 2", "win_threshold": 2000, "arrow_speed": 8, "note_interval_start": 1.5, "note_interval_min": 0.3, "unlocked": False, "background_func": draw_bg_2},
    3: {"name": "Level 3", "win_threshold": 2000, "arrow_speed": 10, "note_interval_start": 1.5, "note_interval_min": 0.3, "unlocked": False, "background_func": draw_bg_3}
}



# === Enhanced Colors ===
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
BLUE = (0, 191, 255)
LIGHT_BLUE = (173, 216, 230)
PURPLE = (128, 0, 128)
DARK_SHADOW = (30, 30, 30)
NEON_RED = (255, 50, 50)
NEON_CYAN = (50, 255, 255)
NEON_VIOLET = (200, 50, 255)
NEON_GREEN = (50, 255, 50)
NEON_YELLOW = (255, 255, 50)
GOLD = (255, 200, 50)


# === Key Bindings ===
KEY_BINDINGS = {
    pygame.K_LEFT: "left",
    pygame.K_a: "left",
    pygame.K_DOWN: "down", 
    pygame.K_s: "down",
    pygame.K_UP: "up",
    pygame.K_w: "up",
    pygame.K_RIGHT: "right",
    pygame.K_d: "right"
}


ARROW_IMAGE_MAPPING = {
    "left": ["assets/arrowSkinLeftDefault.png", "assets/arrowSkinLeftGlow.png"],
    "down": ["assets/arrowSkinDownDefault.png", "assets/arrowSkinDownGlow.png"],
    "up": ["assets/arrowSkinUpDefault.png", "assets/arrowSkinUpGlow.png"],  
    "right": ["assets/arrowSkinRightDefault.png", "assets/arrowSkinRightGlow.png"]
}

def load_image(file_path, fallback_path=None):
    try:
        return pygame.image.load(file_path).convert_alpha()
    except pygame.error:
        if fallback_path:
            return pygame.image.load(fallback_path).convert_alpha()
        raise

def load_arrow_images():
    def scaled_image(path):
        return pygame.transform.scale(load_image(path), (ARROW_SIZE, ARROW_SIZE))

    arrows, glowing = {}, {}
    for direction, (default_path, glow_path) in ARROW_IMAGE_MAPPING.items():
        try:
            arrows[direction] = scaled_image(default_path)
            glowing[direction] = scaled_image(glow_path)
        except Exception as e:
            raise SystemExit(f"Error loading {direction} arrows: {e}")
    return arrows, glowing

def load_lose_image():
    try:
        img = pygame.image.load("assets/LOSE.png").convert_alpha()
        return resizeObject(img, 2)
    except pygame.error as e:
        print(f"Failed to load LOSE.png: {e}")
        return None

def load_win_image():
    try:
        img = pygame.image.load("assets/WIN.png").convert_alpha()
        return resizeObject(img, 2)
    except pygame.error as e:
        print(f"Failed to load WIN.png: {e}")
        return None

def heartbeat_scale(base_size, pulse_rate, time_ms):
    scale_factor = 1 + 0.05 * math.sin(time_ms * pulse_rate)
    new_size = int(base_size[0] * scale_factor), int(base_size[1] * scale_factor)
    return new_size

def render_text_centered(screen, text, font, color, y_offset):
    rendered = font.render(text, True, color)
    x = (SCREEN_WIDTH - rendered.get_width()) // 2
    screen.blit(rendered, (x, y_offset))

# === Enhanced Note Class ===
class Note:
    def __init__(self, direction, x, speed):
        self.direction = direction
        self.x = x
        self.y = SCREEN_HEIGHT
        self.speed = speed
        self.hit = self.missed = False
        self.glow_intensity = 0
        self.rotation = 0
        self.scale = 1.0
        
    def update(self):
        self.y -= self.speed
        self.rotation += 0  # Gentle rotation
        
        # Distance-based glow effect
        distance_to_target = abs(self.y - TARGET_Y)
        if distance_to_target < 100:
            self.glow_intensity = max(0, 100 - distance_to_target) / 100
            self.scale = 1.0 + self.glow_intensity * 0.2
        
        if self.y < TARGET_Y - 50 and not self.hit:
            self.missed = True

    def draw(self, screen, image, particles):
        if not self.hit and not self.missed:
            # Add trail effect when close to target
            if self.glow_intensity > 0.3:
                particles.add_trail(self.x, self.y, NEON_CYAN)
            
            # Scale and rotate the note
            if self.scale != 1.0 or self.rotation != 0:
                scaled_img = pygame.transform.scale(image, 
                    (int(ARROW_SIZE * self.scale), int(ARROW_SIZE * self.scale)))
                rotated_img = pygame.transform.rotate(scaled_img, self.rotation)
                rect = rotated_img.get_rect(center=(self.x, self.y))
                screen.blit(rotated_img, rect)
            else:
                rect = image.get_rect(center=(self.x, self.y))
                screen.blit(image, rect)
            
            # Add glow effect
            if self.glow_intensity > 0:
                glow_surf = pygame.Surface((ARROW_SIZE * 2, ARROW_SIZE * 2), pygame.SRCALPHA)
                glow_color = (*NEON_CYAN[:3], int(50 * self.glow_intensity))
                pygame.draw.circle(glow_surf, glow_color, 
                                 (ARROW_SIZE, ARROW_SIZE), int(ARROW_SIZE * self.glow_intensity))
                screen.blit(glow_surf, (self.x - ARROW_SIZE, self.y - ARROW_SIZE))

def load_progress():
    try:
        with open(SAVE_FILE, 'r') as f:
            progress = json.load(f)
            for level_id, is_unlocked in progress.items():
                if int(level_id) in LEVELS:
                    LEVELS[int(level_id)]["unlocked"] = is_unlocked
    except (FileNotFoundError, json.JSONDecodeError):
        save_progress()

def save_progress():
    progress = {str(level_id): level["unlocked"] for level_id, level in LEVELS.items()}
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(progress, f)
    except Exception as e:
        print(f"Error saving progress: {e}")

def load_beatmap(filename="beatmap.json"):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Beatmap not found.")
        return []
    
def play_intro(screen, clock, font, big_font):
    axel = Character(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, SCREEN_WIDTH, SCREEN_HEIGHT, 8)

    text_lines = [
        "A long time ago...",
        "Ray Gun — a pro dancer — embarrassed the dance community.",
        "He crushed the spirit of freestylers everywhere.",
        "But now...",
        "One dancer will rise...",
        "To restore the rhythm.",
        "To bring the flow back.",
        "To become a legend.",
        "His name is...",
        "AXEL!",
        "FUNKY FLOW FRIDAY — LET'S DANCE."
    ]

    current_line = 0
    line_timer = pygame.time.get_ticks()
    line_delay = 2500  # 2.5 seconds per line
    fade_duration = 500  # ms
    fade_in = True
    alpha = 0

    running = True
    while running:
        screen.fill((0, 0, 0))  # Black background

        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        # Skip on Enter or Space
        if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
            return

        # Manage line change
        if current_time - line_timer > line_delay:
            line_timer = current_time
            current_line += 1
            fade_in = True
            alpha = 0
            if current_line >= len(text_lines):
                running = False

        # Character animation
        axel.update(keys)
        axel.draw(screen)

        # Show line with fade-in
        if current_line < len(text_lines):
            text = text_lines[current_line]
            rendered_text = font.render(text, True, (255, 255, 255))
            fade_surface = pygame.Surface(rendered_text.get_size(), pygame.SRCALPHA)

            if fade_in and alpha < 255:
                alpha += 255 // (fade_duration // (1000 // 60))  # Estimate based on 60 FPS
                alpha = min(255, alpha)
            else:
                alpha = 255

            fade_surface.blit(rendered_text, (0, 0))
            fade_surface.set_alpha(alpha)
            text_rect = fade_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
            screen.blit(fade_surface, text_rect)

        # # Add top-right "Press ENTER to skip"
        # skip_text = font.render("Press ENTER to skip", True, (200, 200, 200))
        # screen.blit(skip_text, (SCREEN_WIDTH - skip_text.get_width() - 20, 20))

        # Add centered game title during final line
        if current_line == len(text_lines) - 1:
            title_surface = big_font.render("FUNKY FLOW FRIDAY", True, (255, 215, 0))
            screen.blit(title_surface, title_surface.get_rect(center=(SCREEN_WIDTH // 2, 80)))

        pygame.display.flip()
        clock.tick(60)



# === Enhanced Menu System ===
def show_menu(screen, clock, font, big_font):
    menu_active = True
    selected_option = 0
    options = []
    particles = ParticleSystem()
    bg_effect = BackgroundEffect()
    menu_time = 0

    for level_id, level_data in sorted(LEVELS.items()):
        if level_data["unlocked"]:
            options.append((level_id, f"{level_data['name']} - Ready"))
        else:
            options.append((level_id, f"{level_data['name']} - LOCKED"))
    
    options.append(("quit", "Quit Game"))
    
    while menu_active:
        menu_time += 1
        bg_effect.update()
        bg_effect.draw_gradient_background(screen)
        
        # Add some ambient particles
        if random.randint(1, 20) == 1:
            particles.add_trail(random.randint(0, SCREEN_WIDTH), 
                              random.randint(0, SCREEN_HEIGHT), 
                              random.choice([NEON_CYAN, NEON_VIOLET, NEON_RED]))
        
        particles.update()
        particles.draw(screen)
        
        # Animated title
        render_neon_title_scaled(screen, big_font, SCREEN_WIDTH, 50, 1.5, menu_time * 0.02)

        render_text_centered(screen, "Choose a level", font, WHITE, 150)
        
        # Enhanced menu options with hover effects
        for i, (level_id, text) in enumerate(options):
            is_selected = i == selected_option
            
            if is_selected:
                # Add selection glow effect
                glow_surf = pygame.Surface((400, 60), pygame.SRCALPHA)
                glow_color = (*NEON_CYAN[:3], 30)
                pygame.draw.rect(glow_surf, glow_color, (0, 0, 400, 60), border_radius=10)
                screen.blit(glow_surf, (SCREEN_WIDTH//2 - 200, 190 + i * 60 - 10))
                
                color = NEON_YELLOW
                # Add selection particles
                if random.randint(1, 5) == 1:
                    particles.add_trail(SCREEN_WIDTH//2 + random.randint(-100, 100), 
                                      200 + i * 60, NEON_YELLOW)
            else:
                color = WHITE
                
            if level_id != "quit" and not LEVELS[level_id]["unlocked"]:
                color = GRAY
                
            option_text = font.render(text, True, color)
            position = (SCREEN_WIDTH // 2 - option_text.get_width() // 2, 200 + i * 60)
            screen.blit(option_text, position)
            
            if is_selected:
                # Animated arrow indicator
                arrow_x = position[0] - 50 + math.sin(menu_time * 0.1) * 5
                indicator = font.render("►", True, color)
                screen.blit(indicator, (arrow_x, position[1]))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                    particles.add_explosion(SCREEN_WIDTH//2, 200 + selected_option * 60, NEON_CYAN)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                    particles.add_explosion(SCREEN_WIDTH//2, 200 + selected_option * 60, NEON_CYAN)
                elif event.key == pygame.K_RETURN:
                    level_id, _ = options[selected_option]
                    if level_id == "quit":
                        pygame.quit()
                        sys.exit()
                    elif LEVELS[level_id]["unlocked"]:
                        # Add selection effect
                        particles.add_explosion(SCREEN_WIDTH//2, 200 + selected_option * 60, 
                                              NEON_GREEN, 25)
                        return level_id
        
        clock.tick(60)


# === Game Loop ===
def play_level(screen, clock, font, big_font, level_id):
    level_config = LEVELS[level_id]
    arrow_speed = level_config["arrow_speed"]
    # win_threshold = level_config["win_threshold"]
    note_interval_start = level_config["note_interval_start"]
    note_interval_min = level_config["note_interval_min"]


    # Initialize game state variables FIRST
    global combo
    notes, score, combo, misses, health = [], 0, 0, 0, INITIAL_HEALTH
    game_over = game_won = paused = False
    current_rating = None
    rating_timer = 0
    last_note_time = time.time()
    note_interval = note_interval_start
    blood_splash_timer = 0
    result_shown = False




    # # Load health bar images
    # health_bg_img = None
    # health_fg_img = None
    # try:
    #     health_bg_img = pygame.image.load("assets/HealthBar.png").convert_alpha()
    #     health_fg_img = pygame.image.load("assets/Health.png").convert_alpha()
    # except:
    #     print("Health bar images not found, using fallback")

    # Load blood splash images
    try:
        bloodSplashWide = pygame.image.load("assets/BloodSplashWide.png").convert_alpha()
        bloodSplashClose = pygame.image.load("assets/BloodSplashClose.png").convert_alpha()
    except:
        print("Blood splash images not found")
        bloodSplashWide = None
        bloodSplashClose = None

    # Now create the HealthBar object with properly initialized variables
    HEALTH_BAR_Y = TARGET_Y - 60  # You can tweak 60 for better spacing
    health_bar = HealthBar(SCREEN_WIDTH // 2 - HEALTH_BAR_WIDTH // 2, HEALTH_BAR_Y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT, MAX_HEALTH)

    # Load beatmap and music based on level
    beat_times = load_beatmap()
    beat_index = 0
    

    if level_id == 1:
        beat_times = load_beatmap("beatmap5.json")
        pygame.mixer.music.load("music/eighties.mp3")
        song_length = pygame.mixer.Sound("music/eighties.mp3").get_length()
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play()


    elif level_id == 2:
        beat_times = load_beatmap("beatmap2.json")
        pygame.mixer.music.load("music/SoulChef.mp3")
        song_length = pygame.mixer.Sound("music/SoulChef.mp3").get_length()
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play()

    elif level_id == 3:
        beat_times = load_beatmap("beatmap.json")
        pygame.mixer.music.load("music/Tetris.mp3")
        song_length = pygame.mixer.Sound("music/Tetris.mp3").get_length()
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play()

    arrows, glowing_arrows = load_arrow_images()

    # Set x positions for each arrow target
    targets = {
        "left": SCREEN_WIDTH // 2 - ARROW_SPACING * 2.0,
        "down": SCREEN_WIDTH // 2 - ARROW_SPACING * 0.75,
        "up": SCREEN_WIDTH // 2 + ARROW_SPACING * 0.75,
        "right": SCREEN_WIDTH // 2 + ARROW_SPACING * 2.0
    }

    # Glow state and timers for each arrow direction
    target_arrows = {
        dir: {"x": x, "glow": False, "timer": 0} for dir, x in targets.items()
    }

    # Pre-rendered rating texts
    ratings = {
        "perfect": pixelGameFont.render("PERFECT!", True, GREEN),
        "good": pixelGameFont.render("GOOD", True, YELLOW),
        "bad": pixelGameFont.render("BAD", True, ORANGE),
        "miss": pixelGameFont.render("MISS", True, RED)
    }

    level_title = pixelGameFont.render(f"{level_config['name']}", True, BLUE)
    particles = ParticleSystem()
    character = Character(
        SCREEN_WIDTH // 2 - 50,  # Approx half-width of character
        SCREEN_HEIGHT // 2 + 100,  # Slightly below center (adjust as needed)
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        4
    )

    # === Game Loop ===
    running = True
    while running:
        current_time = pygame.time.get_ticks()



        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.KEYDOWN: 
                if e.key == pygame.K_ESCAPE:
                    pygame.mixer.music.stop()
                    return "menu"
                if (game_over or game_won) and e.key == pygame.K_r:
                    return play_level(screen, clock, font, big_font, level_id)  # Restart level
                if (game_over or game_won) and e.key == pygame.K_m:
                    pygame.mixer.music.stop()
                    return "menu"
                if not (game_over or game_won):
                    direction = KEY_BINDINGS.get(e.key)
                    if direction:
                        target_arrows[direction]["glow"] = True
                        target_arrows[direction]["timer"] = GLOW_DURATION
                        hit = False
                        for note in notes:
                            if note.direction == direction and not note.hit and not note.missed:
                                distance = abs(note.y - TARGET_Y)
                                if distance < 15:
                                    score += 100
                                    combo += 2
                                    current_rating = ratings["perfect"]
                                    health = min(MAX_HEALTH, health + 10)
                                elif distance < 35:
                                    score += 50
                                    combo += 1
                                    current_rating = ratings["good"]
                                    health = min(MAX_HEALTH, health + 5)
                                elif distance < 55:
                                    score += 10
                                    combo = 0
                                    current_rating = ratings["bad"]
                                    health = min(MAX_HEALTH, health + 2)
                                else:
                                    continue
                                note.hit = True
                                hit = True
                                rating_timer = RATING_DISPLAY_TIME
                                break
                        if not hit:
                            combo = 0
                            current_rating = ratings["miss"]
                            rating_timer = RATING_DISPLAY_TIME
                            health = max(0, health - 5)
                            blood_splash_timer = pygame.time.get_ticks()

        # Check win/loss conditions
        current_time = pygame.mixer.music.get_pos() / 1000.0
        if current_time >= song_length - 0.5:
            game_won, paused = True, True
            pygame.mixer.music.stop()
            if level_id < max(LEVELS.keys()):
                LEVELS[level_id + 1]["unlocked"] = True
                save_progress()

            
        if health <= 0:
            pygame.mixer.music.stop()
            game_over, paused = True, True

        # Spawn notes at intervals
        if not paused:
            if time.time() - last_note_time > note_interval:
                direction = random.choice(list(targets.keys()))
                notes.append(Note(direction, targets[direction], arrow_speed))
                last_note_time = time.time()
                note_interval = max(note_interval_min, note_interval * 0.99)
        
        # Spawn notes based on beat timestamps
        current_time_sec = pygame.mixer.music.get_pos() / 1000.0
        if not paused and beat_index < len(beat_times):
            if current_time_sec >= beat_times[beat_index]:
                direction = random.choice(list(targets.keys()))
                notes.append(Note(direction, targets[direction], arrow_speed))
                beat_index += 1

        # Update glow timers
        for ta in target_arrows.values():
            if ta["timer"] > 0:
                ta["timer"] -= 1
                if ta["timer"] == 0:
                    ta["glow"] = False

        # Update and remove notes
        if not paused:
            for note in notes[:]:
                note.update()
                if note.missed:
                    misses += 1
                    combo = 0
                    current_rating = ratings["miss"]
                    rating_timer = RATING_DISPLAY_TIME
                    health = max(0, health - 5)
                    blood_splash_timer = pygame.time.get_ticks()
                if note.y < 0 or note.hit:
                    notes.remove(note)

        if rating_timer > 0:
            rating_timer -= 1

        # Update particles
        particles.update()

        # === Drawing Section ===
        # Use background function for this level
        bg_func = level_config.get("background_func")
        if bg_func:
            bg_func(screen)

        else:
            screen.fill(RED)  # Fallback background
            print("Drawing red background...")

        keys = pygame.key.get_pressed()
        character.update(keys)
        character.draw(screen)

        # Level title at the top
        screen.blit(level_title, (SCREEN_WIDTH // 2 - level_title.get_width() // 2, 10))

        # Draw target arrows
        for dir, data in target_arrows.items():
            image = glowing_arrows[dir] if data["glow"] else arrows[dir]
            rect = image.get_rect(center=(data["x"], TARGET_Y))
            screen.blit(image, rect)
            pygame.draw.line(screen, GRAY, (data["x"] - ARROW_SIZE, TARGET_Y), (data["x"] + ARROW_SIZE, TARGET_Y), 2)

        # Draw falling notes
        for note in notes:
            note.draw(screen, arrows[note.direction], particles)

        # Draw particles
        particles.draw(screen)

        # UI: Score, combo, misses, health
        # screen.blit(font.render(f"Score: {score}/{max_score}", True, WHITE), (20, 20))
        # screen.blit(font.render(f"Combo: {combo}", True, WHITE), (20, 60))
        # screen.blit(font.render(f"Misses: {misses}", True, WHITE), (20, 100))

        combo_text = pixelGameFontLarge.render(f"{combo} Combo", True, YELLOW)
        combo_x = SCREEN_WIDTH - combo_text.get_width() - 60  # right-aligned
        combo_y = SCREEN_HEIGHT // 2 - 40
        screen.blit(combo_text, (combo_x, combo_y))

        rank, rank_color = get_performance_rank(score, max_score)
        rank_text = pixelGameFontHuge.render(rank, True, rank_color)
        rank_x = SCREEN_WIDTH - rank_text.get_width() - 60
        rank_y = combo_y + combo_text.get_height() + 10
        screen.blit(rank_text, (rank_x, rank_y))



        # Update and draw health bar
        health_bar.update(health, current_time)
        health_bar.draw(screen, health, blood_splash_timer)

        # Progress bar toward win
        # Draw progress bar line
        pygame.draw.line(screen, WHITE, (PROGRESS_BAR_X, PROGRESS_BAR_Y), 
                        (PROGRESS_BAR_X + PROGRESS_BAR_LENGTH, PROGRESS_BAR_Y), 4)

        # Calculate red flag position
        current_time_sec = pygame.mixer.music.get_pos() / 1000.0
        progress_ratio = min(1.0, current_time_sec / song_length)
        red_flag_x = PROGRESS_BAR_X + int(PROGRESS_BAR_LENGTH * progress_ratio)
        f"{int(current_time_sec)} / {int(song_length)} sec"
        time_text = font.render(f"{int(current_time_sec)} / {int(song_length)} sec", True, WHITE)
        screen.blit(time_text, (PROGRESS_BAR_X, PROGRESS_BAR_Y - 30))

        # Draw flags
        red_flag = RedFlag(red_flag_x, PROGRESS_BAR_Y - 40)
        finish_flag = FinishLineFlag(PROGRESS_BAR_X + PROGRESS_BAR_LENGTH, PROGRESS_BAR_Y - 40)

        red_flag.draw(screen)
        finish_flag.draw(screen)


        # Display rating
        if rating_timer > 0 and current_rating:
            rect = current_rating.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(current_rating, rect)

        # === Game Over or Win Screens ===
        if game_over or game_won:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            tickSpeed = pygame.time.get_ticks() / 1000

            if game_over:
                if LOSE_IMAGE:
                    size = heartbeat_scale(LOSE_IMAGE.get_size(), pulse_rate=3.5, time_ms=tickSpeed)
                    scaled = pygame.transform.smoothscale(LOSE_IMAGE, size)
                    lose_rect = scaled.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
                    screen.blit(scaled, lose_rect)
                else:
                    screen.blit(pixelGameFontLarge.render("GAME OVER", True, RED), (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50))

                screen.blit(pixelGameFont.render("Press R to restart, M for menu, ESC to quit", True, WHITE), 
                            (SCREEN_WIDTH // 2 - 210, SCREEN_HEIGHT // 2 + 10))

            elif game_won:
                # screen.blit(pixelGameFontLarge.render("LEVEL COMPLETE!", True, GREEN), 
                #             (SCREEN_WIDTH // 2 - 50 , SCREEN_HEIGHT // 2 - 50))
                
                if WIN_IMAGE:
                    size = heartbeat_scale(WIN_IMAGE.get_size(), pulse_rate=3.5, time_ms=tickSpeed)
                    scaled = pygame.transform.smoothscale(WIN_IMAGE, size)
                    win_rect = scaled.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
                    screen.blit(scaled, win_rect)
                
                if not result_shown:
                    result = Result(score, max_score, "assets/PixelGame.otf")
                    result_shown = True

                if result_shown:
                    result.draw(screen)


                if level_id < max(LEVELS.keys()):
                    next_level_text = font.render(f"Level {level_id + 1} Unlocked!", True, YELLOW)
                    screen.blit(next_level_text, (SCREEN_WIDTH // 2 - next_level_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
                
                screen.blit(pixelGameFont.render("Press R to replay, M for menu, ESC to quit", True, WHITE), 
                            (SCREEN_WIDTH // 2 - 210, SCREEN_HEIGHT // 2 + 80))

        # Instruction line
        else:
            instructions = pixelGameFont.render("Press arrow keys when notes align with targets", True, WHITE)
            screen.blit(instructions, instructions.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)))

        pygame.display.flip()
        clock.tick(60)

    return "menu"

# === Main Function ===
def main():
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("FUNKY FLOW FRIDAY")
    clock = pygame.time.Clock()

    play_intro(screen, clock, pixelGameFontLarge, pixelGameFontHuge)


    font = moldieFont
    big_font = atlantaFontLarge

 
    global LOSE_IMAGE, WIN_IMAGE
    LOSE_IMAGE = load_lose_image()
    WIN_IMAGE = load_win_image()

    show_intro_screen(screen)
    
    # Load saved progress
    load_progress()
    
    # Game state
    game_state = "menu"
    
    # Main game loop
    while True:
        if game_state == "menu":
            level_id = show_menu(screen, clock, font, big_font)
            game_state = level_id
        else:
            game_state = play_level(screen, clock, font, big_font, game_state)

# Run the game
def run_game():
    main()

if __name__ == "__main__":
    main()