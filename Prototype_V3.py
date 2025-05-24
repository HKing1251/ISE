import pygame
import random
import time
import sys
import os
import json
import pygame.mixer
import math
pygame.init()

clock = pygame.time.Clock()

from pathlib import Path

# Set the working directory to the script's location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def resizeObject(originObject, scaledFactor):
    return pygame.transform.scale_by(originObject, scaledFactor)

def load_font(path, size):
    return pygame.font.Font(path, size)

atlantaFont = load_font("assets/Atlanta-College.ttf", 30)
atlantaFontLarge = load_font("assets/Atlanta-College.ttf", 60)
# atlantaFontBold = load_font("assets/Atlanta-College.ttf", 60)

gladoliaFont = load_font("assets/Gladolia-Regular.otf", 30)
gladoliaFontLarge = load_font("assets/Gladolia-Regular.otf", 60)
# gladoliaFontBold = load_font("assets/Gladolia-Regular.ttf", 60)

moldieFont = load_font("assets/Moldie.otf", 30)
moldieFontLarge = load_font("assets/Moldie.otf", 60)



class RainDrop:
    def __init__(self, screen_width, screen_height):
        self.x = random.randint(0, screen_width)
        self.y = random.randint(-screen_height, 0)
        self.length = random.randint(10, 20)
        self.speed = random.uniform(4, 10)
        self.color = LIGHT_BLUE

    def fall(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = random.randint(-50, -10)
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self, screen):
        pygame.draw.line(screen, self.color, (self.x, self.y), (self.x, self.y + self.length), 5)

def render_neon_title_scaled(screen, font, screen_width, y_offset, scale):
    # Step 1: Render to temporary surface
    title_texts = [
        ("F", NEON_RED),
        ("unky ", WHITE),
        ("F", NEON_CYAN),
        ("low ", WHITE),
        ("F", NEON_VIOLET),
        ("riday", WHITE),
    ]

    # parts = []
    total_width = sum(font.render(text, True, color).get_width() for text, color in title_texts)
    height = font.get_height()
    title_surface = pygame.Surface((total_width, height), pygame.SRCALPHA)

    x_offset = 0
    for text, color in title_texts:
        surf = font.render(text, True, color)
        shadow = font.render(text, True, DARK_SHADOW)
        title_surface.blit(shadow, (x_offset + 2, 2))
        title_surface.blit(surf, (x_offset, 0))
        x_offset += surf.get_width()

    # Step 2: Scale it
    scaled_title = resizeObject(title_surface, scale)

    # Step 3: Center and draw on screen
    screen.blit(scaled_title, (
        (screen_width - scaled_title.get_width()) // 2,
        y_offset
    ))


