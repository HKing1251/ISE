# BackgroundLvl2.py - Modular and integrated

import pygame
import math
import random
import os
import json

BASE_PATH = os.path.dirname(__file__)

# Global variables
initialized = False
background_image = None
speaker1 = speaker2 = None
speaker1_pos = speaker2_pos = (0, 0)
speaker1_width = speaker2_width = 250
speaker1_height = speaker2_height = 200
use_first_image = True
last_animation_time = 0

# Pulse timing
beat_pulse_time = 0
beat_pulse_amount = 0
beat_pulse_duration = 150
ambient_pulse = 0
ambient_pulse_direction = 0.02

# Shake timing
last_milestone = 0
shake_start_time = 0
shake_duration = 1000   # ms of shake
shake_amplitude = 5     # pixels of shake

# Try import combo from main module
try:
    import __main__
    MAIN_MODULE_AVAILABLE = True
except ImportError:
    MAIN_MODULE_AVAILABLE = False

# Particle lists and caps
speaker_particles = []
dust_particles = []
MAX_DUST_PARTICLES = 800
MAX_SPEAKER_PARTICLES = 400

# Screen dimensions
screen_width = screen_height = 0

# Beatmap data
beatmap_times = []
current_beat_index = 0
beatmap_loaded = False
last_music_position = 0


def get_current_combo() -> int:
    """Retrieve combo value from main game module if available."""
    if MAIN_MODULE_AVAILABLE:
        try:
            if hasattr(__main__, 'combo'):
                return __main__.combo
            if hasattr(__main__, 'current_combo'):
                return __main__.current_combo
        except:
            pass
    return 0

# Audio simulation
class AudioAnalyzer:
    def __init__(self):
        self.oscillators = [
            {"freq":2.5, "amp":0.3, "phase":0},
            {"freq":4.2, "amp":0.15, "phase":1.3},
            {"freq":1.8, "amp":0.25, "phase":2.7},
            {"freq":6.0, "amp":0.1, "phase":0.5}
        ]
        self.current_volume = 0
        self.frame_count = 0

    def analyze(self):
        self.frame_count += 1
        if self.frame_count % 3 == 0:
            t = pygame.time.get_ticks() * 0.001
            osc = sum(o["amp"] * math.sin(t * o["freq"] + o["phase"]) for o in self.oscillators)
            base = 0.35
            rnd = random.uniform(-0.07, 0.07)
            self.current_volume = max(0.1, min(1.0, base + osc + rnd))
            return self.current_volume
        return 0.0

audio_analyzer = AudioAnalyzer()

# Beatmap loading/reset
def load_beatmap():
    global beatmap_times, beatmap_loaded
    if beatmap_loaded:
        return
    try:
        with open(os.path.join(BASE_PATH, "beatmap2.json"), 'r') as f:
            beatmap_times = json.load(f)
    except:
        beatmap_times = []
    beatmap_loaded = True

def reset_beat_tracking():
    global current_beat_index, last_music_position
    current_beat_index = 0
    last_music_position = 0

