# Design: Weibo Post Text Enhanced

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Request                              │
│              python post_text_enhanced.py                   │
│                   --content-file content.txt                │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│           post_text_enhanced.py (Main Script)               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. Argument Parsing (--content-file, --max-retries)  │  │
│  │ 2. Window Management (find_or_open_weibo)            │  │
│  │ 3. Screenshot Capture (with timestamp)               │  │
│  │ 4. Subagent Analysis (up to 3 retries)               │  │
│  │ 5. Coordinate Calculation (4-point to center)        │  │
│  │ 6. Input & Send Actions                              │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│           Subagent Coordinator                               │
│              subagent_coordinator.py                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  • Build opencode command                             │  │
│  │  • Execute bash command                               │  │
│  │  • Parse JSON response                                │  │
│  │  • Retry logic (max 3 attempts)                       │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│           External Services                                  │
│  ┌──────────────┐  ┌──────────────────────────────────────┐ │
│  │ computer-mcp │  │    ollama-cloud/qwen3.5:397b         │ │
│  │  (screenshot,│  │         (Subagent)                   │ │
│  │   click,     │  │                                      │ │
│  │   type_text) │  │  • Analyze screenshot                │ │
│  └──────────────┘  │  • Detect UI elements                │ │
│                     │  • Return JSON coordinates           │ │
│                     └──────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Main Script: `post_text_enhanced.py`

**Responsibilities:**
- Parse command line arguments
- Coordinate the workflow
- Handle errors and retries
- Output results

**Interface:**
```python
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--content-file", required=True)
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--screenshot-dir", default="screenshots/weibo/")
    args = parser.parse_args()
    
    # Workflow implementation
```

### 2. Subagent Coordinator: `subagent_coordinator.py`

**Responsibilities:**
- Build and execute opencode command
- Parse JSON output
- Implement retry logic
- Handle errors

**Interface:**
```python
class SubagentCoordinator:
    def __init__(self, model="ollama-cloud/qwen3.5:397b"):
        self.model = model
    
    def analyze_screenshot(self, screenshot_path: str, max_retries=3) -> dict:
        """
        Returns: {
            "input_box": [X1, Y1, X2, Y2],
            "send_button": [X1, Y1, X2, Y2],
            "headline_article_button": [X1, Y1, X2, Y2]
        }
        """
```

### 3. Screenshot Manager

**Responsibilities:**
- Generate timestamped filenames
- Ensure directory exists
- Save screenshots with proper naming

**Naming Convention:**
```
screenshots/weibo/weibo_home_YYYYMMDD_HHMMSS.png
```

## Data Flow

### Step-by-Step Flow

```
1. Parse Args
   ↓
2. Find/Open Weibo Window (computer_mcp_client)
   ↓
3. Capture Screenshot (computer-mcp/tool_screenshot)
   ↓
   Save to: screenshots/weibo/weibo_home_20250419_143052.png
   ↓
4. Analyze via Subagent (opencode run)
   Command: opencode run -m ollama-cloud/qwen3.5:397b \
            "请识别..." \
            -f "screenshots/weibo/xxx.png"
   ↓
   Response: {"input_box": [0.47, 0.25, 0.61, 0.30], ...}
   ↓
5. Calculate Centers
   input_center = ((0.47 + 0.61) / 2, (0.25 + 0.30) / 2)
                = (0.54, 0.275)
   ↓
6. Read Content File
   ↓
7. Click Input Box (computer-mcp/tool_click)
   ↓
8. Type Content (computer-mcp/tool_type_text)
   ↓
9. Click Send Button (computer-mcp/tool_click)
   ↓
10. Return Result
```

## Error Handling

### Retry Strategy

| Error Type | Retry Count | Action |
|------------|-------------|--------|
| Subagent timeout | 3 | Wait and retry |
| JSON parse error | 3 | Retry with same screenshot |
| Missing keys in JSON | 3 | Retry |
| Window not found | 0 | Fail immediately |
| Content file not found | 0 | Fail immediately |

### Error Output

```json
{
  "success": false,
  "error": "Subagent analysis failed after 3 retries",
  "screenshot_path": "screenshots/weibo/weibo_home_20250419_143052.png",
  "last_error": "JSON parse error: ..."
}
```

## Coordinate System

### Input Format (from Subagent)

```json
{
  "input_box": [0.47, 0.25, 0.61, 0.30],
  "send_button": [0.72, 0.25, 0.78, 0.30],
  "headline_article_button": [0.15, 0.35, 0.25, 0.40]
}
```

### Conversion to Center Point

```python
def bbox_to_center(bbox: list) -> tuple:
    """
    bbox: [X1, Y1, X2, Y2] in percentage (0-1)
    returns: (center_x, center_y) in percentage
    """
    x1, y1, x2, y2 = bbox
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    return (center_x, center_y)
```

### Screen Coordinate Conversion

```python
def pct_to_screen_coords(pct_x: float, pct_y: float, window_rect: dict) -> tuple:
    """
    Convert percentage (0-1) to screen pixels
    """
    x = window_rect["left"] + int(window_rect["width"] * pct_x)
    y = window_rect["top"] + int(window_rect["height"] * pct_y)
    return (x, y)
```

## Dependencies

### Internal Dependencies

- `weibo/lib/computer_mcp_client.py` - Window management, coordinate conversion
- `computer-mcp/server.py` - Screenshot, click, type_text tools

### External Dependencies

- `opencode` CLI - Subagent execution
- `ollama-cloud/qwen3.5:397b` - Multimodal model for analysis

## Security Considerations

1. **Content File Path**: Validate file exists and is readable
2. **Screenshot Storage**: Ensure screenshots directory is writable
3. **Command Injection**: Sanitize paths in bash commands
4. **Subagent Output**: Validate JSON structure before parsing

## Testing Strategy

### Unit Tests

1. **Coordinate Conversion Tests**
   - Test `bbox_to_center` with various inputs
   - Test `pct_to_screen_coords` with mock window rect

2. **Subagent Coordinator Tests**
   - Mock opencode command execution
   - Test retry logic
   - Test JSON parsing with various outputs

3. **Screenshot Manager Tests**
   - Test filename generation
   - Test directory creation

### Integration Tests

1. **End-to-End Test**
   - Mock subagent response
   - Verify full workflow execution

2. **Error Handling Tests**
   - Test retry exhaustion
   - Test missing content file
   - Test invalid JSON response

## Performance Considerations

| Operation | Expected Time | Optimization |
|-----------|---------------|--------------|
| Screenshot | < 1s | Use existing mss implementation |
| Subagent Analysis | 5-10s | Depends on model response time |
| Window Operations | < 2s | pyautogui is fast |
| Total (no retry) | 10-15s | Acceptable for automation |
| Total (with retries) | 30-45s | Worst case with 3 retries |

## Future Enhancements

1. **Caching**: Cache successful element detections for same resolution
2. **Async**: Parallel screenshot and analysis preparation
3. **Validation**: Add optional OCR-based post-send validation
4. **Batch**: Support multiple content files in one run
