import pygame
import sys
import time
import random
import math

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024) 

screen_width, screen_height = 1000, 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Game Window")


pygame.mixer.music.load('BackgroundTest/Ode.mp3')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1) 


background_image = pygame.image.load(r'BackgroundTest/Bg2.png')
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
speaker1 = pygame.image.load(r'BackgroundTest/Lvl2Speaker1.png')
speaker2 = pygame.image.load(r'BackgroundTest/Lvl2Speaker2.png')

#dimension
speaker1_width, speaker1_height = 250, 200
speaker2_width, speaker2_height = 250, 200
speaker1 = pygame.transform.scale(speaker1, (speaker1_width, speaker1_height))
speaker2 = pygame.transform.scale(speaker2, (speaker2_width, speaker2_height))

# Speaker positions
speaker1_pos = (screen_width // 2 - speaker1_width // 2, 400)
speaker2_pos = (screen_width // 2 - speaker2_width // 2, 400)

# audio analysis
audio_sample_event = pygame.USEREVENT + 1
pygame.time.set_timer(audio_sample_event, 30)  # Check audio levels every 30ms

#particle emission
particle_emit_event = pygame.USEREVENT + 2
pygame.time.set_timer(particle_emit_event, 50)  # Emit every 50ms

#animation update timer
force_animation_event = pygame.USEREVENT + 3
pygame.time.set_timer(force_animation_event, 300)  # every 300ms

use_first_image = True

# Audio detection
class AudioAnalyzer:
    def __init__(self):
        self.beat_threshold = 0.15  # threshold to detect beats
        self.last_beat_time = 0
        self.cooldown = 100  
        self.last_volumes = [0] * 5  # Keep track of last volume samples
        self.current_volume = 0
        self.volume_change_rate = 0
        self.frame_count = 0
    
        self.oscillators = [
            {"freq": 2.5, "amp": 0.3, "phase": 0},           # Main beat
            {"freq": 4.2, "amp": 0.15, "phase": 1.3},        # Faster
            {"freq": 1.8, "amp": 0.25, "phase": 2.7},        # Slower
            {"freq": 6.0, "amp": 0.1, "phase": 0.5}          # High-frequency details
        ]
        
    def analyze(self):
        busy = pygame.mixer.music.get_busy()
        
        # detect peaks
        self.frame_count += 1
        if self.frame_count % 3 == 0 and busy: 
            current_time = pygame.time.get_ticks()
            time_factor = current_time * 0.001 
            
            #vol level
            base_vol = 0.35
            
            #waveform
            oscillation = 0
            for osc in self.oscillators:
                oscillation += osc["amp"] * math.sin(time_factor * osc["freq"] + osc["phase"])
            
            random_vol = random.uniform(-0.07, 0.07)
            
            self.current_volume = min(1.0, max(0.1, base_vol + oscillation + random_vol))
            
            # Update history + calc rate of change
            self.last_volumes.append(self.current_volume)
            self.last_volumes.pop(0)
            
            # weighted average volumes
            weights = [0.1, 0.15, 0.2, 0.25, 0.3]
            avg_past = sum(v * w for v, w in zip(self.last_volumes[:-1], weights[:len(self.last_volumes)-1])) / sum(weights[:len(self.last_volumes)-1]) if len(self.last_volumes) > 1 else 0
            
            # Calc change rate
            self.volume_change_rate = max(0, self.current_volume - avg_past) * 1.5
            
            primary_threshold = self.beat_threshold
            secondary_threshold = self.beat_threshold * 0.7
            
            # big beats
            is_primary_beat = (self.volume_change_rate > primary_threshold and 
                            current_time - self.last_beat_time > self.cooldown)
            
            # smaller beats
            is_secondary_beat = (self.volume_change_rate > secondary_threshold and 
                               current_time - self.last_beat_time > self.cooldown * 0.7 and
                               not is_primary_beat)
            
            #andom beats
            is_random_beat = (random.random() < 0.1 and 
                             current_time - self.last_beat_time > self.cooldown * 1.5 and
                             not (is_primary_beat or is_secondary_beat))
            
            is_beat = is_primary_beat or is_secondary_beat or is_random_beat
            
            if is_beat:
                self.last_beat_time = current_time
                # Return beat intensity (1.0 for primary, 0.7 for secondary, 0.5 for random)
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

# Dust Particle 
class DustParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.uniform(0.8, 3.0) 
        
        brightness = random.randint(180, 240)
        self.color = (brightness, brightness, brightness, random.randint(20, 80))  # Semi-transparent
        
        self.velocityX = random.uniform(-0.2, 0.2)
        self.velocityY = random.uniform(-0.15, 0.15)
        self.life = random.randint(300, 800)
        
        #wobble effect
        self.wobble_speed = random.uniform(0.01, 0.05)
        self.wobble_amount = random.uniform(0.1, 0.4)
        self.wobble_offset = random.uniform(0, math.pi * 2)

    def update(self):
        #sine wave motion for wobble 
        wobble = math.sin(pygame.time.get_ticks() * self.wobble_speed + self.wobble_offset) * self.wobble_amount
        
        self.x += self.velocityX + wobble
        self.y += self.velocityY
        
        self.size -= 0.003
        self.life -= 1
        
        # Remove
        if self.size <= 0 or self.life <= 0 or self.y < -10 or self.y > screen_height + 10 or self.x < -10 or self.x > screen_width + 10:
            dust_particles.remove(self)

    def draw(self, surface):
        # Draw circl;e
        particle_surface = pygame.Surface((int(self.size * 2 + 1), int(self.size * 2 + 1)), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, self.color, (int(self.size + 0.5), int(self.size + 0.5)), int(self.size))
        surface.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))

