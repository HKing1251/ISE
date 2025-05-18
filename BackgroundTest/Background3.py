import pygame
import sys
import time
import random
import math

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)  


screen_width, screen_height = 1000, 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Final Level")


pygame.mixer.music.load('BackgroundTest/Ode.mp3')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)  # Loop indefinitely

background_image = pygame.image.load(r'BackgroundTest/bg3.png')
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

speaker1 = pygame.image.load(r'BackgroundTest/Lvl3Speaker1.png')
speaker2 = pygame.image.load(r'BackgroundTest/Lvl3Speaker2.png')


speaker_width, speaker_height = 150, 150
speaker1 = pygame.transform.scale(speaker1, (speaker_width, speaker_height))
speaker2 = pygame.transform.scale(speaker2, (speaker_width, speaker_height))
left_speaker_pos = (200, 420) 
right_speaker_pos = (650, 420) 

#audio analysis
audio_sample_event = pygame.USEREVENT + 1
pygame.time.set_timer(audio_sample_event, 30)  # Check audio levels every 30ms

#timer for speaker image
speaker_swap_event = pygame.USEREVENT + 2
pygame.time.set_timer(speaker_swap_event, 500) 

#animation update timer
force_animation_event = pygame.USEREVENT + 3
pygame.time.set_timer(force_animation_event, 300)  # Force animation update every 300ms

# Track speaker image to show
use_first_image = True
last_image_swap_time = 0


# Disco Ball Light Class
class DiscoLight:
    def __init__(self):
        # Position
        self.source_x = screen_width // 2
        self.source_y = 140  # Position of the disco ball
        
        #properties
        self.angle = random.uniform(0, 2 * math.pi)
        self.length = random.randint(300, 600)  # Length of  beam
        self.width = random.randint(20, 40)     # Width of beam
        self.rotation_speed = random.uniform(0.005, 0.02)  # speed
        
        # Color
        self.hue = random.random()  #hue
        self.color = self.hsv_to_rgb(self.hue, 0.9, 1.0) 
        
        # Transparency and fade effects
        self.alpha = random.randint(50, 120)    # Semi-transparent
        self.alpha_change = random.uniform(-0.5, 0.5)  # Fading in and out
        
        # Lifespan and tracking
        self.life = random.randint(150, 300)
        
    def hsv_to_rgb(self, h, s, v):
        # HSV to RGB
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
        # Rotate 
        self.angle += self.rotation_speed
        
        # Fade
        self.alpha += self.alpha_change
        if self.alpha <= 30:
            self.alpha = 30
            self.alpha_change = random.uniform(0.2, 0.8)
        elif self.alpha >= 120:
            self.alpha = 120
            self.alpha_change = random.uniform(-0.8, -0.2)
            
        #change color
        self.hue = (self.hue + 0.001) % 1.0
        self.color = self.hsv_to_rgb(self.hue, 0.9, 1.0)
        
        # Decrease lifespan
        self.life -= 1
        
        return self.life > 0
    
    def draw(self, surface):
        # Calc end point
        end_x = self.source_x + math.cos(self.angle) * self.length
        end_y = self.source_y + math.sin(self.angle) * self.length
        
        # surface for the light
        beam_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        
        # widening beam
        angle_perpendicular = self.angle + math.pi/2
        
        # Points near the sourc
        source_width = self.width * 0.2
        p1_near = (self.source_x + math.cos(angle_perpendicular) * source_width,
                   self.source_y + math.sin(angle_perpendicular) * source_width)
        p2_near = (self.source_x - math.cos(angle_perpendicular) * source_width,
                   self.source_y - math.sin(angle_perpendicular) * source_width)
        
        # Points at the end
        p1_far = (end_x + math.cos(angle_perpendicular) * self.width,
                  end_y + math.sin(angle_perpendicular) * self.width)
        p2_far = (end_x - math.cos(angle_perpendicular) * self.width,
                  end_y - math.sin(angle_perpendicular) * self.width)
        
        # Draw
        points = [p1_near, p2_near, p2_far, p1_far]
        color_with_alpha = (*self.color, int(self.alpha))
        pygame.draw.polygon(beam_surface, color_with_alpha, points)
        
        #glow effect
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


