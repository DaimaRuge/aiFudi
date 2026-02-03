#!/usr/bin/env python3
"""
SkyOne Shuge - 邮件发送脚本
发送每日更新的 PRD 到指定邮箱
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# 邮件配置
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "qun.xitang.du@gmail.com"
SENDER_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
RECIPIENT_EMAILS = ["broadbtinp@gmail.com", "dulie@foxmail.com"]

def send_prd_update(version: str, prd_path: str, custom_subject: str = None):
    """发送 PRD 更新邮件"""
    
    # 读取 PRD 内容
    with open(prd_path, 'r', encoding='utf-8') as f:
        prd_content = f.read()
    
    subject = custom_subject or f"[天一阁] PRD v{version} 更新通知"
    
    for recipient in RECIPIENT_EMAILS:
        # 构建邮件
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = recipient
        
        # 邮件正文
        body = f"""
天一阁 (SkyOne Shuge) - 产品需求文档更新

版本: v{version}
更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

请查看附件获取完整的 PRD 文档。

---
此邮件由天一阁 AI 自动发送
"""
        msg.attach(MIMEText(body, "plain", "utf-8"))
        
        # 添加附件
        filename = os.path.basename(prd_path)
        attachment = MIMEText(prd_content, "plain", "utf-8")
        attachment.add_header("Content-Disposition", "attachment", filename=filename)
        msg.attach(attachment)
        
        # 发送邮件
        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            server.quit()
            print(f"✓ 邮件已发送至 {recipient}: v{version}")
        except Exception as e:
            print(f"✗ 发送至 {recipient} 失败: {e}")
            return False
    
    return True

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("用法: python send_mail.py <version> <prd_file_path> [subject]")
        sys.exit(1)
    
    version = sys.argv[1]
    prd_path = sys.argv[2]
    custom_subject = sys.argv[3] if len(sys.argv) > 3 else None
    
    send_prd_update(version, prd_path, custom_subject)
