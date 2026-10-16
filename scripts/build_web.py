"""构建网页版：把游戏源码挑到一个干净目录，再交给 pygbag 编译成 WebAssembly。

为什么先"挑文件"：pygbag 会把所在目录整个打包，pnz 目录里还有 .venv / tests / shots，
不挑出来会打进包里（还会因为它扫到 .venv 里的示例 wav 直接报错）。

产物：webapp/build/web/  ← 整个目录丢到静态托管（GitHub Pages）即可
本地预览：python -m http.server 8000 --directory webapp/build/web

用法：python scripts/build_web.py
"""

import os
import shutil
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGE = os.path.join(BASE, "webapp")

# 游戏真正需要的东西，一个不多一个不少
FILES = ["config.py", "levels.py", "assets.py", "main.py", "web_main.py"]
DIRS = ["core", "entities", "systems", "ui", "scenes"]
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc")


def stage() -> None:
    if os.path.isdir(STAGE):
        shutil.rmtree(STAGE)
    os.makedirs(STAGE)

    for name in FILES:
        shutil.copy2(os.path.join(BASE, name), os.path.join(STAGE, name))
    for name in DIRS:
        shutil.copytree(os.path.join(BASE, name), os.path.join(STAGE, name), ignore=IGNORE)
    # 图片 + 音效 + 子集中文字体
    shutil.copytree(os.path.join(BASE, "assets"), os.path.join(STAGE, "assets"), ignore=IGNORE)

    print("已准备构建目录：", STAGE)


def build() -> int:
    cmd = [
        sys.executable, "-m", "pygbag",
        "--build",
        "--disable-sound-format-error",     # 我们用的是 wav，浏览器能放，只是 pygbag 爱唠叨
        "--ume_block", "0",                 # 不等"用户点一下"再启动，否则面试官打开以为是坏页面
        "--app_name", "pvz",
        "--title", "植物大战僵尸 · Pygame 版",
        "--width", "800",
        "--height", "560",
        "web_main.py",
    ]
    print("执行：", " ".join(cmd))
    return subprocess.call(cmd, cwd=STAGE)


def main() -> int:
    stage()
    code = build()
    out = os.path.join(STAGE, "build", "web")
    if code != 0 or not os.path.exists(os.path.join(out, "index.html")):
        print("构建失败，退出码：", code)
        return 1
    total = 0
    for root, _, files in os.walk(out):
        for f in files:
            total += os.path.getsize(os.path.join(root, f))
    print(f"\n构建成功：{out}")
    print(f"产物体积：{total/1024/1024:.2f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
