#!/bin/bash
# 安装 markdown-to-wechat-html skill 所需的依赖

echo "📦 正在安装依赖..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查是否已安装
if [ -d "node_modules" ]; then
    echo "✅ 依赖已安装"
    exit 0
fi

# 初始化 package.json（如果不存在）
if [ ! -f "package.json" ]; then
    npm init -y
fi

# 安装依赖
npm install marked sanitize-html highlight.js

echo "✅ 依赖安装完成"
echo ""
echo "已安装："
echo "  - marked: Markdown 解析器"
echo "  - sanitize-html: HTML 安全过滤"
echo "  - highlight.js: 代码语法高亮"