# Speaker Particle
class SpeakerParticle:
    def __init__(self, x, y, volume=0.5, intensity=1.0):
        self.center_x = x  
        self.center_y = y  
        
        self.size = random.uniform(0.5, 2.0) * (1 + volume * intensity * 0.5)  
        
       
        color_choice = random.randint(0, 2)
        if color_choice == 0:
            base_color = (255, 0, 0)  # Red
        elif color_choice == 1:
            base_color = (0, 255, 0)  # Green
        else:
            base_color = (0, 0, 255)  # Blue
            
        # alpha for transparency
        alpha = random.randint(150, 220)
        self.color = base_color + (alpha,)
        
        # Concentric movement parameters
        self.angle = random.uniform(0, 2 * math.pi)  
        self.distance = random.uniform(10, 30)  # distance from center
        self.speed = random.uniform(1.0, 3.0) * (0.5 + volume * intensity * 0.8)  # Radial speed
        
        # Current pos from center
        self.x = self.center_x + math.cos(self.angle) * self.distance
        self.y = self.center_y + math.sin(self.angle) * self.distance
        
        self.life = random.randint(15, 35)  
        # travel direction
        self.angle_drift = random.uniform(-0.02, 0.02)
        self.original_size = self.size

    def update(self):
        # Move out
        self.distance += self.speed
        
        #angle drift
        self.angle += self.angle_drift
        
        # Update position
        self.x = self.center_x + math.cos(self.angle) * self.distance
        self.y = self.center_y + math.sin(self.angle) * self.distance
        
        # Reduce size
        self.size = self.original_size * (self.life / 35)  # Fade ou
        self.life -= 1
        
        # Remove
        if self.life <= 0 or self.distance > 150 or self.size <= 0.1:
            speaker_particles.remove(self)

    def draw(self, surface):
        particle_surface = pygame.Surface((int(self.size * 2 + 1), int(self.size * 2 + 1)), pygame.SRCALPHA)
        if len(self.color) == 4: 
            pygame.draw.circle(particle_surface, self.color, (int(self.size + 0.5), int(self.size + 0.5)), int(self.size))
        else:  
            alpha = int(255 * (self.life / 35))  # Fade out with life
            pygame.draw.circle(particle_surface, self.color + (alpha,), (int(self.size + 0.5), int(self.size + 0.5)), int(self.size))
        
        surface.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))

# Init particles + audio analyzer
dust_particles = []
speaker_particles = []
audio_analyzer = AudioAnalyzer()

# Init dust particles
for _ in range(500):  # 500 particles
    x = random.randint(0, screen_width)
    y = random.randint(0, screen_height)
    dust_particles.append(DustParticle(x, y))


clock = pygame.time.Clock()
running = True

#max particles
MAX_DUST_PARTICLES = 800 
MAX_SPEAKER_PARTICLES = 400 

# Variables for beat animation
beat_pulse_time = 0
beat_pulse_duration = 150  
beat_pulse_amount = 0
beat_count = 0
last_animation_time = 0

# Ambient pulse for no beat
ambient_pulse = 0
ambient_pulse_direction = 0.02

