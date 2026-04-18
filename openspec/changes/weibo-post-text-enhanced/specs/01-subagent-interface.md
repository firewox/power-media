# Spec: Subagent Interface

## Overview

定义子智能体（opencode）的调用接口和返回格式。

## Command Format

```bash
opencode run -m ollama-cloud/qwen3.5:397b \
  "请识别这张微博主页截图中的微博发文文本输入框、发送按钮、头条文章按钮，以纯JSON格式返回结果，无多余描述。坐标使用归一化小数格式 [X1,Y1,X2,Y2]，数值范围 0~1，代表元素相对于整张图片的左上角与右下角位置。返回格式：{\"input_box\": [X1,Y1,X2,Y2], \"send_button\": [X1,Y1,X2,Y2], \"headline_article_button\": [X1,Y1,X2,Y2]}" \
  -f "{screenshot_path}"
```

## Prompt Template

```python
SUBAGENT_PROMPT = """请识别这张微博主页截图中的微博发文文本输入框、发送按钮、头条文章按钮，以纯JSON格式返回结果，无多余描述。

坐标使用归一化小数格式 [X1,Y1,X2,Y2]，数值范围 0~1，代表元素相对于整张图片的左上角与右下角位置。

返回格式：
{
  "input_box": [X1,Y1,X2,Y2],
  "send_button": [X1,Y1,X2,Y2],
  "headline_article_button": [X1,Y1,X2,Y2]
}

注意：
1. 只返回JSON，不要任何其他文字
2. 坐标必须是0-1之间的浮点数
3. [X1,Y1]是左上角，[X2,Y2]是右下角
4. 如果某个元素找不到，返回null"""
```

## Response Format

### Success Response

```json
{
  "input_box": [0.47, 0.25, 0.61, 0.30],
  "send_button": [0.72, 0.25, 0.78, 0.30],
  "headline_article_button": [0.15, 0.35, 0.25, 0.40]
}
```

### Partial Success (some elements not found)

```json
{
  "input_box": [0.47, 0.25, 0.61, 0.30],
  "send_button": [0.72, 0.25, 0.78, 0.30],
  "headline_article_button": null
}
```

### Error Handling

If subagent returns non-JSON, coordinator should:
1. Log the raw output
2. Retry up to max_retries
3. Return error after exhaustion

## Validation Rules

1. **Type Check**: All coordinates must be float
2. **Range Check**: 0.0 <= coordinate <= 1.0
3. **Order Check**: X1 < X2, Y1 < Y2
4. **Required Fields**: Must have "input_box" and "send_button"
5. **Optional Fields**: "headline_article_button" can be null

## Timeout

- Default timeout: 30 seconds
- Configurable via `--subagent-timeout` parameter
