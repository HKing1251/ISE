import pygame
import math
import random
import os
import colorsys

BASE_PATH = os.path.dirname(__file__)

# Globals
initialized = False
screen_width = screen_height = 0
background_image = None
left_speaker = right_speaker = None
speaker_width, speaker_height = 180, 180
left_speaker_pos = right_speaker_pos = (0, 0)

#pulse
beat_pulse_time = 0
beat_pulse_amount = 0
beat_pulse_duration = 150
ambient_pulse = 0
ambient_pulse_direction = 0.02

# Combo 
try:
    import __main__
    MAIN_MODULE_AVAILABLE = True
except ImportError:
    MAIN_MODULE_AVAILABLE = False

def get_current_combo() -> int:
    if MAIN_MODULE_AVAILABLE:
        try:
            if hasattr(__main__, 'combo'):
                return __main__.combo
            if hasattr(__main__, 'current_combo'):
                return __main__.current_combo
        except:
            pass
    return 0

# Screen shake on combo milestones
last_milestone = 0
shake_start_time = 0
shake_duration = 1000  
shake_amplitude = 5   

# Smoke effect
SMOKE_IMG = None
smoke_left = smoke_right = None
MAX_PARTICLES = 10
BURST_COUNT = 5

# Spotlights
spotlights = []

def scale(img: pygame.Surface, factor: float) -> pygame.Surface:
    w = int(img.get_width() * factor)
    h = int(img.get_height() * factor)
    return pygame.transform.scale(img, (w, h))

class AudioAnalyzer:
    def __init__(self):
        self.oscillators = [
            {"freq":2.5, "amp":0.3,  "phase":0},
            {"freq":4.2, "amp":0.15, "phase":1.3},
            {"freq":1.8, "amp":0.25, "phase":2.7},
            {"freq":6.0, "amp":0.1,  "phase":0.5}
        ]
        self.current_volume = 0
        self.frame_count = 0

    def analyze(self) -> float:
        self.frame_count += 1
        if self.frame_count % 3 == 0:
            t = pygame.time.get_ticks() * 0.001
            osc = sum(o["amp"] * math.sin(t * o["freq"] + o["phase"])
                      for o in self.oscillators)
            base = 0.35
            rnd = random.uniform(-0.07, 0.07)
            self.current_volume = max(0.1, min(1.0, base + osc + rnd))
            return self.current_volume
        return 0.0

audio_analyzer = AudioAnalyzer()

class SmokeParticle:
    def __init__(self, x: float, y: float):
        self.x, self.y = x, y
        self.scale_k = 0.1
        self.img = scale(SMOKE_IMG, self.scale_k)
        self.alpha = 255
        self.alpha_rate = 3
        self.alive = True
        self.vx = random.uniform(-0.1, 0.1)
        self.vy = random.uniform(4.7, 5.0)

    def update(self):
        self.x += self.vx
        self.y -= self.vy
        self.scale_k += 0.02
        self.alpha -= self.alpha_rate
        if self.alpha <= 0:
            self.alpha = 0
            self.alive = False
        self.alpha_rate = max(1.0, self.alpha_rate - 0.03)
        self.img = scale(SMOKE_IMG, self.scale_k)
        self.img.set_alpha(int(self.alpha))

    def draw(self, surface: pygame.Surface):
        rect = self.img.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(self.img, rect)

class SmokeEmitter:
    def __init__(self, x: float, y: float):
        self.x, self.y = x, y
        self.particles: list[SmokeParticle] = []

    def burst(self):
        for _ in range(BURST_COUNT):
            if len(self.particles) >= MAX_PARTICLES:
                break
            self.particles.append(SmokeParticle(self.x, self.y))

    def update(self):
        alive = []
        for p in self.particles:
            p.update()
            if p.alive:
                alive.append(p)
        self.particles = alive

    def draw(self, surface: pygame.Surface):
        for p in sorted(self.particles, key=lambda p: p.y, reverse=True):
            p.draw(surface)

class Spotlight:
    def __init__(self, x: float, cone_angle=20):
        self.x = x
        self.y = 0
        self.cone_angle = cone_angle
        # timings
        self.pattern_time  = random.uniform(0, 2*math.pi)
        self.pattern_speed = random.uniform(0.02, 0.05)
        self.swing_amount = screen_width * 0.2
        self.zig_amp = screen_height * 0.
        self.hue   = random.random()
        self.alpha = 60

    def update(self):
        # advance time & hue
        self.pattern_time += self.pattern_speed
        self.hue= (self.hue + 0.002) % 1.0
        # target
        tx = self.x + math.sin(self.pattern_time * 3) * self.swing_amount
        ty = screen_height - math.sin(self.pattern_time) * self.zig_amp
        self.target_x, self.target_y = tx, ty

    def draw(self, surface: pygame.Surface):
        cone = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        dx, dy = self.target_x - self.x, self.target_y - self.y
        dist = math.hypot(dx, dy)
        ang  = math.atan2(dy, dx)
        width = 2 * dist * math.tan(math.radians(self.cone_angle / 2))
        p0 = (self.x, self.y)
        p1 = (self.target_x - width/2*math.cos(ang+math.pi/2),self.target_y - width/2*math.sin(ang+math.pi/2))
        p2 = (self.target_x + width/2*math.cos(ang+math.pi/2),self.target_y + width/2*math.sin(ang+math.pi/2))
        #rainbow stuff
        for i in range(5):
            alpha = int(self.alpha * 1.5 * (5 - i) / 5)
            alpha = min(alpha, 255)
            hue_i = (self.hue + i*0.02) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue_i, 1, 1)
            color = (int(r*255), int(g*255), int(b*255), alpha)
    
            sf = 1 + i*0.05
            v1 = (p0[0] + (p1[0]-p0[0])*sf, p0[1] + (p1[1]-p0[1])*sf)
            v2 = (p0[0] + (p2[0]-p0[0])*sf, p0[1] + (p2[1]-p0[1])*sf)
            
            pygame.draw.polygon(cone, color, [p0, v1, v2])
        
        surface.blit(cone, (0,0))

