import pygame
import math
import random
import os

BASE_PATH = os.path.dirname(__file__)

# Screen scaling
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
BASE_WIDTH = 1280
BASE_HEIGHT = 720
scale_x = SCREEN_WIDTH / BASE_WIDTH
scale_y = SCREEN_HEIGHT / BASE_HEIGHT
scale = min(scale_x, scale_y)

def scale_image(image, scale):
    width = int(image.get_width() * scale)
    height = int(image.get_height() * scale)
    return pygame.transform.scale(image, (width, height))

# === Spotlight Class ===
class Spotlight:
    def __init__(self, x, color, cone_angle=20):
        self.x = x
        self.y = int(80 * scale)
        self.color = color
        self.alpha = 80
        self.cone_angle = cone_angle

        self.flicker_amount = 0
        self.swing_amount = 100 * scale
        self.swing_offset = random.uniform(-50, 50)
        self.swing_speed = random.uniform(0.01, 0.03)
        self.swing_time = random.uniform(0, math.pi * 2)

        self.target_x = x
        self.target_y = int(SCREEN_HEIGHT * 0.85)

        self.movement_pattern = "sweep"
        self.pattern_time = 0
        self.pattern_speed = random.uniform(0.02, 0.04)
        self.circular_radius = random.uniform(100, 200) * scale
        self.zigzag_phase = random.uniform(0, math.pi)

        self.random_target_x = x
        self.random_target_y = SCREEN_HEIGHT
        self.crossover_partner = None

    def set_movement_pattern(self, pattern):
        self.movement_pattern = pattern
        self.pattern_time = 0

        if pattern == "circular":
            self.circular_radius = random.uniform(100, 200) * scale
        elif pattern == "random_jump":
            self.random_target_x = random.randint(100, SCREEN_WIDTH - 100)
            self.random_target_y = random.randint(400, SCREEN_HEIGHT)

    def update(self):
        self.pattern_time += self.pattern_speed

        flicker = random.uniform(-self.flicker_amount, self.flicker_amount)
        self.alpha = max(50, min(150, self.alpha + flicker))

        if self.movement_pattern == "sweep":
            self.swing_time += self.swing_speed
            self.target_x = self.x + math.sin(self.swing_time) * self.swing_amount
            self.target_y = int(SCREEN_HEIGHT * 0.85)

        elif self.movement_pattern == "circular":
            self.target_x = self.x + math.cos(self.pattern_time) * self.circular_radius
            self.target_y = SCREEN_HEIGHT - math.sin(self.pattern_time) * self.circular_radius / 2
            self.target_y = max(self.target_y, 400)

        elif self.movement_pattern == "zigzag":
            self.target_x = self.x + math.sin(self.pattern_time * 3) * self.swing_amount
            vertical_offset = math.sin(self.pattern_time + self.zigzag_phase) * 150
            self.target_y = SCREEN_HEIGHT - vertical_offset

        elif self.movement_pattern == "random_jump":
            if random.random() < 0.03:
                self.random_target_x = random.randint(100, SCREEN_WIDTH - 100)
                self.random_target_y = random.randint(400, SCREEN_HEIGHT)
            self.target_x += (self.random_target_x - self.target_x) * 0.05
            self.target_y += (self.random_target_y - self.target_y) * 0.05

        elif self.movement_pattern == "crossover":
            if self.crossover_partner:
                partner_x = self.crossover_partner.x
                progress = (math.sin(self.pattern_time) + 1) / 2
                self.target_x = self.x + (partner_x - self.x) * progress
                self.target_y = SCREEN_HEIGHT - 150 * math.sin(math.pi * progress)
            else:
                self.target_x = self.x + math.sin(self.pattern_time) * self.swing_amount
                self.target_y = SCREEN_HEIGHT

    def change_color(self, new_color=None):
        if new_color:
            self.color = new_color
        else:
            hue = random.random()
            if hue < 1/6:
                self.color = (255, int(255*hue*6), 0)
            elif hue < 2/6:
                self.color = (int(255*(2-hue*6)), 255, 0)
            elif hue < 3/6:
                self.color = (0, 255, int(255*(hue*6-2)))
            elif hue < 4/6:
                self.color = (0, int(255*(4-hue*6)), 255)
            elif hue < 5/6:
                self.color = (int(255*(hue*6-4)), 0, 255)
            else:
                self.color = (255, 0, int(255*(6-hue*6)))

    def draw(self, surface):
        cone_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        distance = math.sqrt((self.target_x - self.x) ** 2 + (self.target_y - self.y) ** 2)
        angle = math.atan2(self.target_y - self.y, self.target_x - self.x)
        cone_width = 2 * distance * math.tan(math.radians(self.cone_angle / 2)) * 0.6

        cone_points = [
            (self.x, self.y),
            (self.target_x - cone_width / 2 * math.cos(angle + math.pi / 2),
             self.target_y - cone_width / 2 * math.sin(angle + math.pi / 2)),
            (self.target_x + cone_width / 2 * math.cos(angle + math.pi / 2),
             self.target_y + cone_width / 2 * math.sin(angle + math.pi / 2))
        ]

        for i in range(5):
            alpha = int(self.alpha * (5 - i) / 5)
            gradient_color = (*self.color, alpha)
            scale_factor = 1 + i * 0.05
            scaled_points = [
                cone_points[0],
                (cone_points[0][0] + scale_factor * (cone_points[1][0] - cone_points[0][0]),
                 cone_points[0][1] + scale_factor * (cone_points[1][1] - cone_points[0][1])),
                (cone_points[0][0] + scale_factor * (cone_points[2][0] - cone_points[0][0]),
                 cone_points[0][1] + scale_factor * (cone_points[2][1] - cone_points[0][1]))
            ]
            pygame.draw.polygon(cone_surface, gradient_color, scaled_points)

        surface.blit(cone_surface, (0, 0))


