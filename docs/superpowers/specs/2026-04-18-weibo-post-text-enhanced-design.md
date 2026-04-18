# Weibo Post Text Enhanced - Design Document

**日期**: 2026-04-18  
**作者**: Claude  
**状态**: Ready for Implementation  
**关联 Change**: [openspec/weibo-post-text-enhanced](../openspec/changes/weibo-post-text-enhanced/)

---

## 1. 背景与目标

### 1.1 问题

当前微博 `post-text` skill 使用固定百分比坐标，存在以下问题：
- **坐标不灵活**：不同分辨率、不同浏览器窗口大小下坐标偏差大
- **无智能识别**：无法自动适应微博页面布局变化
- **无元素检测**：不能自动识别输入框、发送按钮位置

### 1.2 目标

实现增强版微博发送功能，引入子智能体进行截图分析和元素检测：

1. **子智能体视觉分析**
   - 使用多模态模型（ollama-cloud/qwen3.5:397b）分析截图
   - 自动识别输入框、发送按钮、头条文章按钮位置
   - 返回四位百分比坐标 [X1,Y1,X2,Y2]

2. **动态坐标计算**
   - 根据识别结果计算元素中心点
   - 支持不同分辨率和窗口大小

3. **截图存档**
   - 所有截图按时间戳命名保存
   - 便于调试和审计

4. **文件输入**
   - 支持从文本文件读取微博内容
   - 便于批量操作和长文本管理

---

## 2. 架构设计

### 2.1 整体架构

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

### 2.2 组件设计

#### 2.2.1 Main Script: `post_text_enhanced.py`

**职责**:
- 解析命令行参数
- 协调工作流
- 处理错误和重试
- 输出结果

**接口**:
```python
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--content-file", required=True)
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--screenshot-dir", default="screenshots/weibo/")
    args = parser.parse_args()
    # Workflow implementation
```

#### 2.2.2 Subagent Coordinator: `subagent_coordinator.py`

**职责**:
- 构建和执行 opencode 命令
- 解析 JSON 输出
- 实现重试逻辑
- 处理错误

**接口**:
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

#### 2.2.3 Screenshot Manager

**职责**:
- 生成带时间戳的文件名
- 确保目录存在
- 保存截图

**命名规范**:
```
screenshots/weibo/weibo_home_YYYYMMDD_HHMMSS.png
```

---

## 3. 子智能体接口

### 3.1 命令格式

```bash
opencode run -m ollama-cloud/qwen3.5:397b \
  "请识别这张微博主页截图中的微博发文文本输入框、发送按钮、头条文章按钮，以纯JSON格式返回结果，无多余描述。坐标使用归一化小数格式 [X1,Y1,X2,Y2]，数值范围 0~1，代表元素相对于整张图片的左上角与右下角位置。返回格式：{\"input_box\": [X1,Y1,X2,Y2], \"send_button\": [X1,Y1,X2,Y2], \"headline_article_button\": [X1,Y1,X2,Y2]}" \
  -f "{screenshot_path}"
```

### 3.2 Prompt 模板

```python
SUBAGENT_PROMPT = """请识别这张微博主页截图中的微博发文文本输入框、发送按钮、头条文章按钮，以纯JSON格式返回结果，无多余描述。

坐标使用归一化小数格式 [X1,Y1,X2,Y2]，数值范围 0~1，代表元素相对于整张图片的左上角与右下角位置。

返回格式：
{
  "input_box": [X1,Y1,X2,Y2],
  "send_button": [X1,Y1,X2,Y2],
  "headline_article_button": [X1,Y1,X2,Y2]
}

注意：
1. 只返回JSON，不要任何其他文字
2. 坐标必须是0-1之间的浮点数
3. [X1,Y1]是左上角，[X2,Y2]是右下角
4. 如果某个元素找不到，返回null"""
```

### 3.3 返回格式

**成功响应**:
```json
{
  "input_box": [0.47, 0.25, 0.61, 0.30],
  "send_button": [0.72, 0.25, 0.78, 0.30],
  "headline_article_button": [0.15, 0.35, 0.25, 0.40]
}
```

**部分成功**（某些元素未找到）:
```json
{
  "input_box": [0.47, 0.25, 0.61, 0.30],
  "send_button": [0.72, 0.25, 0.78, 0.30],
  "headline_article_button": null
}
```

### 3.4 验证规则

1. **类型检查**: 所有坐标必须是 float
2. **范围检查**: 0.0 <= coordinate <= 1.0
3. **顺序检查**: X1 < X2, Y1 < Y2
4. **必填字段**: 必须有 "input_box" 和 "send_button"
5. **可选字段**: "headline_article_button" 可以为 null

---

## 4. 坐标系统

### 4.1 坐标类型

| 类型 | 格式 | 说明 |
|------|------|------|
| BBox Percentage | [X1, Y1, X2, Y2] | 来自子智能体，元素边界框 |
| Center Percentage | (center_x, center_y) | 内部使用，元素中心点 |
| Screen Pixel | (screen_x, screen_y) | pyautogui 使用，屏幕像素 |

