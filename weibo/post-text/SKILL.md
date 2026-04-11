---
name: weibo-post-text
description: |
  使用 computer-mcp 发布纯文本微博。
  
  当用户说以下任何内容时触发此 skill：
  - "发微博"
  - "发布微博"
  - "发送微博"
  - "发条微博"
  - "post weibo"
  - "发一条微博"
  - 任何涉及发布纯文本微博的请求
  
  脚本执行：
  ```bash
  python weibo/post-text/scripts/post_text.py "微博内容"
  ```
  
  脚本工作流程：
  1. 验证内容长度（最多 140 字符）
  2. 查找或打开微博窗口（复用已登录状态）
  3. 检查登录状态
  4. 点击输入框，输入内容
  5. 点击发送按钮
  6. 验证发布结果
  
  依赖：
  - computer-mcp (focus_window, inspect_screen, click, type_text, confirm_action)
  - Python 3.8+
  - 默认浏览器（复用已登录状态）

compatibility:
  - computer-mcp >= 1.0
  - Python >= 3.8
  - Windows 10/11
  - Edge / Chrome / Firefox 浏览器
---

# 发布纯文本微博

## 脚本调用

### 直接执行脚本
```bash
# 基本用法
python weibo/post-text/scripts/post_text.py "这是一条测试微博"

# 跳过确认直接发布
python weibo/post-text/scripts/post_text.py "这是一条测试微博" --force
```

### 从其他脚本调用
```python
import subprocess
import json

result = subprocess.run(
    ["python", "weibo/post-text/scripts/post_text.py", "测试内容"],
    capture_output=True,
    text=True,
    input="\n"  # 自动确认
)

# 解析结果
output_lines = result.stdout.strip().split('\n')
json_line = output_lines[-1]
result_data = json.loads(json_line)

if result_data["success"]:
    print("发布成功!")
else:
    print(f"发布失败: {result_data.get('error')}")
```

## 工作流程（computer-mcp）

脚本内部执行以下步骤：

### Step 1: 检查登录状态并准备浏览器
脚本会自动：
- 查找现有微博窗口
- 如未找到，打开默认浏览器并访问 weibo.com（复用已登录状态）
- 检查登录状态

如果未登录，返回错误提示。

### Step 2: 聚焦微博窗口
```json
{
  "tool": "computer-mcp/focus_window",
  "params": {"title": "微博"}
}
```

### Step 3: 识别输入框
```json
{
  "tool": "computer-mcp/inspect_screen",
  "params": {}
}
```

从 OCR 结果中定位 "有什么新鲜事想告诉大家" 的坐标。

### Step 4: 点击输入框
```json
{
  "tool": "computer-mcp/click",
  "params": {"x": <detected_x>, "y": <detected_y>}
}
```

### Step 5: 输入内容
```json
{
  "tool": "computer-mcp/type_text",
  "params": {"text": "{{content}}"}
}
```

### Step 6: 找到并点击发送按钮
```json
{
  "tool": "computer-mcp/inspect_screen",
  "params": {}
}
```

从 OCR 结果中找到 "发送" 按钮坐标并点击：
```json
{
  "tool": "computer-mcp/click",
  "params": {"x": <send_button_x>, "y": <send_button_y>}
}
```

### Step 7: 确认发布
```json
{
  "tool": "computer-mcp/confirm_action",
  "params": {"action_description": "确认发布微博？"}
}
```

### Step 8: 验证结果
再次调用 `inspect_screen` 检查是否有 "发布成功" 提示。

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| text | string | 是 | 微博内容，最多 140 字符 |

## 输出结果

```json
{
  "success": true,
  "message": "发布成功",
  "url": "https://weibo.com/xxx/xxx"
}
```

或

```json
{
  "success": false,
  "error": "错误信息"
}
```

## 使用示例

**示例 1：**
```
用户：发条微博说"今天天气真好"
AI：
  1. 检查登录状态 ✓
  2. 聚焦微博窗口
  3. 点击输入框
  4. 输入内容
  5. 点击发送
  6. 确认发布
结果：发布成功！
```

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 未登录 | 返回错误，提示先执行 weibo-login |
| 找不到输入框 | 重试截图，或提示用户检查页面 |
| 内容超长 | Skill 层校验，拒绝执行（>140字符） |
| 发送失败 | 返回错误信息 |

## 注意事项

1. 支持自动打开默认浏览器（Edge/Chrome/Firefox）
2. 会复用浏览器中已保存的登录状态（Cookie）
3. 如已在浏览器中登录微博，打开后会自动保持登录
4. 确保浏览器允许复用已有会话（非隐私模式）
5. 确保微博窗口未被最小化
6. 内容长度限制 140 字符
7. 高风险操作需人工确认
