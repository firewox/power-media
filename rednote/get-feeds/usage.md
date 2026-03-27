# get-feeds

获取小红书推荐列表。

## 安装依赖

```bash
cd rednote/get-feeds/scripts
npm install playwright
```

## 使用方法

```javascript
const { getFeeds } = require('./scripts/get-feeds');

const result = await getFeeds({ count: 20 });
console.log(result.feeds);
```

### CLI

```bash
node scripts/get-feeds.js [--count 20]
```

## 相关 Skills

- `get-feed` - 获取帖子详情
- `search` - 搜索内容
