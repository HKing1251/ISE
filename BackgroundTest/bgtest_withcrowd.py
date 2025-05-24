import pygame
import sys
import time
import random
import math

pygame.init()
pygame.mixer.init()

screen_width, screen_height = 1000, 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Game Window")

# music
pygame.mixer.music.load(r'Ode.mp3')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)  # Loop indefinitely

# background image
background_image = pygame.image.load(r'Bg1.png')
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
# darken
darkened_bg = background_image.copy()
dark_overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
dark_overlay.fill((0, 0, 0, 160))
darkened_bg.blit(dark_overlay, (0, 0))

# speaker images
speaker_left1 = pygame.image.load(r'SpeakRight1.png')
speaker_left2 = pygame.image.load(r'SpeakRight2.png')
speaker_right1 = pygame.image.load(r'SpeakLeft1.png')
speaker_right2 = pygame.image.load(r'SpeakLeft2.png')
# Adjust dimensions
speaker_width, speaker_height = 200, 150
speaker_left1 = pygame.transform.scale(speaker_left1, (speaker_width, speaker_height))
speaker_left2 = pygame.transform.scale(speaker_left2, (speaker_width, speaker_height))
speaker_right1 = pygame.transform.scale(speaker_right1, (speaker_width, speaker_height))
speaker_right2 = pygame.transform.scale(speaker_right2, (speaker_width, speaker_height))
# positions
left_speaker_pos = (100, 500)
right_speaker_pos = (650, 500)

# background crowd
crowd = pygame.image.load(r'bgcrowd.png')
crowd_width, crowd_height = 800, 400
crowd = pygame.transform.scale(crowd, (crowd_width, crowd_height))
crowd_position = (100, 100)  

# Speaker animation timing
speaker_swap_event = pygame.USEREVENT + 1
current_speed = 500  # Initial speed (ms)
pygame.time.set_timer(speaker_swap_event, current_speed)

# spotlight effect timer
spotlight_effect_event = pygame.USEREVENT + 2
pygame.time.set_timer(spotlight_effect_event, 20)

# Color change timer
color_change_event = pygame.USEREVENT + 3
pygame.time.set_timer(color_change_event, 1000)  # Change colors

# Movement change timer
pattern_change_event = pygame.USEREVENT + 4
pygame.time.set_timer(pattern_change_event, 4000)  # Change patterns

# speaker images
use_first_image = True
last_speed_change = 0
speed_change_interval = 2000  # Change 2 seconds

# Possible animation speeds
animation_speeds = [100, 200, 300, 400, 500]

# movement patterns
MOVEMENT_PATTERNS = [
    "sweep",
    "circular",
    "zigzag",
    "random_jump",
    "crossover"
]


