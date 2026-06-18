#!/usr/bin/env python3
"""
快速演示脚本 - 不依赖完整服务，直接展示核心功能
"""

import os
import sys
import json
import time
from pathlib import Path

def print_header(title):
    """打印标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def demo_document_parser():
    """演示文档解析"""
    print_header("📄 文档解析演示")
    
    # 创建测试文档
    test_text = """# 终身学习系统演示

这是一个演示文档，用于展示文档解析功能。

## 核心功能
1. 文档上传和解析
2. 文本向量化
3. 语义搜索
4. AI对话

## 技术特点
- 本地运行，无需外部服务
- 轻量级设计
- 易于扩展

文档解析功能可以处理多种格式，包括PDF、DOCX、TXT和Markdown。
"""
    
    # 模拟解析
    print("✅ 创建测试文档")
    print(f"📝 文档内容（前150字符）:")
    print(f"  {test_text[:150]}...")
    
    # 模拟分块
    print("\n📑 文档分块:")
    chunks = [test_text[i:i+200] for i in range(0, len(test_text), 200)]
    for i, chunk in enumerate(chunks, 1):
        print(f"  分块 {i}: {chunk[:50]}...")
    
    print(f"\n✅ 文档解析完成，生成 {len(chunks)} 个分块")
    return chunks

def demo_vector_search():
    """演示向量搜索"""
    print_header("🔍 向量搜索演示")
    
    # 模拟文档库
    documents = [
        {"title": "终身学习系统", "content": "基于大模型的个人知识管理系统", "type": "系统"},
        {"title": "AI教育应用", "content": "人工智能在教育领域的应用", "type": "AI"},
        {"title": "知识图谱", "content": "使用图数据库表示知识关系", "type": "数据库"},
        {"title": "语义搜索", "content": "基于含义而非关键词的搜索技术", "type": "搜索"},
        {"title": "向量数据库", "content": "存储和检索高维向量的数据库系统", "type": "数据库"}
    ]
    
    # 显示文档库
    print("📚 文档库:")
    for doc in documents:
        print(f"  • {doc['title']} ({doc['type']})")
    
    # 模拟搜索
    query = "数据库"
    print(f"\n🔍 搜索: '{query}'")
    
    # 简单匹配
    results = []
    for doc in documents:
        if query.lower() in doc['content'].lower() or query.lower() in doc['title'].lower():
            score = 0.8 if query.lower() in doc['title'].lower() else 0.5
            results.append({**doc, "score": score})
    
    # 按分数排序
    results.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"\n✅ 搜索结果（按相似度排序）:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result['title']} (相似度: {result['score']:.2%})")
        print(f"     内容: {result['content']}")
    
    return results

def demo_ai_conversation():
    """演示AI对话"""
    print_header("💬 AI对话演示")
    
    # 模拟对话历史
    conversation = [
        {"role": "系统", "content": "你是一个知识渊博的AI助手，专门回答关于学习系统的问题。"}
    ]
    
    # 模拟对话
    questions = [
        "什么是终身学习系统？",
        "它有什么核心功能？",
        "如何使用它？"
    ]
    
    answers = [
        "终身学习系统是一个基于大模型的个人知识管理系统，帮助用户管理、检索和学习知识。",
        "核心功能包括：文档上传解析、文本向量化、语义搜索和AI对话。",
        "使用步骤：1. 上传文档 2. 等待解析 3. 搜索知识 4. AI对话。"
    ]
    
    print("🗣️ 模拟对话:")
    for i, (question, answer) in enumerate(zip(questions, answers), 1):
        print(f"\n  👤 用户: {question}")
        time.sleep(0.5)
        print(f"  🤖 AI: {answer}")
        conversation.append({"role": "用户", "content": question})
        conversation.append({"role": "AI", "content": answer})
    
    print(f"\n✅ 对话演示完成，共 {len(questions)} 轮对话")
    return conversation

def demo_system_architecture():
    """演示系统架构"""
    print_header("🏗️ 系统架构")
    
    architecture = """
