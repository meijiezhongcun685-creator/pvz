"""僵尸波次生成器：按关卡配置的"时间点 + 僵尸类型"出怪。

原版是数帧计数器（数到 100 出一波），跟机器快慢绑定，也没法做关卡差异。
这里把波次写成配置（levels.py），生成器只管按时间触发。
"""

import random

from config import WINDOW_W
from levels import level as get_level


class Spawner:
    def __init__(self, level_index: int, rng: random.Random | None = None):
        cfg = get_level(level_index)
        self.name = cfg["name"]
        self.rng = rng or random.Random()

        # 把 (波次开始时间, 类型列表, 间隔) 展开成一条一条的"出怪时刻表"
        schedule = []
        for start, kinds, gap in cfg["waves"]:
            for i, kind in enumerate(kinds):
                schedule.append((start + i * gap, kind))
        schedule.sort()
        self.schedule = schedule
        self.index = 0
        self.t = 0.0
        self.last_wave_time = schedule[-1][0] if schedule else 0.0

    # ---------------------------------------------------------------- 每帧
    def update(self, dt: float, scene):
        self.t += dt
        while self.index < len(self.schedule) and self.schedule[self.index][0] <= self.t:
            _, kind = self.schedule[self.index]
            scene.spawn_zombie(kind, self._pick_row(scene), self._spawn_x())
            self.index += 1

    @property
    def done(self) -> bool:
        return self.index >= len(self.schedule)

    @property
    def total(self) -> int:
        return len(self.schedule)

    @property
    def spawned(self) -> int:
        return self.index

    def in_final_wave(self) -> bool:
        """最后一波开始之后，HUD 上给个提示。"""
        return self.t >= self.last_wave_time

    # ---------------------------------------------------------------- 内部
    def _spawn_x(self) -> float:
        return float(WINDOW_W + self.rng.randint(0, 160))

    def _pick_row(self, scene) -> int:
        """挑僵尸最少的排，避免全挤在一排。"""
        from config import ROWS
        counts = [0] * ROWS
        for z in scene.zombies:
            if z.alive:
                counts[z.row] += 1
        fewest = min(counts)
        candidates = [r for r, c in enumerate(counts) if c == fewest]
        return self.rng.choice(candidates)