# === Resource Initialization ===
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

    bg_image = pygame.image.load(os.path.join(BASE_PATH, "Bg1.png")).convert()
    darkened_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

    # Speakers
    speaker_left1 = scale_image(pygame.image.load(os.path.join(BASE_PATH, "SpeakLeft1.png")).convert_alpha(), 0.4 * scale)
    speaker_left2 = scale_image(pygame.image.load(os.path.join(BASE_PATH, "SpeakLeft2.png")).convert_alpha(), 0.4 * scale)
    speaker_right1 = scale_image(pygame.image.load(os.path.join(BASE_PATH, "SpeakRight1.png")).convert_alpha(), 0.4 * scale)
    speaker_right2 = scale_image(pygame.image.load(os.path.join(BASE_PATH, "SpeakRight2.png")).convert_alpha(), 0.4 * scale)

    left_speaker_pos = (int(100 * scale), SCREEN_HEIGHT - speaker_left1.get_height())
    right_speaker_pos = (SCREEN_WIDTH - int(100 * scale) - speaker_right1.get_width(), SCREEN_HEIGHT - speaker_right1.get_height())

    # Spotlights
    spotlights = [
        Spotlight(int(SCREEN_WIDTH * 0.2), (255, 255, 255), cone_angle=20),
        Spotlight(int(SCREEN_WIDTH * 0.4), (255, 200, 100), cone_angle=18),
        Spotlight(int(SCREEN_WIDTH * 0.6), (100, 200, 255), cone_angle=18),
        Spotlight(int(SCREEN_WIDTH * 0.8), (255, 100, 255), cone_angle=20)
    ]
    for spotlight in spotlights:
        pattern = random.choice(["sweep", "zigzag", "circular", "random_jump", "crossover"])
        spotlight.set_movement_pattern(pattern)

def draw_dynamic_background(screen):
    global initialized, use_first_image, last_swap_time

    if not initialized:
        init_background(screen)

    current_time = pygame.time.get_ticks()
    if current_time - last_swap_time > swap_interval:
        use_first_image = not use_first_image
        last_swap_time = current_time

    screen.blit(darkened_bg, (0, 0))

    for spotlight in spotlights:
        spotlight.update()
        if random.random() < 0.01:
            spotlight.change_color()
        spotlight.draw(screen)

    if use_first_image:
        screen.blit(speaker_left1, left_speaker_pos)
        screen.blit(speaker_right1, right_speaker_pos)
    else:
        screen.blit(speaker_left2, left_speaker_pos)
        screen.blit(speaker_right2, right_speaker_pos)
