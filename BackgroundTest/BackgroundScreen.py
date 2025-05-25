# BackgroundLvl1.py – Dynamic background with combo-based golden tint & multicolored extended spotlights

import pygame
import math
import random
import os
import colorsys

BASE_PATH = os.path.dirname(__file__)

# Screen scaling
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
BASE_WIDTH = 1280
BASE_HEIGHT = 720
scale_x = SCREEN_WIDTH / BASE_WIDTH
scale_y = SCREEN_HEIGHT / BASE_HEIGHT
scale = min(scale_x, scale_y)

# Combo import
try:
    import __main__
    MAIN_MODULE_AVAILABLE = True
except ImportError:
    MAIN_MODULE_AVAILABLE = False


def get_current_combo() -> int:
    """Retrieve combo from main game module if available."""
    if MAIN_MODULE_AVAILABLE:
        try:
            if hasattr(__main__, 'combo'):
                return __main__.combo
            if hasattr(__main__, 'current_combo'):
                return __main__.current_combo
        except:
            pass
    return 0


def scale_image(image: pygame.Surface, factor: float) -> pygame.Surface:
    width = int(image.get_width() * factor)
    height = int(image.get_height() * factor)
    return pygame.transform.scale(image, (width, height))


class Spotlight:
    def __init__(self, x, color=None, cone_angle=20):
        self.x = x
        self.y = 0  # originate from very top
        self.color = color or (255, 255, 255)
        self.alpha = 80
        self.cone_angle = cone_angle
        self.flicker_amount = 0
        self.swing_amount = SCREEN_WIDTH  # wide swing
        self.swing_speed = random.uniform(0.01, 0.03)
        self.swing_time = random.uniform(0, math.pi * 2)
        self.movement_pattern = "sweep"
        self.pattern_time = 0
        self.pattern_speed = random.uniform(0.02, 0.04)
        self.circular_radius = SCREEN_WIDTH  # extend off-screen
        self.zigzag_phase = random.uniform(0, math.pi)

    def set_movement_pattern(self, pattern):
        self.movement_pattern = pattern
        self.pattern_time = 0

    def update(self):
        self.pattern_time += self.pattern_speed
        flicker = random.uniform(-self.flicker_amount, self.flicker_amount)
        self.alpha = max(50, min(150, self.alpha + flicker))
        combo = get_current_combo()
        # choose movement
        if self.movement_pattern == "sweep":
            self.swing_time += self.swing_speed
            self.target_x = self.x + math.sin(self.swing_time) * self.swing_amount
            self.target_y = SCREEN_HEIGHT + 100
        elif self.movement_pattern == "circular":
            ang = self.pattern_time
            self.target_x = self.x + math.cos(ang) * self.circular_radius
            self.target_y = self.y + math.sin(ang) * SCREEN_HEIGHT
        elif self.movement_pattern == "zigzag" and combo >= 10:
            self.target_x = self.x + math.sin(self.pattern_time * 3) * self.circular_radius
            self.target_y = SCREEN_HEIGHT + 100
        else:
            # fallback to sweep if not zigzag or combo < 10
            self.swing_time += self.swing_speed
            self.target_x = self.x + math.sin(self.swing_time) * self.swing_amount
            self.target_y = SCREEN_HEIGHT + 100

    def draw(self, surface):
        cone = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)
        ang = math.atan2(dy, dx)
        width = 2 * dist * math.tan(math.radians(self.cone_angle / 2))
        base_hue = (pygame.time.get_ticks() * 0.0001 + self.x/SCREEN_WIDTH) % 1.0
        layers = 8
        for i in range(layers):
            hue = (base_hue + i / layers) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            alpha = int(self.alpha * (layers - i) / layers)
            color = (int(r*255), int(g*255), int(b*255), alpha)
            scale_f = 1 + i * 0.1
            end_x = self.x + math.cos(ang) * dist * scale_f
            end_y = self.y + math.sin(ang) * dist * scale_f
            left_x = end_x - math.sin(ang) * width * scale_f / 2
            left_y = end_y + math.cos(ang) * width * scale_f / 2
            right_x = end_x + math.sin(ang) * width * scale_f / 2
            right_y = end_y - math.cos(ang) * width * scale_f / 2
            pts = [(self.x, self.y), (left_x, left_y), (right_x, right_y)]
            pygame.draw.polygon(cone, color, pts)
        surface.blit(cone, (0, 0))

