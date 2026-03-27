---
name: check-login
description: |
  检查小红书账号登录状态。

  当用户说以下任何内容时触发此 skill：
  - "检查小红书登录状态"
  - "查看小红书是否登录"
  - "小红书登录了吗"
  - "检查登录状态"
  - 任何涉及检查小红书账号登录状态的请求

  此 skill 自动完成：
  - 启动浏览器并加载已保存的 Cookie
  - 访问小红书创作者中心
  - 检测登录状态并返回用户信息

  使用前需确保已通过 get-qrcode 完成登录。

compatibility: |
  - Node.js 环境
  - Playwright
  - 依赖：playwright
---

# 检查小红书登录状态

## 工作流程

1. 启动浏览器（加载已保存的 Cookie）
2. 访问小红书创作者中心
3. 检测页面元素判断登录状态
4. 返回登录状态和用户信息

## 输入参数

无必需参数。

可选参数：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| dataPath | string | 否 | 数据存储路径，默认为 `./data` |

## 输出结果

```json
{
  "success": true,
  "isLoggedIn": true,
  "username": "用户昵称",
  "userId": "用户ID",
  "message": "已登录"
}
```

未登录时：
```json
{
  "success": true,
  "isLoggedIn": false,
  "message": "未登录，请先执行 get-qrcode 获取登录二维码"
}
```

## 配置要求

环境变量：
- `XHS_DATA_PATH`: 数据存储路径（可选，默认 `./data`）

## 使用示例

```
用户：检查小红书登录状态
结果：已登录，用户名: xxx，用户ID: xxx

用户：小红书登录了吗
结果：未登录，请先执行 get-qrcode 获取登录二维码
```

## 注意事项

1. 首次使用需先通过 get-qrcode 完成登录
2. Cookie 有效期通常为几天到几周，过期后需重新登录
3. 同一账号只能在一个浏览器实例中保持登录状态
