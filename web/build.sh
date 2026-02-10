#!/bin/bash
# Tailwind CSS 构建脚本

# 检查 Tailwind CLI 是否存在
if [ ! -f "tailwindcss" ]; then
    echo "❌ Tailwind CLI 不存在"
    echo "请从以下地址下载 Tailwind CLI standalone 可执行文件:"
    echo "https://github.com/tailwindlabs/tailwindcss/releases"
    echo ""
    echo "下载后放到 web/ 目录，并重命名为 tailwindcss"
    echo "Linux/Mac: chmod +x tailwindcss"
    exit 1
fi

echo "🔨 构建 Tailwind CSS..."

# 开发模式 - 监听文件变化
if [ "$1" == "--watch" ]; then
    echo "📺 监听模式..."
    ./tailwindcss -i src/input.css -o static/style.css --watch
else
    # 生产构建 - 最小化
    echo "📦 生产构建（最小化）..."
    ./tailwindcss -i src/input.css -o static/style.css --minify
    echo "✓ 构建完成: static/style.css"
fi
