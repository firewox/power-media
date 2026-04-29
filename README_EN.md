# Power Media

> AI-powered social media automation platform — built on Claude Code / OpenCode Skills system and a desktop-control MCP server.

## Overview

Power Media is a suite of social media automation tools that leverages the **Claude Code Skills system** alongside the **computer-mcp desktop control server**, enabling AI to operate Windows desktop browsers for cross-platform content publishing and account management.

### Architecture

```
User Request → Claude Code / OpenCode
                  ├── Skills System (capability modules)
                  │     ├── Weibo (browser automation)
                  │     ├── RedNote / Xiaohongshu (browser automation)
                  │     ├── WeChat Official Account (official API)
                  │     ├── Zhihu (planned)
                  │     └── check-ip (utility)
                  │
                  └── computer-mcp (MCP server)
                        ├── Window management (list/focus)
                        ├── Screen capture + OCR
                        ├── Mouse/keyboard simulation
                        └── High-risk action confirmation guard
```

### Two Operation Modes

| Mode | Platforms | Technology |
|------|-----------|------------|
| **Browser Automation** | Weibo, RedNote | computer-mcp: screenshot recognition + simulated input |
| **Direct API** | WeChat Official Account | WeChat official HTTP API |

---

## Supported Platforms

### Weibo

Browser automation via computer-mcp.

| Skill | Function | Status |
|-------|----------|--------|
| `login` | QR code login | ✅ |
| `logout` | Logout | ✅ |
| `check-login` | Check login state | ✅ |
| `post-text` | Post plain text weibo (≤140 chars) | ✅ |
| `post-text-enhanced` | Enhanced posting (Ollama vision positioning) | ✅ |
| `post-with-image` | Post weibo with images | ✅ |

**Technical details:**
- Percentage-based coordinates for resolution-independent positioning
- Enhanced version integrates Ollama vision model for automatic UI element detection via screenshot
- Built on `WeiboAutomation` (computer_mcp_client.py)

### RedNote / Xiaohongshu

Browser automation via computer-mcp.

| Skill | Function | Status |
|-------|----------|--------|
| `get-qrcode` | Get login QR code | ✅ |
| `check-login` | Check login state | ✅ |
| `get-feed` | Get feed content | ✅ |
| `get-profile` | Get user profile | ✅ |
| `search` | Search notes/users | ✅ |
| `like` | Like a note | ✅ |
| `favorite` | Favorite a note | ✅ |
| `comment` | Comment on a note | ✅ |
| `reply` | Reply to a comment | ✅ |
| `publish-note` | Publish image-text note | ✅ |
| `publish-video` | Publish video note | ✅ |

**Technical details:**
- Targets both Creator Platform (`creator.xiaohongshu.com`) and consumer site (`www.xiaohongshu.com`)
- Built on `RedNoteAutomation` (rednote_automation.py)
- Shares `ComputerMCPClient` modules with Weibo

### WeChat Official Account

Direct API integration — no browser required.

| Skill | Function | Status |
|-------|----------|--------|
| `test-connection` | Test API connection | ✅ |
| `upload-image` | Upload image to material library | ✅ |
| `push-draft-text` | Push text/Markdown to draft box | ✅ |
| `push-draft-markdown` | Push from Markdown file to draft box | ✅ |
| `get-draft-list` | List drafts | ✅ |
| `get-draft-detail` | Get draft details | ✅ |
| `delete-draft` | Delete a single draft | ✅ |
| `delete-all-drafts` | Clear all drafts | ✅ |
| `markdown-to-wechat-html` | Convert Markdown to WeChat-compatible HTML | ✅ |
| `validate-markdown` | Pre-publish validation | ✅ |

**Technical details:**
- Operates via `api.weixin.qq.com` official API
- Automatic access_token retrieval + in-memory caching (refreshes 5 minutes before expiry)
- Configuration priority chain: `wechat-config.json` → `.env` → environment variables
- Uses `sharp` to generate SVG gradient cover images (automatic fallback)
- Code syntax highlighting + WeChat-compatible styling
- Built-in error code mapping table

### Zhihu

Planned, not yet implemented.

### check-ip

IP address lookup utility for debugging network connectivity (e.g., configuring WeChat IP whitelist).

---

## Prerequisites

### General
- **OS**: Windows 10/11
- **Shell**: PowerShell / bash

