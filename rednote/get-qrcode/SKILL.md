---
name: rednote-get-qrcode
description: |
  获取小红书创作者平台登录二维码。

  当用户说以下任何内容时触发此 skill：
  - "获取小红书登录二维码"
  - "小红书扫码登录"
  - "获取登录二维码"
  - "小红书登录"
  - 任何涉及获取小红书登录二维码的请求

  工作流程：
  1. 聚焦/打开创作者平台窗口
  2. 检查是否已登录
  3. 如未登录，截图显示二维码
  4. 循环检测登录状态（最多 2 分钟）

  使用前需确保浏览器已打开。

compatibility: |
  - computer-mcp >= 1.0
  - Windows 10/11
  - Edge / Chrome 浏览器
  - Python 3.8+
---

# 获取小红书创作者平台登录二维码

## 工作流程

### Step 1: 聚焦创作者平台窗口

使用 `rednote_automation.find_or_open_creator()` 自动查找或打开窗口。

### Step 2: 检查是否已登录

调用 `rednote_automation.check_login_status()` 截图，AI 分析：
- 已登录 → 提示用户已登录，无需扫码
- 未登录 → 继续下一步

### Step 3: 截图显示二维码

```json
{"tool": "computer-mcp/inspect_screen", "params": {}}
```

返回截图，二维码应显示在页面中央。

### Step 4: 等待用户扫码

循环检测登录状态（每 3 秒一次，最多 40 次 = 2 分钟）：
1. 截图检查登录状态
2. AI 分析是否已登录
3. 如已登录，退出循环
4. 如超时，提示刷新页面重新获取二维码

## 输入参数

无必需参数。

可选参数：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| timeout | int | 否 | 超时时间（秒），默认 120 |
| checkInterval | int | 否 | 检查间隔（秒），默认 3 |

## 输出结果

**成功（显示二维码）**:
```json
{
  "success": true,
  "status": "showing_qrcode",
  "qrcode_path": "D:\\...\\rednote_qr_xxx.png",
  "message": "请使用小红书 APP 扫码登录",
  "timeout": 120
}
```

**已登录（无需扫码）**:
```json
{
  "success": true,
  "status": "already_logged_in",
  "message": "已登录，无需扫码"
}
```

**登录成功**:
```json
{
  "success": true,
  "status": "login_success",
  "message": "登录成功",
  "elapsed": 30
}
```

**超时**:
```json
{
  "success": false,
  "status": "timeout",
  "message": "登录超时（120 秒），请刷新页面重新获取二维码",
  "elapsed": 120
}
```

## 配置要求

环境变量：
- 无特殊要求

## 使用示例

```
用户：获取小红书登录二维码
结果：二维码已显示，请使用小红书 APP 扫码

用户：小红书扫码登录
结果：已登录，无需扫码

用户：获取登录二维码
结果：登录成功，耗时 25 秒
```

## 注意事项

1. 二维码有效期约 2 分钟
2. 超时需刷新页面重新获取
3. 需要小红书 APP 扫码
4. 同一账号只能在一个浏览器实例中保持登录状态
5. 登录成功后 Cookie 会自动保存，下次无需重新登录
