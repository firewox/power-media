import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from screen_inspector import take_screenshot, inspect_screen

def test_take_screenshot_returns_path():
    result = take_screenshot()
    assert result["success"] is True
    assert os.path.exists(result["path"])
    assert result["path"].endswith(".png")

def test_inspect_screen_returns_structure():
    result = inspect_screen()
    assert "screenshot_path" in result
    assert "ocr_blocks" in result
    assert isinstance(result["ocr_blocks"], list)
