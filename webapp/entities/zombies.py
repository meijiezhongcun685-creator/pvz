"""僵尸：普通、路障、铁桶。

关键改动（对比原版）：
1. 移动按"像素/秒"算，不是"每帧减 1"，换机器速度不变；
2. 是否被植物挡住交给 systems/collision.py 判断，僵尸只负责"啃"和"走"；
3. 走到最左边只把 alive 标掉交给场景处理，不在僵尸里 new 一个游戏对象去结束游戏。
"""

import pygame

import assets
from config import CELL, GRID_TOP, WINDOW_H, ZOMBIE_LOSE_X
from entities.entity import Entity
from levels import ZOMBIE_STATS
from systems import collision

_HAT = {
    "normal": None,
    "cone": "cone",
    "bucket": "bucket",
}

_zombie_img = None
_hat_cache = {}


def _zombie_image() -> pygame.Surface:
    global _zombie_img
    if _zombie_img is None:
        _zombie_img = assets.load_image("zombie.png", (CELL, CELL))
    return _zombie_img


def _hat(kind: str) -> pygame.Surface:
    if kind not in _hat_cache:
        _hat_cache[kind] = assets.make_cone_hat() if kind == "cone" else assets.make_bucket_hat()
    return _hat_cache[kind]


class Zombie(Entity):
    kind = "zombie"

    def __init__(self, zombie_id: str, row: int, x: float):
        stats = ZOMBIE_STATS[zombie_id]
        super().__init__(x, GRID_TOP + row * CELL, CELL, CELL)
        self.zombie_id = zombie_id
        self.stats = stats
        self.row = row
        self.hp = stats["hp"]
        self.max_hp = self.hp
        self.speed = stats["speed"]
        self.eat_dps = stats["eat_dps"]
        self.eating = False
        self.slow_timer = 0.0
        self.image = _zombie_image()
        self.walk_phase = 0.0

    # ---------------------------------------------------------------- 减速
    def apply_slow(self, factor: float, duration: float):
        """寒冰豌豆效果：取更强的减速，时间取更长的，避免叠加到 0 速。"""
        current_factor = 1.0
        if self.slow_timer > 0:
            current_factor = getattr(self, "slow_factor", 1.0)
        self.slow_factor = min(current_factor, factor)
        self.slow_timer = max(self.slow_timer, duration)

    def _current_speed(self) -> float:
        if self.slow_timer > 0:
            return self.speed * getattr(self, "slow_factor", 1.0)
        return self.speed

    # ---------------------------------------------------------------- 每帧
    def update(self, dt: float, scene):
        if self.slow_timer > 0:
            self.slow_timer = max(0.0, self.slow_timer - dt)
            if self.slow_timer == 0:
                self.slow_factor = 1.0

        target = collision.plant_in_front(self, scene.plants)
        if target is not None:
            self.eating = True
            target.take_damage(self.eat_dps * dt)
            target.being_attacked(dt)
        else:
            self.eating = False
            self.x -= self._current_speed() * dt
            self.walk_phase += dt * 6
            if self.x <= ZOMBIE_LOSE_X:
                self.alive = False
                scene.on_zombie_reached_house(self)

    def draw(self, screen: pygame.Surface):
        bob = 0
        if not self.eating:
            bob = -2 if int(self.walk_phase) % 2 == 0 else 0   # 走路上下轻微起伏
        rect = pygame.Rect(int(self.x), int(self.y) + bob, self.w, self.h)
        screen.blit(self.image, rect)

        hat = _HAT.get(self.zombie_id)
        if hat:
            hat_surf = _hat(hat)
            screen.blit(hat_surf, (rect.x, rect.y - 6))

        # 被冰冻时压一层淡蓝，一眼能看出减速中
        if self.slow_timer > 0:
            overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            overlay.fill((120, 180, 255, 70))
            screen.blit(overlay, rect.topleft)

        self.draw_hp_bar(screen, width_ratio=0.6, y_offset=-8)
