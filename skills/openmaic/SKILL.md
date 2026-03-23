---
name: openmaic
description: Guided SOP for setting up and using OpenMAIC from OpenClaw. Use when the user wants to clone the OpenMAIC repo, choose a startup mode, configure recommended API keys, start the service, or generate a classroom from requirements or a PDF. Run one phase at a time and ask for confirmation before each state-changing step.
user-invocable: true
metadata: { "openclaw": { "emoji": "🏫" } }
version: 2.0
updated: 2026-03-23
---

# OpenMAIC Skill

Use this as a guided, confirmation-heavy SOP. Do not compress the whole setup into one reply and do not perform state-changing actions without explicit user confirmation.

## Core Rules

- Move one phase at a time.
- Before any state-changing action, ask for confirmation.
- If local state already exists, show what you found and ask whether to keep it.
- Do not assume the OpenClaw agent's own model or API key will be reused by OpenMAIC.
- OpenMAIC classroom generation uses OpenMAIC server-side provider config.
- This skill must not rely on any request-time model or provider overrides.
- Only OpenMAIC server-side config files may control provider selection and defaults.
- Do not default to asking the user to paste API keys into chat.
- Prefer guiding the user to edit local config files themselves.
- Do not offer to write API keys into config files on the user's behalf.
- Once setup is complete and the user clearly asks to generate a classroom, do not ask for a second confirmation before submitting the generation job.
- Keep confirmations for local file reads such as reading a PDF from disk.

## New Rules (Based on Deployment Experience)

### Port Management
- Check for port conflicts before starting OpenMAIC (default port 3000)
- If port 3000 is occupied, suggest alternative ports (3001, 3002, etc.)
- Provide commands to check and resolve port conflicts

### API Key Recommendations
- Recommend DeepSeek API as primary provider (cost-effective, good performance)
- Recommend Google Gemini API as secondary provider (free tier available)
- Include Tavily API for web search capabilities
- Provide example .env.local configurations

### Startup Issues Resolution
- Handle common startup errors (lock files, permission issues)
- Provide troubleshooting steps for common problems
- Include commands to clean up and restart services

### Health Check
- Always verify service health before classroom generation
- Provide health check endpoint: `GET {url}/api/health`
- Wait for service to be fully ready before proceeding

## Optional Skill Config

If present, read defaults from `~/.openclaw/openclaw.json` under:

```jsonc
{
  "skills": {
    "entries": {
      "openmaic": {
        "enabled": true,
        "config": {
          "accessCode": "sk-xxx",
          "repoDir": "/path/to/OpenMAIC",
          "url": "http://localhost:3000",
          "envFile": "/path/to/.env.local",
          "apiKeys": {
            "deepseek": "sk-xxx",
            "google": "AIza-xxx",
            "tavily": "tvly-xxx"
          }
        }
      }
    }
  }
}
```

- If `accessCode` is present, default to hosted mode and skip the mode-selection prompt.
- Use `repoDir` and `url` only as defaults for local mode.
- If `envFile` is present, check for existing API key configurations.
- If `apiKeys` are provided, suggest using them in configuration.
- Still confirm before acting.

## Recommended Configuration (Based on Experience)

### Optimal API Key Setup
```bash
# .env.local configuration
DEEPSEEK_API_KEY=sk-e0a54ba5a281472ba78041f497453ea1
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODELS=deepseek-chat,deepseek-reasoner

GOOGLE_API_KEY=AIzaSyDy9EgEBWOvqBdG_9vRbQTHBt-i0RYx8cw
GOOGLE_MODELS=gemini-3-flash-preview,gemini-3.1-pro-preview

TAVILY_API_KEY=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

DEFAULT_MODEL=deepseek:deepseek-chat
```

### Default Port Configuration
- Primary port: 3000
- Alternative ports: 3001, 3002, 3003
- Health check: http://localhost:{port}/api/health

## SOP Phases

### 0. Choose Mode

First check skill config for `accessCode`. If present, announce that a stored access code was found and proceed directly to hosted mode (load [references/hosted-mode.md](references/hosted-mode.md), skip phases 1–4). Do not ask the user to paste the code again.

If no `accessCode` in config, ask the user how they want to use OpenMAIC:

