from random import choice

import pygame as pg

# Инициализация PyGame:
pg.init()

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
MARGIN = 2
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
SNAKE_HEAD_COLOR = (0, 128, 0)
STONE_COLOR = (128, 128, 128)
BAD_FOOD_COLOR = (255, 0, 255)
SPEED = 3
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')
clock = pg.time.Clock()


class GameObject:
    """Базовый класс игровых сущностей"""

    def __init__(self, body_color=None):
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color

    def draw(self, surface):
        """Отрисовать"""
        raise NotImplementedError

    @staticmethod
    def draw_rect(coordinates, color, surface, border=True):
        """Отрисовать одну ячейку"""
        rect = pg.Rect(coordinates, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(surface, color, rect)

        if border:
            pg.draw.rect(surface, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Яблоко
    При поедании головой змейки, длина увеличивается на один сегмент
    """

    def __init__(self, body_color=APPLE_COLOR):
        super().__init__(body_color)

    def draw(self, surface):
        """Отрисовать"""
        GameObject.draw_rect(
            (self.position[0], self.position[1]), self.body_color, surface
        )

    def randomize_position(self, snake_positions):
        """Создать новое яблоко"""
        available_rects = []
        for row in range(SCREEN_WIDTH // GRID_SIZE):
            for col in range(SCREEN_HEIGHT // GRID_SIZE):
                rect = (row * GRID_SIZE, col * GRID_SIZE)
                if rect not in snake_positions:
                    available_rects.append((row * GRID_SIZE, col * GRID_SIZE))

        self.position = choice(available_rects)


class Snake(GameObject):
    """Змейка
    Состоит из головы, поедающей яблоки и остального туловища
    """

    def __init__(self, body_color=SNAKE_COLOR):
        super().__init__(body_color)
        self.reset()

    def reset(self, head_color=SNAKE_HEAD_COLOR):
        """Сбросить парамертры змейки и вернуть в исходное положение"""
        screen.fill(BOARD_BACKGROUND_COLOR)
        self.length = 1
        self.positions = [self.position]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.last = None
        self.head_color = head_color

    def draw(self, surface):
        """Отрисовать"""
        # Головоу змейки красим в темно-зеленый цвет
        GameObject.draw_rect((self.positions[0]), self.head_color, surface)

        # Остальное тело окрашиваем в светло-зеленый
        for position in self.positions[1:]:
            GameObject.draw_rect(
                (position[0], position[1]), self.body_color, surface
            )

        # Затирание последнего сегмента
        if self.last:
            GameObject.draw_rect(
                (self.last[0], self.last[1]),
                BOARD_BACKGROUND_COLOR,
                surface,
                False
            )

    def predict_move(self):
        """Вычислить кородинаты следующего хода"""
        head_x, head_y = self.positions[0]
        direction_x, direction_y = self.direction
        position = (
            (head_x + (direction_x * GRID_SIZE)) % SCREEN_WIDTH,
            (head_y + (direction_y * GRID_SIZE)) % SCREEN_HEIGHT
        )

        return position

    def move(self, apple_position, bad_food_position):
        """Нарастить ячейку с головы и удалить с хвоста"""
        self.positions.insert(0, self.predict_move())

        if self.get_head_position() != apple_position:
            self.last = self.positions.pop()

    def update_direction(self):
        """Обновление направления после нажатия на кнопку"""
        pass

    def get_head_position(self):
        """Получить координаты головы"""
        return self.positions[0]

    def check_crossing(self):
        """Проверить пересечения с препятствиями"""
        if self.get_head_position in self.positions[2:]:
            self.reset()


class Stone(GameObject):
    """Камень
    При столкновении с камнем змейка принимает исходное состояние
    """

    def __init__(self, body_color=STONE_COLOR):
        super().__init__(body_color)

    def draw(self, surface):
        """Отрисовать"""
        GameObject.draw_rect(
            (self.position[0], self.position[1]), self.body_color, surface
        )

    def randomize_position(self, snake_positions, apple_position):
        """Создать случайную позицию для камня"""
        available_rects = []
        for row in range(SCREEN_WIDTH // GRID_SIZE):
            for col in range(SCREEN_HEIGHT // GRID_SIZE):
                rect = (row * GRID_SIZE, col * GRID_SIZE)
                if rect not in snake_positions and rect != apple_position:
                    available_rects.append((row * GRID_SIZE, col * GRID_SIZE))

        self.position = choice(available_rects)


class BadFood(GameObject):
    """Плохая еда
    Если змейка съест неправильный корм, её длина уменьшается на один сегмент
    """

    def __init__(self, body_color=BAD_FOOD_COLOR):
        super().__init__(body_color)

    def draw(self, surface):
        """Отрисовать"""
        GameObject.draw_rect(
            (self.position[0], self.position[1]), self.body_color, surface
        )

    def randomize_position(self, snake_positions, apple_position, stone_position):
        """Создать случайную позицию для плохой еды"""
        available_rects = []
        for row in range(SCREEN_WIDTH // GRID_SIZE):
            for col in range(SCREEN_HEIGHT // GRID_SIZE):
                rect = (row * GRID_SIZE, col * GRID_SIZE)
                if rect not in snake_positions and rect != apple_position and rect != stone_position:
                    available_rects.append((row * GRID_SIZE, col * GRID_SIZE))

        self.position = choice(available_rects)


def handle_keys(game_object):
    """Обработка действий пользователя"""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            print(event.key)
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.direction = RIGHT


def main():
    """Основной обработчик игры"""
    screen.fill(BOARD_BACKGROUND_COLOR)

    apple = Apple()
    snake = Snake()
    stone = Stone()
    bad_food = BadFood()

    apple.randomize_position(snake.positions)
    stone.randomize_position(snake.positions, apple.position)
    bad_food.randomize_position(snake.positions, apple.position, stone.position)

    stone.draw(screen)

    while True:
        clock.tick(SPEED)

        handle_keys(snake)

        snake.move(apple.position, bad_food.position)

        if snake.get_head_position() in snake.positions[4:] \
                or snake.get_head_position() == stone.position:
            snake.reset()
            stone.draw(screen)

        if snake.get_head_position() == apple.position:
            apple.randomize_position(snake.positions)

        if snake.get_head_position() == bad_food.position:
            bad_food.randomize_position(snake.positions, apple.position, stone.position)

            if len(snake.positions) > 1:
                snake.positions.pop(0)

        apple.draw(screen)
        snake.draw(screen)
        bad_food.draw(screen)

        pg.display.update()


if __name__ == '__main__':
    main()
