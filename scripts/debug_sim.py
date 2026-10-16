"""无窗口快进一局，每 5 秒打印一次场上状态，用来验证逻辑（不是游戏的一部分）。

用法：python scripts/debug_sim.py [秒数]
"""

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

import main as game_main  # noqa: E402
from config import FPS, WINDOW_H, WINDOW_W  # noqa: E402
from scenes.play import PlayScene  # noqa: E402
from systems.autoplay import AutoPlayer  # noqa: E402


def snapshot(scene):
    kinds = {}
    for p in scene.plants:
        kinds[p.plant_id] = kinds.get(p.plant_id, 0) + 1
    rows = {}
    for z in scene.zombies:
        rows[z.row] = rows.get(z.row, 0) + 1
    return (f"植物={kinds} 僵尸行={rows} 子弹={len(scene.bullets)} "
            f"阳光={scene.economy.sun} 击杀={scene.economy.kills}")


def main():
    seconds = float(sys.argv[1]) if len(sys.argv) > 1 else 60.0
    pygame.init()
    pygame.display.set_mode((WINDOW_W, WINDOW_H))

    game = game_main.Game(0)
    game.scene = PlayScene(game, 0)
    auto = AutoPlayer(game.scene)

    dt = 1.0 / FPS
    t = 0.0
    nxt = 5.0
    while t < seconds:
        auto.update(dt)
        game.scene.update(dt)
        t += dt
        if t >= nxt:
            print(f"t={t:5.1f}s  {snapshot(game.scene)}")
            nxt += 5.0

    s = game.scene
    print("结束:", snapshot(s), "状态=", "win" if s.won else ("lose" if s.lost else "running"))
    pygame.quit()


if __name__ == "__main__":
    main()
