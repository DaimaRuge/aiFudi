# Startup Modes

## Goal

Help the user choose how OpenMAIC should run before you start anything.

## Prerequisites

### Node.js Version Check
OpenMAIC requires Node.js >= 20.9.0. Check before starting:

```bash
node --version
```

If version is too old, upgrade Node.js before continuing.

### Port Conflict Handling

Default port is 3000. Check if it's available:

```bash
# Check if port 3000 is occupied
netstat -tlnp | grep :3000
# or
lsof -i :3000

# If port is occupied by another OpenMAIC instance
# Stop the existing instance first, or use an alternative port

# Use alternative port 3001
pnpm dev -p 3001

# Clean up lock file if startup fails
rm -f .next/dev/lock
```

## Options

### 1. Development Mode

Recommended for first-time setup and debugging.

```bash
pnpm dev
# Or for alternative port
pnpm dev -p 3001
```

Tradeoff:

- Fastest feedback loop
- Best for validating config changes
- Not representative of production startup

### 2. Production-Like Local Mode

Recommended when the user wants behavior closer to a deployed server.

```bash
pnpm build && pnpm start
# Or with alternative port
pnpm build && pnpm start -p 3001
```

Tradeoff:

- Closer to production
- Slower startup than `pnpm dev`

### 3. Docker Compose

Use only when the user explicitly wants containerized startup or wants to avoid local Node setup details.

```bash
docker compose up --build
```

Tradeoff:

- Cleaner isolation
- Heavier and slower
- Harder to debug application-level issues quickly

## Recommendation Order

1. `pnpm dev` (development mode, fastest for testing)
2. `pnpm build && pnpm start` (production-like)
3. `docker compose up --build` (containerized)

## Health Check

After startup, verify:

```bash
curl -fsS http://localhost:3000/api/health
# Or for port 3001
curl -fsS http://localhost:3001/api/health
```

If the skill config provides a custom `url`, use that instead.

Expected response on success:
```json
{"status":"ok"}
```

If no response or error:
1. Check if the service is still starting
2. Check port availability
3. Check for lock file issues
4. Verify Node.js version

## Common Startup Issues

1. **Port already in use**: Use alternative port or stop existing process
2. **Lock file exists**: Remove `.next/dev/lock` and restart
3. **Node version too old**: Upgrade to >= 20.9.0
4. **Dependencies not installed**: Run `pnpm install` first
5. **Out of memory**: Increase available memory or use PM2 for process management

## Confirmation Requirements

- Ask the user to choose one startup mode.
- Ask again before running the selected command.
- Confirm port selection if there's a conflict.
