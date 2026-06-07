# Markdown → WeChat HTML 样式映射规则

基于 `EXAMPLE.1.TEMPLATE.MARKDOWN.md` → `EXAMPLE.1.TEMPLATE.HTML.html` 的对比分析提取。

---

## 1. 全局字体

所有文本元素使用统一字体族：

```
font-family: Roboto, Oxygen, Ubuntu, Cantarell, PingFangSC-light, PingFangTC-light, "Open Sans", "Helvetica Neue", sans-serif
```

---

## 2. 段落 (P) — Markdown 普通文本行

| CSS 属性 | 值 | 说明 |
|----------|-----|------|
| text-align | left | 左对齐 |
| color | #3f3f3f (rgb(63,63,63)) | 深灰色正文 |
| font-size | 14px | 略小于传统 16px |
| line-height | 1.75 | 舒适行高 |
| margin | 1.5em 8px | 上下段间距 + 左右微缩进 |
| letter-spacing | 0.1em | 字间距，提升可读性 |

### 列表项段落 (P 变体 — 无序列表)
| CSS 属性 | 值 |
|----------|-----|
| margin | 20px 10px 20px 0px |
| padding-left | 1em |
| list-style | circle |

### 列表项段落 (P 变体 — 有序列表)
| CSS 属性 | 值 |
|----------|-----|
| margin | 20px 10px 20px 0px |
| padding-left | 1em |

### References 脚注段落 (P 变体)
| CSS 属性 | 值 |
|----------|-----|
| font-size | 80% |
| margin | 0.5em 8px |

---

## 3. 二级标题 (H2) — Markdown `##`

作为主章节分隔标题，使用**白色文字 + 红色背景**的胶囊样式。

| CSS 属性 | 值 | 说明 |
|----------|-----|------|
| text-align | center | 居中 |
| color | #ffffff (rgb(255,255,255)) | 白色文字 |
| background | #fa5151 (rgb(250,81,81)) | 红色背景 |
| font-size | 1.2em | 相对大小 |
| line-height | 1.75 | |
| font-weight | bold | 加粗 |
| display | table | **关键**：让背景仅包裹文字宽度 |
| margin | 4em auto 2em | 大间距居中 |
| padding | 0 0.2em | 左右微留白 |

> 设计意图：H2 是章节的"分割线"，视觉冲击力强，适合长文分隔。

---

## 4. 三级标题 (H3) — Markdown `###`

作为小节标题，使用**左侧红色竖线 + 加粗**的样式。

| CSS 属性 | 值 | 说明 |
|----------|-----|------|
| text-align | left | 左对齐 |
| color | #3f3f3f (rgb(63,63,63)) | 正文字色 |
| font-size | 1.1em | |
| line-height | 1.2 | 紧凑行高 |
| font-weight | bold | 加粗 |
| margin | 2em 8px 0.75em 0px | 上大间距 |
| padding-left | 8px | |
| border-left | 3px solid #fa5151 (rgb(250,81,81)) | **红色左边框** |

---

## 5. 加粗 (STRONG) — Markdown `**text**`

| CSS 属性 | 值 | 说明 |
|----------|-----|------|
| color | rgba(255, 53, 2, 0.9) | 橙红色，醒目但不刺眼 |
| font-size | 14px | |
| font-weight | bold | |
| line-height | 1.75 | |

> 与正文区别：用颜色区分而非仅靠粗细，更醒目。

---

## 6. 内联代码 (CODE) — Markdown `` `code` ``

| CSS 属性 | 值 | 说明 |
|----------|-----|------|
| color | #dd1144 (rgb(221,17,68)) | 粉红色 |
| font-size | 90% | 比正文略小 |
| background | rgba(27, 31, 35, 0.05) | 淡灰背景 |
| padding | 3px 5px | 紧凑内边距 |
| border-radius | 4px | 小圆角 |
| white-space | pre | 保留空格 |

### References 中的编号标记 (CODE 变体)
| CSS 属性 | 值 |
|----------|-----|
| font-size | 90% |
| opacity | 0.6 |

---

## 7. 引用块 (BLOCKQUOTE) — Markdown `> text`

