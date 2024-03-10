from random import randint

import pygame

# Инициализация PyGame:
pygame.init()

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
# SCREEN_WIDTH, SCREEN_HEIGHT = 1600, 1200
# GRID_SIZE = 40
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)
SNAKE_HEAD_COLOR = (0, 128, 0)

# Скорость движения змейки:
SPEED = 3

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Базовый класс игровых сущностей"""

    def __init__(self, body_color=None):
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color

    def draw(self, surface):
        """Отрисовать"""
        raise NotImplementedError


class Apple(GameObject):
    """Яблоко
    При поедании головой змейки, длина увеличивается на один сегмент
    """

    def __init__(self, body_color=APPLE_COLOR):
        super().__init__(body_color)

    def draw(self, surface):
        """Отрисовать"""
        rect = pygame.Rect(
            (self.position[0], self.position[1]),
            (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)

    def randomize_position(self):
        """Создать новое яблоко"""
        self.position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )


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
        self.direction = RIGHT
        self.next_direction = None
        self.last = None
        self.head_color = head_color

    def draw(self, surface):
        """Отрисовать"""
        if len(self.positions) > 1:
            for position in self.positions[1:]:
                rect = (
                    pygame.Rect(position[0], position[1], GRID_SIZE, GRID_SIZE)
                )
                pygame.draw.rect(surface, self.body_color, rect)
                pygame.draw.rect(surface, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.head_color, head_rect)
        pygame.draw.rect(surface, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(
                (self.last[0], self.last[1]),
                (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)

    def predict_move(self):
        """Вычислить кородинаты следующего хода"""
        head_x, head_y = self.positions[0]
        direction_x, direction_y = self.direction

        position = (
            (head_x + (direction_x * GRID_SIZE)) % SCREEN_WIDTH,
            (head_y + (direction_y * GRID_SIZE)) % SCREEN_HEIGHT
        )

        return position

    def move(self):
        """Нарастить ячейку с головы и удалить с хвоста"""
        self.positions.insert(0, self.predict_move())
        self.last = self.positions.pop()

    def update_direction(self):
        """Обновление направления после нажатия на кнопку"""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self):
        """Получить координаты головы"""
        return self.positions[0]

    def grow(self):
        """Нарастить ячейку с головы"""
        self.positions.insert(0, self.predict_move())

    def check_crossing(self):
        # print(self.get_head_position in self.positions)
        # print(self.get_head_position(),self.positions)
        """Проверить пересечения с препятствиями"""
        if self.get_head_position in self.positions[2:]:
            print('врезались')
            self.reset()


class Stone:
    """Камень
    При столкновении с камнем змейка принимает исходное состояние
    """

    pass


class BadFood:
    """Плохая еда
    Если змейка съест неправильный корм, её длина уменьшается на один сегмент
    """


def handle_keys(game_object):
    """Обработка действий пользователя"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            print(event.key)
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Основной обработчик игры"""
    screen.fill(BOARD_BACKGROUND_COLOR)

    apple = Apple()
    snake = Snake()
    stone = Stone()
    bad_food = BadFood()

    apple.randomize_position()
    while True:
        clock.tick(SPEED)

        handle_keys(snake)

        snake.update_direction()
        snake.move()

        if snake.get_head_position() in snake.positions[2:]:
            snake.reset()

        if snake.get_head_position() == apple.position:
            snake.grow()
            apple.randomize_position()

        apple.draw(screen)
        snake.draw(screen)

        pygame.display.update()


if __name__ == '__main__':
    main()
