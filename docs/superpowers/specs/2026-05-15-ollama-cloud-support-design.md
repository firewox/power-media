# Ollama Cloud 支持

**日期**: 2026-05-15
**状态**: 设计中

---

## 背景

`ollama_wrapper.py` 当前仅支持本地 Ollama 实例。需要增加对 Ollama Cloud (`https://ollama.com`) 的支持，通过配置文件切换模式。

## 需求

1. 支持两种运行模式：「本地 Ollama」和「Ollama Cloud」
2. 模式、模型、host 等信息从 `powermedia.config.json` 读取
3. Cloud 模式通过 `OLLAMA_API_KEY` 环境变量鉴权
4. 调用方无需感知当前模式，通过统一的 factory 函数获取实例
5. 接口向后兼容，原有流式、图片、系统提示词等功能保持不变

## 配置 (`powermedia.config.json`)

```json
{
  "ollama": {
    "mode": "local",
    "model": "gemma4:e4b",
    "host": "http://localhost:11434"
  }
}
```

## 架构

采用 **Factory + 子类** 模式：

```
create_ollama_api()          # Factory — 读取配置，返回子类实例
    ├── OllamaLocalAPI       # 本地模式
    └── OllamaCloudAPI       # 云端模式
```

### 类层次

```
OllamaAPI (基类)
├── _client: Client
├── _config: dict
├── _encode_file(file_path) -> str
├── _build_messages(prompt, system_prompt, image_path, image_paths) -> list[dict]
├── chat(prompt, model, system_prompt, image_path, image_paths, stream, max_tokens)
│     -> str | Iterator[str]
├── _stream_text(response) -> Iterator[str]
└── _get_chat_kwargs(model, messages, stream, max_tokens) -> dict   # 子类覆盖

OllamaLocalAPI(OllamaAPI)
├── __init__: Client(host=config["host"])
└── _get_chat_kwargs: 添加 device="cuda"

OllamaCloudAPI(OllamaAPI)
├── __init__: Client(host="https://ollama.com", headers={"Authorization": ...})
└── _get_chat_kwargs: 不添加 device 参数
```

### 差异点

| 维度 | 本地 | 云端 |
|------|------|------|
| host | 配置文件指定 | 固定 `https://ollama.com` |
| auth | 无 | `Bearer <OLLAMA_API_KEY>` |
| device | 传入 `"cuda"` | 不传 |

## 错误处理

| 场景 | 行为 |
|------|------|
| 配置文件不存在 | 使用内置默认值，打印 warning |
| cloud 模式缺 `OLLAMA_API_KEY` | `RuntimeError` |
| 文件/图片不存在 | `FileNotFoundError` |

## 兼容性

现有调用方改动极小：

```python
# 旧
from ollama_wrapper import OllamaAPI
api = OllamaAPI()

# 新
from ollama_wrapper import create_ollama_api
api = create_ollama_api()
```

`chat()` 方法签名和行为完全不变。
