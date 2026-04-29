#!/bin/bash
# 安装 wechat 根目录共享依赖

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "📦 正在安装 wechat skill 共享依赖..."
cd "$SKILL_ROOT"
npm install
echo "✅ 依赖安装完成"
