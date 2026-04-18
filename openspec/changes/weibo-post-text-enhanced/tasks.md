# Tasks: Weibo Post Text Enhanced

## Task 1: Create Subagent Coordinator

**File**: `weibo/lib/subagent_coordinator.py`

### Description
Create a coordinator class to manage subagent (opencode) execution with retry logic.

### Acceptance Criteria
- [ ] `SubagentCoordinator` class with `analyze_screenshot()` method
- [ ] Build opencode command with proper escaping
- [ ] Execute bash command and capture output
- [ ] Parse JSON response
- [ ] Retry logic: up to 3 attempts on failure
- [ ] Validate coordinate ranges (0-1)
- [ ] Proper error messages

### Implementation Notes
```python
class SubagentCoordinator:
    def __init__(self, model="ollama-cloud/qwen3.5:397b", timeout=30):
        self.model = model
        self.timeout = timeout
    
    def analyze_screenshot(self, screenshot_path: str, max_retries=3) -> dict:
        # Build command
        # Execute with retry
        # Parse and validate JSON
        pass
```

---

## Task 2: Create Screenshot Manager

**File**: `weibo/lib/screenshot_manager.py`

### Description
Manage screenshot capture, naming, and storage.

### Acceptance Criteria
- [ ] `ScreenshotManager` class
- [ ] Timestamped filename generation
- [ ] Directory creation if not exists
- [ ] Integration with computer-mcp screenshot tool
- [ ] Configurable base directory
- [ ] Optional auto-cleanup

### Implementation Notes
```python
class ScreenshotManager:
    def __init__(self, base_dir="screenshots/weibo/"):
        pass
    
    def capture_and_save(self, context="home") -> str:
        # Capture via computer-mcp
        # Save with timestamp
        # Return filepath
        pass
```

---

## Task 3: Create Main Script

**File**: `weibo/post-text/scripts/post_text_enhanced.py`

### Description
Main script implementing the enhanced workflow.

### Acceptance Criteria
- [ ] Argument parsing (--content-file, --max-retries, --screenshot-dir)
- [ ] Read content from file
- [ ] Window management (find/open weibo)
- [ ] Screenshot capture and save
- [ ] Subagent analysis with retry
- [ ] Coordinate calculation (4-point to center)
- [ ] Click input box
- [ ] Type content
- [ ] Click send button
- [ ] JSON output with results
- [ ] Proper error handling

### Command Line Interface
```bash
python post_text_enhanced.py \
  --content-file content.txt \
  [--max-retries 3] \
  [--screenshot-dir screenshots/weibo/]
```

### Output Format
```json
{
  "success": true,
  "message": "微博发送完成",
  "screenshot_path": "screenshots/weibo/weibo_home_20250419_143052.png",
  "elements_detected": {
    "input_box": [0.47, 0.25, 0.61, 0.30],
    "send_button": [0.72, 0.25, 0.78, 0.30]
  },
  "content_file": "content.txt",
  "content_length": 42
}
```

---

## Task 4: Add Coordinate Conversion Functions

**File**: `weibo/lib/computer_mcp_client.py` (update)

### Description
Add bbox to center point conversion functions.

### Acceptance Criteria
- [ ] `bbox_to_center(bbox)` function
- [ ] Input validation (4 elements, 0-1 range)
- [ ] Calculate center point correctly
- [ ] Unit tests

### Implementation
```python
def bbox_to_center(bbox: list) -> tuple:
    """Convert [X1,Y1,X2,Y2] to (center_x, center_y)"""
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2, (y1 + y2) / 2)
```

---

## Task 5: Create Tests

**Files**:
- `weibo/tests/test_subagent_coordinator.py`
- `weibo/tests/test_screenshot_manager.py`
- `weibo/tests/test_post_text_enhanced.py`

### Description
Unit and integration tests.

### Acceptance Criteria
- [ ] Test bbox_to_center conversion
- [ ] Test coordinate validation
- [ ] Test retry logic (mock failures)
- [ ] Test JSON parsing
- [ ] Test file reading
- [ ] Mock subagent responses
- [ ] Integration test with mock MCP

---

## Task 6: Update Documentation

**Files**:
- `weibo/post-text/SKILL.md` (update)
- `weibo/README.md` (update)

### Description
Update documentation to include new enhanced script.

### Acceptance Criteria
- [ ] Document new post_text_enhanced.py
- [ ] Explain subagent approach
- [ ] Provide usage examples
- [ ] Document coordinate system
- [ ] Add troubleshooting section

---

## Task 7: Manual Testing

### Test Cases

#### Case 1: Happy Path
- [ ] Script executes successfully
- [ ] Screenshot saved correctly
- [ ] Subagent returns valid JSON
- [ ] Content posted to weibo

#### Case 2: Retry Logic
- [ ] Subagent fails once, retry succeeds
- [ ] Subagent fails 3 times, script exits with error

#### Case 3: Invalid Input
- [ ] Missing content file → error
- [ ] Invalid content file path → error

#### Case 4: Coordinate Validation
- [ ] Out of range coordinates → clamp or error
- [ ] Malformed JSON → retry

---

## Dependencies

### Blocked By
- None (can start immediately)

### Blocks
- None

---

## Estimates

| Task | Estimate |
|------|----------|
| Task 1: Subagent Coordinator | 2 hours |
| Task 2: Screenshot Manager | 1 hour |
| Task 3: Main Script | 3 hours |
| Task 4: Coordinate Conversion | 30 minutes |
| Task 5: Tests | 2 hours |
| Task 6: Documentation | 1 hour |
| Task 7: Manual Testing | 2 hours |
| **Total** | **~12 hours** |