# Resource init
initialized = False
spotlights = []
darkened_bg = None
speaker_left1 = speaker_left2 = None
speaker_right1 = speaker_right2 = None
left_speaker_pos = right_speaker_pos = (0, 0)
use_first_image = True
last_swap_time = 0
swap_interval = 300


def init_background(screen):
    global initialized, SCREEN_WIDTH, SCREEN_HEIGHT, spotlights
    global darkened_bg, speaker_left1, speaker_left2, speaker_right1, speaker_right2
    global left_speaker_pos, right_speaker_pos
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
    initialized = True
    bg = pygame.image.load(os.path.join(BASE_PATH, "Bg1.png")).convert()
    darkened_bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    dark_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    dark_overlay.fill((0, 0, 0, 160))
    darkened_bg.blit(dark_overlay, (0, 0))
    speaker_left1 = scale_image(pygame.image.load(os.path.join(BASE_PATH, "SpeakLeft1.png")).convert_alpha(), 0.2*scale)
    speaker_left2 = scale_image(pygame.image.load(os.path.join(BASE_PATH, "SpeakLeft2.png")).convert_alpha(), 0.2*scale)
    speaker_right1 = scale_image(pygame.image.load(os.path.join(BASE_PATH, "SpeakRight1.png")).convert_alpha(), 0.2*scale)
    speaker_right2 = scale_image(pygame.image.load(os.path.join(BASE_PATH, "SpeakRight2.png")).convert_alpha(), 0.2*scale)
    left_x = int(SCREEN_WIDTH*0.3 - speaker_left1.get_width()/2)
    right_x = int(SCREEN_WIDTH*0.7 - speaker_right1.get_width()/2)
    left_speaker_pos = (left_x, SCREEN_HEIGHT - speaker_left1.get_height()*2)
    right_speaker_pos = (right_x, SCREEN_HEIGHT - speaker_right1.get_height()*2)
    spotlights = [Spotlight(int(SCREEN_WIDTH*x)) for x in [0.2, 0.4, 0.6, 0.8]]
    for sp in spotlights:
        sp.set_movement_pattern(random.choice(["sweep", "zigzag", "circular"]))

# Main draw with golden tint when combo >=10
def draw_dynamic_background(screen):
    global initialized, use_first_image, last_swap_time
    if not initialized:
        init_background(screen)
    current_time = pygame.time.get_ticks()
    if current_time - last_swap_time > swap_interval:
        use_first_image = not use_first_image
        last_swap_time = current_time
    screen.blit(darkened_bg, (0, 0))
    combo = get_current_combo()
    if combo >= 10:
        tint = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        tint.fill((255, 215, 0, 80))
        screen.blit(tint, (0, 0))
    for sp in spotlights:
        sp.update()
        sp.draw(screen)
    # draw speakers
    if use_first_image:
        left_img = speaker_left1
        right_img = speaker_right1
    else:
        left_img = speaker_left2
        right_img = speaker_right2
    if combo >= 10:
        left_img = left_img.copy()
        left_img.fill((255, 215, 0), special_flags=pygame.BLEND_RGB_MULT)
        right_img = right_img.copy()
        right_img.fill((255, 215, 0), special_flags=pygame.BLEND_RGB_MULT)
    screen.blit(left_img, left_speaker_pos)
    screen.blit(right_img, right_speaker_pos)