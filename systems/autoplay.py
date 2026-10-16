"""自动挂机（给截图 / 演示 / 以后做 AI 对战用）。

它不是游戏的一部分，是"用代码当玩家"：
截图脚本用它把一局推进到有僵尸、有植物的画面，不用人守着点鼠标。
"""

from config import ROWS, SUN_VALUE
from core.grid import px_to_cell
from levels import CARD_ORDER, PLANT_STATS


class AutoPlayer:
    def __init__(self, scene, rng=None):
        import random
        self.scene = scene
        self.rng = rng or random.Random(7)
        self.think = 0.0
        self.interval = 0.4          # 每 0.4 秒决策一次

    def update(self, dt: float):
        self.think += dt
        if self.think < self.interval:
            return
        self.think = 0.0
        self._collect_sun()
        self._plant()

    # ---------------------------------------------------------------- 收集阳光
    def _collect_sun(self):
        for sun in list(self.scene.suns):
            if sun.alive and sun.landed:
                sun.collect(self.scene)

    # ---------------------------------------------------------------- 种植物
    def _plant(self):
        """挂机策略：先保证有两三个射手能打，再补向日葵，最后加坚果。"""
        scene = self.scene
        eco = scene.economy

        peas = scene.count_plants("peashooter") + scene.count_plants("snowpea")
        suns = scene.count_plants("sunflower")
        nuts = scene.count_plants("wallnut")

        # 有僵尸的排优先放射手，没有就从上往下铺
        zombie_rows = [z.row for z in scene.zombies if z.alive]
        rows = []
        for row in zombie_rows:
            if row not in rows:
                rows.append(row)
        for row in range(ROWS):
            if row not in rows:
                rows.append(row)

        # 1) 前几个射手优先（不然只种向日葵会一直没输出）
        if peas < 4 and eco.can_buy("peashooter"):
            if self._place("peashooter", range(2, 5), rows):
                return
        # 2) 经济：向日葵铺到 8 棵
        if suns < 8 and eco.can_buy("sunflower"):
            for row in range(ROWS):
                for col in (0, 1):
                    if scene.plant_at(col, row) is None:
                        scene.try_plant("sunflower", col, row)
                        return
        # 3) 接着补射手
        if peas < 10 and eco.can_buy("peashooter"):
            if self._place("peashooter", range(2, 5), rows):
                return
        # 4) 有富余阳光时在前排加坚果挡路
        if nuts < 3 and peas >= 6 and eco.sun >= 150 and eco.can_buy("wallnut"):
            self._place("wallnut", range(6, 7), rows)

    def _place(self, kind: str, cols, rows) -> bool:
        for row in rows:
            for col in cols:
                if self.scene.plant_at(col, row) is None:
                    return self.scene.try_plant(kind, col, row)
        return False
