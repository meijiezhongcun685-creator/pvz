"""生成音效：不依赖任何素材包，用标准库合成几个短音效 wav。

跑一次就够了：python scripts/make_sounds.py
生成的 wav 放在 assets/sounds/，游戏里 assets.play("plant.wav") 直接用。
"""

import math
import os
import struct
import wave

RATE = 22050
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "assets", "sounds")


def write_wav(name, samples):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    with wave.open(path, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        frames = b"".join(struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32767))
                          for s in samples)
        f.writeframes(frames)
    print("...", name, len(samples) // RATE, "秒")


def tone(freq, dur, vol=0.35, decay=True, harmonics=(1.0, 0.3, 0.15)):
    n = int(RATE * dur)
    out = []
    for i in range(n):
        t = i / RATE
        env = (1.0 - i / n) if decay else 1.0
        # 起音做个很短的淡入，避免"啪"的爆音
        attack = min(1.0, i / (RATE * 0.005))
        v = 0.0
        for k, amp in enumerate(harmonics, start=1):
            v += amp * math.sin(2 * math.pi * freq * k * t)
        out.append(v * env * attack * vol / sum(harmonics))
    return out


def sweep(f0, f1, dur, vol=0.35):
    n = int(RATE * dur)
    out = []
    for i in range(n):
        t = i / RATE
        f = f0 + (f1 - f0) * (i / n)
        env = 1.0 - i / n
        out.append(math.sin(2 * math.pi * f * t) * env * vol)
    return out


def noise(dur, vol=0.25, lowpass=0.35):
    import random
    rng = random.Random(3)
    n = int(RATE * dur)
    out = []
    prev = 0.0
    for i in range(n):
        s = rng.uniform(-1, 1)
        prev = prev * (1 - lowpass) + s * lowpass     # 一阶低通，听起来闷一点
        out.append(prev * (1 - i / n) * vol)
    return out


def main():
    # 种植物：往上的"啵"
    write_wav("plant.wav", sweep(420, 760, 0.14, 0.3))
    # 开火：短促的"啾"
    write_wav("shoot.wav", sweep(900, 520, 0.07, 0.22))
    # 命中：闷响
    write_wav("hit.wav", noise(0.06, 0.22))
    # 僵尸死：下滑音
    write_wav("zombie_die.wav", sweep(520, 130, 0.3, 0.3))
    # 收阳光：清脆的两声
    write_wav("collect.wav", tone(880, 0.09, 0.28) + tone(1320, 0.1, 0.25))
    # 僵尸进屋：低沉的失败音
    write_wav("lose.wav", tone(220, 0.35, 0.35) + tone(150, 0.5, 0.35))
    # 过关：三个上行音
    write_wav("level_clear.wav",
              tone(523, 0.12, 0.3) + tone(659, 0.12, 0.3) + tone(784, 0.28, 0.32))


if __name__ == "__main__":
    main()
