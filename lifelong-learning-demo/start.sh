#!/bin/bash

# 个人终身学习数字读书系统 - 启动脚本

set -e

echo "========================================="
echo "  个人终身学习数字读书系统 - MVP演示版"
echo "========================================="
echo ""

# 检查Docker和Docker Compose
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: Docker未安装"
    echo "请先安装Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误: Docker Compose未安装"
    echo "请先安装Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker和Docker Compose已安装"

# 检查环境变量
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "⚠️  警告: DEEPSEEK_API_KEY环境变量未设置"
    echo "将使用模拟AI服务，如需真实AI对话请设置："
    echo "export DEEPSEEK_API_KEY=your_api_key_here"
    echo ""
    read -p "是否继续使用模拟AI服务？(y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "请设置API密钥后重新运行"
        exit 1
    fi
else
    echo "✅ DeepSeek API密钥已设置"
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p backend/uploads backend/chroma_db

# 构建和启动服务
echo "🚀 启动服务..."
docker-compose up --build -d

echo ""
echo "✅ 服务启动成功！"
echo ""
echo "📊 服务访问地址："
echo "  前端界面: http://localhost:8501"
echo "  后端API:  http://localhost:8000"
echo "  API文档:  http://localhost:8000/docs"
echo ""
echo "🔧 管理命令："
echo "  查看日志: docker-compose logs -f"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart"
echo ""
echo "📝 使用说明："
echo "  1. 打开浏览器访问 http://localhost:8501"
echo "  2. 在'文档管理'标签页上传PDF/DOCX/TXT文件"
echo "  3. 在'知识检索'标签页搜索文档内容"
echo "  4. 在'AI对话'标签页与AI助手交流"
echo ""
echo "========================================="