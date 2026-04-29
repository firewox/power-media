---
name: delete-draft
description: |
  删除微信公众号草稿箱文章。

  当用户说以下任何内容时触发此 skill：
  - "删除微信草稿"
  - "删除草稿文章"
  - "移除草稿"
  - "删除公众号草稿"
  - "删除指定草稿"
  - 任何涉及删除微信公众号草稿箱文章的请求

  此 skill 自动完成：
  - 根据 media_id 删除单篇草稿
  - 返回删除结果

  使用前必须配置微信公众号凭据。

compatibility: |
  - Node.js 环境
  - 微信公众号 AppID 和 AppSecret
  - 依赖：axios
---

# 删除微信公众号草稿箱文章

## 工作流程

1. 检查微信配置
2. 获取 access_token
3. 调用微信 API 删除草稿
4. 返回删除结果

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| mediaId | string | 是 | 要删除的草稿 media_id |

## 输出结果

```json
{
  "success": true,
  "message": "草稿删除成功",
  "media_id": "xxxxxx"
}
```

## 配置要求

必须设置环境变量：

```powershell
$env:WECHAT_APP_ID="你的微信公众号 AppID"
$env:WECHAT_APP_SECRET="你的微信公众号 AppSecret"
```

## 使用示例

**示例 1：**
```
用户：删除微信草稿 xxxxx
结果：草稿删除成功
```

**示例 2：**
```
用户：删除 media_id 为 xxxxx 的草稿文章
结果：草稿删除成功
```

## 注意事项

1. **不可恢复**：删除后无法恢复，请谨慎操作
2. **media_id 获取**：可通过 get-draft-list 获取草稿列表
3. **Token 缓存**：access_token 自动缓存

## 依赖安装

```powershell
powershell -ExecutionPolicy Bypass -File D:\08_tmp\02_media\power-media\.claude\skills\wechat\install-deps.ps1
```