# Dust particle
class DustParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.uniform(0.8, 3.0)
        b = random.randint(180, 240)
        self.color = (b, b, b, random.randint(20, 80))
        self.vx = random.uniform(-0.2, 0.2)
        self.vy = random.uniform(-0.15, 0.15)
        self.life = random.randint(300, 800)
        self.wobble_speed = random.uniform(0.01, 0.05)
        self.wobble_amount = random.uniform(0.1, 0.4)
        self.wobble_offset = random.uniform(0, math.pi * 2)

    def update(self):
        wobble = math.sin(pygame.time.get_ticks() * self.wobble_speed + self.wobble_offset) * self.wobble_amount
        self.x += self.vx + wobble
        self.y += self.vy
        self.size -= 0.003
        self.life -= 1
        if (self.size <= 0 or self.life <= 0 or
            self.y < -10 or self.y > screen_height + 10 or
            self.x < -10 or self.x > screen_width + 10):
            return False
        return True

    def draw(self, surface):
        s = int(self.size * 2 + 1)
        surf = pygame.Surface((s, s), pygame.SRCALPHA)
        pygame.draw.circle(surf, self.color, (s//2, s//2), int(self.size))
        surface.blit(surf, (self.x - self.size, self.y - self.size))

# Speaker burst particle
class SpeakerParticle:
    def __init__(self, x, y, volume=0.5):
        self.cx, self.cy = x, y
        angle = random.uniform(0, 2*math.pi)
        speed = random.uniform(2.0, 6.0) * volume
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.size = random.uniform(1.5, 4.0) * volume
        choices = [(255,100,100),(100,255,100),(100,100,255),
                   (255,255,100),(255,100,255),(100,255,255),
                   (255,200,100),(255,255,255)]
        base_col = random.choice(choices)
        alpha = random.randint(150,255)
        self.color = list(base_col) + [alpha]
        self.gravity = 0.12
        self.friction = 0.97
        self.life = random.randint(40,80)
        self.max_life = self.life

    def update(self):
        self.vy += self.gravity
        self.vx *= self.friction
        self.vy *= self.friction
        self.cx += self.vx
        self.cy += self.vy
        self.life -= 1
        ratio = self.life / self.max_life
        self.color[3] = int(self.color[3] * ratio)
        return self.life > 0

    def draw(self, surface):
        if self.life <= 0: return
        size = self.size * (self.life / self.max_life)
        if size < 0.5: return
        s = int(size*2)
        surf = pygame.Surface((s, s), pygame.SRCALPHA)
        pygame.draw.circle(surf, self.color, (s//2, s//2), int(size))
        if size > 2:
            glow = [self.color[0], self.color[1], self.color[2], self.color[3]//4]
            pygame.draw.circle(surf, glow, (s//2, s//2), int(size+1))
        surface.blit(surf, (self.cx-size, self.cy-size))

# Initialize background assets
def init_background(screen):
    global initialized, background_image, speaker1, speaker2
    global speaker1_pos, speaker2_pos, screen_width, screen_height
    if initialized: return
    screen_width, screen_height = screen.get_size()
    initialized = True
    load_beatmap()
    bg = pygame.image.load(os.path.join(BASE_PATH, "Bg2.png")).convert()
    background_image = pygame.transform.scale(bg, (screen_width, screen_height))
    s1 = pygame.image.load(os.path.join(BASE_PATH, "Lvl2Speaker1.png")).convert_alpha()
    s2 = pygame.image.load(os.path.join(BASE_PATH, "Lvl2Speaker2.png")).convert_alpha()
    speaker1 = pygame.transform.scale(s1, (speaker1_width, speaker1_height))
    speaker2 = pygame.transform.scale(s2, (speaker2_width, speaker2_height))
    speaker1_pos = (screen_width//2 - speaker1_width//2, int(screen_height*0.5))
    speaker2_pos = speaker1_pos

# Beatmap timing check
def check_beatmap_timing():
    global current_beat_index, last_music_position
    if not beatmap_times: return False
    try:
        pos_ms = pygame.mixer.music.get_pos()
        if pos_ms == -1: return False
        sec = pos_ms/1000.0
        if sec < last_music_position - 1.0:
            current_beat_index = 0
        last_music_position = sec
        if current_beat_index < len(beatmap_times) and sec >= beatmap_times[current_beat_index]:
            current_beat_index += 1
            return True
    except:
        return False
    return False

# Main draw with shake and pulse
def draw_dynamic_background(screen):
    global use_first_image, beat_pulse_time, last_animation_time
    global beat_pulse_amount, ambient_pulse, ambient_pulse_direction
    global last_milestone, shake_start_time

    if not initialized:
        init_background(screen)

    current_time = pygame.time.get_ticks()
    # combo-driven shake
    combo = get_current_combo()
    if combo > 0 and combo % 5 == 0 and combo != last_milestone:
        shake_start_time = current_time
        last_milestone = combo
    # calculate shake offset
    dx = dy = 0
    if current_time - shake_start_time < shake_duration:
        dx = random.randint(-shake_amplitude, shake_amplitude)
        dy = random.randint(-shake_amplitude, shake_amplitude)
    # render to buffer
    buf = pygame.Surface((screen_width, screen_height))
    buf.blit(background_image, (0, 0))
    # beatmap/music triggers
    if check_beatmap_timing():
        beat_pulse_time = current_time
        beat_pulse_amount = 0.8
        use_first_image = not use_first_image
        last_animation_time = current_time
        cx = speaker1_pos[0] + speaker1_width//2
        cy = speaker1_pos[1] + speaker1_height//2
        for _ in range(min(MAX_SPEAKER_PARTICLES-len(speaker_particles), random.randint(18,28))):
            speaker_particles.append(SpeakerParticle(cx, cy, 0.9))
    # audio fallback
    vol = audio_analyzer.analyze()
    if vol > 0.65 and not beatmap_times:
        beat_pulse_time = current_time
        beat_pulse_amount = vol
        use_first_image = not use_first_image
        last_animation_time = current_time
        cx = speaker1_pos[0] + speaker1_width//2
        cy = speaker1_pos[1] + speaker1_height//2
        for _ in range(min(MAX_SPEAKER_PARTICLES-len(speaker_particles), int(6+vol*8))):
            speaker_particles.append(SpeakerParticle(cx, cy, vol))
    # flip speaker image every 300ms
    if current_time - last_animation_time > 300:
        use_first_image = not use_first_image
        last_animation_time = current_time
    # compute pulse for scale
    if current_time - beat_pulse_time < beat_pulse_duration:
        prog = 1 - ((current_time - beat_pulse_time)/beat_pulse_duration)
        current_pulse = beat_pulse_amount * prog
    else:
        ambient_pulse += ambient_pulse_direction
        if ambient_pulse > 0.15:
            ambient_pulse, ambient_pulse_direction = 0.15, -0.02
        elif ambient_pulse < 0:
            ambient_pulse, ambient_pulse_direction = 0, 0.02
        current_pulse = ambient_pulse
    # draw & scale speaker
    speaker_img = speaker1 if use_first_image else speaker2
    sf = 1.0 + current_pulse*0.25
    w = int(speaker1_width*sf)
    h = int(speaker1_height*sf)
    scaled = pygame.transform.scale(speaker_img,(w,h))
    ox = speaker1_pos[0] - (w-speaker1_width)//2
    oy = speaker1_pos[1] - (h-speaker1_height)//2
    buf.blit(scaled,(ox,oy))
    # emit dust
    if len(dust_particles) < MAX_DUST_PARTICLES:
        for _ in range(3):
            if random.random() < 0.7:
                x,y = random.randint(0,screen_width), random.randint(0,screen_height)
            else:
                edge = random.randint(0,3)
                if edge==0: x,y = random.randint(0,screen_width),0
                elif edge==1: x,y = screen_width,random.randint(0,screen_height)
                elif edge==2: x,y = random.randint(0,screen_width),screen_height
                else: x,y = 0,random.randint(0,screen_height)
            dust_particles.append(DustParticle(x,y))
    # draw dust
    for p in dust_particles[:]:
        if not p.update(): dust_particles.remove(p)
        else: p.draw(buf)
    # draw speaker particles
    for p in speaker_particles[:]:
        if not p.update(): speaker_particles.remove(p)
        else: p.draw(buf)
    # blit buffer with shake
    screen.blit(buf,(dx,dy))