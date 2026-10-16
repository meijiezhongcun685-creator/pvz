"""植物：向日葵、豌豆射手、寒冰射手、坚果墙。

每个植物自己知道"我该干什么"，场景不需要写一堆 isinstance 分支：
原版是用 `if isinstance(plant, Sunflower): ... elif isinstance(...)` 在一个方法里
把几种植物的行为串起来，加一种植物就要改那个方法；这里改成每种植物重写 update。
"""

import pygame

import assets
from config import CELL
from core.grid import cell_center, cell_to_px
from entities.entity import Entity
from levels import PLANT_STATS

_SPRITE_NAME = {
    "sunflower": "sunflower.png",
    "peashooter": "peashooter.png",
    "snowpea": "peashooter.png",   # 寒冰射手 = 豌豆射手染色
    "wallnut": None,               # 坚果用代码画
}

_SNOW_TINT = (120, 170, 255)


def _make_sprite(plant_id: str) -> pygame.Surface:
    if plant_id == "wallnut":
        return assets.make_wallnut()
    if plant_id == "snowpea":
        return assets.tint(_SPRITE_NAME[plant_id], _SNOW_TINT)
    return assets.load_image(_SPRITE_NAME[plant_id], (CELL, CELL))


class Plant(Entity):
    kind = "plant"

    def __init__(self, plant_id: str, col: int, row: int):
        self.plant_id = plant_id
        self.stats = PLANT_STATS[plant_id]
        x, y = cell_to_px(col, row)
        super().__init__(x, y, CELL, CELL)
        self.col = col
        self.row = row
        self.hp = self.stats["hp"]
        self.max_hp = self.hp
        self.timer = 0.0
        self.image = _make_sprite(plant_id)
        self.being_eaten = False

    # 僵尸啃咬走这个方法，方便以后加"被啃时的抖动/掉头"动画
    def being_attacked(self, dt: float):
        self.being_eaten = True

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)
        self.draw_hp_bar(screen, y_offset=-6)
        self.being_eaten = False


class Sunflower(Plant):
    def update(self, dt: float, scene):
        self.timer += dt
        if self.timer >= self.stats["produce_interval"]:
            self.timer = 0.0
            cx, cy = cell_center(self.col, self.row)
            scene.drop_sun(cx, cy - 10, from_sky=False)   # 自己身边产出，不用点太快


class Shooter(Plant):
    """射手基类：同行右侧有僵尸才开火（朝右边打，不打空枪）。"""

    def update(self, dt: float, scene):
        if not scene.has_zombie_in_row(self.row, self.x):
            return
        self.timer += dt
        if self.timer >= self.stats["fire_interval"]:
            self.timer = 0.0
            scene.spawn_bullet(self)


class Peashooter(Shooter):
    bullet_kind = "pea"


class SnowPea(Shooter):
    bullet_kind = "snow"


class WallNut(Plant):
    def update(self, dt: float, scene):
        pass   # 纯肉盾


_CLASS_MAP = {
    "sunflower": Sunflower,
    "peashooter": Peashooter,
    "snowpea": SnowPea,
    "wallnut": WallNut,
}


def build_plant(plant_id: str, col: int, row: int) -> Plant:
    cls = _CLASS_MAP.get(plant_id, Plant)
    return cls(plant_id, col, row)
