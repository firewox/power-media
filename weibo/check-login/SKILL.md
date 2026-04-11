---
name: weibo-check-login
description: |
  使用 computer-mcp 检查微博登录状态。
  
  当用户说以下任何内容时触发此 skill：
  - "检查微博登录状态"
  - "微博是否登录"
  - "查看微博登录"
  - "check weibo login"
  - "微博登录了吗"
  - 任何涉及检查微博登录状态的请求
  
  脚本执行：
  ```bash
  python weibo/check-login/scripts/check_login.py
  ```
  
  脚本工作流程：
  1. 尝试查找现有微博窗口
  2. 如未找到，打开默认浏览器并访问 weibo.com（复用已登录状态）
  3. 调用 computer-mcp/inspect_screen 识别界面元素
  4. 分析 OCR 结果判断登录状态
  5. 返回登录状态和用户名
  
  依赖：
  - computer-mcp (focus_window, inspect_screen, open_browser, type_text, press_key)
  - Python 3.8+
  - 默认浏览器（Edge/Chrome/Firefox）

compatibility:
  - computer-mcp >= 1.0
  - Python >= 3.8
  - Windows 10/11
  - Edge / Chrome / Firefox 浏览器
---

# 检查微博登录状态

## 脚本调用

### 直接执行脚本
```bash
python weibo/check-login/scripts/check_login.py
```

### 从其他脚本调用
```python
import subprocess
import json

result = subprocess.run(
    ["python", "weibo/check-login/scripts/check_login.py"],
    capture_output=True,
    text=True
)

# 解析 JSON 输出（最后一行）
output_lines = result.stdout.strip().split('\n')
json_line = output_lines[-1]
status = json.loads(json_line)

if status["loggedIn"]:
    print(f"已登录: {status['userName']}")
else:
    print("未登录")
```

## 工作流程（computer-mcp）

脚本内部执行以下步骤：

### Step 1: 查找或打开微博窗口

首先尝试聚焦现有的微博窗口。如果找不到，打开默认浏览器并访问 weibo.com，复用已保存的登录状态（Cookie）。

**Python 实现：**
```python
from computer_mcp_client import WeiboAutomation

weibo = WeiboAutomation()
weibo.find_or_open_weibo()  # 自动处理
```

### Step 2: 截图并识别界面
使用 `inspect_screen` 获取界面 OCR 结果。

### Step 3: 分析登录状态
从 OCR 结果中检查：
- **未登录**：检测到 "登录" / "注册" 按钮
- **已登录**：检测到用户名（如 "xxx 的微博"）或用户头像、用户昵称

## 输出结果

```json
{
  "loggedIn": true,
  "userName": "xxx"
}
```

或

```json
{
  "loggedIn": false,
  "userName": null
}
```

## 使用示例

**示例 1：**
```
用户：检查微博登录状态
AI：调用 computer-mcp 检查...
结果：已登录，用户名: xxx
```

**示例 2：**
```
用户：微博是否登录？
AI：调用 computer-mcp 检查...
结果：未登录，请先登录
```

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 找不到微博窗口 | 自动打开默认浏览器并访问 weibo.com |
| 浏览器打开失败 | 提示用户手动打开浏览器 |
| OCR 识别失败 | 重试截图，最多 3 次 |
| 页面加载超时 | 等待 5 秒后重试 |

## 注意事项

1. 支持自动打开默认浏览器（Edge/Chrome/Firefox）
2. 会复用浏览器中已保存的登录状态（Cookie）
3. 如果已在浏览器中登录，打开后会自动保持登录
4. 确保浏览器允许复用已有会话（非隐私模式）
5. 窗口标题应包含 "微博" 以便 focus_window 识别
