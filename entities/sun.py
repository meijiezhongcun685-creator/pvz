"""阳光：天上掉的和向日葵产的，都要玩家点一下才算收到。

原版是"到 25 帧自动加钱"，没有可点击的阳光。
这里做成掉落物：有下落过程、有停留时间、点中才加分。
"""

import math

import assets
from config import CELL, SUN_FALL_SPEED, SUN_LIFETIME, SUN_VALUE
from entities.entity import Entity

SUN_SIZE = 48


class Sun(Entity):
    kind = "sun"

    def __init__(self, x: float, y: float, target_y: float, value: int = SUN_VALUE,
                 from_sky: bool = True):
        super().__init__(x, y, SUN_SIZE, SUN_SIZE)
        self.value = value
        self.target_y = target_y
        self.life = SUN_LIFETIME
        self.from_sky = from_sky
        self.image = assets.make_sun(SUN_SIZE)
        self.spin = 0.0

    @property
    def landed(self) -> bool:
        return self.y >= self.target_y

    def update(self, dt: float, scene):
        if not self.landed:
            self.y = min(self.target_y, self.y + SUN_FALL_SPEED * dt)
        else:
            self.life -= dt
            self.spin += dt * 1.5
            if self.life <= 0:
                self.alive = False

    def draw(self, screen):
        # 快消失的时候闪烁，提示玩家赶紧点
        if self.landed and self.life < 2.0 and int(self.life * 6) % 2 == 0:
            return
        offset = math.sin(self.spin) * 2
        screen.blit(self.image, (int(self.x), int(self.y + offset)))

    def collect(self, scene):
        """被点中：加阳光、消失。"""
        self.alive = False
        scene.add_sun(self.value)
        assets.play("collect.wav", 0.4)
