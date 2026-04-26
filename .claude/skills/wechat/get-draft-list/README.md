# get-draft-list

获取微信公众号草稿箱文章列表。

## 功能

- 获取微信公众号草稿箱中的所有文章列表
- 支持分页获取
- 返回每篇草稿的 media_id、标题、更新时间等信息

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
const { getDraftList } = require('./scripts/get-draft-list');

// 获取前 20 篇草稿
const result = await getDraftList();
console.log(result.items);

// 分页获取
const result = await getDraftList(20, 20); // 从第 20 篇开始，获取 20 篇
```

### CLI 使用

```powershell
node scripts/get-draft-list.js [offset] [count]
node scripts/get-draft-list.js [offset] [count] --json
```

示例：

```powershell
# 获取前 20 篇
node scripts/get-draft-list.js

# 从第 20 篇开始获取 10 篇
node scripts/get-draft-list.js 20 10
```

## API

### getDraftList(offset, count)

获取草稿列表。

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| offset | number | 否 | 偏移量，默认 0 |
| count | number | 否 | 返回数量，默认 20，最大 20 |

**返回值：**

```javascript
{
  success: true,
  total_count: 100,      // 草稿总数
  item_count: 20,        // 本次返回数量
  items: [               // 草稿列表
    {
      media_id: 'xxx',
      content: {
        news_item: [...],
        create_time: 1234567890,
        update_time: 1234567890
      }
    }
  ]
}
```
