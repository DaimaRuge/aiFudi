#天一阁 GitHub 推送指南

## 快速推送到 GitHub

### 方法 1: 使用 GitHub Token (推荐)

```bash
# 设置环境变量
export GITHUB_TOKEN="your_github_personal_access_token"
export GITHUB_USERNAME="your_github_username"

# 运行自动推送脚本
python scripts/create_github_repo.py
```

### 方法 2: 手动推送

```bash
# 1. 在 GitHub 上创建仓库
# 访问 https://github.com/new
# 仓库名: skyone-shuge
# 描述:天一阁 - 智能个人数字文献管理平台
# 不要初始化 README (我们已有)

# 2. 推送代码
git remote add origin https://github.com/YOUR_USERNAME/skyone-shuge.git
git branch -M main
git push -u origin main
```

### 方法 3: 使用 SSH

```bash
# 1. 生成 SSH Key
ssh-keygen -t ed25519 -C "your_email@example.com"

# 2. 添加 SSH Key 到 GitHub
# 访问 https://github.com/settings/keys

# 3. 推送
git remote set-url origin git@github.com:YOUR_USERNAME/skyone-shuge.git
git push -u origin main
```

## 获取 GitHub Token

1. 访问: https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. Note: SkyOne Shuge
4. Scopes: 勾选 `repo` 和 `user`
5. 点击 "Generate token"
6. 复制 token

## 仓库信息

- **本地路径**: `/root/.openclaw/workspace/skyone-shuge`
- **文件数**: 109 个文件
- **提交数**: 1 个提交
- **状态**: 已提交，等待推送

## 推送后

```bash
# 查看提交历史
git log --oneline

# 查看状态
git status

# 查看远程
git remote -v
```

## 后续更新

```bash
# 提交更改
git add .
git commit -m "描述你的更改"
git push
```
