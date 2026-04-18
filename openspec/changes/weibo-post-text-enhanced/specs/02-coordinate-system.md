# Spec: Coordinate System

## Overview

定义四位百分比坐标与屏幕坐标的转换规则。

## Coordinate Types

### 1. BBox Percentage (from Subagent)

```
[X1, Y1, X2, Y2] where:
- X1: Left edge (0.0 - 1.0)
- Y1: Top edge (0.0 - 1.0)
- X2: Right edge (0.0 - 1.0)
- Y2: Bottom edge (0.0 - 1.0)
- Constraint: X1 < X2, Y1 < Y2
```

### 2. Center Percentage (internal)

```
(center_x, center_y) where:
- center_x = (X1 + X2) / 2
- center_y = (Y1 + Y2) / 2
- Range: 0.0 - 1.0
```

### 3. Screen Pixel (for pyautogui)

```
(screen_x, screen_y) where:
- screen_x = window_left + width * center_x
- screen_y = window_top + height * center_y
- Unit: pixels
```

## Conversion Functions

### bbox_to_center

```python
def bbox_to_center(bbox: list) -> tuple:
    """
    Convert bbox [X1,Y1,X2,Y2] to center point (center_x, center_y)
    
    Args:
        bbox: [X1, Y1, X2, Y2] in percentage (0-1)
    
    Returns:
        (center_x, center_y) in percentage
    """
    x1, y1, x2, y2 = bbox
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    return (center_x, center_y)
```

### center_to_screen

```python
def center_to_screen(
    center_pct: tuple,
    window_rect: dict
) -> tuple:
    """
    Convert center percentage to screen pixels
    
    Args:
        center_pct: (center_x, center_y) in percentage (0-1)
        window_rect: {"left": int, "top": int, "width": int, "height": int}
    
    Returns:
        (screen_x, screen_y) in pixels
    """
    center_x, center_y = center_pct
    screen_x = window_rect["left"] + int(window_rect["width"] * center_x)
    screen_y = window_rect["top"] + int(window_rect["height"] * center_y)
    return (screen_x, screen_y)
```

### complete conversion pipeline

```python
def bbox_to_screen(bbox: list, window_rect: dict) -> tuple:
    """
    Complete conversion: bbox -> center -> screen
    """
    center_pct = bbox_to_center(bbox)
    screen_coords = center_to_screen(center_pct, window_rect)
    return screen_coords
```

## Example

### Input

```python
bbox = [0.47, 0.25, 0.61, 0.30]
window_rect = {
    "left": 100,
    "top": 50,
    "width": 1200,
    "height": 800
}
```

### Calculation

```
Step 1: bbox_to_center
  center_x = (0.47 + 0.61) / 2 = 0.54
  center_y = (0.25 + 0.30) / 2 = 0.275

Step 2: center_to_screen
  screen_x = 100 + 1200 * 0.54 = 100 + 648 = 748
  screen_y = 50 + 800 * 0.275 = 50 + 220 = 270
```

### Output

```python
(748, 270)  # screen coordinates for pyautogui.click()
```

## Edge Cases

| Case | Handling |
|------|----------|
| X1 >= X2 | Log warning, swap values |
| Y1 >= Y2 | Log warning, swap values |
| Coordinate > 1.0 | Clamp to 1.0 |
| Coordinate < 0.0 | Clamp to 0.0 |
| bbox is null | Raise ValueError |
