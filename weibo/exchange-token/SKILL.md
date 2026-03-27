---
name: exchange-token
description: |
  用授权码换取微博 Access Token。

  当用户说以下任何内容时触发此 skill：
  - "换取微博 Token"
  - "用 code 换 token"
  - "获取微博 Access Token"
  - "交换授权码"
  - "exchange weibo token"
  - 任何涉及用授权码换取微博 Access Token 的请求

  此 skill 自动完成：
  - 验证环境变量
  - 调用微博 OAuth2 接口
  - 解析并显示 Token 信息
  - 提供环境变量设置指引

  使用前必须配置微博开放平台凭据。

compatibility: |
  - Python 3.8+
  - 微博开放平台 App Key 和 App Secret
  - 有效的授权码（code）
  - 依赖：requests, python-dotenv
---

# 用授权码换取 Access Token

## 工作流程

1. 检查环境变量（WEIBO_APP_KEY, WEIBO_APP_SECRET, WEIBO_REDIRECT_URI）
2. 验证授权码参数
3. 调用微博 OAuth2 接口换取 Token
4. 显示 Token 信息和设置指引

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | 是 | 用户授权后从回调 URL 获取的授权码 |

## 输出结果

```
============================================================
Access Token 获取成功!
============================================================

Access Token: 2.00xxxxxxxxxxxxxxxx
过期时间: 7200 秒
用户 UID: 1234567890

请设置环境变量:
  export WEIBO_ACCESS_TOKEN="2.00xxxxxxxxxxxxxxxx"

或将以下内容添加到 .env 文件:
WEIBO_ACCESS_TOKEN=2.00xxxxxxxxxxxxxxxx

============================================================
```

## 配置要求

必须设置环境变量：

```bash
export WEIBO_APP_KEY="你的 App Key"
export WEIBO_APP_SECRET="你的 App Secret"
export WEIBO_REDIRECT_URI="https://yourdomain.com/callback"
```

## 使用示例

**示例 1：**
```
用户：用授权码 abc123 换取 token
结果：
  Access Token: 2.00xxx
  过期时间: 7200 秒
  用户 UID: 1234567890
  
  请设置环境变量: export WEIBO_ACCESS_TOKEN="2.00xxx"
```

**示例 2：**
```
用户：我获取到了 code=xyz789，怎么换 token？
结果：显示换取 token 的结果
```

## 错误处理

| 错误 | 含义 | 解决方案 |
|------|------|---------|
| `invalid_grant` | 授权码无效或过期 | 重新获取授权码 |
| `redirect_uri_mismatch` | 回调地址不匹配 | 检查 WEIBO_REDIRECT_URI 配置 |
| `invalid_client` | App Key 或 Secret 错误 | 检查环境变量配置 |

## 注意事项

1. **Token 有效期**：默认 2 小时，无 refresh token
2. **授权码时效**：code 获取后需立即使用，有效期很短
3. **安全存储**：Access Token 是敏感信息，请妥善保管

## 依赖安装

```bash
cd /mnt/d/08_tmp/02_media/power-media/weibo/exchange-token/scripts
pip3 install requests python-dotenv
```
