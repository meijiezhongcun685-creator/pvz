"""关卡与数值配置：植物的价格/血量、僵尸属性、每关的波次。

想调平衡（比如僵尸走快点、豌豆伤害高一点）只改这个文件。
"""

# ---------- 植物 ----------
PLANT_STATS = {
    "sunflower": {
        "name": "向日葵", "cost": 50, "hp": 300, "cooldown": 4.0,
        "produce_interval": 8.0, "produce_value": 25,
    },
    "peashooter": {
        "name": "豌豆射手", "cost": 100, "hp": 300, "cooldown": 4.0,
        "fire_interval": 1.2, "damage": 25,
    },
    "snowpea": {
        "name": "寒冰射手", "cost": 175, "hp": 300, "cooldown": 8.0,
        "fire_interval": 1.2, "damage": 25, "slow": 0.5, "slow_time": 3.0,
    },
    "wallnut": {
        "name": "坚果墙", "cost": 50, "hp": 2000, "cooldown": 12.0,
    },
}

# 卡片栏从左到右的顺序
CARD_ORDER = ["sunflower", "peashooter", "snowpea", "wallnut"]

# ---------- 僵尸 ----------
ZOMBIE_STATS = {
    "normal": {"name": "普通僵尸", "hp": 150, "speed": 16, "eat_dps": 30},
    "cone":   {"name": "路障僵尸", "hp": 300, "speed": 16, "eat_dps": 30},
    "bucket": {"name": "铁桶僵尸", "hp": 450, "speed": 14, "eat_dps": 35},
}

# ---------- 关卡 ----------
# 每关一组波次，一个波次 = (开始时间秒, 僵尸类型列表, 同类之间间隔秒)
LEVELS = [
    {
        "name": "第 1 关",
        "waves": [
            (12, ["normal", "normal"], 6),
            (30, ["normal", "normal", "normal"], 5),
            (52, ["normal", "cone", "normal"], 5),
            (75, ["normal", "cone", "cone", "normal"], 4),
        ],
    },
    {
        "name": "第 2 关",
        "waves": [
            (10, ["normal", "cone"], 5),
            (28, ["cone", "cone", "normal"], 4),
            (46, ["bucket", "normal", "cone"], 4),
            (66, ["bucket", "cone", "cone", "normal"], 3),
            (88, ["bucket", "bucket", "cone", "normal", "normal"], 3),
        ],
    },
]


def level(index: int) -> dict:
    """按序号取关卡配置，超出范围就取最后一关。"""
    if index < 0:
        index = 0
    if index >= len(LEVELS):
        index = len(LEVELS) - 1
    return LEVELS[index]
