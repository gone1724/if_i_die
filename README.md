# 博客镜像器(自用)

> 🌱 如果有一天我不在了，我的博客会怎样？在互联网上留下的东西会怎样？

## 这是什么

- 一个用 uv 管理的 Python 小工具，用 wget 把  博客 抓成可直接部署的静态站点。
- 典型用法：把 Typecho 网站静态页面部分爬虫，其他网站自行测试。
  - 只抓公开页面（文章、分页、分类、归档、作者页、主题资源等），排除后台登录、新增评论等功能。
  - 输出目录为 `./site/`，可以直接推送到 Cloudflare Pages / GitHub Pages。
  - 抓取后会**重写所有站内链接为本地相对路径**，确保离线可用。
  - 针对 `img src`的**图片类资源**也会保存并重写相对链接，确保离线可用。
- 本项目由 AI 10分钟完成，又压力 AI 改细节。

## 使用指南

* 环境：Python 3.13 (uv虚拟环境)。
* 推荐安装和使用 uv 管理 Python 项目工程

```bash
pip install uv
uv run python mirror.py
```

* 清理输出（默认清空）：

```bash
uv run python mirror.py                  # 清空后抓取
uv run python mirror.py --no-clean       # 不清空抓取
```

* 试跑（只检查不下载）：

```bash
uv run python mirror.py --spider
```

* 自定义目标站点和输出目录，用于抓取其他博客：

```bash
uv run python mirror.py --url https://example.com/ --output-dir my_site
```

## 自动任务

可以参考`run_mirror.sh`，将本项目部署在服务器上，以实现自动任务。

## 许可证 | License

- 本项目遵循 GNU GPL v3.0 许可证，您可以按许可证条款复制、分发和修改本项目。 This project is licensed under the GNU GPL v3.0; you may copy, distribute, and modify it under the terms of that license.
- wget 选择：Windows 优先使用仓库内 `tools/mingw64/bin/wget.exe`；其他系统优先系统 wget，找不到再用仓库内的。

  - 本项目包含 wget.exe（GNU Wget，GPLv3 许可证） This project includes wget.exe (GNU Wget, GPLv3).
  - 源代码可在以下地址获取 Source code available at: [https://ftp.gnu.org/gnu/wget/](https://ftp.gnu.org/gnu/wget/)
