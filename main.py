"""

Игра жизни Конвея — https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life

"""

from win32api import GetSystemMetrics
from copy import deepcopy
import pygame
pygame.init()


def print_text(message, sc, x, y, font_color=pygame.Color("darkorchid4"),
               font_type=pygame.font.match_font(pygame.font.get_fonts()[0]),
               font_size=25):
    """
    Метод отображения текста на экране

    """

    font_type = pygame.font.Font(font_type, font_size)
    text = font_type.render(message, True, font_color)
    sc.blit(text, (x, y))


class Numbers:
    def __init__(self, x, y, font_size=60, font_type=pygame.font.match_font(pygame.font.get_fonts()[0])):
        self.x = x
        self.y = y
        self.font_size = font_size
        self.font_type = font_type
        self.active = False

    def draw_num(self, num_name, sc, x, y):
        self.x = x
        self.y = y
        font_type = pygame.font.Font(self.font_type, self.font_size)
        if self.active:
            font_color = pygame.Color("darkgreen")
        else:
            font_color = pygame.Color("darkorchid4")
        text = font_type.render(num_name, True, font_color)
        sc.blit(text, (self.x, self.y))


class Cell:
    def __init__(self, x, y, tile=50):
        self.x = x
        self.y = y
        self.tile = tile
        self.live = 0

    def draw(self, sc):
        x, y = self.x * self.tile, self.y * self.tile
        line_w = 2
        cell_color = pygame.Color('darkorchid4')
        pygame.draw.line(sc, cell_color, (x, y), (x + self.tile, y), line_w)
        pygame.draw.line(sc, cell_color, (x + self.tile, y), (x + self.tile, y + self.tile), line_w)
        pygame.draw.line(sc, cell_color, (x + self.tile, y + self.tile), (x, y + self.tile), line_w)
        pygame.draw.line(sc, cell_color, (x, y + self.tile), (x, y), line_w)
        if self.live:
            pygame.draw.rect(sc, pygame.Color('darkgreen'),
                             (x + line_w, y + line_w, self.tile - line_w, self.tile - line_w))

    def set_live(self, live):
        self.live = live


