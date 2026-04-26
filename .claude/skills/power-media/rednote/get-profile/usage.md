# get-profile

获取小红书用户主页信息。

## 安装依赖

```bash
cd rednote/get-profile/scripts
npm install playwright
```

## 使用方法

```javascript
const { getProfile } = require('./scripts/get-profile');

const result = await getProfile({ userId: 'xxxxxx' });
console.log(result);
```

### CLI

```bash
node scripts/get-profile.js --userId "用户ID或URL"
```

## 相关 Skills

- `get-feed` - 获取帖子详情
- `search` - 搜索内容
