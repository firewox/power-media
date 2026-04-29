---
name: validate-markdown
description: |
  发布到微信公众号前校验 Markdown 文件、图片资源和微信配置。
---

# 校验 Markdown 发布输入

用于在真正推送草稿前执行预检：

1. 检查微信公众号配置是否可用
2. 检查 Markdown 文件是否存在且可读取
3. 检查本地图片路径是否有效
4. 检查是否可以成功获取 access_token

适用场景：
- 发布前先做快速校验
- 排查“文件不存在 / 图片丢失 / 配置不生效 / IP 白名单”等问题
