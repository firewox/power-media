# Ollama Cloud 支持 — 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 `ollama_wrapper.py` 增加 Ollama Cloud 支持，通过 Factory + 子类模式在本地和云端之间切换。

**Architecture:** `OllamaAPI` 基类持有共享逻辑（编码、消息构建、流式输出）；`OllamaLocalAPI` 和 `OllamaCloudAPI` 子类分别覆盖 `__init__` 和 `_get_chat_kwargs`；`create_ollama_api()` factory 读取 `powermedia.config.json` 返回对应子类实例。

**Tech Stack:** Python 3.12+, ollama >= 0.6.2, base64, json, os, pathlib

---

## Task 1: 创建配置文件 `powermedia.config.json`

**Files:**
- Create: `powermedia.config.json`

- [ ] **Step 1: 写入配置文件**

```json
{
  "ollama": {
    "mode": "local",
    "model": "gemma4:e4b",
    "host": "http://localhost:11434"
  }
}
```

- [ ] **Step 2: 验证文件存在**

Run: `Get-Content -LiteralPath "D:\08_tmp\01_code\04_personal\power-media\powermedia.config.json"`
Expected: 显示上述 JSON 内容

- [ ] **Step 3: Commit**

```bash
git add powermedia.config.json
git commit -m "feat: add powermedia.config.json for ollama mode configuration"
```

---

## Task 2: 重构 `ollama_wrapper.py` — 基类 + 子类 + factory

**Files:**
- Modify: `ollama_wrapper.py` (完整重写)

- [ ] **Step 1: 重写文件**

```python
import base64
import json
import os
import warnings
from pathlib import Path
from typing import Iterator, Optional, Union

from ollama import Client, ChatResponse


class OllamaAPI:
    def __init__(self, config: dict):
        self._config = config

    def _encode_file(self, file_path: str) -> str:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"file not found: {file_path}")
        return base64.b64encode(path.read_bytes()).decode("utf-8")

    def _build_messages(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        image_path: Optional[str] = None,
        image_paths: Optional[list[str]] = None,
    ) -> list[dict]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        user_msg: dict = {"role": "user", "content": prompt}
        if image_paths:
            user_msg["images"] = [self._encode_file(p) for p in image_paths]
        elif image_path:
            user_msg["images"] = [self._encode_file(image_path)]
        messages.append(user_msg)
        return messages

    def _get_chat_kwargs(
        self,
        model: str,
        messages: list[dict],
        stream: bool,
        max_tokens: Optional[int],
    ) -> dict:
        kwargs: dict = dict(model=model, messages=messages, stream=stream)
        if max_tokens is not None:
            kwargs["options"] = {"num_predict": max_tokens}
        return kwargs

    def chat(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        image_path: Optional[str] = None,
        image_paths: Optional[list[str]] = None,
        stream: bool = False,
        max_tokens: Optional[int] = None,
    ) -> Union[str, Iterator[str]]:
        if model is None:
            model = self._config.get("model", "gemma4:e4b")
        messages = self._build_messages(prompt, system_prompt, image_path, image_paths)
        kwargs = self._get_chat_kwargs(model, messages, stream, max_tokens)
        response = self._client.chat(**kwargs)
        if stream:
            return _stream_text(response)
        return response.message.content


class OllamaLocalAPI(OllamaAPI):
    def __init__(self, config: dict):
        super().__init__(config)
        self._client = Client(host=config.get("host", "http://localhost:11434"))

    def _get_chat_kwargs(
        self,
        model: str,
        messages: list[dict],
        stream: bool,
        max_tokens: Optional[int],
    ) -> dict:
        kwargs = super()._get_chat_kwargs(model, messages, stream, max_tokens)
        kwargs["device"] = "cuda"
        return kwargs


class OllamaCloudAPI(OllamaAPI):
    def __init__(self, config: dict):
        super().__init__(config)
        api_key = os.environ.get("OLLAMA_API_KEY")
        if not api_key:
            raise RuntimeError("OLLAMA_API_KEY environment variable is not set")
        self._client = Client(
            host="https://ollama.com",
            headers={"Authorization": "Bearer " + api_key},
        )

    def _get_chat_kwargs(
        self,
        model: str,
        messages: list[dict],
        stream: bool,
        max_tokens: Optional[int],
    ) -> dict:
        return super()._get_chat_kwargs(model, messages, stream, max_tokens)


def create_ollama_api(config_path: Optional[str] = None) -> OllamaAPI:
    if config_path is None:
        config_path = str(Path(__file__).resolve().parent / "powermedia.config.json")

    config_file = Path(config_path)
    if not config_file.exists():
        warnings.warn(f"config file not found: {config_path}, using default (local)")
        return OllamaLocalAPI({
            "mode": "local",
            "model": "gemma4:e4b",
            "host": "http://localhost:11434",
        })

    config = json.loads(config_file.read_text(encoding="utf-8"))
    ollama_config = config.get("ollama", {})

    mode = ollama_config.get("mode", "local")
    if mode == "cloud":
        return OllamaCloudAPI(ollama_config)
    return OllamaLocalAPI(ollama_config)


def _stream_text(response: Iterator[ChatResponse]) -> Iterator[str]:
    for chunk in response:
        content = chunk.message.content
        if content:
            yield content
```

