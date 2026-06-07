#!/usr/bin/env node
/**
 * md2wechat - Markdown to WeChat Official Account compatible HTML converter
 *
 * Based on the TypeScript md2wechat implementation
 * Converts Markdown to WeChat-compatible HTML with professional styling
 */

const fs = require('fs');
const path = require('path');

// 注意：这些依赖统一在 .claude/skills/wechat 目录安装

let marked, sanitizeHtml, hljs;

try {
  marked = require('marked');
  sanitizeHtml = require('sanitize-html');
  hljs = require('highlight.js');
} catch (e) {
  console.error('缺少依赖包，请先进入 .claude/skills/wechat 运行: npm.cmd install');
  process.exit(1);
}

// Global font family applied to all text elements (from template)
const GLOBAL_FONT_FAMILY = 'Roboto, Oxygen, Ubuntu, Cantarell, PingFangSC-light, PingFangTC-light, "Open Sans", "Helvetica Neue", sans-serif';

// Default styles based on template EXAMPLE2
// Text elements include font_family from GLOBAL_FONT_FAMILY
const DEFAULT_STYLES = {
  // h1 merged with h2 — both use white-on-red capsule style
  title: {
    font_size: '1.2em',
    color: '#ffffff',
    text_align: 'center',
    line_height: '1.75',
    font_weight: 'bold',
    display: 'table',
    margin: '4em auto 2em',
    padding: '0 0.2em',
    background: '#fa5151',
    font_family: GLOBAL_FONT_FAMILY,
  },
  subtitle: {
    font_size: '1em',
    color: '#3f3f3f',
    text_align: 'center',
    line_height: '1.75',
    margin: '2em auto 1.5em',
    font_family: GLOBAL_FONT_FAMILY,
  },
  h2: {
    font_size: '1.2em',
    color: '#ffffff',
    text_align: 'center',
    line_height: '1.75',
    font_weight: 'bold',
    display: 'table',
    margin: '4em auto 2em',
    padding: '0 0.2em',
    background: '#fa5151',
    font_family: GLOBAL_FONT_FAMILY,
  },
  // h3/h4/h5 unified — all use red-left-border style
  h3: {
    font_size: '1.1em',
    color: '#3f3f3f',
    text_align: 'left',
    line_height: '1.2',
    font_weight: 'bold',
    margin: '2em 8px 0.75em 0',
    padding_left: '8px',
    border_left: '3px solid #fa5151',
    font_family: GLOBAL_FONT_FAMILY,
  },
  h4: {
    font_size: '1.1em',
    color: '#3f3f3f',
    text_align: 'left',
    line_height: '1.2',
    font_weight: 'bold',
    margin: '2em 8px 0.75em 0',
    padding_left: '8px',
    border_left: '3px solid #fa5151',
    font_family: GLOBAL_FONT_FAMILY,
  },
  h5: {
    font_size: '1.1em',
    color: '#3f3f3f',
    text_align: 'left',
    line_height: '1.2',
    font_weight: 'bold',
    margin: '2em 8px 0.75em 0',
    padding_left: '8px',
    border_left: '3px solid #fa5151',
    font_family: GLOBAL_FONT_FAMILY,
  },
  p: {
    color: '#3f3f3f',
    font_size: '13px',
    line_height: '1.75',
    text_align: 'left',
    margin: '1.5em 8px',
    letter_spacing: '0.1em',
    font_family: GLOBAL_FONT_FAMILY,
  },
  strong: {
    color: 'rgba(255, 53, 2, 0.9)',
    font_size: '13px',
    font_weight: 'bold',
    line_height: '1.75',
    font_family: GLOBAL_FONT_FAMILY,
  },
  blockquote: {
    color: '#3f3f3f',
    background: 'rgba(27, 31, 35, 0.05)',
    font_size: '13px',
    line_height: '1.75',
    margin: '2em 8px',
    padding: '1em',
    border_radius: '4px',
    font_family: GLOBAL_FONT_FAMILY,
  },
  // List item outer p style
  list_item_p: {
    font_size: '13px',
    color: '#3f3f3f',
    line_height: '1.75',
    margin: '20px 10px 20px 0',
    padding_left: '1em',
    font_family: GLOBAL_FONT_FAMILY,
  },
  // List item inner span (hanging indent wrapper)
  list_item_span: {
    display: 'block',
    text_indent: '-1em',
    margin: '0.2em 8px',
    font_size: '13px',
    color: '#3f3f3f',
    line_height: '1.75',
    font_family: GLOBAL_FONT_FAMILY,
  },
  // Bullet marker span
  list_bullet: {
    margin_right: '10px',
  },
  code: {
    color: '#dd1144',
    background: 'rgba(27, 31, 35, 0.05)',
    font_size: '90%',
    padding: '3px 5px',
    border_radius: '4px',
    white_space: 'pre',
  },
  pre: {
    background: 'rgba(27, 31, 35, 0.05)',
    font_size: '90%',
    padding: '12px',
    border_radius: '6px',
    overflow: 'auto',
    margin: '1em 0',
  },
  table: {
    width: '100%',
    border_collapse: 'collapse',
    margin: '1em 8px',
    font_size: '13px',
    color: '#3f3f3f',
    font_family: GLOBAL_FONT_FAMILY,
  },
  thead: {
    background: 'rgba(0, 0, 0, 0.05)',
    font_weight: 'bold',
    font_family: GLOBAL_FONT_FAMILY,
  },
  th: {
    text_align: 'left',
    border: '1px solid #dfdfdf',
    padding: '0.25em 0.5em',
    font_size: '13px',
    color: '#3f3f3f',
    font_family: GLOBAL_FONT_FAMILY,
  },
  td: {
    text_align: 'left',
    border: '1px solid #dfdfdf',
    padding: '0.25em 0.5em',
    font_size: '13px',
    color: '#3f3f3f',
    line_height: '1.75',
    font_family: GLOBAL_FONT_FAMILY,
  },
  // Hairline divider (0.5px via CSS transform)
  hr: {
    border_style: 'solid',
    border_width: '1px 0 0',
    border_color: 'rgba(0, 0, 0, 0.1)',
    transform_origin: '0 0',
    transform: 'scale(1, 0.5)',
    margin: '2em 0',
  },
  img: {
    display: 'block',
    width: '100% !important',
    border_radius: '4px',
    margin: '0.1em auto 0.5em',
  },
};

