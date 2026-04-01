# 环境配置

## 环境变量

创建 `.env` 文件或在 `.claude/settings.local.json` 中配置：

```bash
# 微信公众号
WECHAT_APP_ID=your-app-id
WECHAT_APP_SECRET=your-app-secret

# 微博
WEIBO_API_KEY=your-api-key
WEIBO_API_SECRET=your-api-secret

# 小红书（需要 Cookie 或第三方 token）
XIAOHONGSHU_COOKIE=your-cookie

# 抖音
DOUYIN_CLIENT_KEY=your-client-key
DOUYIN_CLIENT_SECRET=your-client-secret

# Bilibili
BILIBILI_SESSDATA=your-sessdata
BILIBILI_CSRF=your-csrf

# 知乎
ZHIHU_COOKIE=your-cookie
```

## 平台配置说明

### 微信公众号
1. 登录[微信公众平台](https://mp.weixin.qq.com/)
2. 获取 AppID 和 AppSecret
3. 配置 IP 白名单

### 微博
1. 申请[微博开放平台](https://open.weibo.com/)应用
2. 获取 API Key 和 Secret

### 小红书
- 需要 Cookie 进行模拟登录
- 或使用第三方 API 服务

### 抖音
1. 注册[抖音开放平台](https://open.douyin.com/)
2. 创建应用获取 Client Key 和 Secret

### Bilibili
1. 登录 Bilibili 创作中心
2. 获取 SESSDATA 和 CSRF Token

### 知乎
- 需要 Cookie 进行模拟登录
