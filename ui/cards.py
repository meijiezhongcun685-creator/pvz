"""卡片栏：显示四种植物、价格、冷却，处理"点哪张卡"。

原版用鼠标左键=向日葵、右键=豌豆射手，只能有两张卡。
这里改成标准卡片栏：点卡片选中，再点格子种下，加植物只要在 levels.py 里加一条。
"""

import pygame

import assets
from config import C_HUD_BG2, C_HUD_INK, C_HUD_WARN, C_MASK, C_WHITE
from levels import CARD_ORDER, PLANT_STATS

CARD_W = 58
CARD_H = 66
CARD_GAP = 6

_icon_cache: dict = {}


def _icon(kind: str, size: int = 38) -> pygame.Surface:
    key = (kind, size)
    if key in _icon_cache:
        return _icon_cache[key]
    if kind == "wallnut":
        surf = assets.make_wallnut()
    elif kind == "snowpea":
        surf = assets.tint("peashooter.png", (120, 170, 255))
    elif kind == "sunflower":
        surf = assets.load_image("sunflower.png")
    else:
        surf = assets.load_image("peashooter.png")
    surf = pygame.transform.smoothscale(surf, (size, size))
    _icon_cache[key] = surf
    return surf


class CardBar:
    def __init__(self, x: int, y: int):
        self.rects = {
            kind: pygame.Rect(x + i * (CARD_W + CARD_GAP), y, CARD_W, CARD_H)
            for i, kind in enumerate(CARD_ORDER)
        }

    def card_at(self, pos):
        """返回被点到的卡片类型；点在卡片栏空白处返回 None。"""
        for kind, rect in self.rects.items():
            if rect.collidepoint(pos):
                return kind
        return None

    def draw(self, screen, economy, selected: str | None):
        for kind, rect in self.rects.items():
            stats = PLANT_STATS[kind]
            affordable = economy.sun >= stats["cost"]
            ready = economy.ready_ratio(kind)

            pygame.draw.rect(screen, C_HUD_BG2, rect, border_radius=6)
            pygame.draw.rect(screen, (36, 26, 14), rect, 2, border_radius=6)

            # 图片
            icon = _icon(kind)
            screen.blit(icon, (rect.centerx - icon.get_width() // 2, rect.y + 4))

            # 价格
            color = C_HUD_INK if affordable else C_HUD_WARN
            assets.draw_text(screen, stats["cost"], (rect.centerx, rect.bottom - 10),
                             16, color, center=True)

            # 冷却遮罩：从下往上退
            if ready < 1.0:
                mask_h = int(CARD_H * (1.0 - ready))
                mask = pygame.Surface((CARD_W, mask_h), pygame.SRCALPHA)
                mask.fill(C_MASK)
                screen.blit(mask, (rect.x, rect.y))

            # 选中态
            if kind == selected:
                pygame.draw.rect(screen, (255, 214, 60), rect, 3, border_radius=6)

            # 钱不够时整张压暗
            if not affordable:
                dim = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
                dim.fill((0, 0, 0, 90))
                screen.blit(dim, rect.topleft)
