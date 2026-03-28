# exchange-token

用授权码换取微博 Access Token。

## 功能

- 验证环境变量配置
- 调用微博 OAuth2 接口
- 解析并显示 Token 信息
- 提供环境变量设置指引

## 安装

```bash
cd /mnt/d/08_tmp/02_media/power-media/weibo/exchange-token/scripts
pip3 install requests python-dotenv
```

## 配置

设置环境变量：

```bash
export WEIBO_APP_KEY="你的 App Key"
export WEIBO_APP_SECRET="你的 App Secret"
export WEIBO_REDIRECT_URI="https://yourdomain.com/callback"
```

## 使用方法

### CLI 使用

```bash
python3 scripts/exchange-token.py <code>
```

示例：

```bash
python3 scripts/exchange-token.py abc123
```

### 作为模块使用

```python
from scripts.exchange_token import WeiboAuth

auth = WeiboAuth(app_key, app_secret, redirect_uri)
token_info = auth.exchange_code_for_token("abc123")
print(token_info)
```

## 输出格式

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

## 完整 OAuth2 流程

```bash
# 1. 获取授权 URL
python3 get-auth-url/scripts/get-auth-url.py

# 2. 用户在浏览器中授权，获取 code

# 3. 用 code 换取 Token
python3 exchange-token/scripts/exchange-token.py <code>

# 4. 设置环境变量
export WEIBO_ACCESS_TOKEN="2.00xxx"

# 5. 现在可以发布微博了
python3 post-text/scripts/post-text.py "Hello Weibo!"
```

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| `invalid_grant` | 授权码无效或已使用 | 重新获取授权码 |
| `redirect_uri_mismatch` | 回调地址不匹配 | 检查配置 |
| `invalid_client` | App Key/Secret 错误 | 检查环境变量 |

## 注意事项

- Token 默认有效期 2 小时
- 授权码只能使用一次
- 请妥善保管 Access Token
