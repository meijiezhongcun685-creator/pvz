"""子弹：豌豆、寒冰豌豆。

原版把"加分、过关"写在子弹类的 nextLevel() 里，职责错位；
这里子弹只管飞和标记命中，伤害结算、过关判定都由场景负责。
"""

import assets
from config import WINDOW_W
from entities.entity import Entity

BULLET_SIZE = 25
PEA_SPEED = 300          # px/s
SNOW_TINT = (110, 200, 255)


class Bullet(Entity):
    kind = "bullet"

    def __init__(self, x: float, y: float, damage: int,
                 freeze: bool = False, slow: float = 1.0, slow_time: float = 0.0):
        super().__init__(x, y, BULLET_SIZE, BULLET_SIZE)
        self.damage = damage
        self.freeze = freeze
        self.slow = slow
        self.slow_time = slow_time
        self.image = assets.make_pea_bullet(SNOW_TINT if freeze else (120, 220, 90), BULLET_SIZE)

    def update(self, dt: float, scene):
        self.x += PEA_SPEED * dt
        if self.x > WINDOW_W:
            self.alive = False

    def draw(self, screen):
        screen.blit(self.image, self.rect)
