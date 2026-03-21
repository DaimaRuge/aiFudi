#!/usr/bin/env python3
"""
个人终身学习数字读书系统 - 命令行启动脚本
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """检查依赖"""
    print("🔍 检查系统依赖...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # 检查必要的命令
    required_commands = ['pip']
    for cmd in required_commands:
        try:
            subprocess.run([cmd, '--version'], capture_output=True, check=True)
            print(f"✅ {cmd} 已安装")
        except:
            print(f"❌ {cmd} 未安装")
            return False
    
    return True

def install_dependencies():
    """安装依赖"""
    print("\n📦 安装Python依赖...")
    
    requirements_file = "backend/requirements.txt"
    if not os.path.exists(requirements_file):
        print(f"❌ 依赖文件不存在: {requirements_file}")
        return False
    
    try:
        # 使用pip安装
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", requirements_file],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ 依赖安装成功")
            return True
        else:
            print(f"❌ 依赖安装失败:\n{result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 安装过程出错: {e}")
        return False

def create_directories():
    """创建必要的目录"""
    print("\n📁 创建项目目录...")
    
    directories = [
        "uploads",
        "data",
        "chroma_data",
        "test_documents"
    ]
    
    for dir_name in directories:
        os.makedirs(dir_name, exist_ok=True)
        print(f"✅ 创建目录: {dir_name}")
    
    return True

def create_test_documents():
    """创建测试文档"""
    print("\n📝 创建测试文档...")
    
    test_dir = "test_documents"
    
    # 测试文档1：终身学习
    learning_doc = """# 终身学习的重要性

终身学习是指个人在一生中持续不断地学习和发展的过程。

## 核心价值
1. 提升个人竞争力
2. 适应快速变化的社会
3. 实现自我价值
4. 提高生活质量

## 学习方法
- 制定学习计划
- 利用现代技术
- 建立学习习惯
- 加入学习社区

终身学习不仅是个人发展的需要，也是社会进步的必然要求。"""
    
    # 测试文档2：AI教育
    ai_doc = """# AI在教育中的应用

人工智能正在深刻改变教育的面貌。

## AI教育应用
1. 个性化学习
2. 智能辅导系统
3. 自动评估和反馈
4. 学习分析

## 技术优势
- 提高教学效率
- 提供精准学习建议
- 打破地域限制
- 降低教育成本

## 未来趋势
- 多模态AI学习
- 情感计算
- 沉浸式学习体验
- 自适应学习系统

AI为终身学习提供了新的可能，我们需要积极拥抱这一变革。"""
    
    # 保存测试文档
    with open(os.path.join(test_dir, "终身学习.txt"), "w", encoding="utf-8") as f:
        f.write(learning_doc)
    
    with open(os.path.join(test_dir, "AI教育.txt"), "w", encoding="utf-8") as f:
        f.write(ai_doc)
    
    print("✅ 创建测试文档: 终身学习.txt")
    print("✅ 创建测试文档: AI教育.txt")
    
    return True

def start_backend():
    """启动后端服务"""
    print("\n🚀 启动后端服务...")
    
    try:
        # 在后台启动服务
        backend_process = subprocess.Popen(
            [sys.executable, "backend/simple_app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待服务启动
        print("⏳ 等待服务启动...")
        time.sleep(5)
        
        # 检查服务是否运行
        import requests
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ 后端服务启动成功")
                return backend_process
            else:
                print(f"❌ 后端服务响应异常: {response.status_code}")
                return None
        except:
            print("❌ 后端服务启动失败")
            return None
            
    except Exception as e:
        print(f"❌ 启动后端服务失败: {e}")
        return None

def open_browser():
    """打开浏览器"""
    print("\n🌐 打开浏览器...")
    
    urls = [
        "http://localhost:8000",  # API根目录
        "http://localhost:8000/docs",  # API文档
    ]
    
    for url in urls:
        try:
            webbrowser.open(url)
            print(f"✅ 打开: {url}")
            time.sleep(1)
        except:
            print(f"⚠️  无法打开: {url}")
    
    return True

def show_usage():
    """显示使用说明"""
    print("\n" + "="*60)
    print("个人终身学习数字读书系统 - 使用说明")
    print("="*60)
    print()
    print("📊 系统状态:")
    print("  • 后端API: http://localhost:8000")
    print("  • API文档: http://localhost:8000/docs")
    print()
    print("📝 核心功能:")
    print("  1. 上传文档 - POST /api/upload")
    print("  2. 列出文档 - GET /api/documents")
    print("  3. 搜索文档 - POST /api/search")
    print("  4. AI对话 - POST /api/chat")
    print("  5. 系统统计 - GET /api/stats")
    print()
    print("🔧 测试命令:")
    print("  # 上传测试文档")
    print('  curl -X POST -F "file=@test_documents/终身学习.txt" http://localhost:8000/api/upload')
    print()
    print("  # 搜索文档")
    print('  curl -X POST -H "Content-Type: application/json" -d \'{"query":"终身学习", "limit":5}\' http://localhost:8000/api/search')
    print()
    print("  # AI对话")
    print('  curl -X POST -H "Content-Type: application/json" -d \'{"message":"什么是终身学习？"}\' http://localhost:8000/api/chat')
    print()
    print("🛑 停止服务:")
    print("  按 Ctrl+C 停止服务")
    print()
    print("="*60)

def main():
    """主函数"""
    print("="*60)
    print("个人终身学习数字读书系统 - Python简化版")
    print("="*60)
    
    # 检查当前目录
    current_dir = Path(__file__).parent
    os.chdir(current_dir)
    print(f"📂 工作目录: {current_dir}")
    
    # 执行步骤
    steps = [
        ("检查依赖", check_dependencies),
        ("安装依赖", install_dependencies),
        ("创建目录", create_directories),
        ("创建测试文档", create_test_documents),
        ("启动服务", start_backend),
    ]
    
    backend_process = None
    
    for step_name, step_func in steps:
        print(f"\n▶️  步骤: {step_name}")
        result = step_func()
        
        if step_name == "启动服务":
            backend_process = result
        
        if not result:
            print(f"❌ {step_name} 失败")
            if backend_process:
                backend_process.terminate()
            sys.exit(1)
    
    # 打开浏览器
    open_browser()
    
    # 显示使用说明
    show_usage()
    
    try:
        # 保持运行
        print("\n🎯 系统运行中...")
        if backend_process:
            # 显示后端输出
            print("\n📋 后端日志:")
            for line in backend_process.stdout:
                if line:
                    print(f"  {line.strip()}")
                    
    except KeyboardInterrupt:
        print("\n\n🛑 收到停止信号")
    
    finally:
        # 清理
        print("\n🧹 清理资源...")
        if backend_process:
            backend_process.terminate()
            print("✅ 后端服务已停止")
        
        print("\n👋 再见！")

if __name__ == "__main__":
    main()