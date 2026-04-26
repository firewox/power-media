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

---

## 增强版脚本 (post_text_enhanced.py)

使用子智能体自动识别界面元素的增强版发送脚本。

### 特点

- **自动元素识别**：使用 ollama-cloud/qwen3.5:397b 分析截图，自动定位输入框和发送按钮
- **四位坐标支持**：子智能体返回 [X1,Y1,X2,Y2] 边界框，自动计算中心点
- **截图存档**：所有截图按时间戳保存到 `screenshots/weibo/`
- **文件输入**：从文本文件读取微博内容
- **智能重试**：子智能体分析失败时自动重试（默认3次）

### 使用方法

```bash
# 基本使用
python weibo/post-text/scripts/post_text_enhanced.py --content-file content.txt

# 指定重试次数
python weibo/post-text/scripts/post_text_enhanced.py \
  --content-file content.txt \
  --max-retries 5

# 指定截图目录
python weibo/post-text/scripts/post_text_enhanced.py \
  --content-file content.txt \
  --screenshot-dir ./my_screenshots/
```

### 工作流程

1. 打开/聚焦微博窗口
2. 截图并保存（命名：weibo_home_YYYYMMDD_HHMMSS.png）
3. 启动子智能体分析截图
4. 解析 JSON 坐标 [X1,Y1,X2,Y2]
5. 计算中心点并转换为屏幕坐标
6. 点击输入框
7. 从文件读取内容并填入
8. 点击发送按钮
9. 完成（无验证）

### 子智能体调用

```bash
opencode run -m ollama-cloud/qwen3.5:397b \
  "请识别这张微博主页截图中的微博发文文本输入框、发送按钮..." \
  -f "screenshots/weibo/weibo_home_20250419_143052.png"
```

返回格式：
```json
{
  "input_box": [0.47, 0.25, 0.61, 0.30],
  "send_button": [0.72, 0.25, 0.78, 0.30],
  "headline_article_button": [0.15, 0.35, 0.25, 0.40]
}
```

### 对比

| 特性 | post_text.py | post_text_enhanced.py |
|------|-------------|----------------------|
| 坐标来源 | 手动提供 | 子智能体自动识别 |
| 坐标格式 | 中心点百分比 | 四位边界框 |
| 内容输入 | 命令行参数 | 文件读取 |
| 截图存档 | 否 | 是 |
| 智能重试 | 否 | 是（3次） |
| 适用场景 | 已知坐标 | 动态布局 |
