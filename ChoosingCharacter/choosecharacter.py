import pygame
import sys

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 150, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Load and scale character images
boy_img = pygame.transform.scale(pygame.image.load('boycharacter.jpg'), (200, 200))
girl_img = pygame.transform.scale(pygame.image.load('girlcharacter.jpg'), (200, 200))
mystery_img = pygame.transform.scale(pygame.image.load('mysteryperson.jpg'), (200, 200))

class CharacterMenu:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Character Selection")
        self.clock = pygame.time.Clock()

        # sound effect for button clicks
        self.click_sound = pygame.mixer.Sound("clickingsound.wav")

        # Character data (no hardcoded position)
        self.characters = [
            {"name": "Boy Dancer", "description": "A determined dancer", "image": boy_img},
            {"name": "Girl Dancer", "description": "A determined dancer", "image": girl_img},
            {"name": "Mystery Character", "description": "???", "image": mystery_img}
        ]

        self.current_selection = 0
        self.selected_character = None

        # Fonts
        self.title_font = pygame.font.Font(None, 64)
        self.char_font = pygame.font.Font(None, 48)
        self.desc_font = pygame.font.Font(None, 32)
        self.instruction_font = pygame.font.Font(None, 24)

    def play_click_sound(self):
        self.click_sound.play()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                self.play_click_sound()
                if event.key == pygame.K_LEFT:
                    self.current_selection = (self.current_selection - 1) % len(self.characters)
                elif event.key == pygame.K_RIGHT:
                    self.current_selection = (self.current_selection + 1) % len(self.characters)
                elif event.key == pygame.K_RETURN:
                    self.selected_character = self.characters[self.current_selection]
                    print(f"Selected character: {self.selected_character['name']}")
                    return False
                elif event.key == pygame.K_ESCAPE:
                    return False
        return True

    def draw_arrow(self, x, y, direction, color=WHITE):
        if direction == "left":
            points = [(x + 20, y), (x, y + 15), (x + 20, y + 30)]
        else:
            points = [(x, y), (x + 20, y + 15), (x, y + 30)]
        pygame.draw.polygon(self.screen, color, points)

    def draw(self):
        self.screen.fill(BLACK)

        # Title
        title_text = self.title_font.render("CHOOSE A CHARACTER", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)

        # Character display box
        char_box_width = 300
        char_box_height = 300
        char_box_x = (SCREEN_WIDTH - char_box_width) // 2
        char_box_y = 180
        pygame.draw.rect(self.screen, GRAY, (char_box_x, char_box_y, char_box_width, char_box_height), 2)

        # Get current character
        current_char = self.characters[self.current_selection]
        image = current_char["image"]

        # Center image inside box
        image_rect = image.get_rect(center=(char_box_x + char_box_width // 2, char_box_y + 110))
        self.screen.blit(image, image_rect)

        # Character name centered below image
        name_text = self.char_font.render(current_char["name"], True, WHITE)
        name_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2, image_rect.bottom + 20))
        self.screen.blit(name_text, name_rect)

        # Character description centered below name
        desc_text = self.desc_font.render(current_char["description"], True, WHITE)
        desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH // 2, name_rect.bottom + 20))
        self.screen.blit(desc_text, desc_rect)

        # Arrows for navigation
        self.draw_arrow(char_box_x - 60, char_box_y + char_box_height // 2 - 15, "left")
        self.draw_arrow(char_box_x + char_box_width + 20, char_box_y + char_box_height // 2 - 15, "right")

        # Instructions
        instructions = [
            "Use LEFT/RIGHT arrows to navigate",
            "Press ENTER to select character",
            "Press ESC to exit"
        ]
        for i, instruction in enumerate(instructions):
            inst_text = self.instruction_font.render(instruction, True, WHITE)
            inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, 500 + i * 25))
            self.screen.blit(inst_text, inst_rect)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        return self.selected_character if self.selected_character else None


if __name__ == "__main__":
    menu = CharacterMenu()
    selected = menu.run()

    if selected:
        print(f"You selected: {selected['name']} - {selected['description']}")
    else:
        print("No character selected")

    sys.exit()
