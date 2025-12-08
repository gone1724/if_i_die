> 🌱 如果有一天你不在了，你希望你的博客会怎样？我走后，我在互联网上留下的东西会怎样？
> 这是一个关于纪念、延续、与被看见的问题。

## 这是什么

- 一个用 uv 管理的 Python 小工具，用 wget 把  博客 抓成可直接部署的静态站点，欢迎fork。
- 典型用法：
  - 把 Typecho 网站静态页面部分爬虫，其他网站自行测试。
  - 只抓公开页面（文章、分页、分类、归档、作者页、主题资源等），排除后台、登录、feed。
  - 输出目录为 `./site/`，可以直接推送到 Cloudflare Pages / GitHub Pages。
- 本项目压力 AI 10分钟完成，保持简单、可读、可改。

## 使用指南

* 环境：Python 3.9+。
* 推荐安装和使用 uv

```bash
pip install uv
```

* 运行：如果装了 uv，直接 `uv run python mirror.py`，否则 `python mirror.py`。
* 清理输出（默认清空）：

```bash
python mirror.py                  # 清空后抓取
python mirror.py --no-clean       # 不清空抓取
```

* 试跑（只检查不下载）：

```bash
python mirror.py --spider
```

* 自定义目标站点和输出目录，用于抓取其他博客：

```bash
python mirror.py --url https://example.com/ --output-dir my_site
```

## 其他

wget 选择：Windows 优先使用仓库内 `tools/mingw64/bin/wget.exe`；其他系统优先系统 wget，找不到再用仓库内的。

- 本项目包含 wget.exe（GNU Wget，GPLv3 许可证） This project includes wget.exe (GNU Wget, GPLv3).
- 源代码可在以下地址获取 Source code available at: https://ftp.gnu.org/gnu/wget/
