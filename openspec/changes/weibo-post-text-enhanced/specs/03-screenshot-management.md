# Spec: Screenshot Management

## Overview

定义截图保存的目录结构、命名规范和管理策略。

## Directory Structure

```
screenshots/
└── weibo/
    ├── weibo_home_20250419_143052.png
    ├── weibo_home_20250419_143115.png
    └── weibo_home_20250419_143230.png
```

## Naming Convention

```python
{platform}_{context}_{timestamp}.png

Where:
- platform: "weibo" (fixed)
- context: "home" | "login" | "post" | "error" (optional)
- timestamp: YYYYMMDD_HHMMSS

Examples:
- weibo_home_20250419_143052.png
- weibo_post_20250419_143115.png
- weibo_error_20250419_143230.png
```

## ScreenshotManager Class

```python
class ScreenshotManager:
    def __init__(self, base_dir: str = "screenshots/weibo/"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_filename(self, context: str = "home") -> str:
        """Generate timestamped filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"weibo_{context}_{timestamp}.png"
        return str(self.base_dir / filename)
    
    def save_screenshot(self, screenshot_data: bytes, context: str = "home") -> str:
        """Save screenshot and return path"""
        filepath = self.generate_filename(context)
        with open(filepath, "wb") as f:
            f.write(screenshot_data)
        return filepath
    
    def cleanup_old_screenshots(self, max_age_days: int = 7):
        """Remove screenshots older than max_age_days"""
        cutoff = datetime.now() - timedelta(days=max_age_days)
        for screenshot in self.base_dir.glob("*.png"):
            if datetime.fromtimestamp(screenshot.stat().st_mtime) < cutoff:
                screenshot.unlink()
```

## Integration with computer-mcp

```python
def capture_and_save(self, context: str = "home") -> str:
    """
    Capture screenshot using computer-mcp and save
    
    Returns:
        Path to saved screenshot
    """
    # Call computer-mcp screenshot tool
    result = self.mcp.tool_screenshot()
    
    if not result.get("success"):
        raise ScreenshotError(f"Screenshot failed: {result.get('error')}")
    
    # Read screenshot file from computer-mcp location
    screenshot_path = result["path"]
    with open(screenshot_path, "rb") as f:
        screenshot_data = f.read()
    
    # Save to our managed location
    saved_path = self.save_screenshot(screenshot_data, context)
    
    return saved_path
```

## File Size Considerations

| Resolution | Approx Size | Notes |
|------------|-------------|-------|
| 1920x1080 | ~200KB | Standard |
| 2560x1440 | ~400KB | High res |
| 3840x2160 | ~800KB | 4K |

## Storage Management

- **Auto-cleanup**: Remove screenshots older than 7 days
- **Max storage**: Warn if directory > 100MB
- **Git ignore**: Ensure screenshots/ is in .gitignore
