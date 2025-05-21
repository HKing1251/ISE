import pygame
import time
import json
import sys

# Key to arrow mapping
key_map = {
    pygame.K_LEFT: "left",
    pygame.K_DOWN: "down",
    pygame.K_UP: "up",
    pygame.K_RIGHT: "right"
}

# Initialize pygame and the mixer
pygame.init()
pygame.mixer.init()

# Check for any display issues
try:
    screen = pygame.display.set_mode((400, 200))
    pygame.display.set_caption("Beatmap Recorder")
    print("Pygame window created successfully.")
except Exception as e:
    print(f"Error creating Pygame window: {e}")
    sys.exit(1)

# Load the song
song_path = "music\椎名もた(siinamota) - Young Girl A  少女A.mp3"  # Change this to your song path
try:
    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play()
    print("Song is playing...")
except Exception as e:
    print(f"Error loading the song: {e}")
    sys.exit(1)

# Start time
start_time = time.time()
beatmap = []

print("Press arrow keys to record the beatmap, ESC to finish.")

# Frame rate control
clock = pygame.time.Clock()

try:
    # Main loop to capture key presses
    running = True
    while running:
        for event in pygame.event.get():
            # Print all events for debugging
            print(f"Event detected: {event}")

            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print("Recording stopped.")
                    running = False
                elif event.key in key_map:
                    # Record the timestamp and direction
                    current_time = time.time() - start_time
                    beatmap.append({"time": round(current_time, 3), "direction": key_map[event.key]})
                    print(f"Recorded {key_map[event.key]} at {round(current_time, 3)} seconds")
        
        # Stop if the song ends
        if not pygame.mixer.music.get_busy():
            print("Song finished. Saving beatmap...")
            break

        # Maintain a stable frame rate
        pygame.display.flip()
        clock.tick(60)

finally:
    # Save the beatmap to a file
    if beatmap:
        try:
            with open("beatmap.json", "w") as f:
                json.dump(beatmap, f, indent=4)
            print("Beatmap saved as beatmap.json")
        except Exception as e:
            print(f"Error saving the beatmap: {e}")
    else:
        print("No inputs recorded. Beatmap not saved.")
    pygame.quit()
