import pygame
import random
import time
import sys
import os
import json
from pathlib import Path

# Set the working directory to the script's location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# === Constants ===
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
ARROW_SIZE = 80
ARROW_SPACING = 100
TARGET_Y = 100  # Y position where arrows should be hit
GLOW_DURATION = 15
RATING_DISPLAY_TIME = 30
MAX_HEALTH = 100
INITIAL_HEALTH = 50

# === Level Configuration ===
LEVELS = {
    1: {"name": "Level 1", "win_threshold": 1000, "arrow_speed": 5, "note_interval_start": 1.0, "note_interval_min": 0.3, "unlocked": True},
    2: {"name": "Level 2", "win_threshold": 1500, "arrow_speed": 7, "note_interval_start": 0.8, "note_interval_min": 0.25, "unlocked": False},
    3: {"name": "Level 3", "win_threshold": 3000, "arrow_speed": 9, "note_interval_start": 0.6, "note_interval_min": 0.2, "unlocked": False}
}

# Progress file path
SAVE_FILE = "game_progress.json"

# === Colors ===
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
BLUE = (0, 191, 255)
PURPLE = (128, 0, 128)

# === Key Bindings for Direction Arrows ===
KEY_BINDINGS = {
    pygame.K_LEFT: "left",
    pygame.K_DOWN: "down",
    pygame.K_UP: "up",
    pygame.K_RIGHT: "right"
}

# Mapping of directions to image paths
ARROW_IMAGE_MAPPING = {
    "left": ["assets/arrowSkinLeftDefault.png", "assets/arrowSkinLeftGlow.png"],
    "down": ["assets/arrowSkinDownDefault.png", "assets/arrowSkinDownGlow.png"],
    "up": ["assets/arrowSkinUpDefault.png", "assets/arrowSkinUpGlow.png"],
    "right": ["assets/arrowSkinRightDefault.png", "assets/arrowSkinRightGlow.png"]
}

# Load an image, fall back if needed
def load_image(file_path, fallback_path=None):
    try:
        return pygame.image.load(file_path).convert_alpha()
    except pygame.error:
        if fallback_path:
            return pygame.image.load(fallback_path).convert_alpha()
        raise

# Load and scale all arrow images (default and glowing)
def load_arrow_images():
    def scaled_image(path):
        return pygame.transform.scale(load_image(path), (ARROW_SIZE, ARROW_SIZE))

    arrows, glowing = {}, {}
    for direction, (default_path, glow_path) in ARROW_IMAGE_MAPPING.items():
        try:
            arrows[direction] = scaled_image(default_path)
            glowing[direction] = scaled_image(glow_path)
        except Exception as e:
            raise SystemExit(f"Error loading {direction} arrows: {e}")
    return arrows, glowing

# Render text in the center of the screen
def render_text_centered(screen, text, font, color, y_offset):
    rendered = font.render(text, True, color)
    x = (SCREEN_WIDTH - rendered.get_width()) // 2
    screen.blit(rendered, (x, y_offset))


# === Note Class ===
class Note:
    def __init__(self, direction, x, speed):
        self.direction = direction
        self.x = x
        self.y = SCREEN_HEIGHT
        self.speed = speed
        self.hit = self.missed = False

    def update(self):
        self.y -= self.speed
        if self.y < TARGET_Y - 50 and not self.hit:
            self.missed = True  # Mark note as missed if it goes past the target

    def draw(self, screen, image):
        if not self.hit and not self.missed:
            rect = image.get_rect(center=(self.x, self.y))
            screen.blit(image, rect)

# Load or create progress file
def load_progress():
    try:
        with open(SAVE_FILE, 'r') as f:
            progress = json.load(f)
            # Update LEVELS with saved unlocked status
            for level_id, is_unlocked in progress.items():
                if int(level_id) in LEVELS:
                    LEVELS[int(level_id)]["unlocked"] = is_unlocked
    except (FileNotFoundError, json.JSONDecodeError):
        # Create default progress file
        save_progress()

# Save progress to file
def save_progress():
    progress = {str(level_id): level["unlocked"] for level_id, level in LEVELS.items()}
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(progress, f)
    except Exception as e:
        print(f"Error saving progress: {e}")

