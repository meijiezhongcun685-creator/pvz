"""从系统里的 Noto Sans SC 抽出游戏用到的字，生成一个小字体文件。

为什么要这一步：
浏览器里没有微软雅黑（桌面版靠 SysFont 拿系统字体），网页版必须自备字体；
而完整中文字体有 17 MB，面试官点开网页要等半天，所以只抽游戏里真正出现的字。

输入：C:/Windows/Fonts/NotoSansSC-VF.ttf （SIL OFL 授权，允许打包再分发）
输出：assets/fonts/NotoSansSC.ttf

用法：python scripts/make_font.py
"""

import ast
import os
import string
import sys

from fontTools import subset

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_FONT = r"C:\Windows\Fonts\NotoSansSC-VF.ttf"
FONT_DIR = os.path.join(BASE, "assets", "fonts")
OUT_FONT = os.path.join(FONT_DIR, "NotoSansSC.ttf")

# 界面里可能出现、但源码字符串里不一定有的符号
EXTRA = (
    string.printable
    + "·…—–“”‘’《》【】（）《》、。！？：；"
    + "０１２３４５６７８９％"
    + "←→↑↓★☆✓✕"
    + "阳光僵尸植物关卡击杀波次暂停重开主菜单过关失败"
    + "向日葵豌豆射手寒冰坚果墙路障铁桶普通卡槽冷却"
)


def collect_chars() -> set:
    chars = set(EXTRA)
    for root, dirs, files in os.walk(BASE):
        dirs[:] = [d for d in dirs if d not in {".venv", "__pycache__", "build", "shots", "assets", ".git"}]
        for name in files:
            if not name.endswith(".py"):
                continue
            path = os.path.join(root, name)
            try:
                tree = ast.parse(open(path, encoding="utf-8").read())
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    chars.update(node.value)
    return chars


def main():
    if not os.path.exists(SRC_FONT):
        print("找不到源字体：", SRC_FONT)
        return 1

    chars = collect_chars()
    # 去掉控制字符（换行、制表符保留）
    text = "".join(sorted(c for c in chars if c in "\n\t" or c.isprintable()))
    os.makedirs(FONT_DIR, exist_ok=True)

    subset.main([
        SRC_FONT,
        f"--text={text}",
        f"--output-file={OUT_FONT}",
        "--name-IDs=*",
        "--drop-tables+=DSIG",
        "--recalc-bounds",
        "--no-subset-tables+=HVAR",   # 保留可变字体轴信息，避免字形错乱
    ])

    size = os.path.getsize(OUT_FONT)
    print("字数 =", len(text))
    print(f"输出 = {OUT_FONT}  ({size/1024:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