- [ ] **Step 2: 验证语法正确**

Run: `python -c "import ast; ast.parse(open(r'D:\08_tmp\01_code\04_personal\power-media\ollama_wrapper.py', encoding='utf-8').read()); print('OK')"`
Expected: `OK`

- [ ] **Step 3: 验证模块可导入**

Run: `pip install -e .; if ($?) { python -c "from ollama_wrapper import OllamaAPI, OllamaLocalAPI, OllamaCloudAPI, create_ollama_api; print('import OK')" }`
Workdir: `D:\08_tmp\01_code\04_personal\power-media`
Expected: `import OK`

- [ ] **Step 4: Commit**

```bash
git add ollama_wrapper.py
git commit -m "feat: refactor ollama_wrapper.py with factory + subclass pattern for cloud support"
```

---

## Task 3: 更新 `ollama_example.py` 使用 factory 函数

**Files:**
- Modify: `ollama_example.py:1-3`

- [ ] **Step 1: 替换 import 和实例化**

```python
from ollama_wrapper import create_ollama_api

api = create_ollama_api()
```

确保文件其他部分（`image_test`, `chat_test` 等函数）不做任何改动。

- [ ] **Step 2: 验证语法正确**

Run: `python -c "import ast; ast.parse(open(r'D:\08_tmp\01_code\04_personal\power-media\ollama_example.py', encoding='utf-8').read()); print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add ollama_example.py
git commit -m "feat: update ollama_example.py to use create_ollama_api factory"
```

---

## Task 4: 验证 — 运行示例脚本

**Files:**
- 无新建或修改（仅验证）

- [ ] **Step 1: 验证 local 模式工厂能创建实例**

Run: `python -c "from ollama_wrapper import create_ollama_api; api = create_ollama_api(); print(type(api).__name__)"`
Workdir: `D:\08_tmp\01_code\04_personal\power-media`
Expected: `OllamaLocalAPI`

- [ ] **Step 2: 验证 cloud 模式工厂（环境变量缺失时应报错）**

Run: `python -c "from ollama_wrapper import create_ollama_api; import json, os; from pathlib import Path; text = json.dumps({'ollama': {'mode': 'cloud', 'model': 'gpt-oss:120b'}}); (Path('powermedia.config.cloud.json')).write_text(text, encoding='utf-8'); api = create_ollama_api('powermedia.config.cloud.json')"`
Workdir: `D:\08_tmp\01_code\04_personal\power-media`
Expected: `RuntimeError: OLLAMA_API_KEY environment variable is not set`

- [ ] **Step 3: 验证 cloud 模式（设置 API key 后）**

Run:
```powershell
$env:OLLAMA_API_KEY = "test-key";
python -c "from ollama_wrapper import create_ollama_api; api = create_ollama_api('powermedia.config.cloud.json'); print(type(api).__name__)";
Remove-Item Env:\OLLAMA_API_KEY
```
Workdir: `D:\08_tmp\01_code\04_personal\power-media`
Expected: `OllamaCloudAPI`

- [ ] **Step 4: 清理测试文件**

Run: `Remove-Item -LiteralPath "D:\08_tmp\01_code\04_personal\power-media\powermedia.config.cloud.json"`
Expected: 文件被删除

- [ ] **Step 5: 验证配置文件缺失时的默认行为**

Run:
```powershell
$temp_config = "temp_no_config.json";
python -c "from ollama_wrapper import create_ollama_api; api = create_ollama_api('$temp_config'); print(type(api).__name__)"
```
Workdir: `D:\08_tmp\01_code\04_personal\power-media`
Expected: `OllamaLocalAPI`（输出 warning）

- [ ] **Step 6: commit (no changes, verification only)** — 无需提交，仅验证通过即完成
