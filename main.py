"""入口：初始化 pygame、固定帧率主循环、场景切换。

运行方式：
    python main.py                     # 正常玩（需要显示器）
    python main.py --level 1           # 从第 2 关开始（关卡序号从 0 算）
    python main.py --shots shots       # 截图模式：自动挂机推进并保存若干帧，不需要窗口

主循环固定步长（1/FPS），所有逻辑都用 dt 秒做单位；
原版是"数帧当计时器"，机器一快一慢，产阳光和开火速度就全乱了。
"""

import argparse
import os
import sys

import pygame

import assets
from config import FPS, MAX_DT, SOUND_ON, WINDOW_H, WINDOW_W
from levels import LEVELS


class Game:
    def __init__(self, level_index: int = 0, start: str = "start"):
        self.level_index = max(0, min(level_index, len(LEVELS) - 1))
        self.all_levels = LEVELS
        self.running = True
        self.scene = self._make_scene(start)

    def _make_scene(self, name: str):
        from core.scene import StartScene
        from scenes.play import PlayScene
        if name == "play":
            return PlayScene(self, self.level_index)
        return StartScene(self)

    # ---------------------------------------------------------------- 循环
    def step(self, dt: float):
        """推进一帧：先收事件，再更新当前场景，最后处理场景切换。"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            self.scene.handle_event(event)

        self.scene.update(dt)
        self.scene.draw(pygame.display.get_surface())

        if self.scene.wants_quit:
            self.running = False
            return
        if self.scene.next_scene is not None:
            self.scene = self.scene.next_scene

        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            dt = min(clock.tick(FPS) / 1000.0, MAX_DT)
            self.step(dt)


def run_shots(out_dir: str, level: int, times: list):
    """截图模式：用自动挂机快进，把画面存成 PNG。

    存在的意义：不用显示器也能验证"游戏真的跑起来了、画面是对的"，
    平时改完代码想快速看一眼效果，也不用自己点半小时。
    """
    from core.scene import StartScene
    from scenes.play import PlayScene
    from systems.autoplay import AutoPlayer

    os.makedirs(out_dir, exist_ok=True)
    game = Game(level)

    # 开始界面也存一张
    game.scene.draw(pygame.display.get_surface())
    pygame.image.save(pygame.display.get_surface(), os.path.join(out_dir, "shot_0_start.png"))

    game.scene = PlayScene(game, level)
    auto = AutoPlayer(game.scene)
    dt = 1.0 / FPS
    t = 0.0
    pending = sorted(times)
    shots = 1

    while pending and t < max(pending) + 5:
        if isinstance(game.scene, PlayScene):
            if auto.scene is not game.scene:
                auto = AutoPlayer(game.scene)          # 换关了，重新挂一个
            auto.update(dt)
        game.scene.update(dt)
        game.scene.draw(pygame.display.get_surface())
        pygame.event.pump()
        t += dt
        # 跟正常游玩一样处理场景切换，这样截图里也能有关过/失败界面
        if game.scene.next_scene is not None:
            game.scene = game.scene.next_scene
        while pending and t >= pending[0]:
            pending.pop(0)
            path = os.path.join(out_dir, f"shot_{shots}_t{int(t)}s.png")
            pygame.image.save(pygame.display.get_surface(), path)
            print("saved", path)
            shots += 1

    print(f"[shot mode] 用时={t:.1f}s 当前场景={type(game.scene).__name__}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="植物大战僵尸 · pygame 版")
    parser.add_argument("--level", type=int, default=0, help="起始关卡序号，从 0 开始")
    parser.add_argument("--shots", metavar="DIR", help="截图模式，输出目录")
    parser.add_argument("--shot-times", default="1.5,9,20,30",
                        help="截图时间点（秒），逗号分隔")
    parser.add_argument("--start", default="start", choices=["start", "play"],
                        help="起始场景：start=开始界面，play=直接进游戏")
    parser.add_argument("--mute", action="store_true", help="静音")
    args = parser.parse_args(argv)

    shot_mode = bool(args.shots)
    if shot_mode:
        # 没有显示器 / 不想弹窗时也能跑：用 dummy 驱动
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

    pygame.init()
    pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("植物大战僵尸 · Pygame 版")

    if not args.mute and not shot_mode:
        assets.init_audio()

    if shot_mode:
        times = [float(x) for x in args.shot_times.split(",") if x.strip()]
        run_shots(args.shots, args.level, times)
    else:
        Game(args.level, args.start).run()

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
