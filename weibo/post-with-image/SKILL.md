---
name: post-with-image
description: |
  使用浏览器自动化发布带图片的微博。

  当用户说以下任何内容时触发此 skill：
  - "发带图微博"
  - "发布带图片的微博"
  - "发微博带图"
  - "发图片微博"
  - "post weibo with image"
  - 任何涉及发布带图片的微博的请求

  此 skill 自动完成：
  - 检查登录状态
  - 打开微博首页
  - 上传图片
  - 填写微博内容
  - 点击发送
  - 返回发布结果

  使用 Playwright 浏览器自动化。

compatibility: |
  - Node.js 18+
  - Playwright
  - 已登录的微博账号
  - 依赖：playwright
---

# 发布带图片的微博

## 工作流程

1. 检查登录状态
2. 验证图片文件
3. 启动浏览器
4. 打开微博首页
5. 上传图片
6. 填写微博内容
7. 点击发送
8. 检查发布结果
9. 返回结果

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| text | string | 是 | 微博内容（最多 140 字符）|
| imagePath | string | 是 | 图片文件路径 |

## 输出结果

```json
{
  "success": true,
  "message": "发布成功"
}
```

或

```json
{
  "success": false,
  "error": "错误信息"
}
```

## 使用示例

**示例 1：**
```
用户：发一条带图片的微博，说"分享美景"，图片./photo.jpg
结果：正在发布带图片的微博...
      发布成功！
```

## 依赖安装

```bash
cd /mnt/d/08_tmp/02_media/power-media/weibo/post-with-image/scripts
npm install playwright
npx playwright install chromium
```

## 注意事项

1. 必须先登录微博
2. 内容最多 140 字符
3. 图片格式支持：JPG, PNG, GIF
4. 图片大小建议不超过 5MB
5. 使用 headless 模式（不显示浏览器）
