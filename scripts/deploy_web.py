"""把网页版发布到 GitHub Pages，得到一个能直接发给别人点开玩的网址。

前提：
1. 已经跑过 scripts/build_web.py，webapp/build/web 里是最新产物；
2. 本机 gh 已登录（gh auth status 能看到账号）。

它做三件事：
1. 在 GitHub 上建一个公开仓库（默认 pvz-web，已存在就复用）；
2. 把产物推到 gh-pages 分支；
3. 打开 Pages 服务，最后打印网址。

网址形如：https://<你的用户名>.github.io/pvz-web/

用法：
    python scripts/deploy_web.py                    # 用默认仓库名 pvz-web
    python scripts/deploy_web.py --repo pvz-demo    # 换个仓库名
    python scripts/deploy_web.py --dry-run          # 只看要执行什么，不动 GitHub
"""

import argparse
import os
import shutil
import subprocess
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(BASE, "webapp", "build", "web")
STAGE = os.path.join(BASE, "webapp", "deploy")
GH = shutil.which("gh") or r"C:\Users\EDY\AppData\Local\Programs\gh\bin\gh.exe"

# gh 访问 api.github.com 需要代理（本机 PAC 代理下 gh 不认，得显式给 HTTPS_PROXY）
ENV = dict(os.environ)
ENV.setdefault("HTTPS_PROXY", "socks5://127.0.0.1:1081")
ENV.setdefault("HTTP_PROXY", "socks5://127.0.0.1:1081")


def run(cmd, cwd=None, check=True):
    print("  $", " ".join(cmd))
    r = subprocess.run(cmd, cwd=cwd, env=ENV, capture_output=True, text=True)
    out = (r.stdout or "").strip()
    err = (r.stderr or "").strip()
    if out:
        print("   ", out[:800])
    if err and r.returncode != 0:
        print("   !", err[:800])
    if check and r.returncode != 0:
        raise SystemExit(f"命令失败：{cmd[0]}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="pvz-web", help="GitHub 仓库名")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(os.path.join(WEB, "index.html")):
        print("先跑 scripts/build_web.py 生成产物")
        return 1

    who = run([GH, "api", "user", "--jq", ".login"], check=False)
    if not who:
        print("gh 还没登录，先执行：gh auth login")
        return 1
    user = who.strip().splitlines()[-1]
    print(f"账号：{user}   仓库：{user}/{args.repo}")

    if args.dry_run:
        print("（dry-run，不实际执行）")
        return 0

    # 1) 仓库不存在就建（公开仓库才能免费用 Pages）
    run([GH, "repo", "view", f"{user}/{args.repo}"], check=False)
    if not run([GH, "repo", "view", f"{user}/{args.repo}", "--json", "name", "--jq", ".name"], check=False):
        run([GH, "repo", "create", args.repo, "--public",
             "--description", "植物大战僵尸 · pygame 网页版（pygbag/WebAssembly）"])
    else:
        print("  仓库已存在，直接更新")

    # 2) 把产物拷到一个干净目录，独立初始化 git，推到 gh-pages 分支
    if os.path.isdir(STAGE):
        shutil.rmtree(STAGE)
    shutil.copytree(WEB, STAGE)
    shutil.rmtree(os.path.join(STAGE, "web-cache"), ignore_errors=True)   # 构建缓存不用上传
    # 404 兜底 + 说明，防止有人直接访问子路径时看到 GitHub 的默认 404
    with open(os.path.join(STAGE, ".nojekyll"), "w") as f:
        f.write("")

    run(["git", "init", "-q", "-b", "gh-pages"], cwd=STAGE)
    run(["git", "config", "user.email", "deploy@example.com"], cwd=STAGE)
    run(["git", "config", "user.name", "deploy"], cwd=STAGE)
    run(["git", "add", "-A"], cwd=STAGE)
    run(["git", "commit", "-q", "-m", "deploy web build"], cwd=STAGE)
    remote_url = f"https://github.com/{user}/{args.repo}.git"
    # 这台机器上 git 走 github 需要 repo 级代理设置
    run(["git", "remote", "add", "origin", remote_url], cwd=STAGE)
    run(["git", "config", "http.https://github.com/.proxy", "socks5://127.0.0.1:1081"], cwd=STAGE)
    run(["git", "push", "-f", "origin", "gh-pages"], cwd=STAGE)

    # 3) 打开 Pages（用 gh-pages 分支根目录）
    run([GH, "api", "-X", "POST", f"repos/{user}/{args.repo}/pages",
         "-f", "source[branch]=gh-pages", "-f", "source[path]=/"], check=False)
    time.sleep(5)
    site = run([GH, "api", f"repos/{user}/{args.repo}/pages", "--jq", ".html_url"], check=False)

    url = site.strip().splitlines()[-1] if site else f"https://{user}.github.io/{args.repo}/"
    print("\n发布完成，网址：", url)
    print("第一次打开要等 Pages 构建完成（通常 1 分钟内），页面本身还要下载 ~11MB 的浏览器版 Python。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
