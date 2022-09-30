import sys
import random
from collections import namedtuple
from typing import Iterator, Callable

import pygame

pygame.init()

RGB_COLOR = namedtuple("RGB_COLOR", ["red", "green", "blue"])


class DrawInfo:
    """this class stores all the variables needed for drawing the sorting visualizer."""

    BLACK: RGB_COLOR = RGB_COLOR(0, 0, 0)
    WHITE: RGB_COLOR = RGB_COLOR(255, 255, 255)
    GREEN: RGB_COLOR = RGB_COLOR(0, 255, 0)
    RED: RGB_COLOR = RGB_COLOR(255, 0, 0)
    PURPLE: RGB_COLOR = RGB_COLOR(108, 40, 181)
    GREY_1: RGB_COLOR = RGB_COLOR(128, 128, 128)
    GREY_2: RGB_COLOR = RGB_COLOR(160, 160, 160)
    GREY_3: RGB_COLOR = RGB_COLOR(192, 192, 192)

    GRADIENTS: list[RGB_COLOR] = [GREY_1, GREY_2, GREY_3]

    BG_COLOR: RGB_COLOR = WHITE

    # sum distance of first and last block of value from the side of the window in px.
    SIDE_PAD = 100
    # distance of tallest block of value from the top of the window in px.
    TOP_PAD = 150

    MENU_FONT: pygame.font.Font = pygame.font.SysFont("comidsans", 30)
    LARGE_FONT: pygame.font.Font = pygame.font.SysFont("comidsans", 40)

    def __init__(self, width: int, height: int, lst: list) -> None:
        self.width: int = width
        self.height: int = height
        self.window: pygame.surface.Surface = pygame.display.set_mode(
            (self.width, self.height)
        )
        pygame.display.set_caption("Sorting Algorithm Visualization")
        self.set_list(lst)

    def set_list(self, lst: list) -> None:
        self.lst: list = lst
        self.max_val: int = max(self.lst)
        self.min_val: int = min(self.lst)
        self.block_width: int = round((self.width - self.SIDE_PAD) / len(self.lst))
        self.block_height: int = round(
            (self.height - self.TOP_PAD) / (self.max_val - self.min_val)
        )
        self.start_x: int = self.SIDE_PAD // 2


