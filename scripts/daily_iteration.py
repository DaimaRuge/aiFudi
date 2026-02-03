#!/usr/bin/env python3
"""
SkyOne Shuge - 每日迭代自动化脚本
自动更新 PRD、架构文档，并发送邮件通知
"""

import os
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# 配置
PROJECT_ROOT = Path("/root/.openclaw/workspace/skyone-shuge")
PRD_DIR = PROJECT_ROOT / "prd"
ARCH_DIR = PROJECT_ROOT / "architecture"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
VERSION_FILE = PROJECT_ROOT / "VERSION.txt"
ITERATION_LOG = PROJECT_ROOT / "iteration_log.md"

# 获取当前版本
def get_current_version() -> str:
    if VERSION_FILE.exists():
        return VERSION_FILE.read_text().strip()
    return "0.1"

# 增加版本号
def bump_version(current: str) -> str:
    parts = current.split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    return ".".join(parts)

# 更新迭代日志
def update_iteration_log(new_version: str, changes: list):
    log_entry = f"""
## v{new_version} ({datetime.now().strftime('%Y-%m-%d')})
**更新内容**:
"""
    for change in changes:
        log_entry += f"- {change}\n"
    
    log_entry += f"\n**更新人**: AI Assistant\n"
    log_entry += f"---\n"
    
    if ITERATION_LOG.exists():
        content = ITERATION_LOG.read_text()
    else:
        content = "# 迭代日志\n\n"
    
    ITERATION_LOG.write_text(content + log_entry)

# 备份上一版本
def backup_version(version: str):
    backup_dir = PROJECT_ROOT / "backups" / f"v{version}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # 备份 PRD
    prd_file = PRD_DIR / f"PRODUCT_SPECIFICATION_v{version}.md"
    if prd_file.exists():
        subprocess.run(["cp", str(prd_file), str(backup_dir / prd_file.name)])
    
    # 备份架构
    arch_file = ARCH_DIR / f"SYSTEM_ARCHITECTURE_v{version}.md"
    if arch_file.exists():
        subprocess.run(["cp", str(arch_file), str(backup_dir / arch_file.name)])

# 运行每日迭代
def run_daily_iteration():
    print(f"🚀 开始每日迭代: {datetime.now()}")
    
    current_version = get_current_version()
    new_version = bump_version(current_version)
    
    print(f"📦 版本: {current_version} → {new_version}")
    
    # 1. 备份当前版本
    backup_version(current_version)
    
    # 2. 更新 PRD（这里可以根据需要添加更新逻辑）
    prd_file = PRD_DIR / f"PRODUCT_SPECIFICATION_v{new_version}.md"
    if PRD_DIR / f"PRODUCT_SPECIFICATION_v{current_version}.md":
        subprocess.run(["cp", 
                        str(PRD_DIR / f"PRODUCT_SPECIFICATION_v{current_version}.md"),
                        str(prd_file)])
    print(f"✓ PRD v{new_version} 已创建")
    
    # 3. 更新架构文档
    arch_file = ARCH_DIR / f"SYSTEM_ARCHITECTURE_v{new_version}.md"
    if ARCH_DIR / f"SYSTEM_ARCHITECTURE_v{current_version}.md":
        subprocess.run(["cp",
                        str(ARCH_DIR / f"SYSTEM_ARCHITECTURE_v{current_version}.md"),
                        str(arch_file)])
    print(f"✓ 架构文档 v{new_version} 已创建")
    
    # 4. 更新版本号
    VERSION_FILE.write_text(new_version)
    
    # 5. 更新迭代日志
    changes = [
        "PRD 文档更新",
        "架构文档更新",
        "版本号递增"
    ]
    update_iteration_log(new_version, changes)
    print(f"✓ 迭代日志已更新")
    
    # 6. 发送邮件
    send_mail(new_version)
    
    print(f"\n✅ 迭代完成: v{new_version}")
    return new_version

# 发送邮件
def send_mail(version: str):
    prd_file = PRD_DIR / f"PRODUCT_SPECIFICATION_v{version}.md"
    if not prd_file.exists():
        print(f"⚠️ PRD 文件不存在: {prd_file}")
        return
    
    mail_script = SCRIPTS_DIR / "send_mail.py"
    if mail_script.exists():
        result = subprocess.run(
            ["python3", str(mail_script), version, str(prd_file)],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✓ 邮件已发送: v{version}")
        else:
            print(f"✗ 邮件发送失败: {result.stderr}")
    else:
        print(f"⚠️ 邮件脚本不存在")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--dry-run":
        print("🧪 干运行模式")
        print(f"当前版本: {get_current_version()}")
        print(f"新版本: {bump_version(get_current_version())}")
    else:
        run_daily_iteration()
