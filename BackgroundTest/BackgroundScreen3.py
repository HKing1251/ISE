# BackgroundLvl3.py - Disco-style dynamic background for final level

import pygame
import math
import random
import os

BASE_PATH = os.path.dirname(__file__)

initialized = False
screen_width = screen_height = 0
background_image = None
speaker1 = speaker2 = None
speaker_width, speaker_height = 180, 180
left_speaker_pos = right_speaker_pos = (0, 0)
use_first_image = True
last_image_swap_time = 0
beat_pulse_time = 0
beat_pulse_amount = 0
beat_pulse_duration = 150
ambient_pulse = 0
ambient_pulse_direction = 0.02
disco_lights = []
MAX_DISCO_LIGHTS = 12

class DiscoLight:
    def __init__(self):
        self.source_x = screen_width // 2
        self.source_y = 140
        self.angle = random.uniform(0, 2 * math.pi)
        self.length = random.randint(300, 600)
        self.width = random.randint(20, 40)
        self.rotation_speed = random.uniform(0.005, 0.02)
        self.hue = random.random()
        self.color = self.hsv_to_rgb(self.hue, 0.9, 1.0)
        self.alpha = random.randint(50, 120)
        self.alpha_change = random.uniform(-0.5, 0.5)
        self.life = random.randint(150, 300)

    def hsv_to_rgb(self, h, s, v):
        if s == 0.0:
            return (v, v, v)
        i = int(h * 6.0)
        f = (h * 6.0) - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        i %= 6
        if i == 0: return (int(v * 255), int(t * 255), int(p * 255))
        if i == 1: return (int(q * 255), int(v * 255), int(p * 255))
        if i == 2: return (int(p * 255), int(v * 255), int(t * 255))
        if i == 3: return (int(p * 255), int(q * 255), int(v * 255))
        if i == 4: return (int(t * 255), int(p * 255), int(v * 255))
        if i == 5: return (int(v * 255), int(p * 255), int(q * 255))

    def update(self):
        self.angle += self.rotation_speed
        self.alpha += self.alpha_change
        if self.alpha <= 30:
            self.alpha = 30
            self.alpha_change = random.uniform(0.2, 0.8)
        elif self.alpha >= 120:
            self.alpha = 120
            self.alpha_change = random.uniform(-0.8, -0.2)
        self.hue = (self.hue + 0.001) % 1.0
        self.color = self.hsv_to_rgb(self.hue, 0.9, 1.0)
        self.life -= 1
        return self.life > 0

    def draw(self, surface):
        end_x = self.source_x + math.cos(self.angle) * self.length
        end_y = self.source_y + math.sin(self.angle) * self.length
        beam_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        angle_perpendicular = self.angle + math.pi/2
        source_width = self.width * 0.2
        p1_near = (self.source_x + math.cos(angle_perpendicular) * source_width,
                   self.source_y + math.sin(angle_perpendicular) * source_width)
        p2_near = (self.source_x - math.cos(angle_perpendicular) * source_width,
                   self.source_y - math.sin(angle_perpendicular) * source_width)
        p1_far = (end_x + math.cos(angle_perpendicular) * self.width,
                  end_y + math.sin(angle_perpendicular) * self.width)
        p2_far = (end_x - math.cos(angle_perpendicular) * self.width,
                  end_y - math.sin(angle_perpendicular) * self.width)
        points = [p1_near, p2_near, p2_far, p1_far]
        color_with_alpha = (*self.color, int(self.alpha))
        pygame.draw.polygon(beam_surface, color_with_alpha, points)
        for i in range(3):
            glow_width = source_width * (1 + i * 0.5)
            end_width = self.width * (1 + i * 0.5)
            p1_near_glow = (self.source_x + math.cos(angle_perpendicular) * glow_width,
                           self.source_y + math.sin(angle_perpendicular) * glow_width)
            p2_near_glow = (self.source_x - math.cos(angle_perpendicular) * glow_width,
                           self.source_y - math.sin(angle_perpendicular) * glow_width)
            p1_far_glow = (end_x + math.cos(angle_perpendicular) * end_width,
                          end_y + math.sin(angle_perpendicular) * end_width)
            p2_far_glow = (end_x - math.cos(angle_perpendicular) * end_width,
                          end_y - math.sin(angle_perpendicular) * end_width)
            glow_points = [p1_near_glow, p2_near_glow, p2_far_glow, p1_far_glow]
            glow_alpha = max(10, int(self.alpha * 0.3 * (3-i)/3))
            glow_color = (*self.color, glow_alpha)
            pygame.draw.polygon(beam_surface, glow_color, glow_points)
        surface.blit(beam_surface, (0, 0))

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

def init_background(screen):
    global initialized, background_image, speaker1, speaker2, left_speaker_pos, right_speaker_pos
    global screen_width, screen_height

    if initialized:
        return

    screen_width, screen_height = screen.get_size()
    initialized = True

    bg_path = os.path.join(BASE_PATH, "bg3.png")
    speaker1_path = os.path.join(BASE_PATH, "Lvl3Speaker1.png")
    speaker2_path = os.path.join(BASE_PATH, "Lvl3Speaker2.png")

    background_image = pygame.image.load(bg_path).convert()
    background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

    speaker1 = pygame.image.load(speaker1_path).convert_alpha()
    speaker2 = pygame.image.load(speaker2_path).convert_alpha()
    speaker1 = pygame.transform.scale(speaker1, (speaker_width, speaker_height))
    speaker2 = pygame.transform.scale(speaker2, (speaker_width, speaker_height))

    left_speaker_pos = (int(screen_width * 0.15), int(screen_height * 0.55))
    right_speaker_pos = (int(screen_width * 0.75), int(screen_height * 0.55))

def draw_dynamic_background(screen):
    global use_first_image, beat_pulse_time, last_image_swap_time, beat_pulse_amount
    global ambient_pulse, ambient_pulse_direction

    if not initialized:
        init_background(screen)

    current_time = pygame.time.get_ticks()
    pulse_volume = audio_analyzer.analyze()

    if pulse_volume > 0.5:
        beat_pulse_time = current_time
        beat_pulse_amount = pulse_volume
        use_first_image = not use_first_image
        last_image_swap_time = current_time

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
    current_speaker = speaker1 if use_first_image else speaker2
    scaled = pygame.transform.scale(current_speaker, (int(speaker_width * speaker_scale * 1.5), int(speaker_height * speaker_scale * 1.5)))

    for pos in [left_speaker_pos, right_speaker_pos]:
        adj_x = pos[0] - (scaled.get_width() - speaker_width) // 2
        adj_y = pos[1] - (scaled.get_height() - speaker_height) // 2
        screen.blit(scaled, (adj_x, adj_y))

    for light in disco_lights[:]:
        if not light.update():
            disco_lights.remove(light)
        else:
            light.draw(screen)

    if current_time - last_image_swap_time > 300 and len(disco_lights) < MAX_DISCO_LIGHTS:
        disco_lights.append(DiscoLight())