┌─────────────────────────────────────────────────────────┐
│                    用户界面层                            │
│  • 文件上传 • 文档列表 • 搜索界面 • 对话界面          │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                   API服务层 (FastAPI)                   │
│  • 文档管理API • 搜索API • 对话API • 系统API        │
└──────────────────────┬──────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
┌──────▼──────┐  ┌───▼────┐  ┌────▼─────┐
│ 文档解析器  │  │向量存储│  │ AI服务   │
│ • PDF/DOCX  │  │ChromaDB│  │DeepSeek  │
│ • TXT/MD    │  │BGE模型 │  │模拟服务  │
└─────────────┘  └────────┘  └──────────┘
       │               │               │
       └───────────────┼───────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                   数据存储层                            │
│  • 文件系统 • JSON数据 • 向量数据库                    │
└─────────────────────────────────────────────────────────┘
    """
    
    print(architecture)
    
    print("📋 技术栈:")
    tech_stack = [
        ("Web框架", "FastAPI"),
        ("向量数据库", "ChromaDB"),
        ("Embedding模型", "BGE-small-zh"),
        ("AI服务", "DeepSeek API (可选)"),
        ("文档解析", "PyPDF2 + python-docx"),
        ("编程语言", "Python 3.8+")
    ]
    
    for tech, name in tech_stack:
        print(f"  • {tech}: {name}")

def demo_project_structure():
    """演示项目结构"""
    print_header("📁 项目结构")
    
    structure = """
lifelong-learning-python/
├── backend/
│   ├── simple_app.py      # 主应用（一个文件包含所有功能）
│   └── requirements.txt   # Python依赖
├── test_documents/        # 测试文档
│   ├── 终身学习.txt
│   └── AI教育.txt
├── uploads/              # 上传文件存储
├── data/                 # 文档数据存储
├── chroma_data/         # 向量数据库存储
├── demo.py              # 演示脚本（本文件）
├── run.py               # 一键启动脚本
├── test_api.py          # API测试脚本
├── README.md            # 完整使用文档
└── LICENSE              # 许可证文件
    """
    
    print(structure)
    
    print("📊 核心文件说明:")
    files = [
        ("backend/simple_app.py", "主应用，包含所有功能（文档解析、向量存储、AI服务）"),
        ("run.py", "一键启动脚本，自动安装依赖并启动服务"),
        ("test_api.py", "API测试脚本，完整测试所有功能"),
        ("README.md", "详细的使用文档和开发指南")
    ]
    
    for filename, desc in files:
        print(f"  • {filename}:")
        print(f"    {desc}")

def main():
    """主演示函数"""
    print("="*60)
    print("  个人终身学习数字读书系统 - 快速演示")
    print("="*60)
    print("\n📋 这是一个快速演示，展示系统的核心功能，")
    print("   无需启动完整服务即可体验。")
    
    # 演示项目结构
    demo_project_structure()
    
    # 演示系统架构
    demo_system_architecture()
    
    # 演示文档解析
    demo_document_parser()
    
    # 演示向量搜索
    demo_vector_search()
    
    # 演示AI对话
    demo_ai_conversation()
    
    # 总结
    print_header("🎯 演示总结")
    
    print("✅ 核心功能展示完成！")
    print("\n🚀 下一步操作:")
    print("  1. 运行 'python run.py' 启动完整服务")
    print("  2. 运行 'python test_api.py' 测试API功能")
    print("  3. 阅读 'README.md' 了解详细使用")
    print("\n📊 服务访问:")
    print("  • API地址: http://localhost:8000")
    print("  • API文档: http://localhost:8000/docs")
    print("\n" + "="*60)
    
    # 询问是否启动服务
    print("\n❓ 是否启动完整服务？")
    print("   (这将安装依赖并启动后端)")
    
    try:
        choice = input("\n启动服务？(y/n): ").strip().lower()
        if choice == 'y':
            print("\n🚀 启动服务...")
            print("请运行: python run.py")
            print("或直接访问: http://localhost:8000")
    except KeyboardInterrupt:
        print("\n\n👋 演示结束，再见！")

if __name__ == "__main__":
    main()