# publish-note

发布小红书图文笔记。

## 功能

- 自动上传图片
- 填写标题和正文
- 添加话题标签
- 支持定时发布和可见范围设置

## 安装依赖

```bash
cd rednote/publish-note/scripts
npm install playwright
```

## 配置

设置环境变量（可选）：

```bash
export XHS_DATA_PATH="/path/to/data"
```

## 使用方法

### 作为模块使用

```javascript
const { publishNote } = require('./scripts/publish-note');

const result = await publishNote({
  title: '美食分享',
  content: '今天做了一道美味的菜肴...',
  images: ['/path/to/image1.jpg', '/path/to/image2.jpg'],
  tags: ['美食', '菜谱'],
  visibility: 'public',
  isOriginal: true,
});

console.log(result);
```

### CLI 使用

```bash
node scripts/publish-note.js --title "标题" --content "内容" --images "/path/1.jpg,/path/2.jpg"
```

## 输出

```json
{
  "success": true,
  "noteId": "笔记ID",
  "message": "笔记发布成功"
}
```

## 相关 Skills

- `check-login` - 检查登录状态
- `get-qrcode` - 获取登录二维码
- `publish-video` - 发布视频笔记
