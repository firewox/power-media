# search

搜索小红书内容。

## 安装依赖

```bash
cd rednote/search/scripts
npm install playwright
```

## 使用方法

```javascript
const { search } = require('./scripts/search');

const result = await search({ keyword: '美食' });
console.log(result.feeds);
```

### CLI

```bash
node scripts/search.js --keyword "美食"
```

## 相关 Skills

- `get-feed` - 获取帖子详情
- `get-profile` - 获取用户主页
