#!/usr/bin/env python3
"""
天一阁 - GitHub 仓库创建工具

自动创建 GitHub 仓库并推送代码

用法:
    python scripts/create_github_repo.py

环境变量:
    GITHUB_TOKEN: GitHub Personal Access Token
    GITHUB_USERNAME: GitHub 用户名
    REPO_NAME: 仓库名 (默认: skyone-shuge)
"""

import os
import sys
import subprocess
import requests
import time

# 配置
REPO_NAME = os.environ.get("REPO_NAME", "skyone-shuge")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME", "")

PROJECT_DIR = "/root/.openclaw/workspace/skyone-shuge"
README_CONTENT = """# SkyOne Shuge (天一阁)

智能个人数字文献管理平台

## 功能特性

- 📄 **文档管理** - 支持 PDF、DOCX、PPTX、XLSX、Markdown 等格式
- 🤖 **AI 自动分类** - 基于 GPT-4/Claude 的智能分类
- 🔍 **语义搜索** - 支持关键词和向量语义搜索
- 🏷️ **智能标签** - 自动标签和手动标签
- 👤 **用户认证** - JWT Token 认证
- 📱 **跨平台** - Web API + CLI

## 快速开始

```bash
# 克隆
git clone https://github.com/{username}/skyone-shugeone-shuge

.git
cd sky# 安装依赖
pip install -e .

# 启动服务
uvicorn skyone_shuge.api.main:app --reload
```

## 项目结构

```
skyone_shuge/
├── api/              # FastAPI 应用
├── core/             # 配置和数据库
├── models/           # 数据模型
├── services/         # 业务逻辑
└── utils/            # 工具函数
```

## 许可证

MIT
"""


def run_command(cmd, cwd=None):
    """运行命令"""
    print(f"🔄 执行: {cmd}")
    result = subprocess.run(
        cmd, shell=True, cwd=cwd,
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"❌ 错误: {result.stderr}")
        return False, result.stderr
    print(f"✅ 成功")
    return True, result.stdout


def check_git_status():
    """检查 Git 状态"""
    print("\n📊 检查 Git 状态...")
    
    # 检查是否初始化
    if not os.path.exists(os.path.join(PROJECT_DIR, ".git")):
        print("📦 初始化 Git 仓库...")
        run_command("git init", cwd=PROJECT_DIR)
        run_command('git config user.name "AI Assistant"', cwd=PROJECT_DIR)
        run_command('git config user.email "assistant@skyoneshuge.com"', cwd=PROJECT_DIR)
    
    # 检查远程
    result = run_command("git remote -v", cwd=PROJECT_DIR)
    if "origin" in result[1]:
        print("✓ 远程仓库已配置")
        return True
    
    return False


def create_github_repo():
    """创建 GitHub 仓库"""
    global GITHUB_USERNAME
    
    if not GITHUB_TOKEN:
        print("❌ 错误: 请设置 GITHUB_TOKEN 环境变量")
        print("\n📝 获取 Token 方法:")
        print("1. 访问 https://github.com/settings/tokens")
        print("2. 点击 'Generate new token (classic)'")
        print("3. 选择 scopes: repo, user")
        print("4. 复制 token")
        return False
    
    if not GITHUB_USERNAME:
        # 尝试从 GitHub API 获取用户名
        print("🔍 尝试获取用户名...")
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        resp = requests.get("https://api.github.com/user", headers=headers)
        
        if resp.status_code == 200:
            GITHUB_USERNAME = resp.json()["login"]
            print(f"✓ 用户名: {GITHUB_USERNAME}")
        else:
            print("❌ 错误: 无法获取用户名，请设置 GITHUB_USERNAME")
            return False
    
    # 创建仓库
    print(f"\n🚀 创建仓库: {GITHUB_USERNAME}/{REPO_NAME}")
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "name": REPO_NAME,
        "description": "天一阁 - 智能个人数字文献管理平台",
        "private": False,
        "auto_init": False
    }
    
    resp = requests.post(
        "https://api.github.com/user/repos",
        headers=headers,
        json=data
    )
    
    if resp.status_code == 201:
        print(f"✓ 仓库创建成功!")
        return True
    elif resp.status_code == 422:  # 已存在
        print(f"⚠️ 仓库已存在: {GITHUB_USERNAME}/{REPO_NAME}")
        return True
    else:
        print(f"❌ 错误: {resp.json().get('message', '未知错误')}")
        return False


def push_to_github():
    """推送到 GitHub"""
    print("\n📤 推送代码到 GitHub...")
    
    # 添加远程
    run_command(
        f"git remote add origin https://github.com/{GITHUB_USERNAME}/{REPO_NAME}.git",
        cwd=PROJECT_DIR
    )
    
    # 创建 README
    readme_path = os.path.join(PROJECT_DIR, "README.md")
    if not os.path.exists(readme_path):
        with open(readme_path, "w") as f:
            f.write(README_CONTENT.format(username=GITHUB_USERNAME))
        print("✓ README.md 已创建")
    
    # 添加文件
    print("📦 添加文件...")
    run_command("git add .", cwd=PROJECT_DIR)
    
    # 提交
    run_command('git commit -m "Initial commit: SkyOne Shuge v1.0"', cwd=PROJECT_DIR)
    
    # 推送
    print("🚀 推送到 GitHub...")
    success, output = run_command(
        f"git push -u origin main",
        cwd=PROJECT_DIR
    )
    
    return success


def main():
    """主函数"""
    print("=" * 50)
    print("🌟 SkyOne Shuge - GitHub 部署工具")
    print("=" * 50)
    
    # 检查
    has_remote = check_git_status()
    
    if not has_remote:
        # 创建仓库
        if not create_github_repo():
            return
        
        # 推送
        if not push_to_github():
            print("\n❌ 推送失败，请手动解决冲突后重试")
            return
    
    print("\n" + "=" * 50)
    print("🎉 完成!")
    print(f"📝 仓库地址: https://github.com/{GITHUB_USERNAME}/{REPO_NAME}")
    print("=" * 50)


if __name__ == "__main__":
    main()
