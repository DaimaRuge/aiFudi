#!/usr/bin/env python3
"""
API测试脚本
"""

import requests
import json
import time
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ 健康检查成功: {response.json()}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

def test_upload_document(file_path):
    """测试上传文档"""
    print(f"\n📤 测试上传文档: {file_path}")
    
    if not Path(file_path).exists():
        print(f"❌ 文件不存在: {file_path}")
        return None
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f)}
            response = requests.post(f"{BASE_URL}/api/upload", files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 上传成功: {result}")
            return result.get('document_id')
        else:
            print(f"❌ 上传失败: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 上传异常: {e}")
        return None

def test_list_documents():
    """测试列出文档"""
    print("\n📋 测试列出文档...")
    try:
        response = requests.get(f"{BASE_URL}/api/documents", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 列出文档成功: 共 {result['total']} 个文档")
            for doc in result['documents']:
                print(f"  • {doc['title']} ({doc['type']}) - {doc['status']}")
            return True
        else:
            print(f"❌ 列出文档失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 列出文档异常: {e}")
        return False

def test_search(query, limit=5):
    """测试搜索"""
    print(f"\n🔍 测试搜索: '{query}'")
    try:
        data = {"query": query, "limit": limit}
        response = requests.post(
            f"{BASE_URL}/api/search",
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 搜索成功: 找到 {result['total']} 个结果")
            for i, item in enumerate(result['results'][:3], 1):
                print(f"  结果 {i}:")
                print(f"    标题: {item.get('title', '未知')}")
                print(f"    相似度: {item.get('score', 0):.2%}")
                print(f"    内容: {item.get('text', '')[:100]}...")
            return True
        else:
            print(f"❌ 搜索失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 搜索异常: {e}")
        return False

def test_chat(message):
    """测试AI对话"""
    print(f"\n💬 测试AI对话: '{message}'")
    try:
        data = {"message": message}
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=data,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ AI对话成功:")
            print(f"  回答: {result['response'][:200]}...")
            
            if result.get('sources'):
                print(f"  来源: {len(result['sources'])} 个")
                for i, source in enumerate(result['sources'][:2], 1):
                    print(f"    来源 {i}: {source.get('title', '未知')} ({source.get('score', 0):.2%})")
            return True
        else:
            print(f"❌ AI对话失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ AI对话异常: {e}")
        return False

def test_stats():
    """测试系统统计"""
    print("\n📊 测试系统统计...")
    try:
        response = requests.get(f"{BASE_URL}/api/stats", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 系统统计:")
            print(f"  文档数量: {result.get('documents', 0)}")
            print(f"  分块总数: {result.get('total_chunks', 0)}")
            print(f"  向量存储: {result.get('vector_store', {}).get('total_chunks', 0)} 个分块")
            return True
        else:
            print(f"❌ 系统统计失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 系统统计异常: {e}")
        return False

def test_document_detail(doc_id):
    """测试文档详情"""
    print(f"\n📄 测试文档详情: {doc_id}")
    try:
        response = requests.get(f"{BASE_URL}/api/documents/{doc_id}", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 文档详情:")
            print(f"  标题: {result.get('title', '未知')}")
            print(f"  类型: {result.get('type', '未知')}")
            print(f"  状态: {result.get('status', '未知')}")
            print(f"  分块数: {result.get('chunks_count', 0)}")
            print(f"  内容预览: {result.get('content_preview', '')[:100]}...")
            return True
        else:
            print(f"❌ 文档详情失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 文档详情异常: {e}")
        return False

def main():
    """主测试函数"""
    print("="*60)
    print("个人终身学习数字读书系统 - API测试")
    print("="*60)
    
    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(3)
    
    # 执行测试
    tests = [
        ("健康检查", lambda: test_health()),
    ]
    
    # 上传测试文档
    test_files = [
        "test_documents/终身学习.txt",
        "test_documents/AI教育.txt"
    ]
    
    uploaded_docs = []
    
    for test_file in test_files:
        if Path(test_file).exists():
            doc_id = test_upload_document(test_file)
            if doc_id:
                uploaded_docs.append(doc_id)
                time.sleep(2)  # 等待处理
    
    if uploaded_docs:
        # 添加更多测试
        tests.extend([
            ("列出文档", lambda: test_list_documents()),
            ("搜索测试1", lambda: test_search("终身学习")),
            ("搜索测试2", lambda: test_search("AI教育")),
            ("AI对话测试1", lambda: test_chat("什么是终身学习？")),
            ("AI对话测试2", lambda: test_chat("AI在教育中有什么应用？")),
            ("系统统计", lambda: test_stats()),
        ])
        
        # 测试第一个文档的详情
        if uploaded_docs:
            tests.append(("文档详情", lambda: test_document_detail(uploaded_docs[0])))
    
    # 执行所有测试
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n▶️  测试: {test_name}")
        if test_func():
            passed += 1
    
    # 显示结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    print(f"✅ 通过: {passed}/{total}")
    print(f"📊 成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统运行正常。")
    else:
        print(f"\n⚠️  有 {total-passed} 个测试失败，请检查系统状态。")
    
    print("\n📋 可用API端点:")
    print(f"  • 健康检查: GET {BASE_URL}/health")
    print(f"  • 上传文档: POST {BASE_URL}/api/upload")
    print(f"  • 列出文档: GET {BASE_URL}/api/documents")
    print(f"  • 搜索文档: POST {BASE_URL}/api/search")
    print(f"  • AI对话: POST {BASE_URL}/api/chat")
    print(f"  • 系统统计: GET {BASE_URL}/api/stats")
    print(f"  • 文档详情: GET {BASE_URL}/api/documents/{{id}}")
    
    print("\n🔧 手动测试命令示例:")
    print('  # 上传文档')
    print('  curl -X POST -F "file=@test_documents/终身学习.txt" http://localhost:8000/api/upload')
    print()
    print('  # AI对话')
    print('  curl -X POST -H "Content-Type: application/json" \\')
    print('    -d \'{"message":"什么是终身学习？"}\' \\')
    print('    http://localhost:8000/api/chat')
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)