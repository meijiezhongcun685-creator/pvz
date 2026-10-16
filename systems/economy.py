"""经济系统：阳光收支 + 植物卡片冷却 + 战绩统计。

原版把 money 当全局变量、在事件处理里直接减，卡片冷却干脆没有。
这里收拢成一个对象：谁能买、买完扣多少、冷却好没好，都问它。
"""

from config import START_SUN
from levels import CARD_ORDER, PLANT_STATS


class Economy:
    def __init__(self):
        self.sun = START_SUN
        self.cooldowns = {kind: 0.0 for kind in CARD_ORDER}
        self.kills = 0
        self.planted = 0

    # ---------------------------------------------------------------- 每帧
    def update(self, dt: float):
        for kind in self.cooldowns:
            if self.cooldowns[kind] > 0:
                self.cooldowns[kind] = max(0.0, self.cooldowns[kind] - dt)

    # ---------------------------------------------------------------- 阳光
    def add(self, amount: int):
        self.sun += amount

    def add_kill(self):
        self.kills += 1

    # ---------------------------------------------------------------- 卡片
    def ready_ratio(self, kind: str) -> float:
        """1.0 表示冷却好了，<1 表示还得等（UI 用来画进度遮罩）。"""
        cd = self.cooldowns.get(kind, 0.0)
        total = PLANT_STATS[kind]["cooldown"]
        if total <= 0:
            return 1.0
        return max(0.0, min(1.0, 1.0 - cd / total))

    def can_buy(self, kind: str) -> bool:
        return (self.sun >= PLANT_STATS[kind]["cost"]
                and self.cooldowns.get(kind, 0.0) <= 0.0)

    def buy(self, kind: str) -> bool:
        if not self.can_buy(kind):
            return False
        self.sun -= PLANT_STATS[kind]["cost"]
        self.cooldowns[kind] = PLANT_STATS[kind]["cooldown"]
        self.planted += 1
        return True

    def refund(self, kind: str):
        """种失败（格子被占）时把钱退回，避免"点了没种上还扣钱"。"""
        self.sun += PLANT_STATS[kind]["cost"]
        self.cooldowns[kind] = 0.0
