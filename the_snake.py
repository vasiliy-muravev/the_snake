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
        self.occupied = []

    def draw(self):
        """Отрисовать"""
        raise NotImplementedError(
            'Определите метод draw в %s.' % (self.__class__.__name__))

    @staticmethod
    def draw_rect(coordinates, color):
        """Отрисовать одну ячейку"""
        rect = pg.Rect(coordinates, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)

        if color != BOARD_BACKGROUND_COLOR:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def refresh_occupied(self, snake_position, *positions):
        """Незанятые ячейки"""
        self.occupied = [pos for pos in snake_position]
        for arg in positions:
            self.occupied.append(arg)


class Apple(GameObject):
    """Яблоко
    При поедании головой змейки, длина увеличивается на один сегмент
    """

    def __init__(self, body_color=APPLE_COLOR):
        super().__init__(body_color)

    def draw(self):
        """Отрисовать"""
        self.draw_rect(
            (self.position[0], self.position[1]), self.body_color
        )

    def randomize_position(self):
        """Создать новое яблоко"""
        # Текущий вариант
        available_rects = []
        for row in range(SCREEN_WIDTH // GRID_SIZE):
            for col in range(SCREEN_HEIGHT // GRID_SIZE):
                rect = (row * GRID_SIZE, col * GRID_SIZE)
                if rect not in self.occupied:
                    available_rects.append((row * GRID_SIZE, col * GRID_SIZE))

        self.position = choice(available_rects)

        # Рекурсивный вариант, который вы предлагаете
        # while True:
        #     self.position = (
        #         randint(0, GRID_WIDTH - 1) * GRID_SIZE,
        #         randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        #     )
        #     if self.position not in self.occupied:
        #         break


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

    def draw(self):
        """Отрисовать"""
        # Головоу змейки красим в темно-зеленый цвет
        self.draw_rect((self.positions[0]), self.head_color)

        # Остальное тело окрашиваем в светло-зеленый
        for position in self.positions[1:]:
            self.draw_rect(
                (position[0], position[1]), self.body_color
            )

        # Затирание последнего сегмента
        if self.last:
            self.draw_rect(
                (self.last[0], self.last[1]), BOARD_BACKGROUND_COLOR
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

    def update_direction(self, event_key):
        """Обновление направления после нажатия на кнопку"""
        if event_key == pg.K_UP and self.direction != DOWN:
            self.direction = UP
        elif event_key == pg.K_DOWN and self.direction != UP:
            self.direction = DOWN
        elif event_key == pg.K_LEFT and self.direction != RIGHT:
            self.direction = LEFT
        elif event_key == pg.K_RIGHT and self.direction != LEFT:
            self.direction = RIGHT

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

    def draw(self):
        """Отрисовать"""
        self.draw_rect(
            (self.position[0], self.position[1]), self.body_color
        )

    def randomize_position(self):
        """Создать случайную позицию для камня"""
        available_rects = []
        for row in range(SCREEN_WIDTH // GRID_SIZE):
            for col in range(SCREEN_HEIGHT // GRID_SIZE):
                rect = (row * GRID_SIZE, col * GRID_SIZE)
                if rect not in self.occupied:
                    available_rects.append((row * GRID_SIZE, col * GRID_SIZE))

        self.position = choice(available_rects)


class BadFood(GameObject):
    """Плохая еда
    Если змейка съест неправильный корм, её длина уменьшается на один сегмент
    """

    def __init__(self, body_color=BAD_FOOD_COLOR):
        super().__init__(body_color)

    def draw(self):
        """Отрисовать"""
        self.draw_rect(
            (self.position[0], self.position[1]), self.body_color
        )

    def randomize_position(self):
        """Создать случайную позицию для плохой еды"""
        available_rects = []
        for row in range(SCREEN_WIDTH // GRID_SIZE):
            for col in range(SCREEN_HEIGHT // GRID_SIZE):
                rect = (row * GRID_SIZE, col * GRID_SIZE)
                if rect not in self.occupied:
                    available_rects.append((row * GRID_SIZE, col * GRID_SIZE))

        self.position = choice(available_rects)


def handle_keys(game_object):
    """Обработка действий пользователя"""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            game_object.update_direction(event.key)


def main():
    """Основной обработчик игры"""
    screen.fill(BOARD_BACKGROUND_COLOR)

    apple = Apple()
    snake = Snake()
    stone = Stone()
    bad_food = BadFood()

    GameObject.refresh_occupied(
        GameObject(),
        snake.positions,
        apple.position,
        stone.position,
        bad_food.position
    )

    apple.randomize_position()

    GameObject.refresh_occupied(
        GameObject(),
        snake.positions,
        apple.position,
        stone.position,
        bad_food.position
    )

    stone.randomize_position()

    GameObject.refresh_occupied(
        GameObject(),
        snake.positions,
        apple.position,
        stone.position,
        bad_food.position
    )

    bad_food.randomize_position()

    stone.draw()

    while True:
        clock.tick(SPEED)

        handle_keys(snake)

        snake.move(apple.position, bad_food.position)

        GameObject.refresh_occupied(
            GameObject(),
            snake.positions,
            apple.position,
            stone.position,
            bad_food.position
        )

        if (snake.get_head_position() in snake.positions[4:]
                or snake.get_head_position() == stone.position):
            snake.reset()
            stone.draw()

        if snake.get_head_position() == apple.position:
            apple.randomize_position()

        if snake.get_head_position() == bad_food.position:
            bad_food.randomize_position()

            if len(snake.positions) > 1:
                snake.positions.pop(0)

        apple.draw()
        snake.draw()
        bad_food.draw()

        pg.display.update()


if __name__ == '__main__':
    main()
