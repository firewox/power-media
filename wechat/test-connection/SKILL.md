---
name: test-connection
description: |
  测试微信公众号 API 连接。

  当用户说以下任何内容时触发此 skill：
  - "测试微信连接"
  - "检查微信 API"
  - "验证微信配置"
  - "测试公众号连接"
  - "检查微信配置是否正确"
  - 任何涉及测试微信公众号 API 连接的请求

  此 skill 自动完成：
  - 获取 access_token
  - 验证配置是否正确

  使用前必须配置微信公众号凭据。

compatibility: |
  - Node.js 环境
  - 微信公众号 AppID 和 AppSecret
  - 依赖：axios
---

# 测试微信公众号 API 连接

## 工作流程

1. 检查微信配置（环境变量）
2. 调用微信 API 获取 access_token
3. 验证 access_token 是否有效
4. 返回连接测试结果

## 输入参数

无

## 输出结果

```json
{
  "success": true,
  "message": "微信 API 连接测试成功",
  "appId": "wx...",
  "accessToken": "xxxxx...",
  "expiresIn": 7200
}
```

## 配置要求

支持三种配置方式（按优先级排序）：

### 方式 1：环境变量（优先级最高）

```bash
export WECHAT_APP_ID="你的微信公众号 AppID"
export WECHAT_APP_SECRET="你的微信公众号 AppSecret"
```

### 方式 2：.env 文件

在项目根目录创建 `.env` 文件：

```
WECHAT_APP_ID=你的 AppID
WECHAT_APP_SECRET=你的 AppSecret
```

### 方式 3：wechat-config.json 文件

创建 `wechat-config.json` 文件：

```json
{
  "appId": "你的 AppID",
  "appSecret": "你的 AppSecret"
}
```

配置文件搜索路径（按优先级）：
- `./.env` 或 `./wechat-config.json`（当前目录）
- `../.env` 或 `../wechat-config.json`（上级目录）
- `~/.wechat-config.json`（用户主目录）

## 使用示例

**示例 1：**
```
用户：测试微信连接
结果：微信 API 连接测试成功，access_token 获取成功
```

**示例 2：**
```
用户：检查微信配置
结果：配置检查通过或显示错误信息
```

## 注意事项

1. **配置验证**：如果测试失败，请检查 AppID 和 AppSecret 是否正确
2. **网络问题**：确保能够访问微信 API 服务器
3. **IP 白名单**：确保服务器 IP 已在微信公众号后台配置白名单

## 依赖安装

```bash
cd /mnt/d/08_tmp/02_media/power-media/.claude/skills/wechat/test-connection/scripts
npm install axios
```
