import pygame
import random
import time
import sys
import os
from pathlib import Path

# Force the working directory to the script's location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
ARROW_SIZE = 80
ARROW_SPEED = 5
ARROW_SPACING = 100
TARGET_Y = 100
NOTE_INTERVAL_START = 1.0
NOTE_INTERVAL_MIN = 0.3
GLOW_DURATION = 15
RATING_DISPLAY_TIME = 30
WIN_THRESHOLD = 1000
MAX_HEALTH = 100
INITIAL_HEALTH = 50

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
BLUE = (0, 191, 255)

# Key Bindings
KEY_BINDINGS = {
    pygame.K_LEFT: "left",
    pygame.K_DOWN: "down",
    pygame.K_UP: "up",
    pygame.K_RIGHT: "right"
}

ARROW_IMAGE_MAPPING = {
    "left": ["assets/arrowSkinLeftDefault.png", "assets/arrowSkinLeftGlow.png"],
    "down": ["assets/arrowSkinDownDefault.png", "assets/arrowSkinDownGlow.png"],
    "up": ["assets/arrowSkinUpDefault.png", "assets/arrowSkinUpGlow.png"],
    "right": ["assets/arrowSkinRightDefault.png", "assets/arrowSkinRightGlow.png"]
}

def load_image(file_path, fallback_path=None):
    try:
        return pygame.image.load(file_path).convert_alpha()
    except pygame.error:
        if fallback_path:
            return pygame.image.load(fallback_path).convert_alpha()
        raise

def load_arrow_images():
    arrows, glowing = {}, {}
    for direction, (default_file, glow_file) in ARROW_IMAGE_MAPPING.items():
        try:
            print(f"Loading: {default_file} and {glow_file}")  # Debug line
            normal_img = load_image(default_file)
            glow_img = load_image(glow_file)
        except Exception as e:
            raise SystemExit(f"Error loading arrow images for {direction}: {e}")
        arrows[direction] = pygame.transform.scale(normal_img, (ARROW_SIZE, ARROW_SIZE))
        glowing[direction] = pygame.transform.scale(glow_img, (ARROW_SIZE, ARROW_SIZE))
    return arrows, glowing


class Note:
    def __init__(self, direction, x):
        self.direction = direction
        self.x = x
        self.y = SCREEN_HEIGHT
        self.hit = self.missed = False

    def update(self):
        self.y -= ARROW_SPEED
        if self.y < TARGET_Y - 50 and not self.hit:
            self.missed = True

    def draw(self, screen, image):
        if not self.hit and not self.missed:
            rect = image.get_rect(center=(self.x, self.y))
            screen.blit(image, rect)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Enhanced Rhythm Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 30)
    big_font = pygame.font.SysFont("Arial", 60)

    arrows, glowing_arrows = load_arrow_images()

    targets = {
        "left": SCREEN_WIDTH // 2 - ARROW_SPACING * 1.5,
        "down": SCREEN_WIDTH // 2 - ARROW_SPACING * 0.5,
        "up": SCREEN_WIDTH // 2 + ARROW_SPACING * 0.5,
        "right": SCREEN_WIDTH // 2 + ARROW_SPACING * 1.5
    }

    target_arrows = {
        dir: {"x": x, "glow": False, "timer": 0} for dir, x in targets.items()
    }

    notes, score, combo, misses, health = [], 0, 0, 0, INITIAL_HEALTH
    game_over = game_won = paused = False
    current_rating = None
    rating_timer = 0
    last_note_time = time.time()
    note_interval = NOTE_INTERVAL_START

    ratings = {
        "perfect": font.render("PERFECT!", True, GREEN),
        "good": font.render("GOOD", True, YELLOW),
        "bad": font.render("BAD", True, ORANGE),
        "miss": font.render("MISS", True, RED)
    }

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                if (game_over or game_won) and e.key == pygame.K_r:
                    return main()
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

        if score >= WIN_THRESHOLD:
            game_won, paused = True, True
        if health <= 0:
            game_over, paused = True, True

        if not paused:
            if time.time() - last_note_time > note_interval:
                direction = random.choice(list(targets.keys()))
                notes.append(Note(direction, targets[direction]))
                last_note_time = time.time()
                note_interval = max(NOTE_INTERVAL_MIN, note_interval * 0.99)

        for ta in target_arrows.values():
            if ta["timer"] > 0:
                ta["timer"] -= 1
                if ta["timer"] == 0:
                    ta["glow"] = False

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

        screen.fill(BLACK)

        for dir, data in target_arrows.items():
            image = glowing_arrows[dir] if data["glow"] else arrows[dir]
            rect = image.get_rect(center=(data["x"], TARGET_Y))
            screen.blit(image, rect)
            pygame.draw.line(screen, GRAY, (data["x"] - ARROW_SIZE, TARGET_Y), (data["x"] + ARROW_SIZE, TARGET_Y), 2)

        for note in notes:
            note.draw(screen, arrows[note.direction])

        screen.blit(font.render(f"Score: {score}/{WIN_THRESHOLD}", True, WHITE), (20, 20))
        screen.blit(font.render(f"Combo: {combo}", True, WHITE), (20, 60))
        screen.blit(font.render(f"Misses: {misses}", True, WHITE), (20, 100))

        health_width = int((health / MAX_HEALTH) * 200)
        pygame.draw.rect(screen, GRAY, (SCREEN_WIDTH - 220, 20, 200, 20))
        pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH - 220, 20, health_width, 20))

        score_width = int(min(1.0, score / WIN_THRESHOLD) * 200)
        pygame.draw.rect(screen, GRAY, (SCREEN_WIDTH - 220, 50, 200, 20))
        pygame.draw.rect(screen, BLUE, (SCREEN_WIDTH - 220, 50, score_width, 20))

        if rating_timer > 0 and current_rating:
            rect = current_rating.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(current_rating, rect)

        if game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            screen.blit(big_font.render("GAME OVER", True, RED), (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50))
            screen.blit(font.render("Press R to restart or ESC to quit", True, WHITE), (SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT // 2 + 10))
        elif game_won:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            screen.blit(big_font.render("YOU WIN!", True, GREEN), (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50))
            screen.blit(font.render("Press R to play again or ESC to quit", True, WHITE), (SCREEN_WIDTH // 2 - 190, SCREEN_HEIGHT // 2 + 10))
        else:
            instructions = font.render("Press arrow keys when notes align with targets", True, WHITE)
            screen.blit(instructions, instructions.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