def draw_list(
    draw_info: DrawInfo, color_positions: tuple[int, int] | None = None
) -> None:
    """draw a block(column) for each value in the list of numbers

    Args:
        draw_info (_type_): an instance of DrawInfo class
    """

    lst = draw_info.lst
    text_font: pygame.font.Font = pygame.font.SysFont(
        "Arial", size=draw_info.block_width
    )

    for idx, value in enumerate(lst):
        # x_pos and y_pos are the coords for the top left corner of each block
        x_pos = draw_info.start_x + idx * draw_info.block_width
        y_pos = draw_info.height - (value - draw_info.min_val) * draw_info.block_height

        color = draw_info.GRADIENTS[idx % 3]
        if color_positions:
            if idx == color_positions[0]:
                color = draw_info.GREEN
            if idx == color_positions[1]:
                color = draw_info.RED
        pygame.draw.rect(
            draw_info.window,
            color,
            (
                x_pos,
                y_pos,
                draw_info.block_width,
                (draw_info.height - y_pos) * draw_info.block_height,
            ),
        )

        value_surface: pygame.surface.Surface = text_font.render(
            str(value), True, draw_info.RED
        )
        value_rect: pygame.rect.Rect = value_surface.get_rect(
            midbottom=(x_pos + draw_info.block_width // 2, y_pos)
        )
        draw_info.window.blit(value_surface, value_rect)


def draw_menu(draw_info: DrawInfo, name: str, ascending: bool) -> None:
    menu_surface_1 = draw_info.MENU_FONT.render(
        "R - Reset | SPACE - Start Sorting | A - Ascending | D - Descending",
        True,
        draw_info.BLACK,
    )
    menu_surface_2 = draw_info.MENU_FONT.render(
        "I - Insertion Sort | B - Bubble Sort",
        True,
        draw_info.BLACK,
    )
    menu_rect_1 = menu_surface_1.get_rect(midtop=(draw_info.width / 2, 5))
    menu_rect_2 = menu_surface_2.get_rect(
        midtop=(draw_info.width / 2, menu_rect_1.bottom)
    )
    draw_info.window.blit(menu_surface_1, menu_rect_1)
    draw_info.window.blit(menu_surface_2, menu_rect_2)

    title_surface = draw_info.LARGE_FONT.render(
        f"{name} - {'Ascending' if ascending else 'Descending'} (Left -> Right)",
        True,
        draw_info.PURPLE,
    )
    title_rect = title_surface.get_rect(
        midtop=(draw_info.width / 2, menu_rect_2.bottom)
    )
    draw_info.window.blit(title_surface, title_rect)


def draw(
    draw_info: DrawInfo, color_positions: tuple[int, int], name: str, ascending: bool
) -> None:
    draw_info.window.fill(draw_info.BG_COLOR)
    draw_menu(draw_info, name, ascending)
    draw_list(draw_info, color_positions)
    pygame.display.update()


def generate_starting_list(size: int, min_val: int, max_val: int) -> list[int]:
    """create and return a list of integers.

    Args:
        size (int): size of the list
        min_val (int): minumum possible values for the list
        max_val (int): maximum possible values for the list

    Returns:
        list[int]: created list to return
    """
    lst = random.choices(range(min_val, max_val + 1), k=size)
    return lst


def bubble_sort(
    draw_info: DrawInfo, ascending: bool = True
) -> Iterator[tuple[int, int]]:
    lst = draw_info.lst

    for i in range(len(lst) - 1):
        for j in range(len(lst) - 1 - i):
            num_1 = lst[j]
            num_2 = lst[j + 1]

            if (num_1 > num_2 and ascending) or (num_1 < num_2 and not ascending):
                lst[j], lst[j + 1] = lst[j + 1], lst[j]
                # draw_list(draw_info, {j: draw_info.GREEN, j + 1: draw_info.RED})
                # we use a generator so we can show the steps of sorting mid sorting.
                yield (j, j + 1)


def insertion_sort(draw_info, ascending: bool = True) -> Iterator[tuple[int, int]]:
    lst = draw_info.lst

    for i in range(1, len(lst)):
        current = lst[i]
        while True:
            ascending_sort = i > 0 and lst[i - 1] > current and ascending
            descending_sort = i > 0 and lst[i - 1] < current and not ascending

            if not ascending_sort and not descending_sort:
                break
            lst[i] = lst[i - 1]
            i = i - 1
            lst[i] = current
            yield (i - 1, i)


def main() -> None:

    run: bool = True

    # this variable specifies if we're in the middle sorting or not.
    sorting: bool = False
    # specifies the ascending or descending order the sorting.
    ascending: bool = True

    sorting_algo: Callable[[DrawInfo, bool], Iterator[tuple[int, int]]] = bubble_sort
    sorting_algo_name: str = "Bubble Sort"
    sorting_algo_generator: Iterator[tuple[int, int]] | None = None
    color_positions: tuple[int, int] | None = None

    clock: pygame.time.Clock = pygame.time.Clock()

    lst_size = 50
    min_val = 0
    max_val = 100
    lst = generate_starting_list(lst_size, min_val, max_val)

    draw_info: DrawInfo = DrawInfo(800, 600, lst)

    while run:
        clock.tick(60)
        if sorting:
            try:
                color_positions = next(sorting_algo_generator)  # type: ignore

            except StopIteration:
                sorting = False
        draw(draw_info, color_positions, sorting_algo_name, ascending)  # type: ignore
        color_positions = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # reseting the list of numbers
                    lst = generate_starting_list(lst_size, min_val, max_val)
                    draw_info.set_list(lst)
                    sorting = False
                elif event.key == pygame.K_SPACE and sorting == False:
                    sorting = True
                    sorting_algo_generator = sorting_algo(draw_info, ascending)
                elif event.key == pygame.K_a and not sorting:
                    ascending = True
                elif event.key == pygame.K_d and not sorting:
                    ascending = False
                elif event.key == pygame.K_b and not sorting:
                    sorting_algo = bubble_sort
                    sorting_algo_name = "Bubble Sort"
                elif event.key == pygame.K_i and not sorting:
                    sorting_algo = insertion_sort
                    sorting_algo_name = "Insertion Sort"


if __name__ == "__main__":
    main()