while running:
    current_time = pygame.time.get_ticks()
    
    beat_intensity = audio_analyzer.analyze()  #returns intensity levels
    volume_level = audio_analyzer.get_volume_level()
    volume_change = audio_analyzer.get_volume_change()
    
    # Create beat pulse effect
    if beat_intensity > 0:
        beat_pulse_time = current_time
        beat_pulse_amount = min(1.0, 0.3 + volume_level * beat_intensity)  # Scale with volume and beat intensity
        beat_count += 1
        
        # Toggle speaker on beat
        use_first_image = not use_first_image
        last_animation_time = current_time
        
        # Emit particles on beat
        speaker_center_x = speaker1_pos[0] + speaker1_width // 2
        speaker_center_y = speaker1_pos[1] + speaker1_height // 2
        
        # Num particles on beat intensity
        particles_to_emit = int(20 + 40 * volume_level * beat_intensity)
        
        if len(speaker_particles) < MAX_SPEAKER_PARTICLES:
            for _ in range(min(particles_to_emit, MAX_SPEAKER_PARTICLES - len(speaker_particles))):
                offset_x = random.randint(-speaker1_width//4, speaker1_width//4)
                offset_y = random.randint(-speaker1_height//4, speaker1_height//4)
                
                speaker_particles.append(SpeakerParticle(
                    speaker_center_x + offset_x,
                    speaker_center_y + offset_y,
                    volume_level,
                    beat_intensity
                ))
    
    # Force animation changes if too long since last beat
    if current_time - last_animation_time > 300:  # Force change every 300ms if no beats
        use_first_image = not use_first_image
        last_animation_time = current_time
        # Small pulse
        beat_pulse_time = current_time
        beat_pulse_amount = 0.3 
    
    # Calc current beat puls
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
        elif event.type == force_animation_event:
            if current_time - last_animation_time > 250:  # Only force if no recent beat
                use_first_image = not use_first_image
                last_animation_time = current_time
                if current_time - beat_pulse_time > beat_pulse_duration: 
                    beat_pulse_time = current_time
                    beat_pulse_amount = 0.2
        elif event.type == particle_emit_event:
            # add dust particles
            if len(dust_particles) < MAX_DUST_PARTICLES:
                for _ in range(8):  # Add more particles per interval
                    if random.random() < 0.7: #70% chance in screen
                        x = random.randint(0, screen_width)
                        y = random.randint(0, screen_height)
                    else:  # 30% chance for edge
                        edge = random.randint(0, 3)
                        if edge == 0: 
                            x = random.randint(0, screen_width)
                            y = 0
                        elif edge == 1: 
                            x = screen_width
                            y = random.randint(0, screen_height)
                        elif edge == 2:  
                            x = random.randint(0, screen_width)
                            y = screen_height
                        else: 
                            x = 0
                            y = random.randint(0, screen_height)
                    
                    dust_particles.append(DustParticle(x, y))
            
            #speaker particles when no beat
            if volume_level > 0.1 and len(speaker_particles) < MAX_SPEAKER_PARTICLES:
                speaker_center_x = speaker1_pos[0] + speaker1_width // 2
                speaker_center_y = speaker1_pos[1] + speaker1_height // 2
                
            
                for _ in range(int(1 + volume_level * 3)):
                    offset_x = random.randint(-speaker1_width//4, speaker1_width//4)
                    offset_y = random.randint(-speaker1_height//4, speaker1_height//4)
                    
                    speaker_particles.append(SpeakerParticle(speaker_center_x + offset_x,speaker_center_y + offset_y,volume_level * 0.3,  0.4  ))
    
    
    screen.blit(background_image, (0, 0))
    
    for particle in dust_particles[:]:
        particle.update()
        particle.draw(screen)
    
    # Calc speaker scaling
    speaker_scale = 1.0 + current_pulse * 0.25  # Up to 25%

    #Speaker image wiht pulse
    if use_first_image:
        #Scaling on spker1
        scaled_width = int(speaker1_width * speaker_scale)
        scaled_height = int(speaker1_height * speaker_scale)
        scaled_speaker = pygame.transform.scale(speaker1, (scaled_width, scaled_height))
        # Center the scaled image at the same position
        adjusted_x = speaker1_pos[0] - (scaled_width - speaker1_width) // 2
        adjusted_y = speaker1_pos[1] - (scaled_height - speaker1_height) // 2
        screen.blit(scaled_speaker, (adjusted_x, adjusted_y))
    else:
        #Scaling on speaker2
        scaled_width = int(speaker2_width * speaker_scale)
        scaled_height = int(speaker2_height * speaker_scale)
        scaled_speaker = pygame.transform.scale(speaker2, (scaled_width, scaled_height))
        # Center
        adjusted_x = speaker2_pos[0] - (scaled_width - speaker2_width) // 2
        adjusted_y = speaker2_pos[1] - (scaled_height - speaker2_height) // 2
        screen.blit(scaled_speaker, (adjusted_x, adjusted_y))
    
    for particle in speaker_particles[:]:
        particle.update()
        particle.draw(screen)
    
 
    pygame.display.flip()
    
    
    clock.tick(60)


pygame.mixer.music.stop()
print("Closing...")
pygame.quit()
sys.exit()