def init_background(screen: pygame.Surface):
    global initialized, screen_width, screen_height
    global background_image, left_speaker, right_speaker
    global left_speaker_pos, right_speaker_pos
    global SMOKE_IMG, smoke_left, smoke_right, spotlights

    if initialized:
        return

    screen_width, screen_height = screen.get_size()
    initialized = True

    # bg + speak+ smoke
    bg = pygame.image.load(os.path.join(BASE_PATH, "Bg3.png")).convert()
    background_image = pygame.transform.scale(bg, (screen_width, screen_height))
    ls = pygame.image.load(os.path.join(BASE_PATH, "Lvl3SpeakerLeft.png")).convert_alpha()
    rs = pygame.image.load(os.path.join(BASE_PATH, "Lvl3SpeakerRight.png")).convert_alpha()
    left_speaker = pygame.transform.scale(ls, (speaker_width, speaker_height))
    right_speaker = pygame.transform.scale(rs, (speaker_width, speaker_height))
    left_speaker_pos = (20, 20)
    right_speaker_pos = (screen_width - speaker_width - 20, 20)
    SMOKE_IMG = pygame.image.load(os.path.join(BASE_PATH, "smoke.png")).convert_alpha()
    smoke_left = SmokeEmitter(200, screen_height - 60)
    smoke_right = SmokeEmitter(screen_width - 200, screen_height - 60)

    #spotlights
    spotlights = [
        Spotlight(screen_width * 0.2),
        Spotlight(screen_width * 0.4),
        Spotlight(screen_width * 0.6),
        Spotlight(screen_width * 0.8),
    ]

def draw_dynamic_background(screen: pygame.Surface):
    global beat_pulse_time, beat_pulse_amount
    global ambient_pulse, ambient_pulse_direction
    global last_milestone, shake_start_time

    if not initialized:
        init_background(screen)

    t_now = pygame.time.get_ticks()
    combo = get_current_combo()


    if combo > 0 and combo % 5 == 0 and combo != last_milestone:
        shake_start_time = t_now
        last_milestone = combo
        
    if combo > 0 and combo % 10 == 0 and combo != last_milestone:
        smoke_left.burst()
        smoke_right.burst()

    #shake calcs
    dx = dy = 0
    if t_now - shake_start_time < shake_duration:
        dx = random.randint(-shake_amplitude, shake_amplitude)
        dy = random.randint(-shake_amplitude, shake_amplitude)

    # start buffer
    buf = pygame.Surface((screen_width, screen_height))
    buf.blit(background_image, (0, 0))

    #moke
    smoke_left.update()
    smoke_left.draw(buf)
    smoke_right.update()
    smoke_right.draw(buf)

    #spotlights
    if combo >= 10:
        for sp in spotlights:
            sp.update()
            sp.draw(buf)

    
    vol = audio_analyzer.analyze()
    if vol > 0.5:
        beat_pulse_time = t_now
        beat_pulse_amount = vol
    if t_now - beat_pulse_time < beat_pulse_duration:
        prog = 1 - ((t_now - beat_pulse_time) / beat_pulse_duration)
        current_pulse = beat_pulse_amount * prog
    else:
        ambient_pulse += ambient_pulse_direction
        if ambient_pulse > 0.15:
            ambient_pulse, ambient_pulse_direction = 0.15, -0.02
        elif ambient_pulse < 0:
            ambient_pulse, ambient_pulse_direction = 0, 0.02
        current_pulse = ambient_pulse

    # Speak pulse
    speaker_scale = 1.0 + current_pulse * 0.3
    for img, pos in [(left_speaker, left_speaker_pos), (right_speaker, right_speaker_pos)]:
        w = int(speaker_width * speaker_scale * 1.5)
        h = int(speaker_height * speaker_scale * 1.5)
        scaled = pygame.transform.scale(img, (w, h))
        adj_x = pos[0] - (w - speaker_width) // 2
        adj_y = pos[1] - (h - speaker_height) // 2
        buf.blit(scaled, (adj_x, adj_y))

    # blit for shake
    screen.blit(buf, (dx, dy))
