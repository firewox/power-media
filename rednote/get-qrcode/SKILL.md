---
name: get-qrcode
description: |
  获取小红书登录二维码。

  当用户说以下任何内容时触发此 skill：
  - "获取小红书登录二维码"
  - "小红书登录二维码"
  - "我要登录小红书"
  - "登录小红书"
  - 任何涉及获取小红书登录二维码的请求

  此 skill 自动完成：
  - 启动浏览器并访问小红书登录页面
  - 获取登录二维码
  - 等待用户扫码登录
  - 登录成功后保存 Cookie

  登录成功后，Cookie 会自动保存，后续可直接使用其他 skills。

compatibility: |
  - Node.js 环境
  - Playwright
  - 依赖：playwright
---

# 获取小红书登录二维码

## 工作流程

1. 启动浏览器
2. 访问小红书创作者中心登录页
3. 获取登录二维码图片
4. 显示二维码（控制台输出或保存文件）
5. 等待用户扫码
6. 检测登录成功后保存 Cookie
7. 返回登录结果

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| timeout | number | 否 | 等待扫码超时时间（秒），默认 120 |
| savePath | string | 否 | 二维码保存路径（可选） |
| dataPath | string | 否 | 数据存储路径，默认 `./data` |

## 输出结果

```json
{
  "success": true,
  "qrcodePath": "/path/to/qrcode.png",
  "message": "请扫描二维码登录",
  "deadline": "2026-03-28T12:00:00Z"
}
```

登录成功后：
```json
{
  "success": true,
  "isLoggedIn": true,
  "username": "用户昵称",
  "userId": "用户ID",
  "message": "登录成功"
}
```

## 配置要求

环境变量：
- `XHS_DATA_PATH`: 数据存储路径（可选，默认 `./data`）

## 使用示例

```
用户：获取小红书登录二维码
结果：二维码已保存到 /path/to/qrcode.png，请用小红书 App 扫码登录

用户：登录小红书
结果：登录成功，用户名: xxx
```

## 注意事项

1. 二维码有效期通常为 2-3 分钟，请尽快扫码
2. 同一账号只能在一个浏览器实例中保持登录状态
3. 登录成功后 Cookie 会自动保存，无需重复登录
4. 如果二维码过期，需要重新获取
