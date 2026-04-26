# delete-draft

删除微信公众号草稿箱文章。

## 功能

- 根据 media_id 删除单篇草稿
- 支持 CLI 和模块调用

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
const { deleteDraft } = require('./scripts/delete-draft');

const result = await deleteDraft('media_id_xxxx');
console.log(result.message);
```

### CLI 使用

```powershell
node scripts/delete-draft.js <mediaId>
node scripts/delete-draft.js <mediaId> --json
```

示例：

```powershell
node scripts/delete-draft.js xxxxxxxxxx
```

## API

### deleteDraft(mediaId)

删除草稿。

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| mediaId | string | 是 | 要删除的草稿 media_id |

**返回值：**

```javascript
{
  success: true,
  message: '草稿删除成功',
  media_id: 'xxx'
}
```