# Audio peak 
class AudioAnalyzer:
    def __init__(self):
        self.beat_threshold = 0.15  
        self.last_beat_time = 0
        self.cooldown = 100 
        self.last_volumes = [0] * 5 
        self.current_volume = 0
        self.volume_change_rate = 0
        self.frame_count = 0
        
       
        self.oscillators = [
            {"freq": 2.5, "amp": 0.3, "phase": 0},           # Main beat
            {"freq": 4.2, "amp": 0.15, "phase": 1.3},        # Faster rhythm
            {"freq": 1.8, "amp": 0.25, "phase": 2.7},        # Slower elements
            {"freq": 6.0, "amp": 0.1, "phase": 0.5}          # High-frequency details
        ]
        
    def analyze(self):
        busy = pygame.mixer.music.get_busy()
        
        # detect peaks
        self.frame_count += 1
        if self.frame_count % 3 == 0 and busy:  
            current_time = pygame.time.get_ticks()
            time_factor = current_time * 0.001  
            
            # Base volume level
            base_vol = 0.35
            
            # Sum oscillators
            oscillation = 0
            for osc in self.oscillators:
                oscillation += osc["amp"] * math.sin(time_factor * osc["freq"] + osc["phase"])
            
            # variation 
            random_vol = random.uniform(-0.07, 0.07)
            
            #volume
            self.current_volume = min(1.0, max(0.1, base_vol + oscillation + random_vol))
            
            self.last_volumes.append(self.current_volume)
            self.last_volumes.pop(0)
            
            weights = [0.1, 0.15, 0.2, 0.25, 0.3]
            avg_past = sum(v * w for v, w in zip(self.last_volumes[:-1], weights[:len(self.last_volumes)-1])) / sum(weights[:len(self.last_volumes)-1]) if len(self.last_volumes) > 1 else 0
            
           
            self.volume_change_rate = max(0, self.current_volume - avg_past) * 1.5
            
     
            primary_threshold = self.beat_threshold
            secondary_threshold = self.beat_threshold * 0.7
            
         
            is_primary_beat = (self.volume_change_rate > primary_threshold and 
                            current_time - self.last_beat_time > self.cooldown)
            
         
            is_secondary_beat = (self.volume_change_rate > secondary_threshold and 
                               current_time - self.last_beat_time > self.cooldown * 0.7 and
                               not is_primary_beat)
            
            # Detect occasional random beats for variation
            is_random_beat = (random.random() < 0.1 and 
                             current_time - self.last_beat_time > self.cooldown * 1.5 and
                             not (is_primary_beat or is_secondary_beat))
            
            is_beat = is_primary_beat or is_secondary_beat or is_random_beat
            
            if is_beat:
                self.last_beat_time = current_time
                if is_primary_beat:
                    return 1.0
                elif is_secondary_beat:
                    return 0.7
                else:
                    return 0.5
        
        return 0 
    
    def get_volume_level(self):
        return self.current_volume
    
    def get_volume_change(self):
        return self.volume_change_rate



audio_analyzer = AudioAnalyzer()

# Init disco
disco_lights = []
MAX_DISCO_LIGHTS = 12  # Maximum numlights

# Main Game Loop
clock = pygame.time.Clock()
running = True

# Variables for beat-based animation
beat_pulse_time = 0
beat_pulse_duration = 150 
beat_pulse_amount = 0
beat_count = 0

# Ambient pulse 
ambient_pulse = 0
ambient_pulse_direction = 0.02

# Last time new disco light was added
last_light_time = 0

while running:
    current_time = pygame.time.get_ticks()

    beat_intensity = audio_analyzer.analyze()  
    volume_level = audio_analyzer.get_volume_level()
    volume_change = audio_analyzer.get_volume_change()
    
    if beat_intensity > 0:
        beat_pulse_time = current_time
        beat_pulse_amount = min(1.0, 0.3 + volume_level * beat_intensity)  
        beat_count += 1
        
        # Toggle speaker image
        use_first_image = not use_first_image
        last_image_swap_time = current_time
        
        # disco lights on strong beats
        if beat_intensity > 0.7 and len(disco_lights) < MAX_DISCO_LIGHTS:
            # Add 1-3 new lights on strong beats
            for _ in range(random.randint(1, 3)):
                disco_lights.append(DiscoLight())
    
    # Add disco lights 
    if current_time - last_light_time > 300 and len(disco_lights) < MAX_DISCO_LIGHTS:
        disco_lights.append(DiscoLight())
        last_light_time = current_time
    
    # current beat pulse effect 
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
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == speaker_swap_event:
            if current_time - last_image_swap_time >= 500: 
                use_first_image = not use_first_image
                last_image_swap_time = current_time
                if current_time - beat_pulse_time > beat_pulse_duration: 
                    beat_pulse_time = current_time
                    beat_pulse_amount = 0.2  
    

    screen.blit(background_image, (0, 0))
    
    # Update and draw disco lights
    for light in disco_lights[:]:
        if not light.update():
            disco_lights.remove(light)
        else:
            light.draw(screen)
    
    # scaling based on pulse
    speaker_scale = 1.0 + current_pulse * 0.25 

    #speaker image based on current state
    current_speaker = speaker1 if use_first_image else speaker2
    
    scaled_width = int(speaker_width * speaker_scale)
    scaled_height = int(speaker_height * speaker_scale)
    scaled_speaker = pygame.transform.scale(current_speaker, (scaled_width, scaled_height))

    left_adjusted_x = left_speaker_pos[0] - (scaled_width - speaker_width) // 2
    left_adjusted_y = left_speaker_pos[1] - (scaled_height - speaker_height) // 2
    screen.blit(scaled_speaker, (left_adjusted_x, left_adjusted_y))

    right_adjusted_x = right_speaker_pos[0] - (scaled_width - speaker_width) // 2
    right_adjusted_y = right_speaker_pos[1] - (scaled_height - speaker_height) // 2
    screen.blit(scaled_speaker, (right_adjusted_x, right_adjusted_y))
    
   
    pygame.display.flip()
    
    clock.tick(60)


pygame.mixer.music.stop()
print("Closing...")
pygame.quit()
sys.exit()