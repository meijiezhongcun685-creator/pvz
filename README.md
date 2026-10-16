# 植物大战僵尸 · Pygame 版

复刻自开源项目 [371854496/pygame](https://github.com/371854496/pygame)（作者：楷楷，
教程地址 https://segmentfault.com/a/1190000019418065），在这个基础上重写成了模块化结构，
并补齐了原版没有的内容（开始界面、卡片栏、点击收集阳光、多种植物和僵尸、音效、关卡过渡、暂停/重开）。

## 运行

```bash
cd pvz
.venv/Scripts/python.exe main.py            # 正常玩（有窗口）
.venv/Scripts/python.exe main.py --level 1  # 从第 2 关开始
.venv/Scripts/python.exe main.py --mute     # 静音
```

开发辅助（不需要窗口）：

```bash
.venv/Scripts/python.exe scripts/debug_sim.py 130   # 快进一局并打印状态
.venv/Scripts/python.exe main.py --shots shots      # 自动挂机并截图
.venv/Scripts/python.exe scripts/render_scenes.py   # 单独渲染各个界面
.venv/Scripts/python.exe scripts/make_sounds.py     # 重新生成音效
```

## 操作

- 点卡片选中植物，再点空格子种下
- 点掉落的阳光收集（向日葵产的阳光也要手动收）
- `ESC` 暂停 / `R` 重开本关 / `M` 回主菜单 / 开始界面 `空格` 或点鼠标开始

## 目录结构

```
config.py          全局常量（窗口、网格、颜色、经济、胜负线）
levels.py          关卡与数值配置（植物价格血量、僵尸属性、每关波次）
assets.py          图片/字体/音效加载与缓存，缺图用占位图形兜底，手绘缺失素材
main.py            入口：初始化、固定步长主循环、场景切换、截图模式
core/grid.py       网格与像素坐标换算（像素↔格子、战场边界判断）
core/scene.py      场景基类 + 开始界面 / 过关过渡 / 游戏结束
entities/entity.py 实体基类（位置、血量、存活、update/draw、血条）
entities/plants.py 向日葵、豌豆射手、寒冰射手、坚果墙
entities/zombies.py 普通、路障、铁桶僵尸（含减速状态）
entities/projectile.py 豌豆 / 寒冰豌豆
entities/sun.py    掉落的阳光，点击收集
systems/spawner.py 僵尸波次生成（按关卡配置的时间表）
systems/collision.py 碰撞与伤害结算（僵尸啃植物、子弹打僵尸）
systems/economy.py 阳光收支、卡片冷却、战绩
systems/autoplay.py 自动挂机（截图、演示、以后做 AI 对战用）
ui/cards.py        卡片栏（价格、冷却遮罩、选中态）
ui/hud.py          顶部 HUD（阳光、卡片、关卡、击杀、波次）
scenes/play.py     游戏主场景：把上面这些串起来
scripts/           开发辅助脚本（音效生成、快进验证、界面渲染）
assets/imgs/       原项目的 7 张素材图
assets/sounds/     代码合成的音效
```

## 相比原教程版改了什么

1. 不再拿 `MainGame` 当全局变量用：状态收进 `PlayScene` / `Economy` / `Spawner`。
2. 计时全部改成"秒"（`dt`），不再用"数到第 25 帧"——原版帧计数器会随机器快慢变速度。
3. 严格分开三类东西：配置（levels/config）、逻辑（entities/systems）、表现（ui/scenes）。
4. 死亡只标 `alive=False`，循环结束后统一清理，不在遍历列表时 `remove`（原版的漏元素 bug）。
5. 坐标换算统一走 `core/grid.py`，并且明确区分 HUD 区和战场区，点 UI 不会种到地里。
6. 判断"同行"用行号而不是 `rect.y == rect.y`（原版换素材图高度差 1px 就失效）。
7. 子弹只管飞和标记命中，"加分/过关"由场景判定（原版写在子弹类里）。
8. 缺素材不崩：图片找不到会画占位图形，音效缺失就静音跑。
9. 补齐玩法：开始界面、卡片栏、点击收阳光、寒冰减速、坚果、路障/铁桶僵尸、波次提示、暂停、重开、音效、关卡过渡。

## 版权说明

`assets/imgs/` 下的图片来自上游开源仓库，角色形象版权属于 PvZ 原始权利人（PopCap/EA），
这里只用于学习演示。自己发布时建议换成自绘素材（坚果、寒冰射手、路障/铁桶、阳光、子弹已经是代码画的）。

## 网页版（在浏览器里玩，给面试官点开即玩）

浏览器里没有 Python，所以用 pygbag 把 Python + pygame 编译成 WebAssembly，
同一个游戏在浏览器里跑，桌面版代码一行没改（只多了一个 `web_main.py` 入口）。

```bash
.venv/Scripts/python.exe scripts/build_web.py    # 构建，产物在 webapp/build/web
.venv/Scripts/python.exe scripts/deploy_web.py   # 发布到 GitHub Pages 并打印网址
```

构建脚本会把游戏文件挑到一个干净的 `webapp/` 目录再编译——pygbag 会把所在目录整个打包，
不挑出去会把 `.venv` 一起塞进包里（它还会因为扫到 `.venv` 里的示例 wav 直接报错）。

本地看效果：

```bash
.venv/Scripts/python.exe -m http.server 8077 --directory webapp/build/web
# 然后浏览器打开 http://127.0.0.1:8077/
```

两个必踩的坑，记在这里省得再查：

1. **必须用 `127.0.0.1`，不能用 `localhost`。** pygbag 运行时有这么一段：
   `if (location.hostname === "localhost")` 时会走「本地开发服务器」分支，去 `localhost:8000`
   取 pygame 的 wheel——而那个端口只有 pygbag 自带的开发服务器才有。用 `localhost` 打开会
   永远停在 "Loading, please wait ..."。
2. **首次打开要下约 11MB**（浏览器版 CPython ~9.5MB + pygame-ce 1.5MB），
   国内直连约几十到两百 KB/s，第一次要等 1~3 分钟；之后浏览器有缓存就快了。

中文字体：浏览器里没有微软雅黑，所以 `scripts/make_font.py` 从系统里的 Noto Sans SC
（SIL OFL 授权，允许再分发）抽出游戏用到的 680 个字，生成 `assets/fonts/NotoSansSC.ttf`（332 KB）。
桌面版仍然优先用微软雅黑，行为没变。

