import pygame
from pygame import *
import random
import time
import sys
import os

def main():
    # Initialize Pygame
    pygame.init()
    
    # Set up the display
    screen_width, screen_height = 800, 600
    screen = display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Simple Rhythm Game")
    
    # Define colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    
    # Set up game clock
    clock = pygame.time.Clock()
    
    # Arrow settings
    arrow_size = 60
    arrow_speed = 5
    arrow_spacing = 100
    
    # Define key bindings
    KEY_LEFT = K_LEFT
    KEY_DOWN = K_DOWN
    KEY_UP = K_UP
    KEY_RIGHT = K_RIGHT
    
    # Create a function to extract arrows from the sprite sheet
    # For this example, we'll save the spritesheet and extract from it
    def load_arrow_images(spritesheet_path):
        try:
            # Load the spritesheet
            spritesheet = pygame.image.load(spritesheet_path).convert_alpha()
            
            # Extract the arrows we need - using the first row of arrows
            # These coordinates might need adjustment based on the actual spritesheet
            left_arrow = pygame.Surface((arrow_size, arrow_size), SRCALPHA)
            down_arrow = pygame.Surface((arrow_size, arrow_size), SRCALPHA)
            up_arrow = pygame.Surface((arrow_size, arrow_size), SRCALPHA)
            right_arrow = pygame.Surface((arrow_size, arrow_size), SRCALPHA)
            
            # Extract arrows from first row (blue down, blue down, green up, green up)
            # These are approximations and may need adjustments
            left_arrow.blit(spritesheet, (0, 0), (0, 0, arrow_size, arrow_size))
            down_arrow.blit(spritesheet, (0, 0), (arrow_size, 0, arrow_size, arrow_size))
            up_arrow.blit(spritesheet, (0, 0), (arrow_size*2, 0, arrow_size, arrow_size))
            right_arrow.blit(spritesheet, (0, 0), (arrow_size*3, 0, arrow_size, arrow_size))
            
            return {
                "left": left_arrow,
                "down": down_arrow,
                "up": up_arrow,
                "right": right_arrow
            }
        except pygame.error as e:
            print(f"Error loading spritesheet: {e}")
            # Create colored placeholders if loading fails
            placeholders = {}
            colors = [(0, 0, 255), (0, 255, 0), (255, 255, 0), (255, 0, 0)]
            for i, direction in enumerate(["left", "down", "up", "right"]):
                surf = pygame.Surface((arrow_size, arrow_size), SRCALPHA)
                pygame.draw.polygon(surf, colors[i], [(arrow_size//2, 0), (arrow_size, arrow_size//2), 
                                                     (arrow_size//2, arrow_size), (0, arrow_size//2)])
                placeholders[direction] = surf
            return placeholders
    
    # Save the spritesheet image
    def save_spritesheet(image_data):
        """Save the spritesheet from the provided image data"""
        with open("arrowskin.png", "wb") as f:
            f.write(image_data)
        return "arrowskin.png"
    
    # Generate placeholder images if spritesheet isn't available
    def generate_arrow_images():
        """Generate basic arrow shapes as placeholders"""
        arrows = {}
        
        # Define arrow colors
        colors = {
            "left": (100, 149, 237),  # cornflower blue
            "down": (50, 205, 50),    # lime green
            "up": (154, 205, 50),     # yellow green
            "right": (220, 20, 60)    # crimson
        }
        
        # Create arrow surfaces with basic shapes
        for direction, color in colors.items():
            surf = pygame.Surface((arrow_size, arrow_size), SRCALPHA)
            if direction == "left":
                points = [(arrow_size//4, arrow_size//2), 
                          (arrow_size*3//4, arrow_size//4), 
                          (arrow_size*3//4, arrow_size*3//4)]
            elif direction == "down":
                points = [(arrow_size//2, arrow_size*3//4), 
                          (arrow_size//4, arrow_size//4), 
                          (arrow_size*3//4, arrow_size//4)]
            elif direction == "up":
                points = [(arrow_size//2, arrow_size//4), 
                          (arrow_size//4, arrow_size*3//4), 
                          (arrow_size*3//4, arrow_size*3//4)]
            else:  # right
                points = [(arrow_size*3//4, arrow_size//2), 
                          (arrow_size//4, arrow_size//4), 
                          (arrow_size//4, arrow_size*3//4)]
                
            pygame.draw.polygon(surf, color, points)
            # Add a border
            pygame.draw.polygon(surf, (255, 255, 255), points, 2)
            arrows[direction] = surf
            
        return arrows
    
    # Try to load the spritesheet, or use generated arrows
    try:
        # In a real app, you would save the uploaded image
        # For now we'll use generated arrows
        arrow_images = generate_arrow_images()
    except Exception as e:
        print(f"Error: {e}")
        arrow_images = generate_arrow_images()
    
    # Create target positions for each arrow
    target_y = 100
    targets = {
        "left": {"x": screen_width // 2 - arrow_spacing * 1.5, "y": target_y},
        "down": {"x": screen_width // 2 - arrow_spacing * 0.5, "y": target_y},
        "up": {"x": screen_width // 2 + arrow_spacing * 0.5, "y": target_y},
        "right": {"x": screen_width // 2 + arrow_spacing * 1.5, "y": target_y}
    }
    
    # Create target arrow objects
    target_arrows = []
    for direction, pos in targets.items():
        target_arrows.append({
            "direction": direction,
            "x": pos["x"],
            "y": pos["y"],
            "image": arrow_images[direction]
        })
    
    # Game variables
    score = 0
    combo = 0
    misses = 0
    health = 50
    max_health = 100
    
    # Font for scoring
    font = pygame.font.SysFont("Arial", 30)
    
    # Rating images
    ratings = {
        "perfect": font.render("PERFECT!", True, (0, 255, 0)),
        "good": font.render("GOOD", True, (255, 255, 0)),
        "bad": font.render("BAD", True, (255, 165, 0)),
        "miss": font.render("MISS", True, (255, 0, 0))
    }
    
    # Active rating display
    current_rating = None
    rating_timer = 0
    
    # Game state
    game_over = False
    
    # Note generation
    notes = []
    last_note_time = time.time()
    note_interval = 1.0  # Time between notes in seconds
    
    class Note:
        def __init__(self, direction, target_x, target_y):
            self.direction = direction
            self.x = target_x
            self.y = screen_height
            self.width = arrow_size
            self.height = arrow_size
            self.hit = False
            self.missed = False
            self.image = arrow_images[direction]
        
        def update(self):
            self.y -= arrow_speed
            # Check if note was missed
            if self.y < target_y - 50 and not self.hit and not self.missed:
                self.missed = True
                return "miss"
            return None
        
        def draw(self, surface):
            if not self.hit and not self.missed:
                surface.blit(self.image, (self.x - self.width/2, self.y - self.height/2))
    
    # Main game loop
    running = True
    while running:
        # Handle events
        for e in pygame.event.get():
            if e.type == QUIT:
                running = False
            elif e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    running = False
                
                # Handle key presses for arrows
                direction = None
                if e.key == KEY_LEFT:
                    direction = "left"
                elif e.key == KEY_DOWN:
                    direction = "down"
                elif e.key == KEY_UP:
                    direction = "up"
                elif e.key == KEY_RIGHT:
                    direction = "right"
                
                if direction:
                    hit_note = False
                    for note in notes:
                        if note.direction == direction and not note.hit and not note.missed:
                            # Calculate distance from target
                            distance = abs(note.y - target_y)
                            
                            # Different ratings based on distance
                            if distance < 10:
                                score += 100
                                combo += 1
                                current_rating = ratings["perfect"]
                                health = min(max_health, health + 2)
                            elif distance < 30:
                                score += 50
                                combo += 1
                                current_rating = ratings["good"]
                                health = min(max_health, health + 1)
                            elif distance < 50:
                                score += 10
                                combo = 0
                                current_rating = ratings["bad"]
                            else:
                                # Too far, count as miss
                                continue
                            
                            rating_timer = 30  # Display rating for 30 frames
                            note.hit = True
                            hit_note = True
                            break
                    
                    # If no note was hit within the valid distance, it's a miss
                    if not hit_note:
                        combo = 0
                        current_rating = ratings["miss"]
                        rating_timer = 30
                        health = max(0, health - 5)
        
        # Generate new notes
        current_time = time.time()
        if current_time - last_note_time > note_interval:
            # Randomly choose which arrow to generate
            directions = ["left", "down", "up", "right"]
            direction = random.choice(directions)
            target_x = targets[direction]["x"]
            new_note = Note(direction, target_x, target_y)
            notes.append(new_note)
            last_note_time = current_time
            
            # Make notes appear more frequently as game progresses
            note_interval = max(0.3, note_interval * 0.99)
        
        # Update notes
        for note in notes[:]:
            result = note.update()
            if result == "miss" and not note.missed:
                misses += 1
                combo = 0
                current_rating = ratings["miss"]
                rating_timer = 30
                health = max(0, health - 5)
            
            # Remove notes that are off screen or have been hit
            if note.y < 0 or note.hit:
                notes.remove(note)
        
        # Decrease rating timer
        if rating_timer > 0:
            rating_timer -= 1
        
        # Check if game over
        if health <= 0:
            game_over = True
        
        # Drawing
        screen.fill(BLACK)
        
        # Draw health bar
        health_bar_width = 200
        health_bar_height = 20
        health_bar_x = screen_width - health_bar_width - 20
        health_bar_y = 20
        
        # Background of health bar
        pygame.draw.rect(screen, (100, 100, 100), 
                         (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        
        # Actual health
        health_width = int((health / max_health) * health_bar_width)
        pygame.draw.rect(screen, (0, 255, 0), 
                         (health_bar_x, health_bar_y, health_width, health_bar_height))
        
        # Draw target arrows
        for arrow in target_arrows:
            arrow_rect = arrow["image"].get_rect(center=(arrow["x"], arrow["y"]))
            screen.blit(arrow["image"], arrow_rect)
            
            # Draw target line/area
            pygame.draw.line(screen, (150, 150, 150), 
                             (arrow["x"] - arrow_size, arrow["y"]), 
                             (arrow["x"] + arrow_size, arrow["y"]), 2)
        
        # Draw notes
        for note in notes:
            if not note.hit and not note.missed:
                note_rect = note.image.get_rect(center=(note.x, note.y))
                screen.blit(note.image, note_rect)
        
        # Draw score and combo
        score_text = font.render(f"Score: {score}", True, WHITE)
        combo_text = font.render(f"Combo: {combo}", True, WHITE)
        miss_text = font.render(f"Misses: {misses}", True, WHITE)
        
        screen.blit(score_text, (20, 20))
        screen.blit(combo_text, (20, 60))
        screen.blit(miss_text, (20, 100))
        
        # Draw current rating
        if rating_timer > 0 and current_rating:
            rating_rect = current_rating.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(current_rating, rating_rect)
        
        # Game over screen
        if game_over:
            game_over_text = font.render("GAME OVER", True, (255, 0, 0))
            restart_text = font.render("Press R to restart or ESC to quit", True, WHITE)
            
            game_over_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
            restart_rect = restart_text.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
            
            screen.blit(game_over_text, game_over_rect)
            screen.blit(restart_text, restart_rect)
            
            # Check for restart
            keys = pygame.key.get_pressed()
            if keys[K_r]:
                # Reset game variables
                score = 0
                combo = 0
                misses = 0
                health = 50
                notes = []
                last_note_time = time.time()
                note_interval = 1.0
                game_over = False
        
        # Draw instructions at the bottom
        instructions = font.render("Press arrow keys when notes align with targets", True, WHITE)
        inst_rect = instructions.get_rect(center=(screen_width // 2, screen_height - 30))
        screen.blit(instructions, inst_rect)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
