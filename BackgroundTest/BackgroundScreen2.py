# BackgroundLvl2.py - Modular and integrated version for use in Prototype_V5.py

import pygame
import math
import random
import os

BASE_PATH = os.path.dirname(__file__)

# Global variables initialized at runtime
initialized = False
background_image = None
speaker1 = speaker2 = None
speaker1_pos = speaker2_pos = (0, 0)
speaker1_width = speaker2_width = 250
speaker1_height = speaker2_height = 200
use_first_image = True
last_animation_time = 0
beat_pulse_time = 0
beat_pulse_amount = 0
beat_pulse_duration = 150
ambient_pulse = 0
ambient_pulse_direction = 0.02

# Particles
speaker_particles = []
dust_particles = []
MAX_DUST_PARTICLES = 800
MAX_SPEAKER_PARTICLES = 400

# Audio simulation object
class AudioAnalyzer:
    def __init__(self):
        self.oscillators = [
            {"freq": 2.5, "amp": 0.3, "phase": 0},
            {"freq": 4.2, "amp": 0.15, "phase": 1.3},
            {"freq": 1.8, "amp": 0.25, "phase": 2.7},
            {"freq": 6.0, "amp": 0.1, "phase": 0.5}
        ]
        self.current_volume = 0
        self.frame_count = 0

    def analyze(self):
        self.frame_count += 1
        if self.frame_count % 3 == 0:
            time_factor = pygame.time.get_ticks() * 0.001
            oscillation = sum(osc["amp"] * math.sin(time_factor * osc["freq"] + osc["phase"]) for osc in self.oscillators)
            base_vol = 0.35
            random_vol = random.uniform(-0.07, 0.07)
            self.current_volume = max(0.1, min(1.0, base_vol + oscillation + random_vol))
            return self.current_volume
        return 0

audio_analyzer = AudioAnalyzer()

# Speaker particle effect
class SpeakerParticle:
    def __init__(self, x, y, volume=0.5):
        self.x = x
        self.y = y
        self.size = random.uniform(1.5, 3.5) * volume
        self.color = (255, 255, 255, random.randint(100, 200))
        self.speed = random.uniform(0.3, 0.6)  # Slower movement
        self.life = 40

    def update(self):
        self.y -= self.speed
        self.life -= 1
        return self.life > 0

    def draw(self, surface):
        surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, self.color, (int(self.size), int(self.size)), int(self.size))
        surface.blit(surf, (self.x - self.size, self.y - self.size))

# Initialize resources

def init_background(screen):
    global initialized, background_image, speaker1, speaker2, speaker1_pos, speaker2_pos
    global screen_width, screen_height

    if initialized:
        return

    screen_width, screen_height = screen.get_size()
    initialized = True

    bg_path = os.path.join(BASE_PATH, "Bg2.png")
    speaker1_path = os.path.join(BASE_PATH, "Lvl2Speaker1.png")
    speaker2_path = os.path.join(BASE_PATH, "Lvl2Speaker2.png")

    background_image = pygame.image.load(bg_path).convert()
    background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

    speaker1 = pygame.image.load(speaker1_path).convert_alpha()
    speaker2 = pygame.image.load(speaker2_path).convert_alpha()
    speaker1 = pygame.transform.scale(speaker1, (speaker1_width, speaker1_height))
    speaker2 = pygame.transform.scale(speaker2, (speaker2_width, speaker2_height))

    speaker1_pos = (screen_width // 2 - speaker1_width // 2, int(screen_height * 0.5))
    speaker2_pos = speaker1_pos

# Draw function called from play_level

def draw_dynamic_background(screen):
    global use_first_image, beat_pulse_time, last_animation_time, beat_pulse_amount
    global ambient_pulse, ambient_pulse_direction

    if not initialized:
        init_background(screen)

    current_time = pygame.time.get_ticks()
    pulse_volume = audio_analyzer.analyze()

    if pulse_volume > 0.5:
        beat_pulse_time = current_time
        beat_pulse_amount = pulse_volume
        use_first_image = not use_first_image
        last_animation_time = current_time

        center_x = speaker1_pos[0] + speaker1_width // 2
        center_y = speaker1_pos[1] + speaker1_height // 2

        if len(speaker_particles) < MAX_SPEAKER_PARTICLES:
            for _ in range(6):  # Reduced particle count for cleanliness
                speaker_particles.append(SpeakerParticle(center_x, center_y, pulse_volume))

    if current_time - last_animation_time > 300:
        use_first_image = not use_first_image
        last_animation_time = current_time

    if current_time - beat_pulse_time < beat_pulse_duration:
        pulse_progress = 1 - ((current_time - beat_pulse_time) / beat_pulse_duration)
        current_pulse = beat_pulse_amount * pulse_progress
    else:
        ambient_pulse += ambient_pulse_direction
        if ambient_pulse > 0.15:
            ambient_pulse = 0.15
            ambient_pulse_direction = -0.02
        elif ambient_pulse < 0:
            ambient_pulse = 0
            ambient_pulse_direction = 0.02
        current_pulse = ambient_pulse

    screen.blit(background_image, (0, 0))

    speaker_scale = 1.0 + current_pulse * 0.25
    speaker_img = speaker1 if use_first_image else speaker2
    scaled = pygame.transform.scale(speaker_img, (int(speaker1_width * speaker_scale), int(speaker1_height * speaker_scale)))
    offset_x = speaker1_pos[0] - (scaled.get_width() - speaker1_width) // 2
    offset_y = speaker1_pos[1] - (scaled.get_height() - speaker1_height) // 2
    screen.blit(scaled, (offset_x, offset_y))

    # for particle in speaker_particles[:]:
    #     if not particle.update():
    #         speaker_particles.remove(particle)
    #     else:
    #         particle.draw(screen)

    # for particle in dust_particles[:]:
    #     if not hasattr(particle, 'life'):
    #         particle.life = 60
    #     particle.life -= 1
    #     if particle.life <= 0:
    #         dust_particles.remove(particle)
    #         continue
    #     particle.draw(screen)
