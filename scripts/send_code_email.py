#!/usr/bin/env python3
"""
天一阁 - 代码打包邮件工具

自动打包代码并发送邮件给收件人

用法:
    python scripts/send_code_email.py

环境变量:
    GMAIL_APP_PASSWORD: Gmail App Password
"""

import os
import tarfile
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import shutil
import sys

# 配置
SENDER = "qun.xitang.du@gmail.com"
PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
RECIPIENTS = ["broadbtinp@gmail.com", "dulie@foxmail.com"]
PROJECT_DIR = "/root/.openclaw/workspace/skyone-shuge"
ATTACH_DIR = "/tmp/skyone_code"

VERSION_FILE = os.path.join(PROJECT_DIR, "VERSION.txt")


def get_version():
    """获取当前版本"""
    try:
        with open(VERSION_FILE, "r") as f:
            return f.read().strip()
    except:
        return "unknown"


def package_code(version: str):
    """打包代码"""
    src_dir = os.path.join(PROJECT_DIR, "src")
    output_file = f"/tmp/skyone_code_{version}.tar.gz"
    
    print(f"📦 打包代码: {version}")
    
    with tarfile.open(output_file, "w:gz") as tar:
        tar.add(src_dir, arcname="skyone_code")
    
    print(f"✅ 已创建: {output_file}")
    return output_file


def send_email(version: str, attachment_path: str):
    """发送邮件"""
    subject = f"[天一阁] 🎉 v{version} 代码包"
    
    body = f"""
天一阁 v{version} 代码包

🎉 代码已打包，请查收附件！

## 版本信息

- 版本: v{version}
- 时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- 项目: {PROJECT_DIR}

## 安装运行

```bash
# 解压
tar -xzvf skyone_code_{version}.tar.gz
cd skyone_code

# 安装依赖
pip install -e .

# 启动服务
uvicorn skyone_shuge.api.main:app --reload
```

感谢您的支持！
"""
    
    filename = f"skyone_code_{version}.tar.gz"
    
    for recipient in RECIPIENTS:
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = SENDER
        msg["To"] = recipient
        msg.attach(MIMEText(body, "plain", "utf-8"))
        
        # 添加附件
        with open(attachment_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename= "{filename}"'
            )
            msg.attach(part)
        
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(SENDER, PASSWORD)
            server.send_message(msg)
            server.quit()
            print(f"✓ 已发送至 {recipient}")
        except Exception as e:
            print(f"✗ 失败: {e}")


def cleanup(attachment_path: str):
    """清理临时文件"""
    if os.path.exists(attachment_path):
        os.remove(attachment_path)
        print(f"🧹 已清理临时文件")


def main():
    """主函数"""
    if not PASSWORD:
        print("❌ 错误: 请设置 GMAIL_APP_PASSWORD 环境变量")
        sys.exit(1)
    
    version = get_version()
    print(f"📨 发送 v{version} 代码包...")
    
    # 打包
    attachment_path = package_code(version)
    
    # 发送
    send_email(version, attachment_path)
    
    # 清理
    cleanup(attachment_path)
    
    print(f"\n🎉 v{version} 代码包发送完成!")


if __name__ == "__main__":
    main()
