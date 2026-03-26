---
name: upload-image
description: |
  上传图片到微信公众号素材库。

  当用户说以下任何内容时触发此 skill：
  - "上传图片"
  - "把图片上传到微信"
  - "上传图片到公众号"
  - "上传图片到素材库"
  - "上传临时图片"
  - "上传永久图片"
  - 任何涉及上传图片到微信公众号的请求

  支持的图片源：
  - 网络图片 URL
  - 本地图片文件路径

  支持的图片类型：JPG, PNG, GIF, BMP, WEBP

compatibility: |
  - Node.js 环境
  - 微信公众号 AppID 和 AppSecret
  - 依赖：axios, form-data
---

# 上传图片到微信公众号素材库

## 工作流程

1. 加载微信配置（环境变量 / .env / wechat-config.json）
2. 获取 access_token
3. 下载网络图片或读取本地文件
4. 上传图片到微信素材库
5. 返回上传结果（media_id 和 url）

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| imageSource | string | 是 | 图片 URL 或本地文件路径 |
| isTemporary | boolean | 否 | 是否上传为临时素材（默认 false） |

## 输出结果

```json
{
  "success": true,
  "mediaId": "xxxxxxxxxxxxxxxx",
  "url": "https://mmbiz.qpic.cn/xxxx",
  "type": "image",
  "createdAt": 1234567890
}
```

## 配置要求

与 test-connection skill 相同，支持三种配置方式：

### 方式 1：环境变量
```bash
export WECHAT_APP_ID="你的 AppID"
export WECHAT_APP_SECRET="你的 AppSecret"
```

### 方式 2：.env 文件
```
WECHAT_APP_ID=你的 AppID
WECHAT_APP_SECRET=你的 AppSecret
```

### 方式 3：wechat-config.json
```json
{
  "appId": "你的 AppID",
  "appSecret": "你的 AppSecret"
}
```

## 使用示例

**示例 1：上传网络图片**
```
用户：上传图片 https://example.com/photo.jpg
结果：图片上传成功，media_id: xxx
```

**示例 2：上传本地图片**
```
用户：把 ./images/logo.png 上传到微信
结果：图片上传成功，media_id: xxx
```

**示例 3：上传临时素材**
```
用户：上传临时图片 https://example.com/tmp.gif
结果：临时素材上传成功，media_id: xxx
```

## 图片要求

- **格式**：JPG, PNG, GIF, BMP, WEBP
- **大小**：不超过 2MB
- **永久素材**：用于图文消息，无过期时间
- **临时素材**：用于消息接口，3天后过期

## 常见错误

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 40001 | access_token 过期 | 会自动重新获取 |
| 40007 | 图片格式不正确 | 检查图片格式是否为支持的类型 |
| 41005 | 图片数据为空或损坏 | 检查图片 URL 是否可访问或文件是否完整 |
| 45009 | 超过每日上传限制 | 减少上传频率 |
| 48001 | API 未授权 | 检查公众号是否开通了素材管理权限 |

## 依赖安装

```bash
cd /mnt/d/08_tmp/02_media/power-media/wechat/upload-image/scripts
npm install axios form-data
```
