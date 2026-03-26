---
name: markdown-to-wechat-html
description: |
  将 Markdown 文件转换为微信公众号兼容的 HTML 格式。

  当用户说以下任何内容时触发此 skill：
  - "转换 markdown 生成 html"
  - "markdown 转 html"
  - "把 markdown 转成微信公众号格式"
  - "生成微信文章 html"
  - "转换 md 文件"
  - 任何涉及将 Markdown 文件转换为 HTML 用于微信公众号的请求

  此 skill 专门处理微信公众号的 HTML 格式要求，包括：
  - Markdown 解析为 HTML
  - 应用微信兼容的内联样式
  - 代码语法高亮
  - 列表转换为段落格式（微信兼容性优化）
  - HTML 白名单过滤

  注意：图片自动上传功能尚未实现（TODO）

compatibility: |
  - Node.js 环境
  - 依赖：marked, sanitize-html, highlight.js
---

# Markdown 转微信公众号 HTML

## 工作流程

1. 读取用户提供的 Markdown 文件路径
2. 使用 md2wechat 转换器处理内容：
   - 预处理代码块（语法高亮）
   - Markdown 转 HTML（使用 marked）
   - HTML 安全过滤（白名单）
   - 列表转段落（微信兼容性）
   - 应用微信样式
3. 生成 HTML 文件并保存到同一目录
4. 返回生成的 HTML 文件路径

## 转换细节

### 代码高亮
使用 highlight.js 对代码块进行语法高亮处理。

### HTML 清理
使用白名单过滤，只允许以下标签：
p, br, h1-h6, strong, em, blockquote, hr, code, pre, ul, ol, li, span, div, sup, sub, del, img, table, tr, th, td, section

### 列表转段落
微信公众号对列表支持不佳，将：
- 无序列表 `<ul><li>` 转换为 `<p>• 内容</p>`
- 有序列表 `<ol><li>` 转换为 `<p>1. 内容</p>`

### 默认样式

**标题样式：**
- H1: 24px, #DC143C（红色）, 居中, 加粗
- H2: 22px, #0000CD（蓝色）, 左边框 4px 红色, 加粗
- H3: 20px, #0000CD, 加粗

**正文样式：**
- 段落: 16px, #333333, 行高 1.75
- 粗体: #DC143C（红色）
- 引用块: 浅灰背景, 左边框 4px 红色

**代码样式：**
- 内联代码: 浅灰背景, 圆角
- 代码块: 浅灰背景, 圆角, 自动换行

**图片样式：**
- 最大宽度 100%
- 圆角 8px
- 阴影效果

**表格样式：**
- 全宽, 边框合并
- 表头: 浅灰背景, 居中
- 单元格: 1px 边框

## 输出文件

生成的 HTML 文件命名规则：
- 输入：`article.md`
- 输出：`article-wechat.html`

## 待实现功能（TODO）

- [ ] 图片自动上传到微信素材库
  - 提取 Markdown 中的图片链接
  - 上传图片到微信公众号素材库
  - 替换图片链接为微信素材 URL

## 使用示例

**示例 1：**
用户："把 /home/user/article.md 转换成微信公众号 HTML"
输出：读取文件 → 转换 → 保存为 /home/user/article-wechat.html

**示例 2：**
用户："转换 markdown 生成 html，文件在 ./posts/blog.md"
输出：读取文件 → 转换 → 保存为 ./posts/blog-wechat.html
