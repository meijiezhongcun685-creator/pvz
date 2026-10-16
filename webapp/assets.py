"""资源层：图片 / 字体 / 音效的统一加载与缓存。

为什么单独一层：
1. 所有用到的素材从这里拿，缺图不崩（给占位图形兜底），不会像原版那样一张图没有就崩在加载行；
2. 有缓存，同一张图不会反复从磁盘读；
3. 补齐原项目缺少的素材（坚果、寒冰射手、路障/铁桶僵尸、阳光），全部用代码画，避免版权问题。
"""

import os

import pygame

from config import CELL

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "assets", "imgs")
SOUND_DIR = os.path.join(BASE_DIR, "assets", "sounds")

_image_cache: dict = {}
_sound_cache: dict = {}
_font_cache: dict = {}
_original: dict = {}          # 原图，用于染色时保持原始像素


# ---------------------------------------------------------------- 图片
def load_image(name: str, size=None) -> pygame.Surface:
    """按文件名加载 assets/imgs 下的图，带缓存；缺图返回占位方块。"""
    key = (name, size)
    if key in _image_cache:
        return _image_cache[key]

    path = os.path.join(IMG_DIR, name)
    if os.path.exists(path):
        surf = pygame.image.load(path).convert_alpha()
        _original[name] = surf.copy()
    else:
        surf = _placeholder(name)

    if size and surf.get_size() != tuple(size):
        surf = pygame.transform.smoothscale(surf, size)

    _image_cache[key] = surf
    return surf