def show_intro_screen(screen):
    # Music setup
    pygame.mixer.music.load('BackgroundTest/SoulChef.mp3')
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    screen_width, screen_height = screen.get_size()

    # Load and scale images
    bg_back = pygame.transform.scale(pygame.image.load('assets/MainMenuSky.png').convert(), (screen_width, screen_height))
    bg_front = pygame.transform.scale(pygame.image.load('assets/MainMenuScreen.png').convert_alpha(), (screen_width, screen_height))

    # Dark overlay
    # dark_overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    # dark_overlay.fill((0, 0, 0, 160))
    # darkened_front = bg_front.copy()
    # darkened_front.blit(dark_overlay, (0, 0))

    # Fonts
    font = atlantaFontLarge
    small_font = atlantaFont
    prompt = font.render("Press any key to continue...", True, GRAY)

    # Scroll background setup
    bg_x = 0
    scroll_speed = 01.5

    rain_drops = [RainDrop(screen.get_width(), screen.get_height()) for _ in range(150)]
    
    clock = pygame.time.Clock()
    running = True

    while running:
        bg_x = (bg_x + scroll_speed) % screen_width
        screen.blit(bg_back, (-bg_x, 0))
        screen.blit(bg_back, (screen_width - bg_x, 0))

        screen.blit(bg_front, (0, 50))

        

        for drop in rain_drops:
            drop.fall()
            drop.draw(screen)

        # Draw title and prompt
        render_neon_title_scaled(screen, font, screen_width, y_offset=80, scale=1.9)
        screen.blit(prompt, ((screen_width - prompt.get_width()) // 2, 225))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                running = False

        pygame.display.flip()
        clock.tick(60)

    



# === Constants ===
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

ARROW_SIZE = 80
ARROW_SPACING = 100
TARGET_Y = 100  # Y position where arrows should be hit
GLOW_DURATION = 15
RATING_DISPLAY_TIME = 30
MAX_HEALTH = 200
INITIAL_HEALTH = 100

# === Level Configuration ===
LEVELS = {
    1: {"name": "Level 1", "win_threshold": 200, "arrow_speed": 5, "note_interval_start": 1.0, "note_interval_min": 0.3, "unlocked": True},
    2: {"name": "Level 2", "win_threshold": 1500, "arrow_speed": 9, "note_interval_start": 0.8, "note_interval_min": 0.25, "unlocked": False},
    3: {"name": "Level 3", "win_threshold": 3000, "arrow_speed": 7, "note_interval_start": 0.6, "note_interval_min": 0.2, "unlocked": False}
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
LIGHT_BLUE = (173, 216, 230) 
PURPLE = (128, 0, 128)
DARK_SHADOW = (30, 30, 30)
NEON_RED = (255, 50, 50)
NEON_CYAN = (50, 255, 255)
NEON_VIOLET = (200, 50, 255)

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

def load_lose_image():
    try:
        img = pygame.image.load("assets/LOSE.png").convert_alpha()
        return resizeObject(img, 2)
    except pygame.error as e:
        print(f"Failed to load LOSE.png: {e}")
        return None

def load_win_image():
    try:
        img = pygame.image.load("assets/WIN.png").convert_alpha()
        return resizeObject(img, 2)
    except pygame.error as e:
        print(f"Failed to load WIN.png: {e}")
        return None



def heartbeat_scale(base_size, pulse_rate, time_ms):
    # Use sine wave to create pulsing effect (range: ~0.9 to ~1.1)
    scale_factor = 1 + 0.05 * math.sin(time_ms * pulse_rate)
    new_size = int(base_size[0] * scale_factor), int(base_size[1] * scale_factor)
    return new_size

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
        render_text_centered(screen, "Choose a level", font, WHITE, 120)
        
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

def load_beatmap(filename="beatmap.json"):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Beatmap not found.")
        return []


# === Game Loop ===
def play_level(screen, clock, font, big_font, level_id):
    level_config = LEVELS[level_id]
    arrow_speed = level_config["arrow_speed"]
    win_threshold = level_config["win_threshold"]
    note_interval_start = level_config["note_interval_start"]
    note_interval_min = level_config["note_interval_min"]
    
    beat_times = load_beatmap()
    beat_index = 0

    if level_id == 1:
        beat_times = load_beatmap("beatmap.json")
        pygame.mixer.music.load("music/Tetris.mp3")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play()

    elif level_id == 2:
        beat_times = load_beatmap("beatmap2.json")
        pygame.mixer.music.load("music/SoulChef.mp3")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play()

    elif level_id == 3:
        # beat_times = load_beatmap("beatmap3.json")
        # pygame.mixer.music.load("music/_Tengen Toppa Gurren Lagann 1 Opening.mp3")
        # pygame.mixer.music.set_volume(0.3)
        # pygame.mixer.music.play()
        beat_times = load_beatmap("beatmap.json")
        pygame.mixer.music.load("music/Tetris.mp3")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play()

    
    arrows, glowing_arrows = load_arrow_images()

    # Set x positions for each arrow target
    targets = {
        "left": SCREEN_WIDTH // 2 - ARROW_SPACING * 2.0,
        "down": SCREEN_WIDTH // 2 - ARROW_SPACING * 0.75,
        "up": SCREEN_WIDTH // 2 + ARROW_SPACING * 0.75,
        "right": SCREEN_WIDTH // 2 + ARROW_SPACING * 2.0
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


    bloodSplashWide = pygame.image.load("assets/BloodSplashWide.png").convert_alpha()
    bloodSplashClose = pygame.image.load("assets/BloodSplashClose.png").convert_alpha()
    blood_splash_timer = 0
    BLOOD_SPLASH_DURATION = 500  # in milliseconds

    # === Game Loop ===
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.KEYDOWN: 
                if e.key == pygame.K_ESCAPE:
                    pygame.mixer.music.stop()
                    return "menu"
                if (game_over or game_won) and e.key == pygame.K_r:
                    return play_level(screen, clock, font, big_font, level_id)  # Restart level
                if (game_over or game_won) and e.key == pygame.K_m:
                    pygame.mixer.music.stop()
                    return "menu"
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
                                    health = min(MAX_HEALTH, health + 5)
                                elif distance < 30:
                                    score += 50
                                    combo += 1
                                    current_rating = ratings["good"]
                                    health = min(MAX_HEALTH, health + 2)
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
                            blood_splash_timer = pygame.time.get_ticks()

        # Check win/loss conditions
        if score >= win_threshold:
            pygame.mixer.music.stop()
            if level_id < max(LEVELS.keys()):
                LEVELS[level_id + 1]["unlocked"] = True
                save_progress()
            game_won, paused = True, True

        if health <= 0:
            pygame.mixer.music.stop()
            game_over, paused = True, True

        # Spawn notes at intervals
        if not paused:
            if time.time() - last_note_time > note_interval:
                direction = random.choice(list(targets.keys()))
                notes.append(Note(direction, targets[direction], arrow_speed))
                last_note_time = time.time()
                note_interval = max(note_interval_min, note_interval * 0.99)  # Accelerate note speed
        
        # Spawn notes based on beat timestamps
        current_time_sec = pygame.mixer.music.get_pos() / 1000.0
        if not paused and beat_index < len(beat_times):
            if current_time_sec >= beat_times[beat_index]:
                direction = random.choice(list(targets.keys()))
                notes.append(Note(direction, targets[direction], arrow_speed))
                beat_index += 1

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
                blood_splash_timer = pygame.time.get_ticks()
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

        # Load only once (do this outside the main loop ideally)
        health_bar_img = pygame.image.load("assets/HealthBar.png").convert_alpha()
        health_bar_img_full_width = health_bar_img.get_width()
        original_height = health_bar_img.get_height()

        # Inside the game loop:
        bar_x = SCREEN_WIDTH - 300  # Shift left to fit
        bar_y = 30
        bar_width = 300  # Longer
        bar_height = int(original_height * 2.5)  # Taller (increase as needed)

        # Background
        pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))

        # Subsurface based on actual health width
        scaled_width = int((health / MAX_HEALTH) * health_bar_img_full_width)

        if scaled_width > 0:
            # Crop from the original image based on current health width
            cropped_surface = health_bar_img.subsurface((0, 0, scaled_width, original_height))
            
            # Scale the cropped part to match bar dimensions (scaled height)
            scaled_bar = pygame.transform.scale(cropped_surface, (int((health / MAX_HEALTH) * bar_width), bar_height))

            # Draw it (adjust position if needed)
            screen.blit(scaled_bar, (bar_x - 5, bar_y))

        # 🔴 Blood Splash — moved here to show during duration
        if pygame.time.get_ticks() - blood_splash_timer < BLOOD_SPLASH_DURATION:
            splash_scaled = pygame.transform.scale(bloodSplashClose, (bar_width + 20, bar_height + 20))
            screen.blit(splash_scaled, (bar_x - 20, bar_y - 5))  # on the left side

        # Progress bar toward win
        score_width = int(min(1.0, score / win_threshold) * 200)
        pygame.draw.rect(screen, GRAY, (SCREEN_WIDTH - 220, 50, 200, 20))
        pygame.draw.rect(screen, BLUE, (SCREEN_WIDTH - 220, 50, score_width, 20))

        # Display rating
        if rating_timer > 0 and current_rating:
            rect = current_rating.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(current_rating, rect)

        # === Game Over or Win Screens ===
        if game_over or game_won:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            tickSpeed = pygame.time.get_ticks() / 1000

            if game_over:
                if LOSE_IMAGE:
                    size = heartbeat_scale(LOSE_IMAGE.get_size(), pulse_rate=3.5, time_ms=tickSpeed)
                    scaled = pygame.transform.smoothscale(LOSE_IMAGE, size)
                    lose_rect = scaled.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
                    screen.blit(scaled, lose_rect)
                else:
                    print("LOSE_IMAGE is None!")
                    screen.blit(big_font.render("GAME OVER", True, RED), (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50))

                screen.blit(font.render("Press R to restart, M for menu, ESC to quit", True, WHITE), 
                            (SCREEN_WIDTH // 2 - 210, SCREEN_HEIGHT // 2 + 10))

            elif game_won:
                screen.blit(big_font.render("LEVEL COMPLETE!", True, GREEN), 
                            (SCREEN_WIDTH // 2 - 210, SCREEN_HEIGHT // 2 - 100))
                
                if WIN_IMAGE:
                    size = heartbeat_scale(WIN_IMAGE.get_size(), pulse_rate=3.5, time_ms=tickSpeed)
                    scaled = pygame.transform.smoothscale(WIN_IMAGE, size)
                    win_rect = scaled.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
                    screen.blit(scaled, win_rect)
                else:
                    print("WIN_IMAGE is None!")

                if level_id < max(LEVELS.keys()):
                    next_level_text = font.render(f"Level {level_id + 1} Unlocked!", True, YELLOW)
                    screen.blit(next_level_text, (SCREEN_WIDTH // 2 - next_level_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
                
                screen.blit(font.render("Press R to replay, M for menu, ESC to quit", True, WHITE), 
                            (SCREEN_WIDTH // 2 - 210, SCREEN_HEIGHT // 2 + 80))

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
    pygame.font.init()

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Rhythm Game with Levels")
    clock = pygame.time.Clock()

    font = moldieFont
    big_font = atlantaFontLarge
 
    global LOSE_IMAGE, WIN_IMAGE
    LOSE_IMAGE = load_lose_image()
    WIN_IMAGE = load_win_image()

    show_intro_screen(screen)
    
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


        # Health bar

        # # Load only once (do this outside the main loop ideally)
        # health_bar_img = pygame.image.load("assets/Health.png").convert_alpha()
        # health_bar_img_full_width = health_bar_img.get_width()
        # original_height = health_bar_img.get_height()

        # # Inside the game loop:
        # bar_x = SCREEN_WIDTH - 400  # Shift left to fit
        # bar_y = 30
        # bar_width = 500  # Longer
        # bar_height = int(original_height * 2.5)  # Taller (increase as needed)
        

        # # Background
        # pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))

        # # Subsurface based on actual health width
        # scaled_width = int((health / MAX_HEALTH) * health_bar_img_full_width)

        # if scaled_width > 0:
        #     # Crop from the original image based on current health width
        #     cropped_surface = health_bar_img.subsurface((0, 0, scaled_width, original_height))
            
        #     # Scale the cropped part to match bar dimensions (scaled height)
        #     scaled_bar = pygame.transform.scale(cropped_surface, (int((health / MAX_HEALTH) * bar_width), bar_height))

        #     # Draw it (adjust position if needed)
        #     screen.blit(scaled_bar, (bar_x - 5, bar_y))

        # # 🔴 Blood Splash — moved here to show during duration
        # if pygame.time.get_ticks() - blood_splash_timer < BLOOD_SPLASH_DURATION:
        #     splash_scaled = pygame.transform.scale(bloodSplashClose, (bar_width + 20, bar_height + 20))
        #     screen.blit(splash_scaled, (bar_x - 20, bar_y - 5))  # on the left side

        # def draw_enhanced_health_bar(screen, x, y, width, height, health, max_health, 
        #                    bg_img=None, fg_img=None, splash_img=None, 
        #                    splash_timer=0, game_time=0):
        #     # """
        #     # Enhanced health bar drawing function with all effects
        #     # """
        #     # Calculate shake effect for low health
        #     shake_x = shake_y = 0
        #     if health < MAX_HEALTH * 0.25:
        #         shake_x = random.randint(-SHAKE_INTENSITY, SHAKE_INTENSITY)
        #         shake_y = random.randint(-SHAKE_INTENSITY, SHAKE_INTENSITY)
            
        #     # Calculate pulse effect for critical health
        #     pulse_scale = 1.0
        #     # if health < MAX_HEALTH * 0.15:
        #     #     pulse_scale = 1.0 + 0.1 * math.sin(game_time * 0.01)
            
        #     # Apply effects to position and size
        #     draw_x = x + shake_x
        #     draw_y = y + shake_y
        #     scaled_width = int(SCREEN_WIDTH * pulse_scale)
        #     scaled_height = int(SCREEN_HEIGHT * pulse_scale)
            
        #     # Center the scaled bar
        #     centered_x = draw_x - (scaled_width - SCREEN_WIDTH) // 2
        #     centered_y = draw_y - (scaled_height - SCREEN_HEIGHT) // 2

        #     fg_img = pygame.image.load("assets/Health.png").convert_alpha()
        #     bg_img = pygame.image.load("assets/HealthBar.png").convert_alpha()
            
        #     # Draw background
        #     if bg_img:
        #         try:
        #             bg_scaled = pygame.transform.scale(bg_img, (scaled_width, scaled_height))
        #             screen.blit(bg_scaled, (centered_x, centered_y))
        #         except:
        #             pygame.draw.rect(screen, GRAY, (centered_x, centered_y, scaled_width, scaled_height))
        #     else:
        #         pygame.draw.rect(screen, GRAY, (centered_x, centered_y, scaled_width, scaled_height))
            
        #     # Draw health fill
        #     health_ratio = max(0, min(1, health / MAX_HEALTH))
        #     fill_width = int(scaled_width * health_ratio)
            
        #     if fill_width > 0:
        #         if fg_img:
        #             try:
        #                 fill_surface = pygame.Surface((fill_width, scaled_height), pygame.SRCALPHA)
        #                 scaled_fg = pygame.transform.scale(fg_img, (scaled_width, scaled_height))
        #                 fill_surface.blit(scaled_fg, (0, 0), (0, 0, fill_width, scaled_height))
        #                 screen.blit(fill_surface, (centered_x, centered_y))
        #             except:
        #                 # Fallback color
        #                 color = GREEN if health_ratio > 0.6 else YELLOW if health_ratio > 0.3 else RED
        #                 pygame.draw.rect(screen, color, (centered_x, centered_y, fill_width, scaled_height))
        #         else:
        #             # Simple colored fill
        #             color = GREEN if health_ratio > 0.6 else YELLOW if health_ratio > 0.3 else RED
        #             pygame.draw.rect(screen, color, (centered_x, centered_y, fill_width, scaled_height))
            
        #     # Draw border
        #     border_color = WHITE if health > MAX_HEALTH * 0.25 else RED
        #     pygame.draw.rect(screen, border_color, (centered_x - 2, centered_y - 2, 
        #                     scaled_width + 4, scaled_height + 4), 2)
            
        #     # Draw health text
        #     health_text = f"{int(health)}/{int(MAX_HEALTH)}"
        #     text_surface = atlantaFont.render(health_text, True, WHITE)
        #     text_rect = text_surface.get_rect(center=(centered_x + scaled_width // 2, 
        #                                             centered_y + scaled_height // 2))
            
        #     # Text shadow
        #     shadow_surface = atlantaFont.render(health_text, True, BLACK)
        #     shadow_rect = text_rect.copy()
        #     shadow_rect.x += 1
        #     shadow_rect.y += 1
        #     screen.blit(shadow_surface, shadow_rect)
        #     screen.blit(text_surface, text_rect)

        #     splash_timer = max(0, splash_timer - 1)
        #     splash_img = pygame.image.load("assets/BloodSplashClose.png").convert_alpha()
            
        #     # Blood splash effect
        #     if pygame.time.get_ticks() - splash_timer < BLOOD_SPLASH_DURATION and splash_img:
        #         try:
        #             splash_scaled = pygame.transform.scale(splash_img, (scaled_width + 40, scaled_height + 40))
        #             screen.blit(splash_scaled, (centered_x - 20, centered_y - 20))
        #         except:
        #             # Simple red flash fallback
        #             flash_surface = pygame.Surface((scaled_width + 20, scaled_height + 20), pygame.SRCALPHA)
        #             flash_surface.fill((255, 0, 0, 100))
        #             screen.blit(flash_surface, (centered_x - 10, centered_y - 10))
