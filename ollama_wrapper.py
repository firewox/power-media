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