1. **Use hosted OpenMAIC** (recommended for quick start) — Requires an access code from open.maic.chat. No local setup needed.
2. **Run locally** — Clone the repo, configure provider keys, and run on your machine.
3. **Use existing local installation** — If OpenMAIC is already installed locally, use existing setup.

If the user chooses hosted mode, load [references/hosted-mode.md](references/hosted-mode.md) and skip phases 1–4.
If the user chooses local mode, proceed to phase 1 as usual.
If the user chooses existing installation, check for existing setup and proceed to phase 4.

### 1. Clone Or Reuse Existing Repo

Load [references/clone.md](references/clone.md).

Use this when the user has not installed OpenMAIC yet or when you need to confirm which local checkout to use.

### 2. Choose Startup Mode

Load [references/startup-modes.md](references/startup-modes.md).

Use this after the repo location is confirmed. Present the available startup modes, recommend one, and wait for the user's choice.

### 3. Configure Provider Keys

Load [references/provider-keys.md](references/provider-keys.md).

Use this before starting classroom generation. Recommend a provider path and tell the user exactly which config file to edit themselves. If generation later fails due to provider/model/auth issues, return to this phase and direct the user to update the same server-side config files.

### 4. Start And Verify OpenMAIC

After the user has chosen a startup mode and configured keys, start OpenMAIC using the chosen method, then verify the service with `GET {url}/api/health`.

#### Port Conflict Resolution
Before starting OpenMAIC, check for port conflicts:

```bash
# Check if port 3000 is occupied
netstat -tlnp | grep :3000
lsof -i :3000

# If port is occupied, suggest alternatives
# Option 1: Stop the occupying process
kill <PID>

# Option 2: Use alternative port
npm run dev -p 3001

# Option 3: Clean lock files
rm -f .next/dev/lock
```

#### Common Startup Issues
1. **Lock file exists**: Remove `.next/dev/lock` and restart
2. **Port already in use**: Use alternative port (3001, 3002, etc.)
3. **Permission issues**: Ensure proper file permissions
4. **Node version**: Ensure Node.js >= 20.9.0

#### Health Check Commands
```bash
# Check service health
curl http://localhost:3000/api/health

# If using alternative port
curl http://localhost:3001/api/health

# Check Next.js dev server status
curl http://localhost:3000/_next/static/development/_devPagesManifest.json
```

### 5. Generate A Classroom

Load [references/generate-flow.md](references/generate-flow.md).

Use this only after the service is healthy. Confirm before reading local PDFs. If the user has already clearly asked to generate, do not ask for a second confirmation before submitting the generation job, and then follow the polling loop until it succeeds or fails. Only send the supported content fields for generation requests. For long-running jobs, prefer sparse polling and tell the user to check back later if the turn ends before completion.

## Response Style

- Keep each step short and explicit.
- Prefer 2-3 concrete options when the user must choose.
- Always include the recommended option first and explain why in one sentence.
- After a step completes, say what changed and what the next confirmation is for.
- When returning a classroom link, place the raw absolute URL on its own line with no bold, markdown link syntax, code formatting, or tables.

## Best Practices (Based on Experience)

### Configuration Recommendations
1. **Primary LLM Provider**: DeepSeek API (cost-effective, good Chinese support)
2. **Secondary LLM Provider**: Google Gemini (free tier, good for testing)
3. **Search Provider**: Tavily API (web search capabilities)
4. **Default Model**: `deepseek:deepseek-chat`

### Troubleshooting Checklist
- [ ] Check port availability (3000, 3001, etc.)
- [ ] Verify Node.js version (>= 20.9.0)
- [ ] Check API key configuration in `.env.local`
- [ ] Remove lock files if startup fails
- [ ] Verify service health before generation

### Performance Tips
1. **Development Mode**: Use `npm run dev` for local development
2. **Production Mode**: Use `npm run build && npm start` for production
3. **Memory Management**: Monitor memory usage for large classroom generation
4. **Timeout Settings**: Adjust timeout for long-running generation jobs

### Security Considerations
1. **API Keys**: Never commit `.env.local` to version control
2. **Access Control**: Use environment variables for sensitive data
3. **Network Security**: Use HTTPS in production environments
4. **Rate Limiting**: Implement rate limiting for API endpoints
