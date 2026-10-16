"""实体基类：植物、僵尸、子弹、阳光都从这里继承。

统一约定：
- 位置用浮点 x/y（移动更平滑），要矩形时用 .rect 取；
- update(dt, scene) 负责自己的逻辑，draw(screen) 只负责画；
- 死亡只标记 alive=False，由场景在循环结束后统一清理（不在遍历中删元素）。
"""

import pygame

from config import C_BLACK, C_HP_BAD, C_HP_OK


class Entity:
    kind = "entity"

    def __init__(self, x: float, y: float, w: int, h: int):
        self.x = float(x)
        self.y = float(y)
        self.w = int(w)
        self.h = int(h)
        self.hp = 1
        self.max_hp = 1
        self.alive = True

    # ---------------------------------------------------------------- 基础
    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    @property
    def center(self):
        return int(self.x) + self.w // 2, int(self.y) + self.h // 2

    @property
    def hp_ratio(self) -> float:
        if self.max_hp <= 0:
            return 0.0
        return max(0.0, min(1.0, self.hp / self.max_hp))

    def take_damage(self, amount: float):
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    # ---------------------------------------------------------------- 虚函数
    def update(self, dt: float, scene):
        pass

    def draw(self, screen: pygame.Surface):
        pass

    # ---------------------------------------------------------------- 通用绘制
    def draw_hp_bar(self, screen, width_ratio: float = 0.7, y_offset: int = -7):
        """受伤后才画血条，满血不显示，画面更干净。"""
        if self.hp >= self.max_hp:
            return
        w = int(self.w * width_ratio)
        x = int(self.x) + (self.w - w) // 2
        y = int(self.y) + y_offset
        pygame.draw.rect(screen, C_BLACK, (x, y, w, 5))
        pygame.draw.rect(screen, C_HP_OK if self.hp_ratio > 0.35 else C_HP_BAD,
                         (x, y, int(w * self.hp_ratio), 5))
