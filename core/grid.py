"""网格与坐标换算：像素 <-> 格子，只在这里做，其他地方不要再写 //80。

原版是直接 `x = pos[0] // 80` 拿去索引，没有边界判断，
点在顶部 HUD 上就会索引越界或者种到 UI 上。这里把这些判断收拢。
"""

from config import CELL, COLS, GRID_TOP, ROWS, WINDOW_H, WINDOW_W


def cell_to_px(col: int, row: int):
    """格子坐标 -> 左上角像素坐标。"""
    return col * CELL, GRID_TOP + row * CELL


def cell_center(col: int, row: int):
    x, y = cell_to_px(col, row)
    return x + CELL // 2, y + CELL // 2


def px_to_cell(x: int, y: int):
    """像素坐标 -> 格子坐标；不在战场内返回 None。

    战场区是 y >= GRID_TOP 的那块，HUD 区直接返回 None，
    这样点击卡片栏永远不会被当成"在格子上种植物"。
    """
    if y < GRID_TOP or x < 0 or y >= WINDOW_H or x >= WINDOW_W:
        return None
    col = x // CELL
    row = (y - GRID_TOP) // CELL
    if 0 <= col < COLS and 0 <= row < ROWS:
        return int(col), int(row)
    return None


def battlefield_rect():
    """战场区域，画背景和裁剪的时候用。"""
    import pygame
    return pygame.Rect(0, GRID_TOP, COLS * CELL, ROWS * CELL)


def all_cells():
    """遍历所有格子。"""
    for row in range(ROWS):
        for col in range(COLS):
            yield col, row
