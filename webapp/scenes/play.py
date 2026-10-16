"""游戏主场景：把各个系统串起来跑一局。

这一层只做"编排"，不实现具体规则：
- 出怪交给 systems/spawner.py
- 伤害结算交给 systems/collision.py
- 阳光和冷却交给 systems/economy.py
- 界面画给 ui/hud.py、ui/cards.py
"""

import random

import pygame

import assets
from config import (CELL, COLS, C_BATTLE_BG, C_WHITE, GRID_TOP, ROWS,
                    SKY_SUN_INTERVAL, SUN_VALUE, WINDOW_H, WINDOW_W)
from core.grid import cell_center, cell_to_px, px_to_cell
from core.scene import Scene
from entities.plants import build_plant
from entities.projectile import Bullet
from entities.sun import Sun
from entities.zombies import Zombie
from levels import PLANT_STATS, ZOMBIE_STATS
from systems import collision
from systems.economy import Economy
from systems.spawner import Spawner
from ui.hud import Hud


class PlayScene(Scene):
    def __init__(self, game, level_index: int):
        super().__init__(game)
        self.level_index = level_index
        self.rng = random.Random(20260716 + level_index)

        self.economy = Economy()
        self.spawner = Spawner(level_index, self.rng)
        self.level_name = self.spawner.name
        self.hud = Hud()

        self.plants: list = []
        self.zombies: list = []
        self.bullets: list = []
        self.suns: list = []

        self.selected_card = None
        self.paused = False
        self.elapsed = 0.0
        self.sky_sun_timer = 3.0
        self.lost = False
        self.won = False
        self.shake = 0.0                 # 僵尸进屋时的屏幕抖动

        self.background = self._build_background()

    # ================================================================ 背景
    def _build_background(self) -> pygame.Surface:
        surf = pygame.Surface((WINDOW_W, WINDOW_H))
        surf.fill(C_BATTLE_BG)
        grass = assets.load_image("grassland.png", (WINDOW_W, WINDOW_H))
        surf.blit(grass, (0, 0))
        # 淡淡的棋盘格，让玩家知道哪里能种
        for row in range(ROWS):
            for col in range(COLS):
                if (col + row) % 2 == 0:
                    x, y = cell_to_px(col, row)
                    tile = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
                    tile.fill((255, 255, 255, 26))
                    surf.blit(tile, (x, y))
        return surf

    # ================================================================ 事件
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.paused = not self.paused
            elif event.key == pygame.K_r:
                self.next_scene = PlayScene(self.game, self.level_index)
            elif event.key == pygame.K_m:
                from core.scene import StartScene
                self.next_scene = StartScene(self.game)
            return

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        if self.paused:
            self.paused = False
            return

        pos = event.pos

        # 1) 先看是不是点了卡片
        kind = self.hud.card_at(pos)
        if kind:
            self.selected_card = None if self.selected_card == kind else kind
            return

        # 2) 再看是不是点了阳光
        for sun in reversed(self.suns):
            if sun.alive and sun.rect.collidepoint(pos):
                sun.collect(self)
                return

        # 3) 最后才是种植物
        if not self.selected_card:
            return
        cell = px_to_cell(*pos)
        if cell is None:
            return
        self.try_plant(self.selected_card, cell[0], cell[1])

    # ================================================================ 每帧
    def update(self, dt: float):
        if self.paused or self.lost or self.won:
            return

        self.elapsed += dt
        self.shake = max(0.0, self.shake - dt)

        # 经济与冷却
        self.economy.update(dt)

        # 天上掉阳光
        self.sky_sun_timer -= dt
        if self.sky_sun_timer <= 0:
            self.sky_sun_timer = SKY_SUN_INTERVAL + self.rng.uniform(-1.0, 1.5)
            self.drop_sun(self.rng.randint(60, WINDOW_W - 60),
                          GRID_TOP + self.rng.randint(20, ROWS * CELL - 60), from_sky=True)

        # 出怪
        self.spawner.update(dt, self)

        # 各实体自己更新
        for plant in self.plants:
            if plant.alive:
                plant.update(dt, self)
        for zombie in self.zombies:
            if zombie.alive:
                zombie.update(dt, self)
        for bullet in self.bullets:
            if bullet.alive:
                bullet.update(dt, self)
        for sun in self.suns:
            if sun.alive:
                sun.update(dt, self)

        # 子弹命中结算
        killed = collision.resolve_bullets(self.bullets, self.zombies, self)
        for zombie in killed:
            self.economy.add_kill()
            zombie.zombie_id = zombie.zombie_id     # 留个位置给以后加"掉阳光"
        if killed:
            assets.play("zombie_die.wav", 0.4)

        # 统一清理（不在遍历里删元素，这就是原版最容易出 bug 的地方）
        self.plants = [p for p in self.plants if p.alive]
        self.zombies = [z for z in self.zombies if z.alive]
        self.bullets = [b for b in self.bullets if b.alive]
        self.suns = [s for s in self.suns if s.alive]

        # 胜负判定
        if self.lost:
            from core.scene import GameOverScene
            self.next_scene = GameOverScene(self.game, self.level_index, self.economy.kills)
        elif self.spawner.done and not self.zombies:
            self.won = True
            assets.play("level_clear.wav", 0.5)
            from core.scene import LevelClearScene
            self.next_scene = LevelClearScene(self.game, self.level_index,
                                              self.economy.kills, self.elapsed)

    # ================================================================ 对外接口
    # 植物/僵尸/子弹之间不直接互相调用，都经过场景，方便以后换实现。

    def plant_at(self, col: int, row: int):
        for plant in self.plants:
            if plant.alive and plant.col == col and plant.row == row:
                return plant
        return None

    def count_plants(self, kind: str) -> int:
        return sum(1 for p in self.plants if p.alive and p.plant_id == kind)

    def try_plant(self, kind: str, col: int, row: int) -> bool:
        """种一株植物：格子空、钱够、冷却好才行。"""
        if self.plant_at(col, row) is not None:
            return False
        if not self.economy.can_buy(kind):
            return False
        if not self.economy.buy(kind):
            return False
        plant = build_plant(kind, col, row)
        self.plants.append(plant)
        self.selected_card = None
        assets.play("plant.wav", 0.45)
        return True

    def spawn_bullet(self, plant):
        """射手开火。寒冰射手额外带上减速参数。"""
        from entities.projectile import BULLET_SIZE
        bx = plant.x + plant.w - 8
        by = plant.y + plant.h // 2 - BULLET_SIZE // 2
        if plant.bullet_kind == "snow":
            stats = PLANT_STATS[plant.plant_id]
            bullet = Bullet(bx, by, stats["damage"], freeze=True,
                            slow=stats["slow"], slow_time=stats["slow_time"])
        else:
            bullet = Bullet(bx, by, PLANT_STATS[plant.plant_id]["damage"])
        self.bullets.append(bullet)
        assets.play("shoot.wav", 0.25)

    def spawn_zombie(self, zombie_id: str, row: int, x: float):
        self.zombies.append(Zombie(zombie_id, row, x))

    def drop_sun(self, x: float, target_y: float, from_sky: bool = True):
        spawn_y = -40 if from_sky else target_y - 26
        self.suns.append(Sun(x, spawn_y, target_y, SUN_VALUE, from_sky))

    def add_sun(self, amount: int):
        self.economy.add(amount)

    def has_zombie_in_row(self, row: int, x: float) -> bool:
        """同一排、在自己右边（还没越过自己）的僵尸 —— 射手据此决定开不开火。"""
        for zombie in self.zombies:
            if zombie.alive and zombie.row == row and zombie.x + 30 > x and zombie.x < WINDOW_W + 40:
                return True
        return False

    def on_bullet_hit(self, zombie, bullet):
        assets.play("hit.wav", 0.2)

    def on_zombie_reached_house(self, zombie):
        self.lost = True
        self.shake = 0.4
        assets.play("lose.wav", 0.6)

    # ================================================================ 绘制
    def draw(self, screen):
        offset = (0, 0)
        if self.shake > 0:
            offset = (self.rng.randint(-4, 4), self.rng.randint(-3, 3))
        screen.blit(self.background, offset)

        for sun in self.suns:
            sun.draw(screen)
        for plant in self.plants:
            plant.draw(screen)
        for zombie in self.zombies:
            zombie.draw(screen)
        for bullet in self.bullets:
            bullet.draw(screen)

        self.hud.draw(screen, self)

        if self.paused:
            mask = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 140))
            screen.blit(mask, (0, 0))
            assets.draw_text(screen, "已暂停", (WINDOW_W // 2, WINDOW_H // 2 - 20),
                             52, C_WHITE, center=True)
            assets.draw_text(screen, "按 ESC 继续 · R 重开本关 · M 回主菜单",
                             (WINDOW_W // 2, WINDOW_H // 2 + 50), 22, (230, 230, 230), center=True)

    @property
    def selected_card_name(self) -> str:
        if not self.selected_card:
            return ""
        return PLANT_STATS[self.selected_card]["name"]
