import pygame
import random
import sys


# Размеры окна в пикселях
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

CELL_SIZE = 20

# Размеры сетки в ячейках
WIDTH = int(WINDOW_WIDTH / CELL_SIZE)
HEIGHT = int(WINDOW_HEIGHT / CELL_SIZE)

# Цвета
BG_COLOR = (0, 0, 0)
GRID_COLOR = (40, 40, 40)
APPLE_COLOR = (255, 0, 0)
APPLE_OUTER_COLOR = (155, 0, 0)
SNAKE_COLOR = (0, 255, 0)
SNAKE_OUTER_COLOR = (0, 155, 0)


UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0


FPS = 15


class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def main():
    global FPS_CLOCK
    global DISPLAY

    pygame.init()
    FPS_CLOCK = pygame.time.Clock()
    DISPLAY = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Wormy')

    while True:
        # Мы всегда будем начинать игру с начала. После проигрыша сразу
        # начинается следующая.
        run_game()


def run_game():
    apple = Cell(20, 10)
    snake = [Cell(5, 10), Cell(4, 10), Cell(3, 10)]
    direction = RIGHT
    game_over = False  # Add a game over flag

    while not game_over:  # Loop until game over
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != DOWN:
                    direction = UP
                elif event.key == pygame.K_DOWN and direction != UP:
                    direction = DOWN
                elif event.key == pygame.K_LEFT and direction != RIGHT:
                    direction = LEFT
                elif event.key == pygame.K_RIGHT and direction != LEFT:
                    direction = RIGHT

        move_snake(snake, direction)

        if snake_hit_edge(snake):
            game_over = True
        elif snake_hit_self(snake):
            game_over = True
        elif snake_hit_apple(snake, apple):
            move_snake(snake, direction, grow=True)
            apple = new_apple(snake)

        draw_frame(snake, apple)
        FPS_CLOCK.tick(FPS)

    # Game over sequence (optional: you can add a game over screen here)
    print("Game Over!") # For now, just print to the console
    # The main() loop will restart the game automatically
        
def draw_frame(snake, apple):
    DISPLAY.fill(BG_COLOR)
    draw_grid()
    draw_snake(snake)
    draw_apple(apple)
    pygame.display.update()


def draw_grid():
    for x in range(0, WINDOW_WIDTH, CELL_SIZE):  # Draw vertical lines
        pygame.draw.line(DISPLAY, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT))
    for y in range(0, WINDOW_HEIGHT, CELL_SIZE):  # Draw horizontal lines
        pygame.draw.line(DISPLAY, GRID_COLOR, (0, y), (WINDOW_WIDTH, y))


def draw_apple(apple):
    if apple:
        draw_cell(apple, APPLE_OUTER_COLOR, APPLE_COLOR)


def draw_snake(snake):
    if snake:
        for segment in snake:
            draw_cell(segment, SNAKE_OUTER_COLOR, SNAKE_COLOR)


def draw_cell(cell, outer_color, inner_color):
    outer_rect = pygame.Rect(cell.x * CELL_SIZE, cell.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(DISPLAY, outer_color, outer_rect)

    inner_size = CELL_SIZE - 4  # 4 pixels margin on each side (total 8)
    inner_rect = pygame.Rect(cell.x * CELL_SIZE + 2, cell.y * CELL_SIZE + 2, inner_size, inner_size)
    pygame.draw.rect(DISPLAY, inner_color, inner_rect)


def move_snake(snake, direction, grow=False):
    if direction == UP:
        new_head = Cell(snake[HEAD].x, snake[HEAD].y - 1)
    elif direction == DOWN:
        new_head = Cell(snake[HEAD].x, snake[HEAD].y + 1)
    elif direction == LEFT:
        new_head = Cell(snake[HEAD].x - 1, snake[HEAD].y)
    elif direction == RIGHT:
        new_head = Cell(snake[HEAD].x + 1, snake[HEAD].y)

    snake.insert(0, new_head)
    if not grow:  # Only remove the tail if not growing
        snake.pop()


def get_snake_new_head():
    # TODO(4.4): реализовать функцию определения нового
    #  положения головы змейки.
    #  * Какие параметры будет принимать функция?
    #  * Что функция будет возвращать?
    ...


def snake_hit_edge(snake):
    head = snake[HEAD]
    return not (0 <= head.x < WIDTH and 0 <= head.y < HEIGHT)


def snake_hit_apple(snake, apple):
    return snake[HEAD].x == apple.x and snake[HEAD].y == apple.y


def snake_grow():
    # TODO(6.3): предложите максимально простой
    #  способ увеличения длины змейки.
    ...

def new_apple(snake):
    while True:
        x = random.randint(0, WIDTH - 1)
        y = random.randint(0, HEIGHT - 1)
        new_apple_pos = Cell(x, y)
        if new_apple_pos not in snake:  # Make sure the apple doesn't spawn on the snake
            return new_apple_pos

# Muser in 2023: Yes, this is very needed!
# Muser in 2025: For what this is?
def get_direction():
    # TODO(7.3): функция возвращает направление движения
    #  в зависимости от нажатой клавиши:
    #  * pygame.K_LEFT
    #  * pygame.K_RIGHT
    #  * pygame.K_UP
    #  * pygame.K_DOWN
    #  Если нажата клавиша противоположного направления движения,
    #  то не менять направление.
    ...

def snake_hit_self(snake):
    # The head is the first element [0]. We need to check if the head's position
    # is the same as any of the other segments in the snake's body [1:].
    return snake[HEAD] in snake[1:]


def terminate():
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()