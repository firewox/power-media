# delete-all-drafts

批量删除微信公众号草稿箱所有文章。

## 功能

- 获取所有草稿列表
- 逐个删除所有草稿
- 需要 confirm=true 确认，防止误操作
- 返回删除结果统计

## 安装

```powershell
powershell -ExecutionPolicy Bypass -File D:\08_tmp\02_media\power-media\.claude\skills\wechat\install-deps.ps1
```

## 配置

支持以下优先级：

1. `.claude/skills/wechat/wechat-config.json`
2. 项目根目录 `.env`
3. 环境变量

环境变量示例：

```powershell
$env:WECHAT_APP_ID="你的 AppID"
$env:WECHAT_APP_SECRET="你的 AppSecret"
```

## 使用方法

### 作为模块使用

```javascript
const { deleteAllDrafts } = require('./scripts/delete-all-drafts');

// 必须设置 confirm=true
const result = await deleteAllDrafts(true);
console.log(result.message);
console.log(`删除: ${result.deleted}, 失败: ${result.failed}`);
```

### CLI 使用

```powershell
node scripts/delete-all-drafts.js <confirm>
node scripts/delete-all-drafts.js <confirm> --json
```

示例：

```powershell
# 查看草稿数量（不删除）
node scripts/delete-all-drafts.js

# 确认删除所有草稿
node scripts/delete-all-drafts.js true
```

## API

### deleteAllDrafts(confirm)

删除所有草稿。

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| confirm | boolean | 是 | 必须设为 true 确认删除 |

**返回值：**

```javascript
{
  success: true,
  message: '成功删除 50 篇草稿',
  total: 50,          // 草稿总数
  deleted: 50,        // 成功删除数量
  failed: 0,          // 失败数量
  errors: []          // 错误信息列表
}
```

## 警告

**此操作不可恢复！**删除后所有草稿将无法恢复，请谨慎使用。