### 4.2 转换函数

#### bbox_to_center

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

#### center_to_screen

```python
def center_to_screen(center_pct: tuple, window_rect: dict) -> tuple:
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

### 4.3 完整转换示例

```python
# Input from subagent
bbox = [0.47, 0.25, 0.61, 0.30]
window_rect = {
    "left": 100,
    "top": 50,
    "width": 1200,
    "height": 800
}

# Step 1: bbox to center percentage
center_x = (0.47 + 0.61) / 2  # = 0.54
center_y = (0.25 + 0.30) / 2  # = 0.275

# Step 2: center to screen pixels
screen_x = 100 + 1200 * 0.54  # = 748
screen_y = 50 + 800 * 0.275   # = 270

# Result for pyautogui.click()
(748, 270)
```

---

## 5. 工作流程

### 5.1 完整流程图

```
1. 解析参数 (--content-file)
   ↓
2. 打开/聚焦微博窗口
   ↓
3. 截图保存 (screenshots/weibo/YYYYMMDD_HHMMSS.png)
   ↓
4. 子智能体分析 (opencode run)
   ↓ 成功？
   ├─ 是 → 继续
   └─ 否 → 重试 (最多3次)
          ↓ 3次都失败
          报错退出
   ↓
5. 解析 JSON 坐标
   ↓
6. 计算中心点
   ↓
7. 从文件读取内容
   ↓
8. 点击输入框
   ↓
9. 填入内容
   ↓
10. 点击发送按钮
    ↓
11. 返回结果
```

### 5.2 命令行接口

```bash
python weibo/post-text/scripts/post_text_enhanced.py \
    --content-file weibo_content.txt \
    [--max-retries 3] \
    [--screenshot-dir screenshots/weibo/]
```

### 5.3 输出格式

```json
{
  "success": true,
  "message": "微博发送完成",
  "screenshot_path": "screenshots/weibo/weibo_home_20250419_143052.png",
  "elements_detected": {
    "input_box": [0.47, 0.25, 0.61, 0.30],
    "send_button": [0.72, 0.25, 0.78, 0.30]
  },
  "content_file": "weibo_content.txt",
  "content_length": 42
}
```

---

## 6. 错误处理

### 6.1 重试策略

| 错误类型 | 重试次数 | 操作 |
|----------|----------|------|
| 子智能体超时 | 3 | 等待后重试 |
| JSON 解析错误 | 3 | 使用相同截图重试 |
| 缺少必要字段 | 3 | 重试 |
| 窗口未找到 | 0 | 立即失败 |
| 内容文件不存在 | 0 | 立即失败 |

### 6.2 错误输出

```json
{
  "success": false,
  "error": "Subagent analysis failed after 3 retries",
  "screenshot_path": "screenshots/weibo/weibo_home_20250419_143052.png",
  "last_error": "JSON parse error: Expecting value: line 1 column 1"
}
```

---

## 7. 文件结构

```
weibo/
├── lib/
│   ├── computer_mcp_client.py      # 现有：窗口管理、坐标转换
│   ├── subagent_coordinator.py     # 新增：子智能体协调器
│   └── screenshot_manager.py       # 新增：截图管理器
├── post-text/
│   ├── SKILL.md                    # 现有：Skill定义
│   ├── scripts/
│   │   ├── post_text.py            # 现有：原脚本
│   │   └── post_text_enhanced.py   # 新增：增强版脚本
│   └── usage.md                    # 更新：使用文档
└── tests/                          # 新增：测试目录
    ├── test_subagent_coordinator.py
    ├── test_screenshot_manager.py
    └── test_post_text_enhanced.py
```

---

## 8. 依赖关系

### 8.1 内部依赖

- `weibo/lib/computer_mcp_client.py` - 窗口管理、坐标转换
- `computer-mcp/server.py` - Screenshot, click, type_text tools

### 8.2 外部依赖

- `opencode` CLI - 子智能体执行
- `ollama-cloud/qwen3.5:397b` - 多模态模型

---

## 9. 性能考量

| 操作 | 预计时间 | 说明 |
|------|----------|------|
| 截图 | < 1s | 使用现有 mss 实现 |
| 子智能体分析 | 5-10s | 取决于模型响应 |
| 窗口操作 | < 2s | pyautogui 快速 |
| 总计（无重试） | 10-15s | 可接受 |
| 总计（3次重试） | 30-45s | 最坏情况 |

---

## 10. 安全考虑

1. **内容文件路径**: 验证文件存在且可读
2. **截图存储**: 确保截图目录可写
3. **命令注入**: 清理 bash 命令中的路径
4. **子智能体输出**: 解析前验证 JSON 结构

---

## 11. 相关文档

- [openspec change](../openspec/changes/weibo-post-text-enhanced/) - OpenSpec 完整规范
- [weibo/session-weibo.md](../../weibo/session-weibo.md) - 微博开发记录
- [坐标映射规则](../COORDINATE-MAPPING-RULE.md) - 项目坐标规范
- [computer-mcp 文档](../../computer-mcp/README.md) - MCP 工具说明
