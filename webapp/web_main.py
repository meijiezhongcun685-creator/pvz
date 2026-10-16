"""网页版入口：pygbag 把 Python + pygame 编译成 WebAssembly，在浏览器里跑同一个游戏。

跟 main.py 的区别只有两点：
1. 主循环必须是 async，每帧 `await asyncio.sleep(1/FPS)` 让出主线程。
   注意不要用 pygame.time.Clock().tick() 限帧——浏览器里它会阻塞主线程，
   表现是页面永远停在 pygbag 的 "Loading, please wait ..."，画布也不出来。
2. 时间用 pygame.time.get_ticks() 自己算，逻辑代码依旧是 dt 秒驱动。

本地预览（必须用 127.0.0.1，不能用 localhost，原因见 docs/网页版说明.md）：
    cd pvz && python -m http.server 8000 --directory webapp/build/web
"""

import asyncio

import pygame

import assets
from config import FPS, MAX_DT, WINDOW_H, WINDOW_W
import main as game_main


async def run():
    pygame.init()
    pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("植物大战僵尸 · Pygame 版")
    assets.init_audio()

    game = game_main.Game(0)

    dt_step = 1.0 / FPS
    last = pygame.time.get_ticks() / 1000.0

    while game.running:
        now = pygame.time.get_ticks() / 1000.0
        dt = min(max(now - last, 0.0), MAX_DT)
        last = now

        game.step(dt)
        await asyncio.sleep(dt_step)      # 让出主线程给浏览器，同时把帧率压在 60 附近

    pygame.quit()


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
