"""把几个非游戏中的界面单独渲染成图片，用来检查排版（开发辅助，不是游戏的一部分）。

用法：python scripts/render_scenes.py
输出：shots/ui_*.png
"""

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

import pygame  # noqa: E402

import assets  # noqa: E402
import main as game_main  # noqa: E402
from config import WINDOW_H, WINDOW_W  # noqa: E402
from core.scene import GameOverScene, LevelClearScene, StartScene  # noqa: E402
from scenes.play import PlayScene  # noqa: E402
from systems.autoplay import AutoPlayer  # noqa: E402

OUT = os.path.join(BASE, "shots")


def save(screen, name):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    pygame.image.save(screen, path)
    print("saved", path)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    assets.init_audio()
    game = game_main.Game(0)

    # 开始界面
    start = StartScene(game)
    start.update(0.5)
    start.draw(screen)
    save(screen, "ui_1_start.png")

    # 暂停画面：先跑 40 秒再暂停
    game.scene = PlayScene(game, 0)
    auto = AutoPlayer(game.scene)
    for _ in range(40 * 60):
        auto.update(1 / 60)
        game.scene.update(1 / 60)
    game.scene.paused = True
    game.scene.draw(screen)
    save(screen, "ui_2_paused.png")

    # 过关界面
    clear = LevelClearScene(game, 0, kills=12, seconds=98.0)
    clear.update(1.0)
    clear.draw(screen)
    save(screen, "ui_3_level_clear.png")

    # 失败界面
    over = GameOverScene(game, 0, kills=5)
    over.draw(screen)
    save(screen, "ui_4_game_over.png")

    pygame.quit()


if __name__ == "__main__":
    main()
