---
name: delete-all-drafts
description: |
  批量删除微信公众号草稿箱所有文章。

  当用户说以下任何内容时触发此 skill：
  - "删除所有微信草稿"
  - "清空草稿箱"
  - "批量删除草稿"
  - "删除公众号所有草稿"
  - "清空所有草稿"
  - 任何涉及批量删除微信公众号草稿箱所有文章的请求

  此 skill 自动完成：
  - 获取所有草稿列表
  - 逐个删除所有草稿
  - 需要 confirm=true 确认

  使用前必须配置微信公众号凭据。

compatibility: |
  - Node.js 环境
  - 微信公众号 AppID 和 AppSecret
  - 依赖：axios
---

# 批量删除微信公众号草稿箱所有文章

## 工作流程

1. 检查微信配置
2. 确认 confirm=true
3. 获取所有草稿列表
4. 逐个删除所有草稿
5. 返回删除结果统计

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| confirm | boolean | 是 | 必须设为 true 确认删除，防止误操作 |

## 输出结果

```json
{
  "success": true,
  "message": "成功删除 X 篇草稿",
  "total": 50,
  "deleted": 50,
  "failed": 0,
  "errors": []
}
```

## 配置要求

支持以下优先级：

1. `.claude/skills/wechat/wechat-config.json`
2. 项目根目录 `.env`
3. 环境变量

环境变量格式：

```powershell
$env:WECHAT_APP_ID="你的微信公众号 AppID"
$env:WECHAT_APP_SECRET="你的微信公众号 AppSecret"
```

## 使用示例

**示例 1：**
```
用户：清空草稿箱
结果：需要确认：请设置 confirm=true 以确认删除所有 50 篇草稿
```

**示例 2：**
```
用户：删除所有微信草稿，确认
结果：成功删除 50 篇草稿
```

## 注意事项

1. **危险操作**：此操作会删除所有草稿，不可恢复
2. **需要确认**：必须设置 confirm=true 才会执行删除
3. **分批处理**：如果草稿较多，会分批获取和删除
4. **Token 缓存**：access_token 自动缓存

## 依赖安装

```powershell
powershell -ExecutionPolicy Bypass -File D:\08_tmp\02_media\power-media\.claude\skills\wechat\install-deps.ps1
```
