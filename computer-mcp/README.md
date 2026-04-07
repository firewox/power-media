# computer-mcp

Local MCP server that gives AI desktop control over Windows browser windows.

## Setup

```bash
cd computer-mcp
pip install -r requirements.txt
python server.py
```

## Tools

screenshot, list_windows, focus_window, click, double_click, drag,
type_text, press_key, hotkey, scroll, wait, inspect_screen,
get_cursor, confirm_action

## Usage with OpenCode / Claude

Add to your MCP config (`.claude/settings.local.json`):

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

## Architecture

```
Claude / Skills
   -> MCP client
      -> computer-mcp (server.py)
         -> screen_inspector   (screenshot + OCR)
         -> windows_backend    (mouse / keyboard / window focus)
         -> confirm_guard      (high-risk action gating)
         -> logger             (action log, secret redaction)
```

## Safety

- High-risk actions (publish, delete, submit) require human confirmation via `confirm_action`.
- Secrets passed with `secret=True` are redacted in logs.
- Action log written to `computer-mcp.log` in working directory.
