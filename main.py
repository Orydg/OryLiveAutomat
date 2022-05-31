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
    Метод отображения текста на экране.

    message - выводимо сообщение.
    sc - поверхность, на которой будет отображаться сообщение.
    x, y - координаты верхнего левого угла рамки сообщения.
    font_color - цвет текста сообщения.
    font_type - шрифт сообщения.
    font_size - размер шрифта.

    """

    font_type = pygame.font.Font(font_type, font_size)
    text = font_type.render(message, True, font_color)
    sc.blit(text, (x, y))


class Numbers:
    """
    Класс для формирования объектов - цифр на доске правил формирования жизни.

    При создании объектов класса используются следующие аргументы:
    x, y - координаты верхнего левого угла цифры.
    font_size - размер шрифта цифры.
    font_type - шрифт цифры.

    Внутренние атрибуты объектов класса:
    active - флаг, имеющий положения True, False, по которому можно узнать, активна ли цифра в данный момент.
    num_name - имя цифры, точнее сама цифра (0, 1, 2 или любое другое число в текстовом формате).

    """

    def __init__(self, x, y, font_size=60, font_type=pygame.font.match_font(pygame.font.get_fonts()[0])):
        self.x = x
        self.y = y
        self.font_size = font_size
        self.font_type = font_type
        self.active = False
        self.num_name = None

    def draw_num(self, num_name, sc, x, y):
        """
        Метод объектов класс Numbers, отвечающий за отрисовку объекта - цифры.

        Аргументы метода:
        num_name - число в текстовом формате данных (str(int)).
        sc - поверхность на которой будет нарисовано число.
        x, y - координаты левого верхнего угла числа.

        """

        self.x = x
        self.y = y
        self.num_name = num_name
        font_type = pygame.font.Font(self.font_type, self.font_size)
        if self.active:
            font_color = pygame.Color("darkgreen")
        else:
            font_color = pygame.Color("darkorchid4")
        text = font_type.render(num_name, True, font_color)
        sc.blit(text, (self.x, self.y))


class Cell:
    """
    Класс ячеек.

     При создании объектов класса используются следующие аргументы:
     x, y - координаты левого верхнего угла ячейки.
     tile - размер ячейки по ширине и высоте (одно число, так как они квадратные).

     Внутренние атрибуты объектов класса:
     live - флаг, показывающий живая сейчас ячейка или нет, принимает значения 0 (мертвая) или 1 (живая).

    """
    def __init__(self, x, y, tile=50):
        self.x = x
        self.y = y
        self.tile = tile
        self.live = 0

    def draw(self, sc):
        """
        Метод объектов класса Cell, отвечающий за отрисовку клеток.

        Аргументы метода:
        sc - плоскость на которой будут нарисованы клетки.

        """

        # координаты клетки
        x, y = self.x * self.tile, self.y * self.tile

        # ширина стенки клетки (в пикселях)
        line_w = 2

        # цвет стенок клетки
        cell_color = pygame.Color('darkorchid4')

        # отрисовка стенок клетки
        pygame.draw.line(sc, cell_color, (x, y), (x + self.tile, y), line_w)
        pygame.draw.line(sc, cell_color, (x + self.tile, y), (x + self.tile, y + self.tile), line_w)
        pygame.draw.line(sc, cell_color, (x + self.tile, y + self.tile), (x, y + self.tile), line_w)
        pygame.draw.line(sc, cell_color, (x, y + self.tile), (x, y), line_w)

        # закрашивание клетки, если она живая
        if self.live:
            pygame.draw.rect(sc, pygame.Color('darkgreen'),
                             (x + line_w, y + line_w, self.tile - line_w, self.tile - line_w))

    def set_live(self, live):
        """

        Метод объектов класса Cell, отвечающий за смену атрибута live.

        Аргументы метода:
        live - принимает значения 0 или 1.

        """

        if self.live in [0, 1]:
            self.live = live


class Field:
    """

    Класс поля клеток.

    При создании объектов класса используются следующие аргументы:
    tile - ширина клетки.
    live_cell - правила жизни клеток.

    Внутренние атрибуты объектов класса:
    x, y - количество клеток по ширине и высоте экрана.
    cells - двумерный список объектов клеток - класса Cell.
    field - двумерный список нулей и единиц, в котором обрабатывается поиск соседей клеток.
    next_field - двумерный список нулей и единиц, результат поиска соседей в field,
    после используется для передачи данных о состоянии жизни в каждую клетку.
    num_law - двумерный список цифр для доски с правилами жизни (содержит объекты класса Numbers).

    """
    def __init__(self, tile, live_cell):

        self.tile = tile
        self.x = GetSystemMetrics(0) // tile
        self.y = GetSystemMetrics(1) // tile
        self.cells = [[Cell(i, j, tile) for j in range(self.y)] for i in range(self.x)]
        self.field = [[0 for _ in range(self.y)] for _ in range(self.x)]
        self.next_field = [[0 for _ in range(self.y)] for _ in range(self.x)]
        self.live_cell = live_cell
        self.num_law = [[Numbers(i, j) for j in range(9)] for i in range(2)]

    def checking_neighbors(self):
        """

        Метод объектов класс Field, отвечающий за поиск соседей клетки.
        Соседи ищутся даже с противоположного края - пространство топологически замкнуто.

        """
        for i in range(self.x):
            for j in range(self.y):
                # список соседей исследуемой клетки
                check_res = []
                # проверяем всех соседей для это клетки
                for xi in -1, 0, 1:
                    for yj in -1, 0, 1:
                        if xi == 0 and yj == 0:
                            continue
                        rx, ry = i + xi, j + yj
                        if rx == self.x:
                            rx = 0
                        if ry == self.y:
                            ry = 0
                        # записываем в список состояние найденного соседа (0 или 1)
                        check_res.append(self.field[rx][ry])

                # проверяем правило выживания (статус исследуемой клетки "жива" - 1)
                if self.field[i][j]:
                    # если количество живых соседей удовлетворяет правилам, то она жива
                    if sum(check_res) in self.live_cell[0]:
                        self.next_field[i][j] = 1
                    # если нет - мертва
                    else:
                        self.next_field[i][j] = 0

                # проверяем правило рождения (статус исследуемой клетки "мертва" - 0)
                else:
                    # если количество живых соседей удовлетворяет правилам, то она жива
                    if sum(check_res) in self.live_cell[1]:
                        self.next_field[i][j] = 1
                    # если нет - мертва
                    else:
                        self.next_field[i][j] = 0

        # глубокое копирование списка нового состояния поля клеток,
        # чтобы избежать свойст редактируемых объектов в Python
        self.field = deepcopy(self.next_field)

    def click(self, x, y):
        """

        Метод объектов класс Field, отвечающий за обработку нажатий ЛКМ по клетке.

         Аргументы метода:
         x, y - координаты ЛКМ в момент нажатия

        """

        # получаем из координат ЛКМ позиции клеток в списке клеток
        x, y = x // self.tile, y // self.tile

        # проверка на наличие исключений, если клик ЛКМ был за границей сетки клеток
        try:
            if self.field[x][y]:
                self.field[x][y] = 0
            else:
                self.field[x][y] = 1
        except IndexError:
            pass

    def draw_field(self, sc):
        """

        Метод объектов класс Field, отвечающий за отрисовку клеток.

        Аргументы метода:
        sc - поверхность для отрисовки.

        """
        for i in range(self.x):
            for j in range(self.y):
                # клетка
                self.cells[i][j].set_live(self.field[i][j])
                self.cells[i][j].draw(sc)

    def click_nums(self, x, y):
        """

        Метод объектов класс Field, отвечающий за обработку нажатий ЛКМ по цифрам на доске правил жизни клеток.

        Аргументы метода:
        x, y - координаты курсора в момент нажатия ЛКМ.

        """
        size = self.num_law[0][0].font_size
        for num in self.num_law[0]:
            if num.x <= x <= num.x + size // 2 and num.y <= y <= num.y + size:
                if num.active:
                    self.live_cell[1].remove(int(num.num_name))
                else:
                    self.live_cell[1].append(int(num.num_name))
        for num in self.num_law[1]:
            if num.x <= x <= num.x + size // 2 and num.y <= y <= num.y + size:
                if num.active:
                    self.live_cell[0].remove(int(num.num_name))
                else:
                    self.live_cell[0].append(int(num.num_name))

    def draw_rules_space(self, sc):
        """

        Метод объектов класс Field, отвечающий за отрисовку цифр на доске правил жизни клеток.

        """

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
            num.draw_num(num_name=str(i), sc=sc, x=size[0] // 3.5 + i * self.tile, y=size[1] // 6.0)

        # вторая строка текста
        print_text("Закон выживания существующей жизни!", sc, size[0] // 3.25, size[1] // 2.2)

        # прорисовка второго ряда
        for i, num in enumerate(self.num_law[1]):
            if i in self.live_cell[0]:
                num.active = True
            else:
                num.active = False
            num.draw_num(num_name=str(i), sc=sc, x=size[0] // 3.5 + i * self.tile, y=size[1] // 1.7)

        # заключительный текст
        print_text("В прочих случаях жизни не существует!", sc, size[0] // 3.25, size[1] // 1.2)


class GUI:
    """

    Класс, отвечающий за визуализацию.

    При создании объектов класса используются следующие аргументы:
    field - объект класс Field.
    fps - количество кадров в секунду (целое число от 0 до 30).

    Внутренние атрибуты объектов класса:
    width_screen, height_screen - ширина и высота пользовательского окна (фулскрин по умолчанию)
    sc - плоскость пользовательского окна.
    pause - флаг паузы (True или False).
    rules_board - флаг активности доски правил жизни клеток (True или False).
    rules_space_w, rules_space_h - ширина и высота доски правил жизни клеток.
    rules_space - плоскость для изображения доски правил жизни клеток.

    """

    def __init__(self, field,  fps=10):
        # название окна
        pygame.display.set_caption('OryLiveAutomat')

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

        # rules board
        self.rules_board = False
        self.rules_space_w = self.width_screen // 10 * 6
        self.rules_space_h = self.height_screen // 10 * 3
        self.rules_space = pygame.Surface((self.rules_space_w, self.rules_space_h))

        # обработка событий (этот метод в конструкторе идет последним, после него конструктор читает)
        self.event_loop()

    def event_loop(self):
        """

        Метод класс GUI, отвечающий за обработку событий.

        """

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
                    if event.key == pygame.K_ESCAPE:
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

                # анализ нажатия кнопок мыши
                if event.type == pygame.MOUSEBUTTONDOWN and event.button in [1]:  # ЛКМ
                    if not self.rules_board:
                        mx, my = event.pos
                        self.field.click(mx, my)
                    else:
                        self.field.click_nums(event.pos[0] - (self.width_screen // 2 - self.rules_space_w // 2),
                                              event.pos[1] - (self.height_screen // 2 - self.rules_space_h // 2))

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
    """

    Функция запуска программы.

    """

    # Параметры клеток
    tile = 50

    # правила игры [выживание], [рождение]
    live_cell = [[2, 3], [3]]

    # создать сетку
    field = Field(tile, live_cell)

    # запуск визуализации
    GUI(field)


if __name__ == "__main__":

    run()
