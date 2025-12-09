#!/bin/bash
set -e

# 1. 到仓库目录
cd "$(dirname "$0")"

# 2. 确保是最新代码（可选）
git pull --rebase || true

# 3. 运行镜像脚本
uv run python mirror.py

# 4. 把新生成的内容加入 git
git add .

# 5. 提交（如果没有变更就跳过）
if ! git diff --cached --quiet; then
  git commit -m "chore: daily mirror $(date -Iseconds)"
  git push origin master
fi
