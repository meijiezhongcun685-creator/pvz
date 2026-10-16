"""HUD：顶部那条——阳光数、卡片栏、关卡信息、波次提示。"""

import pygame

import assets
from config import C_HUD_BG, C_HUD_INK, C_HUD_WARN, WINDOW_W
from ui.cards import CARD_H, CardBar

HUD_H = 80
SUN_BOX_W = 78


def _right_text(screen, text, right_x, y, size, color=C_HUD_INK):
    """右对齐画一行字。"""
    surf = assets.get_font(size).render(str(text), True, color)
    screen.blit(surf, (right_x - surf.get_width(), y))


class Hud:
    def __init__(self):
        self.sun_rect = pygame.Rect(8, 8, SUN_BOX_W, CARD_H)
        self.cards = CardBar(self.sun_rect.right + 12, 8)

    def card_at(self, pos):
        return self.cards.card_at(pos)

    # ---------------------------------------------------------------- 绘制
    def draw(self, screen, scene):
        # 底条
        pygame.draw.rect(screen, C_HUD_BG, (0, 0, WINDOW_W, HUD_H))
        pygame.draw.line(screen, (32, 22, 12), (0, HUD_H - 2), (WINDOW_W, HUD_H - 2), 2)

        # 阳光数
        pygame.draw.rect(screen, (245, 232, 200), self.sun_rect, border_radius=6)
        pygame.draw.rect(screen, (150, 122, 70), self.sun_rect, 2, border_radius=6)
        icon = pygame.transform.smoothscale(assets.make_sun(48), (30, 30))
        screen.blit(icon, (self.sun_rect.x + 4, self.sun_rect.y + 6))
        assets.draw_text(screen, scene.economy.sun,
                         (self.sun_rect.centerx + 8, self.sun_rect.y + 22), 24, (40, 30, 10))

        # 卡片栏
        self.cards.draw(screen, scene.economy, scene.selected_card)

        # 右侧信息
        right = WINDOW_W - 12
        _right_text(screen, scene.level_name, right, 10, 22)
        _right_text(screen, f"击杀 {scene.economy.kills}", right, 34, 18)
        _right_text(screen, f"僵尸 {scene.spawner.spawned}/{scene.spawner.total}", right, 56, 18)

        # 战场里的临时文字提示（选中卡片 / 最后一波）
        if scene.selected_card:
            assets.draw_text(screen, f"已选 {scene.selected_card_name}：点一个空格子种下",
                             (WINDOW_W // 2, HUD_H + 8), 18, (255, 255, 210), center=True)
        if scene.spawner.in_final_wave() and not scene.spawner.done:
            assets.draw_text(screen, "最后一波！", (WINDOW_W // 2, HUD_H + 32),
                             22, C_HUD_WARN, center=True)

        # 操作提示
        _right_text(screen, "ESC 暂停 / R 重开", WINDOW_W - 10, HUD_H + 8, 16, (235, 240, 220))
