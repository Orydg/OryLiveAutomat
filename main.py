""" Симуляция "Жизни".

Игра жизни Конвея — это классическая  автоматизация, созданная в 1970 году Джоном
Конвей. https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life

"""

from win32api import GetSystemMetrics
from copy import deepcopy
import pygame
pygame.init()


class Cell:
    def __init__(self, x, y, tile=50):
        self.x = x
        self.y = y
        self.tile = tile
        self.live = 0

    def draw(self, sc):
        x, y = self.x * self.tile, self.y * self.tile
        line_w = 2
        pygame.draw.line(sc, pygame.Color('darkorange1'), (x, y), (x + self.tile, y), line_w)
        pygame.draw.line(sc, pygame.Color('darkorange1'), (x + self.tile, y), (x + self.tile, y + self.tile), line_w)
        pygame.draw.line(sc, pygame.Color('darkorange1'), (x + self.tile, y + self.tile), (x, y + self.tile), line_w)
        pygame.draw.line(sc, pygame.Color('darkorange1'), (x, y + self.tile), (x, y), line_w)
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
        # self.field[0][1] = 1
        # self.field[0][2] = 1
        self.next_field = [[0 for _ in range(self.y)] for _ in range(self.x)]
        self.live_cell = live_cell

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
                            rx = -1
                        if ry == self.y:
                            ry = -1
                        cell_neighbor = self.field[rx][ry]
                        check_res.append(cell_neighbor)
                if sum(check_res) in self.live_cell:
                    self.next_field[i][j] = 1
                else:
                    self.next_field[i][j] = 0

        self.field = deepcopy(self.next_field)

    def click(self, x, y):
        if self.field[x][y]:
            self.field[x][y] = 0
        else:
            self.field[x][y] = 1

    def draw(self, sc):
        for i in range(self.x):
            for j in range(self.y):
                # клетка
                self.cells[i][j].set_live(self.field[i][j])
                self.cells[i][j].draw(sc)


class GUI:

    def __init__(self, field,  fps=1):
        # название окна
        pygame.display.set_caption('OLA')

        # ширина и высота окна берутся из системных настроек монитора (для режима FULLSCREEN)
        self.width_screen, self.height_screen = GetSystemMetrics(0), GetSystemMetrics(1)

        # количество кадров в секунду
        self.fps = fps

        # создание пользовательского окна
        self.sc = pygame.display.set_mode((self.width_screen, self.height_screen), pygame.FULLSCREEN)

        # флаг паузы
        self.pause = False

        # field
        self.field = field

        # tile cell
        self.tile = field.tile

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

                    # пауза
                    elif event.key == pygame.K_SPACE:
                        if self.pause:
                            self.pause = False
                        else:
                            self.pause = True

                # обработка отжатий клавиш
                elif event.type == pygame.KEYUP:
                    pass

                # анализ нажатия кнопок мыши
                if event.type == pygame.MOUSEBUTTONDOWN and event.button in [1]:  # ЛКМ
                    mx, my = event.pos
                    mx, my = mx // self.tile, my // self.tile
                    self.field.click(mx, my)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button in [3]:  # ПКМ
                    pass

            # обновить состояние сетки
            if not self.pause:
                self.field.checking_neighbors()

            # отрисовать сетку
            self.field.draw(self.sc)

            # после отрисовки всего, переворачиваем экран
            pygame.display.update()

            # держим цикл на правильной скорости
            pygame.time.Clock().tick(self.fps)


def run():

    # Параметры клеток
    tile = 50

    # правила игры
    live_cell = [3, 4]

    # создать сетку
    field = Field(tile, live_cell)

    # запуск визуализации
    GUI(field)


if __name__ == "__main__":

    run()
