# Markdown to WeChat HTML Skill

将 Markdown 文件转换为微信公众号兼容的 HTML 格式。

## 功能特点

- ✅ Markdown 转 HTML
- ✅ 代码语法高亮
- ✅ 微信兼容的内联样式
- ✅ 列表转段落（微信兼容性优化）
- ✅ HTML 白名单过滤
- ⬜ 图片自动上传（TODO）

## 安装依赖

在使用此 skill 前，需要安装以下依赖：

```powershell
powershell -ExecutionPolicy Bypass -File D:\08_tmp\02_media\power-media\.claude\skills\wechat\install-deps.ps1
```

## 使用方法

### 方式 1：通过 Claude Code 调用

当 Claude 询问时，直接说：
- "把 ./article.md 转换成微信公众号 HTML"
- "转换 markdown 生成 html"
- "生成微信文章 html"

### 方式 2：直接使用脚本

```powershell
node scripts/md2wechat.js input.md [output.html]
```

## 样式说明

### 标题样式
- **H1**: 24px, 红色(#DC143C), 居中, 加粗
- **H2**: 22px, 蓝色(#0000CD), 左边框红色, 加粗
- **H3**: 20px, 蓝色, 加粗

### 正文样式
- 段落: 16px, 深灰(#333), 行高 1.75
- 粗体: 红色
- 引用: 浅灰背景 + 红色左边框

### 代码样式
- 自动语法高亮
- 浅灰背景 + 圆角

### 图片样式
- 最大宽度 100%
- 圆角 + 阴影效果

## TODO

- [ ] 图片自动上传到微信素材库
  - 提取 Markdown 中的图片链接
  - 上传图片获取 media_id
  - 替换图片链接为微信 URL

## 技术实现

基于 `md2wechat` 转换器，转换流程：
1. 预处理代码块（语法高亮）
2. Markdown 转 HTML（marked）
3. HTML 安全过滤（白名单）
4. 列表转段落（微信兼容性）
5. 应用微信样式

## 文件结构

```
markdown-to-wechat-html/
├── SKILL.md              # Skill 定义
├── README.md             # 说明文档
└── scripts/
    └── md2wechat.js      # 转换脚本
```
