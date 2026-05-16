---
name: eye-util
description: |
  封装 Ollama API 的调用工具，支持本地和云端两种模式。
  自动读取 powermedia.config.json 配置，提供 chat、多模态图片理解等能力。

  当用户说以下内容时触发此 skill：
  - "用 Ollama 分析图片"
  - "ollama 问答"
  - "让模型看看这张图"
  - "调用云端模型"
  - 任何需要调用 Ollama 模型（本地或云端）的请求

  支持功能：
  - 文本对话（支持 system prompt）
  - 单图/多图理解
  - 流式输出
  - 本地模式（localhost:11434） / 云端模式（ollama.com）

  配置：
  - 读取项目根目录 powermedia.config.json
  - 云端模式需要环境变量 OLLAMA_API_KEY
  - 默认使用 gemma4:31b-cloud

compatibility:
  - Python >= 3.12
  - ollama >= 0.6.2
  - Windows 10/11
---

# eye-util - Ollama 模型调用工具

## 概述

提供统一的 Ollama API 封装，自动根据 `powermedia.config.json` 切换本地/云端模式。

## 配置

在项目根目录的 `powermedia.config.json` 中配置：

```json
{
  "ollama": {
    "mode": "cloud",
    "model": "gemma4:31b-cloud",
    "host": "https://ollama.com"
  }
}
```

| 字段 | 说明 |
|------|------|
| mode | `local` 或 `cloud`（本地模式连接 localhost:11434） |
| model | 默认模型名 |
| host | Ollama 服务地址 |

云端模式需要设置环境变量 `OLLAMA_API_KEY`。

## 使用方法

### 从命令行调用
```bash
python -c "from eye_util.scripts.ollama_wrapper import create_ollama_api; api = create_ollama_api(); print(api.chat(prompt='你好'))"
```

### 从 Python 代码调用
```python
from eye_util.scripts.ollama_wrapper import create_ollama_api

api = create_ollama_api()

# 文本对话
result = api.chat(prompt="解释什么是神经网络", system_prompt="你是AI专家")
print(result)

# 流式输出
for chunk in api.chat(prompt="讲个笑话", stream=True):
    print(chunk, end="", flush=True)

# 图片理解
result = api.chat(
    prompt="这张图里有什么？",
    image_path="screenshot.png",
)
print(result)

# 多图理解
result = api.chat(
    prompt="这两张图有什么关联？",
    image_paths=["image1.png", "image2.png"],
)
print(result)
```

## API 参考

### `create_ollama_api(config_path=None) → OllamaAPI`

工厂函数，读取配置文件返回 `OllamaCloudAPI` 或 `OllamaLocalAPI`。

### `api.chat(prompt, model=None, system_prompt=None, image_path=None, image_paths=None, stream=False, max_tokens=None)`

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| prompt | str | 必填 | 用户输入 |
| model | str | 配置中的 model | 模型名，可覆盖默认值 |
| system_prompt | str | None | 系统提示词 |
| image_path | str | None | 单张图片路径 |
| image_paths | list[str] | None | 多张图片路径列表 |
| stream | bool | False | 是否流式 |
| max_tokens | int | None | 最大输出 token 数 |

返回值：`stream=True` 时返回 `Iterator[str]`，否则返回 `str`。
