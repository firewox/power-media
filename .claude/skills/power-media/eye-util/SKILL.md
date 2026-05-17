---
name: eye-util
description: |
  封装多模型后端的统一调用工具，支持 Ollama（本地/云端）和 LMStudio（OpenAI 兼容）两种后端。
  自动读取 powermedia.config.json 配置，提供 chat、多模态图片理解等能力。

  当用户说以下内容时触发此 skill：
  - "用 Ollama 分析图片"
  - "用 LMStudio 问答"
  - "让模型看看这张图"
  - "调用云端模型"
  - "调用本地模型"
  - 任何需要调用视觉模型（Ollama / LMStudio）的请求

  支持后端：
  1. Ollama — 本地 Ollama 服务 + ollama.com 云端 API
  2. LMStudio — 本地 LMStudio 服务（OpenAI 兼容接口）

  共同能力：
  - 文本对话（支持 system prompt）
  - 单图/多图理解
  - 流式输出
  - <image> 占位符内联图片（LMStudio）/ base64 图片（Ollama）

  配置：
  - 读取项目根目录 powermedia.config.json
  - Ollama 云端模式需要环境变量 OLLAMA_API_KEY
  - LMStudio 默认连接 localhost:1234

compatibility:
  - Python >= 3.12
  - ollama >= 0.6.2（Ollama 后端）
  - openai >= 1.0（LMStudio 后端）
  - Windows 10/11
---

# eye-util - 多模型后端调用工具

## 概述

提供统一的多后端 API 封装，支持 Ollama 和 LMStudio，自动根据 `powermedia.config.json` 切换后端。

## 后端对比

| 特性 | Ollama | LMStudio |
|------|--------|----------|
| 协议 | Ollama 原生 API | OpenAI 兼容 API |
| 本地连接 | localhost:11434 | localhost:1234/v1 |
| 云端支持 | ollama.com 云端 API | 无（仅本地） |
| 图片格式 | base64 字符串 | data URL（base64 + MIME） |
| 图片占位 | 不支持内联占位 | 支持 `<image>` 内联占位 |
| temperature | 不支持 | 支持 |
| system_prompt | 支持 | 支持 |
| 依赖 | `ollama` | `openai` |

## 配置

在项目根目录的 `powermedia.config.json` 中配置：

```json
{
  "ollama": {
    "mode": "cloud",
    "model": "gemma4:31b-cloud",
    "host": "https://ollama.com"
  },
  "lmstudio": {
    "model": "google/gemma-4-e4b",
    "host": "http://localhost:1234/v1"
  }
}
```

| 字段 | 说明 |
|------|------|
| ollama.mode | `local` 或 `cloud`（本地模式连接 localhost:11434） |
| ollama.model | Ollama 默认模型名 |
| ollama.host | Ollama 服务地址 |
| lmstudio.model | LMStudio 默认模型名 |
| lmstudio.host | LMStudio OpenAI 兼容端点 |

- Ollama 云端模式需要设置环境变量 `OLLAMA_API_KEY`
- LMStudio 无需额外认证，端口和模型通过 LMStudio 桌面端配置

## 使用方法

### Ollama 后端

#### 从命令行调用
```bash
python -c "from eye_util.scripts.ollama_wrapper import create_ollama_api; api = create_ollama_api(); print(api.chat(prompt='你好'))"
```

#### 从 Python 代码调用
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

### LMStudio 后端

#### 从命令行调用
```bash
python -c "from eye_util.scripts.lmstudio_wrapper import create_lmstudio_api; api = create_lmstudio_api(); print(api.chat(prompt='你好'))"
```

#### 从 Python 代码调用
```python
from eye_util.scripts.lmstudio_wrapper import create_lmstudio_api

api = create_lmstudio_api()

# 文本对话
for chunk in api.chat("用中文简单介绍一下你自己", stream=True):
    print(chunk, end="", flush=True)

# 单图理解（<image> 占位符内联）
result = api.chat(
    "这是图片：<image>，请描述它的内容",
    image_path="screenshot.png",
)

# 多图对比（<image> 占位符精确位置）
result = api.chat(
    "图片1：<image>，图片2：<image>，两者有什么不同？",
    image_paths=["image1.png", "image2.png"],
)

# System Prompt + Temperature
result = api.chat(
    prompt="你是谁？",
    system_prompt="你是一个猫娘，用喵结尾",
    temperature=0.8,
)

# 列出可用模型
models = api.list_models()
```

## API 参考

### Ollama 后端

#### `create_ollama_api(config_path=None) → OllamaAPI`

工厂函数，读取配置文件返回 `OllamaCloudAPI` 或 `OllamaLocalAPI`。

#### `api.chat(prompt, model=None, system_prompt=None, image_path=None, image_paths=None, stream=False, max_tokens=None)`

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

### LMStudio 后端

#### `create_lmstudio_api(config_path=None) → LMStudioAPI`

工厂函数，读取配置文件 `lmstudio` 节，返回 `LMStudioAPI` 实例。

#### `api.chat(prompt, model=None, system_prompt=None, image_path=None, image_paths=None, temperature=0.7, max_tokens=1024, stream=False)`

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| prompt | str | 必填 | 用户输入，支持 `<image>` 占位符 |
| model | str | 配置中的 model | 模型名，可覆盖默认值 |
| system_prompt | str | None | 系统提示词 |
| image_path | str | None | 单张图片路径 |
| image_paths | list[str] | None | 多张图片路径列表 |
| temperature | float | 0.7 | 生成温度 (0.0 ~ 2.0) |
| max_tokens | int | 1024 | 最大输出 token 数 |
| stream | bool | False | 是否流式 |

返回值：`stream=True` 时返回 `Iterator[str]`，否则返回 `str`。

#### `<image>` 占位符机制

LMStudio 支持 `<image>` 占位符将图片精确嵌入 prompt 中的指定位置：

```python
# 无占位符：图片自动追加到 prompt 末尾
api.chat("描述这些图片", image_paths=["a.png", "b.png"])

# 有占位符：图片按占位符位置插入
api.chat("<image> 和 <image> 有什么区别？", image_paths=["a.png", "b.png"])
```

占位符数量必须与 `image_paths` 数量一致，否则抛出 `ValueError`。

#### `api.list_models()`

返回 LMStudio 当前加载的模型列表。

#### `api.warm_up()`

发送一条短请求预热模型，减少首次调用的延迟。