// WeChat allowed HTML tags
const WECHAT_ALLOWED_TAGS = [
  'p', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
  'strong', 'em', 'blockquote', 'hr', 'code', 'pre',
  'ul', 'ol', 'li', 'span', 'div', 'sup', 'sub', 'del',
  'img', 'table', 'tr', 'th', 'td', 'section',
];

// WeChat allowed attributes
const WECHAT_ALLOWED_ATTRIBUTES = {
  '*': ['style'],
  'img': ['src', 'alt', 'width', 'height'],
  'th': ['colspan', 'rowspan'],
  'td': ['colspan', 'rowspan'],
};

// Allowed CSS properties for sanitization
const ALLOWED_CSS_PROPERTIES = [
  'background', 'padding', 'border-radius', 'overflow',
  'font-family', 'color', 'font-weight', 'font-style',
  'text-align', 'line-height', 'white-space', 'display',
  'margin', 'border', 'border-left', 'border-top', 'width',
  'height', 'list-style-type', 'box-shadow', 'letter-spacing',
  'border-collapse', 'text-decoration',
];

/**
 * Build CSS style string from style object
 */
function buildStyleString(styles) {
  return Object.entries(styles)
    .map(([key, value]) => `${key.replace(/_/g, '-')}:${value}`)
    .join(';') + ';';
}

/**
 * Build marked renderer with code highlighting
 */
function buildMarkedRenderer() {
  const renderer = new marked.Renderer();
  renderer.code = function(obj) {
    const code = typeof obj === 'object' ? (obj.text || '') : obj;
    const language = typeof obj === 'object' ? (obj.lang || '') : (arguments[1] || '');
    let highlighted;
    try {
      const lang = language || 'text';
      highlighted = (lang && lang !== 'text')
        ? hljs.highlight(code, { language: lang }).value
        : hljs.highlightAuto(code).value;
    } catch (e) {
      highlighted = code;
    }
    const codeStyle = buildStyleString(DEFAULT_STYLES.code);
    const preStyle = buildStyleString(DEFAULT_STYLES.pre);
    return `<pre style="${preStyle}"><code style="${codeStyle}">${highlighted}</code></pre>`;
  };
  return renderer;
}