class Spotlight:
    def __init__(self, x, color, cone_angle=15):
        self.x = x  # X
        self.y = 0  # Y
        self.color = color  # color of light
        self.alpha = 80  # transparency
        self.cone_angle = cone_angle  # Width

        # Movement and effect properties
        self.flicker_amount = 0
        self.swing_amount = 100
        self.swing_offset = random.uniform(-50, 50)  # starting position
        self.swing_speed = random.uniform(0.01, 0.03)  # How fast the light swings
        self.swing_time = random.uniform(0, math.pi * 2)  # starting phase

        # Target position
        self.target_x = x  # Current target X position
        self.target_y = screen_height  # Current target Y position

        # Movement pattern properties
        self.movement_pattern = "sweep"  # starting pattern
        self.pattern_time = 0  # time for pattern
        self.pattern_speed = random.uniform(0.02, 0.04)  # movement speed
        self.circular_radius = random.uniform(100, 200)  # size of circle
        self.zigzag_phase = random.uniform(0, math.pi)  # zigzag pattern

        # Properties for random and crossover patterns
        self.random_target_x = x  # Target
        self.random_target_y = screen_height  # Target
        self.crossover_partner = None  # Another spotlight this one interacts with

    # Sets the movement pattern and resets timing
    def set_movement_pattern(self, pattern):
        self.movement_pattern = pattern
        self.pattern_time = 0  # Reset pattern timer

        # pattern-specific parameters
        if pattern == "circular":
            # size for circular movement
            self.circular_radius = random.uniform(100, 200)
        elif pattern == "random_jump":
            # target for jumping pattern
            self.random_target_x = random.randint(100, screen_width - 100)
            self.random_target_y = random.randint(400, screen_height)

    # spotlight position and effects
    def update(self):
        # Increment pattern animation time
        self.pattern_time += self.pattern_speed

        # flickering effect to light
        flicker = random.uniform(-self.flicker_amount, self.flicker_amount)
        self.alpha = max(50, min(150, self.alpha + flicker))

        # Update target position based on current movement pattern
        if self.movement_pattern == "sweep":
            self.swing_time += self.swing_speed
            self.target_x = self.x + math.sin(self.swing_time) * self.swing_amount
            self.target_y = screen_height

        elif self.movement_pattern == "circular":
            self.target_x = self.x + math.cos(self.pattern_time) * self.circular_radius
            self.target_y = screen_height - math.sin(self.pattern_time) * self.circular_radius / 2
            self.target_y = max(self.target_y, 400)

        elif self.movement_pattern == "zigzag":
            self.target_x = self.x + math.sin(self.pattern_time * 3) * self.swing_amount
            vertical_offset = math.sin(self.pattern_time + self.zigzag_phase) * 150
            self.target_y = screen_height - vertical_offset

        elif self.movement_pattern == "random_jump":
            # jump to new positions
            if random.random() < 0.03:  # 3% chance each update to pick a new target
                self.random_target_x = random.randint(100, screen_width - 100)
                self.random_target_y = random.randint(400, screen_height)

            # move toward target
            self.target_x += (self.random_target_x - self.target_x) * 0.05
            self.target_y += (self.random_target_y - self.target_y) * 0.05

        elif self.movement_pattern == "crossover":
            # Beams crossing each other
            if self.crossover_partner:
                partner_base_x = self.crossover_partner.x
                progress = (math.sin(self.pattern_time) + 1) / 2  # Value from 0 to 1
                self.target_x = self.x + (partner_base_x - self.x) * progress
                # arcing motion during crossover
                self.target_y = screen_height - 150 * math.sin(math.pi * progress)
            else:
                # Default to sweep pattern if no partner is assigned
                self.target_x = self.x + math.sin(self.pattern_time) * self.swing_amount
                self.target_y = screen_height

    def change_color(self, new_color=None):
        if new_color:
            self.color = new_color
        else:
            # Generate random color
            hue = random.random()

            if hue < 1 / 6:  # Red to Yellow
                self.color = (255, int(255 * hue * 6), 0)
            elif hue < 2 / 6:  # Yellow to Green
                self.color = (int(255 * (2 - hue * 6)), 255, 0)
            elif hue < 3 / 6:  # Green to Cyan
                self.color = (0, 255, int(255 * (hue * 6 - 2)))
            elif hue < 4 / 6:  # Cyan to Blue
                self.color = (0, int(255 * (4 - hue * 6)), 255)
            elif hue < 5 / 6:  # Blue to Magenta
                self.color = (int(255 * (hue * 6 - 4)), 0, 255)
            else:  # Magenta to Red
                self.color = (255, 0, int(255 * (6 - hue * 6)))

    # Draw the spotlight beam on the screen
    def draw(self, surface):
        # transparent surface
        cone_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

        # distance from light source to target
        distance = math.sqrt((self.target_x - self.x) ** 2 + (self.target_y - self.y) ** 2)

        # angle to the target
        angle = math.atan2(self.target_y - self.y, self.target_x - self.x)

        # how wide the cone should be at the target distance
        cone_width = 2 * distance * math.tan(math.radians(self.cone_angle / 2))

        # three points of the cone triangle
        cone_points = [
            (self.x, self.y),  # Top point (source of light)
            (self.target_x - cone_width / 2 * math.cos(angle + math.pi / 2),
             self.target_y - cone_width / 2 * math.sin(angle + math.pi / 2)),  # Left point
            (self.target_x + cone_width / 2 * math.cos(angle + math.pi / 2),
             self.target_y + cone_width / 2 * math.sin(angle + math.pi / 2))  # Right point
        ]

        # gradient effect
        for i in range(5):
            # Calculate alpha for  layer
            alpha = int(self.alpha * (5 - i) / 5)
            gradient_color = (*self.color, alpha)

            # each layer slightly larger
            scale_factor = 1 + i * 0.05
            scaled_points = [
                cone_points[0],  # Source point stays the same
                (cone_points[0][0] + scale_factor * (cone_points[1][0] - cone_points[0][0]),
                 cone_points[0][1] + scale_factor * (cone_points[1][1] - cone_points[0][1])),
                (cone_points[0][0] + scale_factor * (cone_points[2][0] - cone_points[0][0]),
                 cone_points[0][1] + scale_factor * (cone_points[2][1] - cone_points[0][1]))
            ]

            pygame.draw.polygon(cone_surface, gradient_color, scaled_points)

        surface.blit(cone_surface, (0, 0))


