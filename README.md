# if_i_die

🌱 如果有一天你不在了，你希望你的博客会怎样？
很多人都会突然想到这个问题：“我走后，我在互联网上留下的东西会怎样？”
这是一个关于纪念、延续、与被看见的问题。

## 这是什么

- 一个用 uv 管理的 Python 小工具，用 wget 把 https://blog.sixhz.top/ 抓成可直接部署的静态站点。
- 只抓公开页面（文章、分页、分类、归档、作者页、主题资源等），排除后台、登录、feed。
- 输出目录为 `site/`，可以直接推送到 Cloudflare Pages / GitHub Pages。

## 怎么用

- 环境：Python 3.9+；如果装了 uv，直接 `uv run python mirror.py`，否则 `python mirror.py`。
- 清理输出：默认会清空 `site/` 后再抓取，如需保留旧文件加 `--no-clean`。
- 试跑：只检查链接不下载，加 `--spider`。
- 自定义：`--url` 改起始站点，`--output-dir` 改输出目录。
- wget 选择：Windows 优先使用仓库内 `tools/mingw64/bin/wget.exe`；其他系统优先系统 wget，找不到再用仓库内的。