def tint(name: str, color) -> pygame.Surface:
    """给图片整体染色（用乘法混合），用来做寒冰射手这类换色精灵。"""
    key = ("tint", name, color)
    if key in _image_cache:
        return _image_cache[key]
    base = _original.get(name) or load_image(name)
    surf = base.copy()
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    layer.fill(color)
    surf.blit(layer, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    _image_cache[key] = surf
    return surf


def _placeholder(name: str) -> pygame.Surface:
    """缺图时的占位图形：灰色方块 + 文件名首字母，一眼能看出少哪张图。"""
    surf = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
    surf.fill((150, 150, 150, 200))
    pygame.draw.rect(surf, (90, 90, 90), surf.get_rect(), 3)
    f = get_font(28)
    text = f.render(name[:3], True, (40, 40, 40))
    surf.blit(text, text.get_rect(center=surf.get_rect().center))
    return surf


# ---------------------------------------------------------------- 手绘素材
def make_sun(size: int = 48) -> pygame.Surface:
    """阳光：黄色圆 + 放射光刺。"""
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    c = size // 2
    for i in range(12):
        angle = i * 30
        end = _rotate((0, -c + 2), angle, c, c)
        pygame.draw.line(surf, (255, 214, 92), (c, c), end, 3)
    pygame.draw.circle(surf, (255, 205, 60), (c, c), c - 8)
    pygame.draw.circle(surf, (255, 240, 170), (c - 4, c - 5), max(3, c // 5))
    return surf


def _rotate(point, degrees, cx, cy):
    import math
    rad = math.radians(degrees)
    x, y = point
    dx, dy = x - cx, y - cy
    return (cx + dx * math.cos(rad) - dy * math.sin(rad),
            cy + dx * math.sin(rad) + dy * math.cos(rad))


def make_wallnut() -> pygame.Surface:
    """坚果墙：棕色椭圆 + 高光 + 一张脸（原版没有这张素材，用代码画）。"""
    surf = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
    rect = pygame.Rect(16, 12, CELL - 32, CELL - 24)
    pygame.draw.ellipse(surf, (176, 116, 60), rect)
    pygame.draw.ellipse(surf, (118, 70, 32), rect, 3)
    # 高光
    pygame.draw.ellipse(surf, (214, 164, 108), pygame.Rect(28, 22, 14, 10))
    # 眼睛
    pygame.draw.circle(surf, (60, 36, 16), (rect.x + 18, rect.y + 28), 5)
    pygame.draw.circle(surf, (60, 36, 16), (rect.right - 18, rect.y + 28), 5)
    pygame.draw.circle(surf, (255, 255, 255), (rect.x + 16, rect.y + 26), 2)
    pygame.draw.circle(surf, (255, 255, 255), (rect.right - 20, rect.y + 26), 2)
    # 嘴
    pygame.draw.arc(surf, (90, 52, 22), pygame.Rect(rect.x + 20, rect.y + 34, rect.w - 40, 22),
                    3.4, 6.0, 3)
    return surf


def make_pea_bullet(color=(120, 220, 90), size: int = 25) -> pygame.Surface:
    """子弹兜底素材：圆球。"""
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(surf, color, (size // 2, size // 2), size // 2 - 1)
    pygame.draw.circle(surf, (255, 255, 255), (size // 2 - 4, size // 2 - 4), 3)
    return surf


def make_cone_hat() -> pygame.Surface:
    """路障僵尸头顶的橙色锥。"""
    surf = pygame.Surface((CELL, 34), pygame.SRCALPHA)
    pygame.draw.polygon(surf, (226, 130, 46), [(CELL // 2, 0), (CELL // 2 - 22, 34), (CELL // 2 + 22, 34)])
    pygame.draw.polygon(surf, (150, 76, 20), [(CELL // 2, 0), (CELL // 2 - 22, 34), (CELL // 2 + 22, 34)], 3)
    return surf


def make_bucket_hat() -> pygame.Surface:
    """铁桶僵尸头顶的桶。"""
    surf = pygame.Surface((CELL, 32), pygame.SRCALPHA)
    rect = pygame.Rect(CELL // 2 - 20, 4, 40, 28)
    pygame.draw.rect(surf, (168, 172, 178), rect, border_radius=4)
    pygame.draw.rect(surf, (96, 100, 106), rect, 3, border_radius=4)
    pygame.draw.line(surf, (210, 214, 220), (CELL // 2 - 14, 8), (CELL // 2 - 14, 30), 3)
    return surf


FONT_DIR = os.path.join(BASE_DIR, "assets", "fonts")
FONT_FILE = os.path.join(FONT_DIR, "NotoSansSC.ttf")   # 网页版自带的中文字体
# pygbag 在浏览器里会把 PYGBAG 环境变量设上；浏览器里没有系统字体，只能自带
IN_BROWSER = bool(os.environ.get("PYGBAG"))


# ---------------------------------------------------------------- 字体
def get_font(size: int = 22) -> pygame.font.Font:
    """中文字体：桌面用微软雅黑，网页版用自带字体，都没有就退回默认。"""
    if size in _font_cache:
        return _font_cache[size]

    font = None
    if not IN_BROWSER:
        try:
            font = pygame.font.SysFont("Microsoft YaHei,SimHei,SimSun,Arial", size)
        except Exception:
            font = None
    if font is None and os.path.exists(FONT_FILE):
        font = pygame.font.Font(FONT_FILE, size)
    if font is None:
        font = pygame.font.Font(None, size)

    _font_cache[size] = font
    return font


def draw_text(screen, text, pos, size: int = 22, color=(255, 255, 255), center=False):
    surf = get_font(size).render(str(text), True, color)
    rect = surf.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    screen.blit(surf, rect)
    return rect


# ---------------------------------------------------------------- 音效
def init_audio() -> bool:
    """初始化混音器；失败就静音运行，不影响游戏。

    浏览器里第一次初始化可能因为还没收到用户操作而被拒，所以这里兜住所有异常，
    宁可没声音也不能白屏。开始界面按空格/点击那一下正好可以作为解锁时机。
    """
    try:
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        return True
    except Exception:
        return False


_audio_retry_at = 0.0


def _ensure_audio() -> bool:
    """混音器没起来就再试一次。

    浏览器（pygbag）里音频要等用户操作过一次才能解锁，所以不能只在启动时初始化一次，
    否则整局都是静音的。这里做惰性重试，最多每秒一次。
    """
    global _audio_retry_at
    if pygame.mixer.get_init():
        return True
    now = pygame.time.get_ticks() / 1000.0
    if now - _audio_retry_at < 1.0:
        return False
    _audio_retry_at = now
    return init_audio()


def play(name: str, volume: float = 0.5):
    """播放 assets/sounds 下的音效，缺失就静默跳过。"""
    if not pygame.mixer.get_init() and not _ensure_audio():
        return
    if name in _sound_cache:
        snd = _sound_cache[name]
    else:
        path = os.path.join(SOUND_DIR, name)
        if not os.path.exists(path):
            _sound_cache[name] = None
            return
        try:
            snd = pygame.mixer.Sound(path)
        except Exception:
            snd = None
        _sound_cache[name] = snd
    if snd:
        try:
            snd.set_volume(volume)
            snd.play()
        except Exception:
            pass
