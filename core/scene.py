"""场景基类 + 开始界面 / 过关过渡 / 游戏结束界面。

原版只有一个 while 循环，没有开始界面也没有"过关"这一幕，
输了直接 gameOver() 把窗口画一行字就退出。这里把"游戏状态"拆成场景。
"""

import pygame

import assets
from config import C_BLACK, C_HUD_INK, C_WHITE, WINDOW_H, WINDOW_W


class Scene:
    """所有场景的基类：handle_event / update / draw 三件套。"""

    def __init__(self, game):
        self.game = game
        self.next_scene = None      # 想切换场景就赋值，由 Game 统一处理
        self.wants_quit = False

    def handle_event(self, event: pygame.event.Event):
        pass

    def update(self, dt: float):
        pass

    def draw(self, screen: pygame.Surface):
        pass


class StartScene(Scene):
    """开始界面：标题 + 操作说明 + 开始/退出。"""

    TIPS = [
        "点卡片选中植物，再点格子种下",
        "向日葵产阳光，豌豆射手打僵尸，坚果墙挡路",
        "掉下来的阳光点一下才算收到",
        "僵尸走到最左边就输了，撑过所有波次即过关",
        "ESC 暂停 / R 重开",
    ]

    def __init__(self, game):
        super().__init__(game)
        self.t = 0.0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._start()
            elif event.key == pygame.K_ESCAPE:
                self.wants_quit = True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._start()

    def update(self, dt):
        self.t += dt

    def _start(self):
        from scenes.play import PlayScene
        assets.play("level_clear.wav", 0.4)
        self.next_scene = PlayScene(self.game, self.game.level_index)

    def draw(self, screen):
        screen.fill((46, 94, 52))
        for y in range(0, WINDOW_H, 40):
            for x in range(0, WINDOW_W, 40):
                if (x // 40 + y // 40) % 2 == 0:
                    pygame.draw.rect(screen, (52, 104, 58), (x, y, 40, 40))

        # 标题
        assets.draw_text(screen, "植物大战僵尸 · Pygame 版", (WINDOW_W // 2, 120),
                         46, (255, 240, 200), center=True)
        assets.draw_text(screen, "Python + pygame 完整小游戏", (WINDOW_W // 2, 170),
                         20, (222, 236, 214), center=True)

        # 说明
        y = 240
        for tip in self.TIPS:
            assets.draw_text(screen, f"· {tip}", (WINDOW_W // 2, y), 20, C_WHITE, center=True)
            y += 30

        # 闪烁的开始提示
        if int(self.t * 2) % 2 == 0:
            assets.draw_text(screen, "按 空格 / 回车 或点一下鼠标开始",
                             (WINDOW_W // 2, WINDOW_H - 70), 24, (255, 214, 60), center=True)


class LevelClearScene(Scene):
    """过关过渡：显示本关战绩，自动进入下一关（也可按键立刻继续）。"""

    def __init__(self, game, level_index: int, kills: int, seconds: float):
        super().__init__(game)
        self.level_index = level_index
        self.kills = kills
        self.seconds = seconds
        self.t = 0.0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._go()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._go()

    def update(self, dt):
        self.t += dt
        if self.t >= 3.0:
            self._go()

    def _go(self):
        if self.next_scene is not None:
            return
        from scenes.play import PlayScene
        self.game.level_index = min(self.level_index + 1, len(self.game.all_levels) - 1)
        self.next_scene = PlayScene(self.game, self.game.level_index)

    def draw(self, screen):
        screen.fill((28, 62, 38))
        assets.draw_text(screen, f"{self.level_index + 1} 关通过！", (WINDOW_W // 2, 190),
                         48, (255, 236, 150), center=True)
        assets.draw_text(screen, f"击杀 {self.kills} 个僵尸 · 用时 {self.seconds:.0f} 秒",
                         (WINDOW_W // 2, 260), 24, C_WHITE, center=True)
        if int(self.t * 2) % 2 == 0:
            assets.draw_text(screen, "正在进入下一关…（按空格跳过）",
                             (WINDOW_W // 2, 340), 22, (200, 230, 200), center=True)


class GameOverScene(Scene):
    """游戏结束：重开本关 / 回主菜单 / 退出。"""

    def __init__(self, game, level_index: int, kills: int):
        super().__init__(game)
        self.level_index = level_index
        self.kills = kills
        self.t = 0.0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self._retry()
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                self.wants_quit = True
            elif event.key == pygame.K_m:
                self.next_scene = StartScene(self.game)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._retry()

    def update(self, dt):
        self.t += dt

    def _retry(self):
        from scenes.play import PlayScene
        self.next_scene = PlayScene(self.game, self.level_index)

    def draw(self, screen):
        screen.fill((26, 20, 20))
        assets.draw_text(screen, "僵尸吃掉了你的脑子", (WINDOW_W // 2, 200),
                         42, (232, 92, 92), center=True)
        assets.draw_text(screen, f"本关击杀 {self.kills} 个僵尸", (WINDOW_W // 2, 265),
                         22, C_WHITE, center=True)
        assets.draw_text(screen, "R 重开本关  ·  M 回主菜单  ·  ESC 退出",
                         (WINDOW_W // 2, 330), 22, C_HUD_INK, center=True)
