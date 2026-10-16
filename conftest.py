"""pytest 公共配置：把游戏目录加进 sys.path，并用无显示器驱动初始化 pygame。

跑法（在 pvz 目录下）：
    .venv/Scripts/python.exe -m pytest -q
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402
import pytest  # noqa: E402

from config import WINDOW_H, WINDOW_W  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _display():
    """assets 里用了 convert_alpha，必须先有 display surface。"""
    pygame.init()
    pygame.display.set_mode((WINDOW_W, WINDOW_H))
    yield
    pygame.quit()
