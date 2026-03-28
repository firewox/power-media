---
name: post-with-image
description: |
  发布带图片的微博到新浪微博。

  当用户说以下任何内容时触发此 skill：
  - "发带图微博"
  - "发布带图片的微博"
  - "发微博带图"
  - "发图片微博"
  - "post weibo with image"
  - 任何涉及发布带图片的微博到新浪微博的请求

  此 skill 自动完成：
  - 验证微博内容长度（140 字符限制）
  - 验证图片格式和大小（最大 5MB）
  - 调用微博 API 发布带图片的微博
  - 返回发布结果和微博链接

  使用前必须配置微博开放平台凭据。

compatibility: |
  - Python 3.8+
  - 微博开放平台 App Key 和 App Secret
  - 有效的 Access Token
  - 依赖：requests, python-dotenv
---

# 发布带图片的微博

## 工作流程

1. 检查环境变量（WEIBO_ACCESS_TOKEN）
2. 验证微博内容（长度限制 140 字符）
3. 验证图片文件（格式、大小限制 5MB）
4. 调用微博 API 发布带图片的微博
5. 返回发布结果

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | string | 是 | 微博内容（最多 140 个中文字符）|
| image_path | string | 是 | 图片文件路径 |

## 输出结果

```json
{
  "success": true,
  "weibo_id": "1234567890",
  "url": "https://weibo.com/xxx/xxx",
  "created_at": "Mon Mar 27 10:30:00 +0800 2026",
  "text": "微博内容",
  "pic_url": "http://wx.sinaimg.cn/xxx.jpg"
}
```

## 配置要求

必须设置环境变量：

```bash
export WEIBO_ACCESS_TOKEN="你的 Access Token"
```

## 图片要求

- **格式**: JPEG, GIF, PNG
- **大小**: 单张最大 5MB
- **数量**: 单次调用只能上传 1 张（多图需先预上传获取 pic_id）

## 使用示例

**示例 1：**
```
用户：发一条带图片的微博，内容是"分享美景"，图片是./photo.jpg
结果：发布成功！微博链接: https://weibo.com/xxx/xxx
```

**示例 2：**
```
用户：帮我发一张美食图片到微博
结果：请提供微博文字内容和图片路径
```

## 注意事项

1. **字符限制**：微博内容最多 140 个中文字符
2. **图片限制**：单张最大 5MB，支持 JPEG/GIF/PNG
3. **Token 有效期**：Access Token 默认 2 小时过期
4. **发布频率**：每小时最多 30 条

## 依赖安装

```bash
cd /mnt/d/08_tmp/02_media/power-media/weibo/post-with-image/scripts
pip3 install requests python-dotenv
```