/**
 * Convert lists to paragraphs for better WeChat compatibility
 */
function convertListsToParagraphs(html) {
  const pStyle = buildStyleString(DEFAULT_STYLES.list_item_p);
  const spanStyle = buildStyleString(DEFAULT_STYLES.list_item_span);
  const bulletStyle = buildStyleString(DEFAULT_STYLES.list_bullet);

  // Process unordered lists
  html = html.replace(/<ul[^>]*>([\s\S]*?)<\/ul>/gi, (match, content) => {
    const items = [];
    content.replace(/<li[^>]*>([\s\S]*?)<\/li>/gi, (liMatch, liContent) => {
      let cleaned = liContent
        .replace(/<p[^>]*>\s*<\/p>/gi, '')
        .replace(/<p[^>]*>/gi, '')
        .replace(/<\/p>/gi, '')
        .replace(/^\s+|\s+$/g, '')
        .replace(/\s+/g, ' ')
        .replace(/\n/g, ' ')
        .trim();
      items.push(`<p data-list-item="true" style="${pStyle}"><span style="${spanStyle}"><span style="${bulletStyle}">•</span>${cleaned}</span></p>`);
      return '';
    });
    return items.join('');
  });

  // Process ordered lists
  html = html.replace(/<ol[^>]*>([\s\S]*?)<\/ol>/gi, (match, content) => {
    const items = [];
    let counter = 1;
    content.replace(/<li[^>]*>([\s\S]*?)<\/li>/gi, (liMatch, liContent) => {
      let cleaned = liContent
        .replace(/<p[^>]*>\s*<\/p>/gi, '')
        .replace(/<p[^>]*>/gi, '')
        .replace(/<\/p>/gi, '')
        .replace(/^\s+|\s+$/g, '')
        .replace(/\s+/g, ' ')
        .replace(/\n/g, ' ')
        .trim();
      items.push(`<p data-list-item="true" style="${pStyle}"><span style="${spanStyle}"><span style="${bulletStyle}">${counter}.</span>${cleaned}</span></p>`);
      counter++;
      return '';
    });
    return items.join('');
  });

  return html + '<br/>';
}

/**
 * Apply element styles to HTML
 */
function applyElementStyles(html, customStyles) {
  const styles = { ...DEFAULT_STYLES, ...customStyles };

  html = html.replace(/<h1([^>]*)>/gi, `<h1 style="${buildStyleString(styles.title)}"$1>`);
  html = html.replace(/<h2([^>]*)>/gi, `<h2 style="${buildStyleString(styles.h2)}"$1>`);
  html = html.replace(/<h3([^>]*)>/gi, `<h3 style="${buildStyleString(styles.h3)}"$1>`);
  html = html.replace(/<h4([^>]*)>/gi, `<h4 style="${buildStyleString(styles.h4)}"$1>`);
  html = html.replace(/<h5([^>]*)>/gi, `<h5 style="${buildStyleString(styles.h5)}"$1>`);
  // Skip paragraphs that are already styled as list items
  // (?=[\s>]) prevents matching <pre>, <param>, <picture> etc.
  html = html.replace(/<p(?=[\s>])(?!\sdata-list-item="true")([^>]*)>/gi, `<p style="${buildStyleString(styles.p)}"$1>`);
  html = html.replace(/<strong([^>]*)>/gi, `<strong style="${buildStyleString(styles.strong)}"$1>`);
  html = html.replace(/<blockquote([^>]*)>/gi, `<blockquote style="${buildStyleString(styles.blockquote)}"$1>`);
  html = html.replace(/<hr\s*\/?>/gi, `<hr style="${buildStyleString(styles.hr)}">`);
  html = html.replace(/<img\s/gi, `<img style="${buildStyleString(styles.img)}" `);
  html = html.replace(/<table([^>]*)>/gi, `<table style="${buildStyleString(styles.table)}"$1>`);
  html = html.replace(/<thead([^>]*)>/gi, `<thead style="${buildStyleString(styles.thead)}"$1>`);
  html = html.replace(/<th(?=[\s>])([^>]*)>/gi, `<th style="${buildStyleString(styles.th)}"$1>`);
  html = html.replace(/<td(?=[\s>])([^>]*)>/gi, `<td style="${buildStyleString(styles.td)}"$1>`);

  return html;
}