# four spotlights at the top
spotlights = []
spacing = screen_width / 5  # space the spotlights

# Spotlight positions across the top of the screen
spotlight_positions = [spacing, spacing * 2, spacing * 3, spacing * 4]

# Initial spotlight colors
spotlight_colors = [
    (255, 50, 50),  # Red
    (50, 255, 50),  # Green
    (50, 50, 255),  # Blue
    (255, 255, 50)  # Yellow
]

for i in range(4):
    x = spotlight_positions[i]
    # Create the spotlight
    spotlight = Spotlight(x, spotlight_colors[i], cone_angle=15)
    # Set movement and flicker properties
    spotlight.flicker_amount = 5
    spotlight.swing_amount = 150
    spotlights.append(spotlight)

# crossover partners
spotlights[0].crossover_partner = spotlights[3]
spotlights[1].crossover_partner = spotlights[2]
spotlights[2].crossover_partner = spotlights[1]
spotlights[3].crossover_partner = spotlights[0]

# Initial pattern
current_pattern = "sweep"
for spotlight in spotlights:
    spotlight.set_movement_pattern(current_pattern)

clock = pygame.time.Clock()
running = True
while running:
    current_time = pygame.time.get_ticks()

    # change the animation speed periodically
    if current_time - last_speed_change > speed_change_interval:
        new_speed = random.choice(animation_speeds)
        pygame.time.set_timer(speaker_swap_event, new_speed)
        last_speed_change = current_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == speaker_swap_event:
            # Toggle speaker images
            use_first_image = not use_first_image
        elif event.type == spotlight_effect_event:
            # Update spotlight movements
            for spotlight in spotlights:
                spotlight.update()
        elif event.type == color_change_event:
            # change spotlight colors
            for spotlight in spotlights:
                if random.random() < 0.6:
                    spotlight.change_color()
        elif event.type == pattern_change_event:
            # Change the movement pattern
            current_pattern = random.choice(MOVEMENT_PATTERNS)
            for spotlight in spotlights:
                spotlight.set_movement_pattern(current_pattern)

    # bg image
    screen.blit(darkened_bg, (0, 0))

    # Draw the background crowd
    screen.blit(crowd, crowd_position)

    # spotlight (drawn after crowd so they appear on top)
    for spotlight in spotlights:
        spotlight.draw(screen)

    # speaker images (drawn last so they appear on top)
    if use_first_image:
        screen.blit(speaker_left1, left_speaker_pos)
        screen.blit(speaker_right1, right_speaker_pos)
    else:
        screen.blit(speaker_left2, left_speaker_pos)
        screen.blit(speaker_right2, right_speaker_pos)

    pygame.display.flip()

    clock.tick(60)

pygame.mixer.music.stop()
print("Closing...")
pygame.quit()
sys.exit()