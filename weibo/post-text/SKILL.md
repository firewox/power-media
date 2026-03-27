---
name: post-text
description: |
  发布纯文本微博到新浪微博。

  当用户说以下任何内容时触发此 skill：
  - "发微博"
  - "发布微博"
  - "发送微博"
  - "发条微博"
  - "post weibo"
  - 任何涉及发布纯文本微博到新浪微博的请求

  此 skill 自动完成：
  - 验证微博内容长度（140 字符限制）
  - 调用微博 API 发布微博
  - 返回发布结果和微博链接

  使用前必须配置微博开放平台凭据。

compatibility: |
  - Python 3.8+
  - 微博开放平台 App Key 和 App Secret
  - 有效的 Access Token
  - 依赖：requests, python-dotenv
---

# 发布纯文本微博

## 工作流程

1. 检查环境变量（WEIBO_ACCESS_TOKEN）
2. 验证微博内容（长度限制 140 字符）
3. 调用微博 API 发布微博
4. 返回发布结果

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | string | 是 | 微博内容（最多 140 个中文字符）|

## 输出结果

```json
{
  "success": true,
  "weibo_id": "1234567890",
  "url": "https://weibo.com/xxx/xxx",
  "created_at": "Mon Mar 27 10:30:00 +0800 2026",
  "text": "微博内容"
}
```

## 配置要求

必须设置环境变量：

```bash
export WEIBO_ACCESS_TOKEN="你的 Access Token"
```

或创建 `.env` 文件：
```
WEIBO_ACCESS_TOKEN=2.00xxxxxxxxxxxxxx
```

## 使用示例

**示例 1：**
```
用户：发条微博说"今天天气真好"
结果：发布成功！微博链接: https://weibo.com/xxx/xxx
```

**示例 2：**
```
用户：帮我发个微博：Hello Weibo!
结果：发布成功！微博 ID: 1234567890
```

## 注意事项

1. **字符限制**：微博内容最多 140 个中文字符
2. **Token 有效期**：Access Token 默认 2 小时过期
3. **发布频率**：每小时最多 30 条
4. **重复内容**：相同内容可能导致发布失败

## 错误码

| 错误码 | 含义 | 处理策略 |
|--------|------|---------|
| `21301` | 认证失败 | 检查 Access Token 有效性 |
| `21327` | Token 过期 | 需要重新授权获取新 Token |
| `20016` | 发布太频繁 | 等待一段时间后重试 |
| `20017` | 内容重复 | 修改内容后重试 |
| `20012` | 文本过长 | 缩减至 140 字符以内 |

## 依赖安装

```bash
cd /mnt/d/08_tmp/02_media/power-media/weibo/post-text/scripts
pip3 install requests python-dotenv
```
