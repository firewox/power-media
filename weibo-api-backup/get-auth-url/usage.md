# get-auth-url

获取微博 OAuth2 授权 URL。

## 功能

- 生成 OAuth2 授权 URL
- 提供完整的授权步骤说明
- 验证环境变量配置

## 配置

设置环境变量：

```bash
export WEIBO_APP_KEY="你的 App Key"
export WEIBO_APP_SECRET="你的 App Secret"
export WEIBO_REDIRECT_URI="https://yourdomain.com/callback"
```

或在项目根目录创建 `.env` 文件。

## 使用方法

### CLI 使用

```bash
python3 scripts/get-auth-url.py
```

### 输出示例

```
============================================================
微博 OAuth2 授权
============================================================

请按以下步骤操作:

1. 在浏览器中打开以下 URL:
   https://api.weibo.com/oauth2/authorize?client_id=xxx&redirect_uri=xxx&response_type=code

2. 登录微博账号并授权应用

3. 授权后，浏览器将跳转到回调地址，
   从 URL 中获取 'code' 参数值
   例如: https://yourdomain.com/callback?code=abc123

4. 运行以下命令换取 Access Token:
   python3 exchange-token/scripts/exchange-token.py abc123

============================================================
```

## OAuth2 授权流程

完整的授权流程需要以下步骤：

1. **获取授权 URL**（本工具）
   ```bash
   python3 get-auth-url/scripts/get-auth-url.py
   ```

2. **用户授权**
   - 在浏览器中打开授权 URL
   - 登录微博账号
   - 点击授权按钮

3. **获取授权码**
   - 浏览器重定向到回调地址
   - 从 URL 中提取 `code` 参数
   - 例如：`?code=abc123`

4. **换取 Access Token**（使用 exchange-token）
   ```bash
   python3 exchange-token/scripts/exchange-token.py abc123
   ```

5. **保存 Token**
   ```bash
   export WEIBO_ACCESS_TOKEN="2.00xxx"
   ```

## 注意事项

- 回调地址必须与微博开放平台配置的一致
- 授权码（code）有效期较短，获取后需立即使用
- App Secret 不要暴露在客户端代码中
