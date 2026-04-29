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

// Default styles matching md2wechat implementation
const DEFAULT_STYLES = {
  title: {
    font_size: '24px',
    color: '#DC143C',
    text_align: 'center',
    line_height: '1.2',
    letter_spacing: '1px',
    margin: '0.5em 0',
    font_weight: 'bold',
  },
  subtitle: {
    font_size: '22px',
    color: '#555555',
    text_align: 'center',
    line_height: '1.3',
    margin: '0 0 1em 0',
  },
  h2: {
    font_size: '22px',
    color: '#0000CD',
    line_height: '1.4',
    margin: '1.5em 0 0.8em 0',
    font_weight: 'bold',
    border_left: '4px solid #DC143C',
    padding_left: '12px',
  },
  h3: {
    font_size: '20px',
    color: '#0000CD',
    line_height: '1.5',
    margin: '2em 0 0.8em 0',
    font_weight: 'bold',
  },
  p: {
    color: '#333333',
    font_size: '16px',
    line_height: '1.75',
  },
  strong: {
    color: '#DC143C',
  },
  blockquote: {
    background: '#f5f5f5',
    border_left: '4px solid #DC143C',
    padding: '12px 16px',
    margin: '1em 0',
    color: '#666666',
  },
  list_item: {
    font_size: '17px',
    color: '#333333',
  },
  code: {
    background: '#f5f5f5',
    padding: '2px 6px',
    border_radius: '4px',
    font_family: 'Consolas, Monaco, monospace',
  },
  pre: {
    background: '#f5f5f5',
    padding: '12px',
    border_radius: '6px',
    overflow: 'auto',
    margin: '1em 0',
  },
  table: {
    width: '100%',
    border_collapse: 'collapse',
    margin: '1em 0',
  },
  th: {
    background: '#f0f0f0',
    padding: '10px',
    text_align: 'center',
    border: '1px solid #dddddd',
    font_weight: 'bold',
  },
  td: {
    padding: '10px',
    border: '1px solid #dddddd',
    text_align: 'center',
  },
  hr: {
    border: 'none',
    border_top: '1px dashed #cccccc',
    margin: '2em 0',
  },
  img: {
    max_width: '100%',
    border_radius: '8px',
    box_shadow: '0 4px 6px rgba(0,0,0,0.15)',
    display: 'block',
    margin: '1.5em auto',
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
 * Highlight code blocks using highlight.js
 */
function highlightCodeBlock(code, lang) {
  try {
    const highlighted = lang && lang !== 'text'
      ? hljs.highlight(code, { language: lang }).value
      : hljs.highlightAuto(code).value;

    const codeStyle = buildStyleString(DEFAULT_STYLES.code);
    const preStyle = buildStyleString(DEFAULT_STYLES.pre);

    return `<pre style="${preStyle}"><code style="${codeStyle}">${highlighted}</code></pre>`;
  } catch {
    const codeStyle = buildStyleString(DEFAULT_STYLES.code);
    const preStyle = buildStyleString(DEFAULT_STYLES.pre);
    return `<pre style="${preStyle}"><code style="${codeStyle}">${code}</code></pre>`;
  }
}

/**
 * Preprocess markdown to handle code blocks with syntax highlighting
 */
function preprocessMarkdown(mdContent) {
  const codeBlockPattern = /```(\w*)\n([\s\S]*?)```/g;

  return mdContent.replace(codeBlockPattern, (match, lang, code) => {
    return highlightCodeBlock(code.trim(), lang || 'text');
  });
}

/**
 * Convert lists to paragraphs for better WeChat compatibility
 */
function convertListsToParagraphs(html) {
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
      items.push(`<p data-list-item="true" style="${buildStyleString(DEFAULT_STYLES.list_item)}">• ${cleaned}</p>`);
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
      items.push(`<p data-list-item="true" style="${buildStyleString(DEFAULT_STYLES.list_item)}">${counter}. ${cleaned}</p>`);
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

  // Apply styles using regex replacements
  html = html.replace(/<h1([^>]*)>/gi, `<h1 style="${buildStyleString(styles.title)}"$1>`);
  html = html.replace(/<h2([^>]*)>/gi, `<h2 style="${buildStyleString(styles.h2)}"$1>`);
  html = html.replace(/<h3([^>]*)>/gi, `<h3 style="${buildStyleString(styles.h3)}"$1>`);
  html = html.replace(/<p([^>]*)>/gi, `<p style="${buildStyleString(styles.p)}"$1>`);
  html = html.replace(/<strong([^>]*)>/gi, `<strong style="color:${styles.strong.color};"$1>`);
  html = html.replace(/<blockquote>/gi, `<blockquote style="${buildStyleString(styles.blockquote)}">`);
  html = html.replace(/<hr\s*\/?>/gi, `<hr style="${buildStyleString(styles.hr)}">`);
  html = html.replace(/<img\s/gi, `<img style="${buildStyleString(styles.img)}" `);
  html = html.replace(/<table>/gi, `<table style="${buildStyleString(styles.table)}">`);
  html = html.replace(/<th>/gi, `<th style="${buildStyleString(styles.th)}">`);
  html = html.replace(/<td>/gi, `<td style="${buildStyleString(styles.td)}">`);

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
  // Step 1: Preprocess markdown (code highlighting)
  const processedMd = preprocessMarkdown(mdContent);

  // Step 2: Convert to HTML using marked
  const html = marked.parse(processedMd, {
    breaks: true,
    gfm: true,
  });

  // Step 3: Sanitize HTML (whitelist filtering)
  const cleanHtml = sanitizeHtmlContent(html);

  // Step 4: Convert lists to paragraphs (WeChat compatibility)
  const withParaLists = convertListsToParagraphs(cleanHtml);

  // Step 5: Apply element styles
  const styledHtml = applyElementStyles(withParaLists, customStyles);

  // Step 6: Clean up excessive newlines
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
