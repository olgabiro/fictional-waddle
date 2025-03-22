import random

import pygame

# Initialize Pygame
pygame.init()
pygame.mixer.init()

pygame.mixer.music.load('resources/background.mp3')
pygame.mixer.music.play(-1)

# Constants
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 8, 8
TILE_SIZE = WIDTH // COLS
HALF_TILE_SIZE = TILE_SIZE // 2
CIRCLE_RADIUS = HALF_TILE_SIZE - 2
FPS = 60

# Colors
COLORS = [
    (255, 105, 97),  # Moderate Red
    (144, 238, 144),  # Moderate Green
    (135, 206, 250),  # Moderate Blue
    (255, 255, 153),  # Moderate Yellow
    (255, 179, 71),  # Moderate Orange
    (221, 160, 221)  # Moderate Purple
]

BACKGROUND_COLOR = (75, 70, 75)

# Load sound effects
swap_sound = pygame.mixer.Sound('resources/swap.mp3')
match_sound = pygame.mixer.Sound('resources/match.mp3')

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Kwazy Catcakes")

# Create the grid
grid = [[random.choice(COLORS) for _ in range(COLS)] for _ in range(ROWS)]

score = 0
level = 1


def draw_grid():
    for row in range(ROWS):
        for col in range(COLS):
            if grid[row][col] is not None:
                pygame.draw.circle(screen, grid[row][col],
                                   (col * TILE_SIZE + HALF_TILE_SIZE, row * TILE_SIZE + HALF_TILE_SIZE), CIRCLE_RADIUS)


def swap_tiles(pos1: tuple[int, int], pos2: tuple[int, int]) -> None:
    grid[pos1[1]][pos1[0]], grid[pos2[1]][pos2[0]] = grid[pos2[1]][pos2[0]], grid[pos1[1]][pos1[0]]


def find_matches() -> list[tuple[int, int]]:
    matches = []
    for row in range(ROWS):
        for col in range(COLS - 2):
            if grid[row][col] == grid[row][col + 1] == grid[row][col + 2]:
                matches.append((row, col))
                matches.append((row, col + 1))
                matches.append((row, col + 2))
    for col in range(COLS):
        for row in range(ROWS - 2):
            if grid[row][col] == grid[row + 1][col] == grid[row + 2][col]:
                matches.append((row, col))
                matches.append((row + 1, col))
                matches.append((row + 2, col))
    return matches


def remove_matches(matches: list[tuple[int, int]]) -> None:
    global score
    for match in matches:
        grid[match[0]][match[1]] = None
    score += len(matches) * 10


def refill_grid():
    for col in range(COLS):
        for row in range(ROWS - 1, -1, -1):
            if grid[row][col] is None:
                propagate_items_from_up(col, row)


def propagate_items_from_up(col, row):
    for k in range(row - 1, -1, -1):
        if grid[k][col] is not None:
            grid[row][col], grid[k][col] = grid[k][col], None
            break
    else:
        grid[row][col] = random.choice(COLORS)


def animate_swap(pos1, pos2):
    swap_sound.play()
    x1, y1 = pos1[0] * TILE_SIZE, pos1[1] * TILE_SIZE
    x2, y2 = pos2[0] * TILE_SIZE, pos2[1] * TILE_SIZE
    dx, dy = (x2 - x1) // FPS, (y2 - y1) // FPS
    for _ in range(FPS):
        screen.fill(BACKGROUND_COLOR)
        draw_grid()
        pygame.draw.circle(screen, grid[pos1[1]][pos1[0]], (x1 + HALF_TILE_SIZE, y1 + HALF_TILE_SIZE), CIRCLE_RADIUS)
        pygame.draw.circle(screen, grid[pos2[1]][pos2[0]], (x2 + HALF_TILE_SIZE, y2 + HALF_TILE_SIZE), CIRCLE_RADIUS)
        pygame.display.flip()
        x1 += dx
        y1 += dy
        x2 -= dx
        y2 -= dy
        pygame.time.delay(10)


def animate_removal(matches):
    for _ in range(FPS):
        screen.fill(BACKGROUND_COLOR)
        draw_grid()
        for match in matches:
            pygame.draw.rect(screen, BACKGROUND_COLOR,
                             (match[1] * TILE_SIZE, match[0] * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        pygame.display.flip()
        pygame.time.delay(10)


def check_level_up():
    global level
    if score >= level * 100:  # Example criteria: 100 points per level
        level += 1

def draw_ui():
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    level_text = font.render(f"Level: {level}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 50))


def main():
    clock = pygame.time.Clock()
    running = True
    selected_tile = None

    while running:
        for event in pygame.event.get():
            handle_matches(find_matches())
            if hasattr(event, "pos"):
                x, y = event.pos
                col, row = x // TILE_SIZE, y // TILE_SIZE
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONUP:
                if selected_tile:
                    make_a_move(col, row, selected_tile)
                    selected_tile = None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                selected_tile = (col, row)

        # Draw everything
        screen.fill(BACKGROUND_COLOR)
        draw_grid()
        draw_ui()
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


def make_a_move(col, row, selected_tile):
    animate_swap(selected_tile, (col, row))
    swap_tiles(selected_tile, (col, row))
    matches = find_matches()
    if matches:
        handle_matches(matches)
    else:
        animate_swap((col, row), selected_tile)  # Swap back if no match
        swap_tiles(selected_tile, (col, row))

def handle_matches(matches):
    if matches:
        match_sound.play()
        animate_removal(matches)
        remove_matches(matches)
        refill_grid()
        check_level_up()



if __name__ == "__main__":
    main()
