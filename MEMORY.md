# MEMORY.md - Long-term Memory

## System Configuration

### OpenClaw Setup
- **Gateway**: Running on port 18789
- **Channels**: Feishu, Telegram, Discord, QQ Bot configured
- **Streaming**: Enabled for Feishu (channels.feishu.streaming = true)

### Daily Automation
- **Morning Report**: 07:00 daily - System status self-check
- **Evening Summary**: 23:00 daily - Conversation and task summary
- **Cron Job IDs**: 
  - 0a50559c-6ffd-4531-b317-1b29b589ab1f (morning)
  - db6d0ac8-1866-43cb-93a2-2417cb0cf202 (evening)

### DeepSeek Integration (2026-03-13)
- **Provider**: deepseek
- **API Key**: Configured successfully
- **Models**: V3 (chat) and R1 (reasoner) available
- **Status**: API accessible, model switching needs verification
- **Default Model**: Set to deepseek/deepseek-chat

## User Information
- **Name**: 群哥 (Qun Ge)
- **Timezone**: Asia/Shanghai
- **Language**: Prefers Chinese (Simplified)
- **Communication Style**: Values clear, step-by-step explanations with examples

## Important Projects
- **华住项目功能优势对比**: Document created and distributed
- **Agent Learning 学习工程**: 8周系统学习计划，涵盖Agent开发全栈技能
- **终身学习演示项目**: Docker和Python两个版本实现
- **GitHub Repo**: https://github.com/DaimaRuge/aiFudi (包含学习工程)
- **Email**: qun.xitang.du@gmail.com

## GitHub Account Information
- **Username**: DaimaRuge
- **Access Token**: 已配置（见 ~/.git-credentials）
- **Full Name**: Amogha Du
- **Company**: Liminfini Technology Co., Ltd.
- **Location**: Shanghai, China
- **Role**: Product Manager
- **Public Repositories**: 26
- **Private Repositories**: 7
- **Key Projects**: aiFudi (Fudi VoiceOS), OpenClaw, Agent-Learning, Product-Manager-Skills

## Security Notes
- **Gateway Security Warnings**: 6 critical issues (open groupPolicy, extensions without plugins.allow)
- **Recommendation**: Run `openclaw doctor --repair` when possible

## Skills Store Policy
1. Try `skillhub` first (cn-optimized)
2. Fallback to `clawhub` if unavailable
3. No exclusivity claims - public and private registries allowed
4. Summarize source/version/risks before installation
5. For searches: execute `skillhub search <keywords>` first
6. Reply directly in session, no `message` tool for progress updates

## MinerU 配置 (2026-03-27)
- **技能**: 已安装于 `~/.openclaw/workspace/skills/mineru/`
- **API Token**: 已配置到 `~/.bashrc`（MINERU_TOKEN）
- **过期**: 2025-08-21
- **功能**: PDF/Word/PPT/图片 → Markdown，公式表格全保留

## Lessons Learned
- **Document Storage**: Always save documents in `/root/.openclaw/workspace/`
- **PPT Generation**: Automatically send email, sync GitHub, upload to Feishu
- **Model Switching**: `/model` command may require session restart or gateway restart
- **Gateway Restart**: Sometimes fails with code 1, but service may still be running
- **GitHub Access**: username=DaimaRuge, token 已配置（见 ~/.git-credentials）
- **学习工程管理**: 重要学习项目必须及时上传GitHub并建立进度跟踪系统

## Preferences
- **Weather Checks**: User interested in Shanghai weather
- **Testing**: User likes to test new configurations (e.g., DeepSeek connectivity)
- **Automation**: Appreciates daily automated reports