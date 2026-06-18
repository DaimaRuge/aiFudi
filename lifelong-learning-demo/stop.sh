#!/bin/bash

# 个人终身学习数字读书系统 - 停止脚本

echo "========================================="
echo "  停止个人终身学习数字读书系统"
echo "========================================="
echo ""

# 停止服务
echo "🛑 停止服务..."
docker-compose down

echo ""
echo "✅ 服务已停止"
echo ""
echo "📁 数据保留在以下目录："
echo "  上传文件: ./backend/uploads/"
echo "  向量数据库: ./backend/chroma_db/"
echo ""
echo "⚠️  注意："
echo "  如需完全清理数据，请手动删除上述目录"
echo ""
echo "========================================="