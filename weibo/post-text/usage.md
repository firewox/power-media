# post-text

发布纯文本微博到新浪微博。

## 功能

- 验证微博内容长度（140 字符限制）
- 发布纯文本微博
- 返回发布结果和微博链接
- 完善的错误处理

## 安装

```bash
cd /mnt/d/08_tmp/02_media/power-media/weibo/post-text/scripts
pip3 install requests python-dotenv
```

## 配置

设置环境变量：

```bash
export WEIBO_ACCESS_TOKEN="你的 Access Token"
```

或在项目根目录创建 `.env` 文件。

## 使用方法

### CLI 使用

```bash
python3 scripts/post-text.py "微博内容"
```

示例：

```bash
python3 scripts/post-text.py "Hello Weibo! 👋"
```

### 作为模块使用

```python
from scripts.post_text import WeiboPoster

poster = WeiboPoster(access_token)
result = poster.post_text("微博内容")
print(result)
```

## 输出格式

```json
{
  "success": true,
  "weibo_id": "1234567890",
  "url": "https://weibo.com/xxx/xxx",
  "created_at": "Mon Mar 27 10:30:00 +0800 2026",
  "text": "微博内容"
}
```

## 注意事项

- 微博内容最多 140 个中文字符
- Access Token 默认 2 小时过期
- 每小时最多发布 30 条微博