/**
 * Sanitize HTML using whitelist
 */
function sanitizeHtmlContent(html) {
  return sanitizeHtml(html, {
    allowedTags: WECHAT_ALLOWED_TAGS,
    allowedAttributes: WECHAT_ALLOWED_ATTRIBUTES,
    allowedStyles: {
      '*': ALLOWED_CSS_PROPERTIES.reduce((acc, prop) => {
        acc[prop] = [new RegExp('.*')];
        return acc;
      }, {}),
    },
    disallowedTagsMode: 'discard',
  });
}

/**
 * Main conversion function
 * @param {string} mdContent - Markdown content to convert
 * @param {object} customStyles - Optional custom style overrides
 * @returns {string} WeChat-compatible HTML string
 */
function convert(mdContent, customStyles) {
  // Step 1: Convert markdown to HTML with code highlighting via custom renderer
  const renderer = buildMarkedRenderer();
  const html = marked.parse(mdContent, {
    breaks: true,
    gfm: true,
    renderer,
  });

  // Step 2: Sanitize HTML (whitelist filtering)
  const cleanHtml = sanitizeHtmlContent(html);

  // Step 3: Convert lists to paragraphs (WeChat compatibility)
  const withParaLists = convertListsToParagraphs(cleanHtml);

  // Step 4: Apply element styles
  const styledHtml = applyElementStyles(withParaLists, customStyles);

  // Step 5: Clean up excessive newlines
  const finalHtml = styledHtml.replace(/\n{3,}/g, '\n\n');

  return finalHtml;
}

/**
 * Process Markdown file and generate HTML file
 * @param {string} inputPath - Path to Markdown file
 * @param {string} outputPath - Path for output HTML file (optional)
 * @returns {object} Result with inputPath, outputPath, and html content
 */
function processMarkdownFile(inputPath, outputPath) {
  // Resolve absolute path
  const resolvedInputPath = path.resolve(inputPath);

  // Check if file exists
  if (!fs.existsSync(resolvedInputPath)) {
    throw new Error(`文件不存在：${resolvedInputPath}`);
  }

  // Read Markdown content
  const mdContent = fs.readFileSync(resolvedInputPath, 'utf-8');

  // Convert to HTML
  const html = convert(mdContent);

  // Generate output path if not provided
  const finalOutputPath = outputPath || resolvedInputPath.replace(/\.md$/i, '-wechat.html');

  // Write HTML file
  fs.writeFileSync(finalOutputPath, html, 'utf-8');

  return {
    inputPath: resolvedInputPath,
    outputPath: finalOutputPath,
    html: html,
  };
}

// CLI usage
if (require.main === module) {
  const args = process.argv.slice(2);

  if (args.length < 1) {
    console.log('Usage: node md2wechat.js <input.md> [output.html]');
    console.log('  input.md    - Path to Markdown file');
    console.log('  output.html - Optional output HTML file path');
    process.exit(1);
  }

  const inputPath = args[0];
  const outputPath = args[1];

  try {
    const result = processMarkdownFile(inputPath, outputPath);
    console.log('✅ 转换成功！');
    console.log(`📝 输入文件：${result.inputPath}`);
    console.log(`💾 输出文件：${result.outputPath}`);
    console.log(`📊 HTML 长度：${result.html.length} 字符`);
  } catch (error) {
    console.error('❌ 转换失败：', error.message);
    process.exit(1);
  }
}

// Export for programmatic usage
module.exports = {
  convert,
  processMarkdownFile,
  DEFAULT_STYLES,
  WECHAT_ALLOWED_TAGS,
  WECHAT_ALLOWED_ATTRIBUTES,
};
