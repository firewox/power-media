# 使用示例

## 发布微信公众号文章

```
用户: 帮我写一篇关于 AI 发展趋势的文章，并发布到微信公众号草稿箱

Claude:
1. 生成文章内容
2. 调用 wechat:push-draft skill
3. 返回文章链接和 mediaId
```

---

## 多平台同步发布

```
用户: 把这个内容同步发布到微博和小红书

Claude:
1. 根据各平台特点调整内容格式
   - 微博：添加话题标签，控制字数
   - 小红书：添加 emoji，优化排版
2. 调用 weibo:post 发布微博
3. 调用 xiaohongshu:post-note 发布笔记
4. 汇总各平台发布结果
```

---

## 批量管理

```
用户: 查看我所有平台的草稿箱

Claude:
1. 调用 wechat:get-drafts 获取微信草稿
2. 调用 weibo:get-drafts 获取微博草稿
3. 汇总展示所有草稿列表
```