### computer-mcp (Desktop Control)
- **Python**: 3.8+
- **Node.js**: Optional (some helper scripts)
- **Browser**: Edge / Chrome / Firefox (must be logged in)
- **Install dependencies**:
  ```bash
  cd computer-mcp
  pip install -r requirements.txt
  ```

#### Dependencies
| Package | Purpose |
|---------|---------|
| `mcp` | MCP server framework |
| `pyautogui` | Mouse/keyboard simulation |
| `pywinauto` | Windows GUI automation |
| `mss` | High-performance screen capture |
| `easyocr` | OCR text recognition |
| `opencv-python` | Image processing |
| `Pillow` | Image processing |

### WeChat Official Account API
- **Node.js**: 18+
- **Install dependencies**:
  ```bash
  cd .claude/skills/power-media/wechat
  npm install
  ```
- **Dependencies**: axios, form-data, marked, sanitize-html, highlight.js, sharp

---

## Quick Start

### 1. Start computer-mcp server

```bash
cd computer-mcp
pip install -r requirements.txt
python server.py
```

### 2. Configure MCP

Add to `.claude/settings.local.json`:

```json
{
  "mcpServers": {
    "computer": {
      "command": "python",
      "args": ["computer-mcp/server.py"]
    }
  }
}
```

### 3. Configure WeChat Credentials (optional)

Create `.claude/skills/power-media/wechat/wechat-config.json`:

```json
{
  "WECHAT_APP_ID": "your-app-id",
  "WECHAT_APP_SECRET": "your-app-secret",
  "WECHAT_DEFAULT_AUTHOR": "Author Name",
  "WECHAT_NEED_OPEN_COMMENT": "true",
  "WECHAT_ONLY_FANS_CAN_COMMENT": "true"
}
```

---

## Safety Design

- **High-risk confirmation**: Publishing, deletion, and other destructive actions require manual confirmation (`confirm_guard.py`)
- **Credential tiering**: Configuration searched in `config file → .env → environment variables` order — never hardcoded
- **In-memory token caching**: access_token lives in process memory only, never written to disk
- **Log redaction**: Sensitive parameters marked with `secret=True` are automatically hidden in logs
- **Delete protection**: `delete-all-drafts` requires an explicit confirmation parameter

---

## Project Structure

```
power-media/
├── computer-mcp/                    # MCP desktop control server
│   ├── server.py                    # FastMCP server entry point
│   ├── windows_backend.py           # Window/mouse/keyboard operations
│   ├── screen_inspector.py          # Screenshot + OCR
│   ├── confirm_guard.py             # Action confirmation guard
│   ├── logger.py                    # Action log (with redaction)
│   ├── requirements.txt
│   └── tests/
│
└── .claude/skills/power-media/       # Skills directory
    ├── check-ip/                     # IP lookup utility
    ├── computer-mcp/                 # computer-mcp skill entry
    ├── weibo/                        # Weibo skills
    │   ├── lib/                      # Shared libraries
    │   │   ├── computer_mcp_client.py
    │   │   ├── screenshot_manager.py
    │   │   └── ollama_vision.py
    │   └── {login,logout,post-text,...}/
    ├── rednote/                      # RedNote skills
    │   ├── lib/
    │   │   ├── rednote_automation.py
    │   │   └── computer_mcp_client.py
    │   └── {publish-note,search,...}/
    ├── wechat/                       # WeChat OA skills
    │   ├── lib/
    │   │   └── wechat-common.js      # Shared library
    │   └── {test-connection,push-draft-text,...}/
    └── zhihu/                        # Zhihu (planned)
```

Each sub-skill directory follows this structure:
```
skill-name/
├── SKILL.md          ← YAML frontmatter + Markdown docs
├── README.md         ← Brief description
└── scripts/
    └── skill.{py,js}  ← Core implementation
```

---

## FAQ

**Q: Weibo posting fails?**
A: Ensure the browser is logged into Weibo and computer-mcp is running. Screen resolution differences may require coordinate adjustments.

**Q: WeChat API returns error 40001?**
A: The system auto-refreshes access_token. If it persists, verify your AppSecret is correct.

**Q: Image upload fails?**
A: Check the image format (supported: JPG/PNG/GIF/BMP/WEBP), file size (max 2MB), and your WeChat backend IP whitelist configuration.

**Q: Missing dependency errors?**
A: Run the appropriate install script. Python deps: `pip install -r computer-mcp/requirements.txt`. WeChat Node deps: `cd .claude/skills/power-media/wechat && npm install`.