| CSS 属性 | 值 | 说明 |
|----------|-----|------|
| color | #3f3f3f | 正文字色 |
| font-size | 14px | |
| line-height | 1.75 | |
| background | rgba(27, 31, 35, 0.05) | 淡灰背景 |
| margin | 2em 8px | |
| padding | 1em | |
| border-radius | 4px | 圆角 |
| border-left | none | **不再使用左侧竖线** |

> 与旧版区别：从"左边框式"变为"圆角背景卡片式"。

---

## 8. 图片 (IMG) — Markdown `![](url)`

| CSS 属性 | 值 | 说明 |
|----------|-----|------|
| display | block | 块级 |
| width | 100% !important | 撑满容器宽度 |
| margin | 0.1em auto 0.5em | 居中上下留白 |
| border-radius | 4px | 小圆角 |

> 与旧版区别：去掉了 box-shadow，圆角从 8px → 4px，强调 width 100%。

---

## 9. 链接 (A / SPAN) — Markdown `[text](url)`

链接使用 `span` 标签包裹，颜色为蓝灰色。

| CSS 属性 | 值 |
|----------|-----|
| color | #576b95 (rgb(87,107,149)) |

> 微信内部链接可正常跳转；外部链接通常被转为脚注形式。

---

## 10. 表格 (TABLE / THEAD / TD)

### TABLE
| CSS 属性 | 值 |
|----------|-----|
| border-collapse | collapse |
| margin | 1em 8px |
| font-size | 14px |
| color | #3f3f3f |

### THEAD
| CSS 属性 | 值 |
|----------|-----|
| background | rgba(0, 0, 0, 0.05) |
| font-weight | bold |

### TD / TH
| CSS 属性 | 值 | 说明 |
|----------|-----|------|
| text-align | left | **非居中！左对齐** |
| border | 1px solid #dfdfdf | |
| padding | 0.25em 0.5em | 紧凑内边距 |

> 与旧版区别：单元格左对齐（非居中）、更小的 padding、无单独的表头背景色（统一用 thead 控制）。

---

## 11. 代码块 (PRE) — Markdown ` ```lang `

模板中未直接展示代码块的完整样式（模板的代码块可能通过外部工具高亮后粘贴），但根据整体设计语言推断：

| CSS 属性 | 值 |
|----------|-----|
| background | rgba(27, 31, 35, 0.05) |
| border-radius | 6px |
| padding | 12px |
| overflow | auto |
| margin | 1em 0 |
| font-size | 90% |

使用 highlight.js 做语法高亮，代码块内不应用全局 font-family。

---

## 12. 分隔线 (HR) — Markdown `---`

| CSS 属性 | 值 |
|----------|-----|
| border | none |
| border-top | 1px dashed #cccccc |
| margin | 2em 0 |

> 模板中未直观显示，此为保留的现有样式（合理）。

---

## 13. Ruby 注音 (RT) — Markdown `漢字{かんじ}` 或 `漢字【かんじ】`

| CSS 属性 | 值 |
|----------|-----|
| line-height | 1 |
| font-size | 10px |

> 模板通过 `<ruby>` + `<rt>` 标签实现注音，当前代码未处理此特性。

---

## 新旧样式对比速查

| 元素 | 旧 (当前代码) | 新 (模板规则) |
|------|-------------|-------------|
| **P 字体大小** | 16px | 14px |
| **P 字间距** | 无 | 0.1em |
| **P margin** | 无 | 1.5em 8px |
| **H2 文字色** | #0000CD (蓝) | #ffffff (白) |
| **H2 背景** | 无 | #fa5151 (红) |
| **H2 布局** | 左对齐+红色左边框 | 居中+红色背景胶囊 |
| **H3 样式** | 蓝色加粗无边框 | 深灰加粗+红色左边框 |
| **STRONG 颜色** | #DC143C | rgba(255,53,2,0.9) |
| **BLOCKQUOTE** | 红色左边框+灰底 | 灰底圆角无边框 |
| **IMG 圆角** | 8px + 阴影 | 4px 无阴影 |
| **IMG 宽度** | max-width:100% | width:100%!important |
| **TD 对齐** | center | left |
| **TD padding** | 10px | 0.25em 0.5em |
| **TH 背景** | #f0f0f0 通过TH | rgba(0,0,0,0.05) 通过THEAD |
| **CODE 颜色** | 无特殊色 | #dd1144 |
| **CODE 背景** | #f5f5f5 | rgba(27,31,35,0.05) |
