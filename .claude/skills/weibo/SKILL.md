# Weibo Skill

微博内容发布和管理工具

## 描述

通过微博开放平台 API，实现自动发布微博内容（纯文本/带图片）。支持 OAuth2 认证、限流检查等功能。

## 前提条件

1. 微博开放平台开发者账号
2. 已创建微博应用（获取 App Key 和 App Secret）
3. 配置回调地址（Redirect URI）
4. 获取 Access Token（通过 OAuth2 授权流程）

## 环境变量

```bash
WEIBO_APP_KEY=your_app_key
WEIBO_APP_SECRET=your_app_secret
WEIBO_REDIRECT_URI=https://yourdomain.com/callback
WEIBO_ACCESS_TOKEN=your_access_token
```

## 工具

### weibo:auth

**描述**: 获取 OAuth2 授权 URL 或交换 Access Token

**用法**:
```bash
# 步骤1: 获取授权 URL
python scripts/auth.py --get-url

# 步骤2: 用 code 换取 Access Token
python scripts/auth.py --exchange-code <code>
```

**输出**:
- 授权 URL（步骤1）
- Access Token、过期时间、用户 UID（步骤2）

### weibo:post

**描述**: 发布微博（纯文本或带图片）

**参数**:
- `status` (必需): 微博内容，最多 140 个中文字符
- `image_path` (可选): 图片文件路径

**用法**:
```bash
# 发布纯文本微博
python scripts/post.py --status "这是一条测试微博"

# 发布带图片的微博
python scripts/post.py --status "带图片的微博" --image /path/to/image.jpg
```

**约束**:
- 文本长度: 最多 140 个中文字符
- 图片格式: JPEG, GIF, PNG
- 图片大小: 单张最大 5MB
- 发布频率: 每小时最多 30 条

**输出**:
```json
{
  "success": true,
  "weibo_id": "1234567890",
  "url": "https://weibo.com/xxx/xxx",
  "created_at": "Mon Mar 27 10:30:00 +0800 2026"
}
```

### weibo:check-limit

**描述**: 检查 API 限流状态

**用法**:
```bash
python scripts/check_limit.py
```

**输出**:
```json
{
  "ip_limit": 15000,
  "ip_remaining": 14950,
  "user_limit": 30,
  "user_remaining": 25,
  "reset_time": "2026-03-27 11:00:00"
}
```

## 错误处理

### 常见错误码

| 错误码 | 含义 | 处理策略 |
|--------|------|---------|
| `21301` | 认证失败 | 检查 Access Token 有效性 |
| `21327` | Token 过期 | 需要重新授权获取新的 Token |
| `20016` | 发布太频繁 | 等待一段时间后重试 |
| `20017` | 重复内容 | 修改内容后重试 |
| `20012` | 文本过长 | 缩减内容至 140 字符以内 |
| `10023` | 超出限流 | 暂停操作，检查限流状态 |

## 使用示例

### 完整发布流程

```bash
# 1. 获取授权 URL
python scripts/auth.py --get-url
# 输出: 请在浏览器中打开以下 URL 并授权:
# https://api.weibo.com/oauth2/authorize?client_id=xxx&redirect_uri=xxx&response_type=code

# 2. 用户授权后，获取 code，然后换取 Access Token
python scripts/auth.py --exchange-code <授权码>
# 输出: Access Token: 2.00xxxx
#       过期时间: 7200 秒
#       用户 UID: 1234567890

# 3. 设置环境变量（或通过 .env 文件）
export WEIBO_ACCESS_TOKEN=2.00xxxx

# 4. 发布微博
python scripts/post.py --status "Hello Weibo! 👋"

# 5. 检查限流状态
python scripts/check_limit.py
```

### 在 Claude Code 中使用

```
用户: 帮我发条微博，内容是"今天天气真好"
Claude: 正在为您发布微博...
      [调用 weibo:post 工具]
      发布成功！微博链接: https://weibo.com/xxx/xxx
```

## 技术限制

- **Token 有效期**: 默认 2 小时（无 refresh token）
- **发布频率**: 每小时最多 30 条
- **IP 限流**: 每小时 15,000 请求
- **测试账号**: 未审核应用仅支持 15 个测试账号

## 依赖

```bash
pip install requests python-dotenv
```

## 文件结构

```
.claude/skills/weibo/
├── SKILL.md              # 本文件
├── scripts/
│   ├── auth.py          # OAuth2 认证
│   ├── post.py          # 发布微博
│   └── check_limit.py   # 限流检查
└── README.md            # 详细使用说明
```

## 参考资料

- [微博开放平台](https://open.weibo.com)
- [API 文档 V2](https://open.weibo.com/wiki/API%E6%96%87%E6%A1%A3_V2)
- [OAuth2 文档](https://open.weibo.com/wiki/Oauth)