# === Menu System ===
def show_menu(screen, clock, font, big_font):
    menu_active = True
    selected_option = 0
    options = []

    
    
    # Build options list based on unlocked levels
    for level_id, level_data in sorted(LEVELS.items()):
        if level_data["unlocked"]:
            options.append((level_id, f"{level_data['name']} - {level_data['win_threshold']} pts"))
        else:
            options.append((level_id, f"{level_data['name']} - LOCKED"))
    
    options.append(("quit", "Quit Game"))
    
    while menu_active:
        screen.fill(BLACK)
        
        # Render title
        render_text_centered(screen, "Funky Flow Friday ", big_font, BLUE, 50)

        # Instructions
        render_text_centered(screen, "Choose a level with UP/DOWN keys, press ENTER", font, WHITE, 120)
        
        # Draw menu options
        for i, (level_id, text) in enumerate(options):
            color = YELLOW if i == selected_option else WHITE
            if level_id != "quit" and not LEVELS[level_id]["unlocked"]:
                color = GRAY  # Grayed out for locked levels
                
            option_text = font.render(text, True, color)
            position = (SCREEN_WIDTH // 2 - option_text.get_width() // 2, 200 + i * 50)
            screen.blit(option_text, position)
            
            # Add arrow indicator for selected option
            if i == selected_option:
                indicator = font.render("> ", True, color)
                screen.blit(indicator, (position[0] - indicator.get_width(), position[1]))
        
        pygame.display.flip()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    level_id, _ = options[selected_option]
                    if level_id == "quit":
                        pygame.quit()
                        sys.exit()
                    elif LEVELS[level_id]["unlocked"]:
                        return level_id
        
        clock.tick(60)

# === Game Loop ===
def play_level(screen, clock, font, big_font, level_id):
    level_config = LEVELS[level_id]
    arrow_speed = level_config["arrow_speed"]
    win_threshold = level_config["win_threshold"]
    note_interval_start = level_config["note_interval_start"]
    note_interval_min = level_config["note_interval_min"]
    
    arrows, glowing_arrows = load_arrow_images()

    # Set x positions for each arrow target
    targets = {
        "left": SCREEN_WIDTH // 2 - ARROW_SPACING * 1.5,
        "down": SCREEN_WIDTH // 2 - ARROW_SPACING * 0.5,
        "up": SCREEN_WIDTH // 2 + ARROW_SPACING * 0.5,
        "right": SCREEN_WIDTH // 2 + ARROW_SPACING * 1.5
    }

    # Glow state and timers for each arrow direction
    target_arrows = {
        dir: {"x": x, "glow": False, "timer": 0} for dir, x in targets.items()
    }

    # Game state variables
    notes, score, combo, misses, health = [], 0, 0, 0, INITIAL_HEALTH
    game_over = game_won = paused = False
    current_rating = None
    rating_timer = 0
    last_note_time = time.time()
    note_interval = note_interval_start

    # Pre-rendered rating texts
    ratings = {
        "perfect": font.render("PERFECT!", True, GREEN),
        "good": font.render("GOOD", True, YELLOW),
        "bad": font.render("BAD", True, ORANGE),
        "miss": font.render("MISS", True, RED)
    }

    level_title = font.render(f"{level_config['name']} - Target: {win_threshold} pts", True, BLUE)

    # === Game Loop ===
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return "menu"  # Return to menu
                if (game_over or game_won) and e.key == pygame.K_r:
                    return play_level(screen, clock, font, big_font, level_id)  # Restart level
                if (game_over or game_won) and e.key == pygame.K_m:
                    return "menu"  # Go to menu
                if not (game_over or game_won):
                    direction = KEY_BINDINGS.get(e.key)
                    if direction:
                        target_arrows[direction]["glow"] = True
                        target_arrows[direction]["timer"] = GLOW_DURATION
                        hit = False
                        for note in notes:
                            if note.direction == direction and not note.hit and not note.missed:
                                distance = abs(note.y - TARGET_Y)
                                if distance < 10:
                                    score += 100
                                    combo += 1
                                    current_rating = ratings["perfect"]
                                    health = min(MAX_HEALTH, health + 2)
                                elif distance < 30:
                                    score += 50
                                    combo += 1
                                    current_rating = ratings["good"]
                                    health = min(MAX_HEALTH, health + 1)
                                elif distance < 50:
                                    score += 10
                                    combo = 0
                                    current_rating = ratings["bad"]
                                else:
                                    continue
                                note.hit = True
                                hit = True
                                rating_timer = RATING_DISPLAY_TIME
                                break
                        if not hit:
                            combo = 0
                            current_rating = ratings["miss"]
                            rating_timer = RATING_DISPLAY_TIME
                            health = max(0, health - 5)

        # Check win/loss conditions
        if score >= win_threshold:
            # Unlock next level if this one is completed
            if level_id < max(LEVELS.keys()):
                LEVELS[level_id + 1]["unlocked"] = True
                save_progress()
            game_won, paused = True, True
        if health <= 0:
            game_over, paused = True, True

        # Spawn notes at intervals
        if not paused:
            if time.time() - last_note_time > note_interval:
                direction = random.choice(list(targets.keys()))
                notes.append(Note(direction, targets[direction], arrow_speed))
                last_note_time = time.time()
                note_interval = max(note_interval_min, note_interval * 0.99)  # Accelerate note speed

        # Update glow timers
        for ta in target_arrows.values():
            if ta["timer"] > 0:
                ta["timer"] -= 1
                if ta["timer"] == 0:
                    ta["glow"] = False

        # Update and remove notes
        for note in notes[:]:
            note.update()
            if note.missed:
                misses += 1
                combo = 0
                current_rating = ratings["miss"]
                rating_timer = RATING_DISPLAY_TIME
                health = max(0, health - 5)
            if note.y < 0 or note.hit:
                notes.remove(note)

        if rating_timer > 0:
            rating_timer -= 1

        # === Drawing Section ===
        screen.fill(BLACK)

        # Level title at the top
        screen.blit(level_title, (SCREEN_WIDTH // 2 - level_title.get_width() // 2, 10))

        # Draw target arrows
        for dir, data in target_arrows.items():
            image = glowing_arrows[dir] if data["glow"] else arrows[dir]
            rect = image.get_rect(center=(data["x"], TARGET_Y))
            screen.blit(image, rect)
            pygame.draw.line(screen, GRAY, (data["x"] - ARROW_SIZE, TARGET_Y), (data["x"] + ARROW_SIZE, TARGET_Y), 2)

        # Draw falling notes
        for note in notes:
            note.draw(screen, arrows[note.direction])

        # UI: Score, combo, misses
        screen.blit(font.render(f"Score: {score}/{win_threshold}", True, WHITE), (20, 20))
        screen.blit(font.render(f"Combo: {combo}", True, WHITE), (20, 60))
        screen.blit(font.render(f"Misses: {misses}", True, WHITE), (20, 100))

        # Health bar
        health_width = int((health / MAX_HEALTH) * 200)
        pygame.draw.rect(screen, GRAY, (SCREEN_WIDTH - 220, 20, 200, 20))
        pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH - 220, 20, health_width, 20))

        # Progress bar toward win
        score_width = int(min(1.0, score / win_threshold) * 200)
        pygame.draw.rect(screen, GRAY, (SCREEN_WIDTH - 220, 50, 200, 20))
        pygame.draw.rect(screen, BLUE, (SCREEN_WIDTH - 220, 50, score_width, 20))

        # Display rating
        if rating_timer > 0 and current_rating:
            rect = current_rating.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(current_rating, rect)

        # Game over screen
        if game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            screen.blit(big_font.render("GAME OVER", True, RED), (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50))
            screen.blit(font.render("Press R to restart, M for menu, ESC to quit", True, WHITE), (SCREEN_WIDTH // 2 - 210, SCREEN_HEIGHT // 2 + 10))
        # Win screen
        elif game_won:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            screen.blit(big_font.render("LEVEL COMPLETE!", True, GREEN), (SCREEN_WIDTH // 2 - 210, SCREEN_HEIGHT // 2 - 50))
            
            if level_id < max(LEVELS.keys()):
                next_level_text = font.render(f"Level {level_id + 1} Unlocked!", True, YELLOW)
                screen.blit(next_level_text, (SCREEN_WIDTH // 2 - next_level_text.get_width() // 2, SCREEN_HEIGHT // 2))
            
            screen.blit(font.render("Press R to replay, M for menu, ESC to quit", True, WHITE), (SCREEN_WIDTH // 2 - 210, SCREEN_HEIGHT // 2 + 50))
        # Instruction line
        else:
            instructions = font.render("Press arrow keys when notes align with targets", True, WHITE)
            screen.blit(instructions, instructions.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)))

        pygame.display.flip()
        clock.tick(60)

    return "menu"

# === Main Function ===
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Rhythm Game with Levels")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 30)
    big_font = pygame.font.SysFont("Arial", 60)
    
    # Load saved progress
    load_progress()
    
    # Game state
    game_state = "menu"
    
    # Main game loop
    while True:
        if game_state == "menu":
            level_id = show_menu(screen, clock, font, big_font)
            game_state = level_id
        else:
            game_state = play_level(screen, clock, font, big_font, game_state)

# Run the game
if __name__ == "__main__":
    main()