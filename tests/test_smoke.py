"""冒烟测试：把"游戏能玩"这件事变成可重复执行的断言。

不测画面好不好看（那个靠截图核对），只测逻辑是否正确、跑一局会不会崩。
"""

from config import CELL, GRID_TOP, ROWS, START_SUN, SUN_VALUE
from core.grid import cell_to_px, px_to_cell
from entities.plants import build_plant
from entities.sun import Sun
from entities.zombies import Zombie
from levels import LEVELS, PLANT_STATS
from systems import collision
from systems.autoplay import AutoPlayer
from systems.economy import Economy

import main as game_main
from core.scene import LevelClearScene
from scenes.play import PlayScene


# ---------------------------------------------------------------- 网格
def test_px_to_cell_basic():
    assert px_to_cell(10, GRID_TOP + 10) == (0, 0)
    assert px_to_cell(CELL + 5, GRID_TOP + CELL + 5) == (1, 1)


def test_px_to_cell_rejects_hud_and_outside():
    assert px_to_cell(10, 10) is None                # 点在 HUD 上
    assert px_to_cell(-1, GRID_TOP + 10) is None     # 窗口外
    assert px_to_cell(10, GRID_TOP + ROWS * CELL + 1) is None


def test_cell_to_px_round_trip():
    for col in (0, 3, 9):
        for row in (0, 2, 5):
            x, y = cell_to_px(col, row)
            assert px_to_cell(x + 1, y + 1) == (col, row)


# ---------------------------------------------------------------- 经济
def test_economy_buy_and_cooldown():
    eco = Economy()
    assert eco.sun == START_SUN
    assert eco.can_buy("peashooter")
    assert eco.buy("peashooter")
    assert eco.sun == START_SUN - PLANT_STATS["peashooter"]["cost"]
    assert not eco.can_buy("peashooter")            # 冷却中
    assert not eco.buy("snowpea")                   # 钱不够（剩 50 < 175）
    eco.update(PLANT_STATS["peashooter"]["cooldown"])
    assert eco.ready_ratio("peashooter") == 1.0


def test_economy_refund_restores_money():
    eco = Economy()
    eco.buy("sunflower")
    after = eco.sun
    eco.refund("sunflower")
    assert eco.sun == after + PLANT_STATS["sunflower"]["cost"]
    assert eco.can_buy("sunflower")


# ---------------------------------------------------------------- 碰撞
def test_zombie_eats_plant_in_same_row():
    plant = build_plant("peashooter", 3, 2)
    zombie = Zombie("normal", 2, plant.x + 40)
    assert collision.plant_in_front(zombie, [plant]) is plant


def test_zombie_ignores_plant_in_other_row():
    plant = build_plant("peashooter", 3, 2)
    zombie = Zombie("normal", 4, plant.x + 40)
    assert collision.plant_in_front(zombie, [plant]) is None


# ---------------------------------------------------------------- 阳光
class _DummyScene:
    def __init__(self):
        self.gained = 0

    def add_sun(self, amount):
        self.gained += amount


def test_sun_collect_adds_sun_once():
    scene = _DummyScene()
    sun = Sun(100, 0, 200, SUN_VALUE)
    sun.collect(scene)
    assert scene.gained == SUN_VALUE
    assert not sun.alive                            # 收完就消失，不能重复收


# ---------------------------------------------------------------- 缺素材兜底
def test_missing_image_falls_back_to_placeholder():
    import assets
    surf = assets.load_image("这个文件不存在.png", (40, 40))
    assert surf.get_size() == (40, 40)


# ---------------------------------------------------------------- 整局
def test_level_one_is_beatable():
    """自动挂机跑完第 1 关：僵尸必须被清空、判定为胜利、阳光不能变负。"""
    game = game_main.Game(0)
    game.scene = PlayScene(game, 0)
    auto = AutoPlayer(game.scene)

    dt = 1 / 60
    for _ in range(int(110 / dt)):
        auto.update(dt)
        game.scene.update(dt)
        if game.scene.next_scene is not None:
            break

    scene = game.scene
    total = LEVELS[0]["waves"]
    expected = sum(len(kinds) for _, kinds, _ in total)
    assert scene.spawner.total == expected
    assert scene.economy.kills == expected          # 一个不剩
    assert scene.won and not scene.lost
    assert scene.economy.sun >= 0
    assert isinstance(scene.next_scene, LevelClearScene)


def test_planting_blocked_by_occupied_cell_and_money():
    game = game_main.Game(0)
    scene = PlayScene(game, 0)
    assert scene.try_plant("sunflower", 0, 0)
    assert not scene.try_plant("sunflower", 0, 0)   # 格子被占
    scene.economy.sun = 0
    assert not scene.try_plant("peashooter", 5, 5)  # 没钱
