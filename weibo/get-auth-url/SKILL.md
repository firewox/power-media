---
name: get-auth-url
description: |
  获取微博 OAuth2 授权 URL。

  当用户说以下任何内容时触发此 skill：
  - "获取微博授权链接"
  - "微博授权 URL"
  - "如何授权微博"
  - "微博 OAuth 授权"
  - "get weibo auth url"
  - 任何涉及获取微博 OAuth2 授权 URL 的请求

  此 skill 自动生成：
  - OAuth2 授权 URL
  - 授权步骤说明
  - 下一步操作指引

  使用前必须配置微博开放平台凭据。

compatibility: |
  - Python 3.8+
  - 微博开放平台 App Key 和 App Secret
  - 已配置的 Redirect URI
  - 依赖：python-dotenv
---

# 获取微博 OAuth2 授权 URL

## 工作流程

1. 检查环境变量（WEIBO_APP_KEY, WEIBO_APP_SECRET, WEIBO_REDIRECT_URI）
2. 生成 OAuth2 授权 URL
3. 输出授权步骤说明

## 输入参数

无

## 输出结果

```
============================================================
微博 OAuth2 授权
============================================================

请按以下步骤操作:

1. 在浏览器中打开以下 URL:
   https://api.weibo.com/oauth2/authorize?client_id=xxx...

2. 登录微博账号并授权应用

3. 授权后，浏览器将跳转到回调地址，
   从 URL 中获取 'code' 参数值
   例如: https://yourdomain.com/callback?code=xxx

4. 运行以下命令换取 Access Token:
   python3 exchange-token/scripts/exchange-token.py <code>

============================================================
```

## 配置要求

必须设置环境变量：

```bash
export WEIBO_APP_KEY="你的 App Key"
export WEIBO_APP_SECRET="你的 App Secret"
export WEIBO_REDIRECT_URI="https://yourdomain.com/callback"
```

或在项目根目录创建 `.env` 文件。

## 授权流程

1. **获取授权 URL**（本 skill）
2. **用户授权**（用户在浏览器中完成）
3. **获取授权码**（从回调 URL 中提取 code）
4. **换取 Access Token**（使用 exchange-token skill）

## 使用示例

**示例 1：**
```
用户：获取微博授权链接
结果：
  请在浏览器中打开以下 URL:
  https://api.weibo.com/oauth2/authorize?client_id=xxx...
  
  授权后，从回调 URL 获取 code 参数
```

**示例 2：**
```
用户：如何进行微博 OAuth 授权？
结果：显示完整的授权步骤说明
```

## 注意事项

1. **回调地址**：必须在微博开放平台配置的回调地址一致
2. **授权码有效期**：code 有效期较短，获取后需立即换取 token
3. **安全提醒**：不要将 App Secret 暴露给客户端

## 依赖安装

```bash
cd /mnt/d/08_tmp/02_media/power-media/weibo/get-auth-url/scripts
# 无需额外依赖，仅使用标准库
```