class Field:
    def __init__(self, tile, live_cell):

        self.tile = tile
        self.x = GetSystemMetrics(0) // tile
        self.y = GetSystemMetrics(1) // tile
        self.cells = [[Cell(i, j, tile) for j in range(self.y)] for i in range(self.x)]
        self.field = [[0 for _ in range(self.y)] for _ in range(self.x)]
        self.next_field = [[0 for _ in range(self.y)] for _ in range(self.x)]
        self.live_cell = live_cell
        self.num_law = [[Numbers(i, j) for j in range(10)] for i in range(2)]

    def checking_neighbors(self):
        for i in range(self.x):
            for j in range(self.y):
                # проверяем всех соседей для это клетки
                check_res = []
                for xi in -1, 0, 1:
                    for yj in -1, 0, 1:
                        if xi == 0 and yj == 0:
                            continue
                        rx, ry = i + xi, j + yj
                        if rx == self.x:
                            rx = 0
                        if ry == self.y:
                            ry = 0
                        cell_neighbor = self.field[rx][ry]
                        check_res.append(cell_neighbor)

                # выживание
                if self.field[i][j]:
                    if sum(check_res) in self.live_cell[0]:
                        self.next_field[i][j] = 1
                    else:
                        self.next_field[i][j] = 0

                # рождение
                else:
                    if sum(check_res) in self.live_cell[1]:
                        self.next_field[i][j] = 1
                    else:
                        self.next_field[i][j] = 0

        self.field = deepcopy(self.next_field)

    def click(self, x, y):
        if self.field[x][y]:
            self.field[x][y] = 0
        else:
            self.field[x][y] = 1

    def draw_field(self, sc):
        for i in range(self.x):
            for j in range(self.y):
                # клетка
                self.cells[i][j].set_live(self.field[i][j])
                self.cells[i][j].draw(sc)

    def draw_rules_space(self, sc):
        # размеры выводимой области
        size = sc.get_size()

        # первая строка текста
        print_text("Закон формирования новой жизни!", sc, size[0] // 3, size[1] // 20)

        # прорисовка первого ряда
        for i, num in enumerate(self.num_law[0]):
            if i in self.live_cell[1]:
                num.active = True
            else:
                num.active = False
            num.draw_num(num_name=str(i), sc=sc, x=size[0] // 4 + i * self.tile, y=size[1] // 6.0)

        # вторая строка текста
        print_text("Закон выживания существующей жизни!", sc, size[0] // 3.25, size[1] // 2.2)

        # прорисовка второго ряда
        for i, num in enumerate(self.num_law[1]):
            if i in self.live_cell[0]:
                num.active = True
            else:
                num.active = False
            num.draw_num(num_name=str(i), sc=sc, x=size[0] // 4 + i * self.tile, y=size[1] // 1.7)

        # заключительный текст
        print_text("В прочих случаях жизни не существует!", sc, size[0] // 3.25, size[1] // 1.2)


class GUI:

    def __init__(self, field,  fps=10):
        # название окна
        pygame.display.set_caption('OLA')

        # ширина и высота окна берутся из системных настроек монитора (для режима FULLSCREEN)
        self.width_screen, self.height_screen = GetSystemMetrics(0), GetSystemMetrics(1)

        # количество кадров в секунду
        self.fps = fps

        # создание пользовательского окна
        self.sc = pygame.display.set_mode((self.width_screen, self.height_screen), pygame.FULLSCREEN)

        # флаг паузы
        self.pause = True

        # field
        self.field = field

        # tile cell
        self.tile = field.tile

        # rules board
        self.rules_board = False
        self.rules_space_w = self.width_screen // 10 * 6
        self.rules_space_h = self.height_screen // 10 * 3
        self.rules_space = pygame.Surface((self.rules_space_w, self.rules_space_h))

        # обработка событий (этот метод в конструкторе идет последним, после него конструктор читает)
        self.event_loop()

    def event_loop(self):

        # Ввод процесса (события)
        while True:

            # обновление фона
            self.sc.fill(pygame.Color('#000020'))

            # цикл обработки событий
            for event in pygame.event.get():

                # проверить закрытие окна
                if event.type == pygame.QUIT:
                    exit()

                # обработка нажатий клавиш
                if event.type == pygame.KEYDOWN:

                    # закрыть программу
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        exit()

                    # очистить поле
                    elif event.key == pygame.K_r:
                        self.field.field = [[0 for _ in range(self.field.y)] for _ in range(self.field.x)]

                    # ввод правил
                    elif event.key == pygame.K_TAB:
                        if not self.pause:
                            self.pause = True
                        if self.rules_board:
                            self.rules_board = False
                        else:
                            self.rules_board = True

                    # пауза
                    elif event.key == pygame.K_SPACE:
                        if not self.rules_board:
                            if self.pause:
                                self.pause = False
                            else:
                                self.pause = True

                # обработка отжатий клавиш
                elif event.type == pygame.KEYUP:
                    pass

                # анализ нажатия кнопок мыши
                if event.type == pygame.MOUSEBUTTONDOWN and event.button in [1]:  # ЛКМ
                    if not self.rules_board:
                        mx, my = event.pos
                        mx, my = mx // self.tile, my // self.tile
                        self.field.click(mx, my)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button in [3]:  # ПКМ
                    pass

            # обновить состояние сетки
            if not self.pause:
                self.field.checking_neighbors()

            # отрисовать сетку
            self.field.draw_field(self.sc)

            # ввод правил
            if self.rules_board:
                if self.pause:
                    self.rules_space.fill(pygame.Color('floralwhite'))
                    self.field.draw_rules_space(self.rules_space)
                    self.sc.blit(self.rules_space, (self.width_screen // 2 - self.rules_space_w // 2,
                                                    self.height_screen // 2 - self.rules_space_h // 2))

            # после отрисовки всего, переворачиваем экран
            pygame.display.update()

            # держим цикл на правильной скорости
            pygame.time.Clock().tick(self.fps)


def run():

    # Параметры клеток
    tile = 50

    # правила игры [выжвание], [рождение]
    live_cell = [[2, 3], [3]]

    # создать сетку
    field = Field(tile, live_cell)

    # запуск визуализации
    GUI(field)


if __name__ == "__main__":

    run()
