# get-feed

获取小红书帖子详情。

## 安装依赖

```bash
cd rednote/get-feed/scripts
npm install playwright
```

## 使用方法

```javascript
const { getFeed } = require('./scripts/get-feed');

const result = await getFeed({ noteId: 'xxxxxx' });
console.log(result);
```

### CLI

```bash
node scripts/get-feed.js --noteId "笔记ID"
```

## 相关 Skills

- `search` - 搜索内容
- `get-feeds` - 获取推荐列表
