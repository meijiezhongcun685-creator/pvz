"""碰撞与伤害结算：集中在这里，实体自己不互查。

只依赖 rect 和少量属性（row / alive / take_damage / apply_slow），
不 import 具体实体类，避免循环依赖。
"""

import pygame


def plant_in_front(zombie, plants):
    """僵尸嘴前的矩形，撞到哪棵植物就啃哪棵（同一排里最靠前的那棵）。

    注意：原版是用 `zombie.rect.y == plant.rect.y` 判断同行，
    换一套素材图高度差 1px 就永远不开火/不啃。这里用行号比，稳。
    """
    mouth = pygame.Rect(int(zombie.x) + 4, int(zombie.y) + 16, 24, zombie.h - 30)
    best = None
    for plant in plants:
        if not plant.alive or plant.row != zombie.row:
            continue
        if mouth.colliderect(plant.rect):
            # 同一排可能同时碰到多棵，取最靠左（离僵尸最近）的那棵
            if best is None or plant.x < best.x:
                best = plant
    return best


def resolve_bullets(bullets, zombies, scene):
    """子弹打僵尸：命中就结算伤害、上减速、子弹消失。返回本帧被打死的僵尸列表。"""
    killed = []
    for bullet in bullets:
        if not bullet.alive:
            continue
        for zombie in zombies:
            if not zombie.alive:
                continue
            if bullet.rect.colliderect(zombie.rect):
                bullet.alive = False
                zombie.take_damage(bullet.damage)
                if bullet.freeze:
                    zombie.apply_slow(bullet.slow, bullet.slow_time)
                if not zombie.alive:
                    killed.append(zombie)
                scene.on_bullet_hit(zombie, bullet)
                break
    return killed
