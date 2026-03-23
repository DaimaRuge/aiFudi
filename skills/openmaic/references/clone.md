# Clone Or Reuse Existing Repo

## Goal

Establish which OpenMAIC checkout will be used for setup and runtime actions.

## Procedure

1. Check whether OpenMAIC already exists locally.
2. If a checkout exists, show the path and ask whether to reuse it.
3. If no checkout exists, propose cloning the repo and ask for confirmation.
4. After clone, confirm dependency installation separately.
5. After installation, check for common issues before proceeding.

## Recommended Path

- Recommended: reuse an existing checkout if it is already on the target branch.
- Otherwise: clone a fresh checkout from GitHub, then install dependencies.

## Check for Existing Installation

Search common locations:

```bash
# Check current directory
find . -name "OpenMAIC" -type d

# Check user home directory
find ~ -name "OpenMAIC" -type d

# Check workspace directory
find /root/.openclaw/workspace -name "OpenMAIC" -type d
```

If found, show the path and ask to reuse it.

## Commands

Clone:

```bash
git clone https://github.com/THU-MAIC/OpenMAIC.git
cd OpenMAIC
```

Checkout specific branch if needed (default is main):

```bash
# Already on main by default
git checkout main
git pull
```

Install dependencies:

```bash
# Using pnpm (recommended by OpenMAIC)
pnpm install

# After installation, build sub-packages
pnpm postinstall
```

## Post-Installation Checks

1. **Check `.env.local`**:
   - If `.env.local` doesn't exist, copy from `.env.example`:
     ```bash
     cp .env.example .env.local
     ```
   - Tell the user they need to edit `.env.local` to add API keys

2. **Check Node.js version**:
   ```bash
   node --version
   # Should be >= 20.9.0
   ```

3. **Check disk space**:
   - OpenMAIC with node_modules is ~1-2GB
   - Ensure sufficient disk space before proceeding

## Common Issues

1. **pnpm not installed**: Install pnpm first:
   ```bash
   npm install -g pnpm
   ```

2. **Installation fails**: Clean and retry:
   ```bash
   rm -rf node_modules
   rm pnpm-lock.yaml
   pnpm install
   ```

3. **Sub-package build fails**:
   ```bash
   pnpm postinstall
   # or
   cd packages/mathml2omml && npm run build
   cd ../pptxgenjs && npm run build
   ```

## Confirmation Requirements

- Ask before `git clone`.
- Ask before `pnpm install`.
- If the repo is dirty, tell the user and ask whether to continue with that checkout.
- Confirm post-installation steps before proceeding.
