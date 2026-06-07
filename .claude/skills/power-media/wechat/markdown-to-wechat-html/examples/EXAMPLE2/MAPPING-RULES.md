# Markdown → WeChat HTML 样式映射规则 (EXAMPLE2)

基于 `EXAMPLE.2.TEMPLATE.MARKDOWN.md` → `EXAMPLE.2.TEMPLATE.HTML.html` 对比分析。

> 与 EXAMPLE1 的主要差异：全局字大小从 14px → 13px；标题层级简化（h1/h2 统一，h3/h4/h5 统一）；分隔线改为 0.5px hairline；列表使用 span 子弹。

---

## 1. 标题层级简化

EXAMPLE2 将所有标题简化为两种视觉层级：

| Markdown | HTML 输出 | 样式 | 说明 |
|----------|-----------|------|------|
| `#` | `<h2>` | white-on-red | 文章顶层标题 |
| `##` | `<h2>` | white-on-red | 章节标题 |
| `###` | `<h3>` | red left border | 小节标题 |
| `####` | `<h3>` | red left border | 子小节（视觉同 h3）|
| `#####` | `<h3>` | red left border | 微小节（视觉同 h3）|

### H1/H2 统一样式（白字红底胶囊）
```
text-align: center
color: #ffffff
background: #fa5151 (rgb(250,81,81))
font-size: 1.2em
font-weight: bold
display: table
margin: 4em auto 2em
padding: 0 0.2em
font-family: *global*
```

### H3/H4/H5 统一样式（红色左边框）
```
text-align: left
color: #3f3f3f
font-size: 1.1em
font-weight: bold
line-height: 1.2
margin: 2em 8px 0.75em 0
padding-left: 8px
border-left: 3px solid #fa5151
font-family: *global*
```

---

## 2. 全局字体大小：13px

EXAMPLE2 的正文使用 **13px**（而非 EXAMPLE1 的 14px）：

| 元素 | font-size |
|------|-----------|
| p | 13px |
| strong | 13px |
| blockquote | 13px |
| blockquote > p | 13px |
| 列表项 p | 13px |

表格和标题保持相对大小（1.1em, 1.2em, 90% 等）。

---

## 3. 段落 (P) — 与 EXAMPLE1 变化

| CSS 属性 | 值 | vs EXAMPLE1 |
|----------|-----|-------------|
| font-size | 13px | 14px → 13px |
| color | #3f3f3f | 不变 |
| line-height | 1.75 | 不变 |
| margin | 1.5em 8px | 不变 |
| letter-spacing | 0.1em | 不变 |

---

## 4. 列表项 — 新增 Span 子弹结构

与 EXAMPLE1 的纯文本 `• ` 不同，EXAMPLE2 使用嵌套 span 结构：

```html
<p style="margin:20px 10px 20px 0; padding-left:1em; font-size:13px;">
  <span style="display:block; text-indent:-1em; margin:0.2em 8px;">
    <span style="margin-right:10px;">•</span>文本内容
  </span>
</p>
```

三层结构：
| 层级 | 标签 | 作用 |
|------|------|------|
| 外层 | `<p>` | 提供列表项整体间距 (margin/padding) |
| 中层 | `<span display:block>` | 悬挂缩进控制 (text-indent: -1em) |
| 内层 | `<span margin-right:10px>` | 子弹标记 (bullet/number) |

有序列表同理，内层 span 内容为 `1.` `2.` 等。

---

## 5. 分隔线 (HR) — Hairline 0.5px

从 EXAMPLE1 的虚线改为 CSS transform 实现的 hairline：

| CSS 属性 | 值 | 说明 |
|----------|-----|------|
| border-style | solid | |
| border-width | 1px 0 0 | 仅上边框 1px |
| border-color | rgba(0, 0, 0, 0.1) | 10% 黑 |
| transform | scale(1, 0.5) | **垂直缩小到 0.5px** |
| transform-origin | 0 0 | |

> 这是微信排版中常用的技法，通过缩放生成真正的 0.5px 细线。

---

## 6. 加粗 (STRONG) — 仅字体大小变化

| CSS 属性 | 值 | vs EXAMPLE1 |
|----------|-----|-------------|
| color | rgba(255, 53, 2, 0.9) | 不变（橙红） |
| font-size | 13px | 14px → 13px |
| font-weight | bold | 不变 |

---

## 7. 引用块 (BLOCKQUOTE) — 仅字体大小变化

| CSS 属性 | 值 | vs EXAMPLE1 |
|----------|-----|-------------|
| background | rgba(27, 31, 35, 0.05) | 不变 |
| font-size | 13px | 14px → 13px |
| border-radius | 4px | 不变 |
| padding | 1em | 不变 |
| margin | 2em 8px | 不变 |

---

## 8. 内联代码 (CODE) — 不变

| CSS 属性 | 值 |
|----------|-----|
| color | #dd1144 |
| background | rgba(27, 31, 35, 0.05) |
| font-size | 90% |
| padding | 3px 5px |
| border-radius | 4px |

---

## 9. 代码块 — 带行号的 Section 结构

EXAMPLE2 的代码块使用了特殊的 `section.code-snippet__fix` 结构，包含行号列表和代码区域：

```html
<section class="code-snippet__fix code-snippet__js">
  <ul class="code-snippet__line-index code-snippet__js">
    <li></li>...  <!-- 行号占位 -->
  </ul>
  <pre class="code-snippet__js" data-lang="text">
    <code><span class="code-snippet_outer">代码行</span></code>
  </pre>
</section>
```

> 这是 Markdown Nice 等工具的代码块输出格式，包含行号列和代码列。当前代码使用 highlight.js 高亮，暂不实现行号功能。

---

## 10. LaTeX 数学公式 — 内联保留

`$$ ... $$` 公式直接内联在段落中，不单独成块：

```html
<p>所以：$$\frac{dL}{dw} = \frac{dL}{dy} \times \frac{dy}{dw}$$</p>
```

> 微信不支持 MathJax/KaTeX，公式以纯文本形式保留。

---

## 与 EXAMPLE1 的差异总表

| 项目 | EXAMPLE1 | EXAMPLE2 |
|------|----------|----------|
| 正文字体 | 14px | **13px** |
| h1/h2 关系 | 分离（h1独有样式） | **统一为 white-on-red** |
| h3/h4/h5 | h4/h5 未定义 | **统一为 red left border** |
| 列表子弹 | 纯文本 `• ` | **嵌套 span 结构** |
| HR 分隔线 | 1px dashed #ccc | **0.5px solid hairline** |
| 代码块 | pre > code | section.code-snippet（带行号）|
| 数学公式 | 不处理 | 内联保留 |
