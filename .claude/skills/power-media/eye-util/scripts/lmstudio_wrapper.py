import base64
import json
import mimetypes
import warnings
from pathlib import Path
from typing import Iterator, Optional, Union

from openai import OpenAI


class LMStudioAPI:
    def __init__(self, config: dict):
        self._config = config
        self._client = OpenAI(
            base_url=config.get("host", "http://localhost:1234/v1"),
            api_key="lm-studio",
        )
        self._model = config.get("model", "google/gemma-4-e4b")

    def warm_up(self):
        try:
            self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=1,
            )
        except Exception:
            pass

    def list_models(self) -> list[dict]:
        return self._client.models.list().data

    def _image_to_data_url(self, image_path: str) -> str:
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"file not found: {image_path}")
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = "image/png"
        encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
        return f"data:{mime_type};base64,{encoded}"

    def _build_content(
        self,
        prompt: str,
        image_paths: list[str],
    ) -> list[dict]:
        placeholder = "<image>"
        count = prompt.count(placeholder)

        if count == 0:
            content: list[dict] = [{"type": "text", "text": prompt}]
            for p in image_paths:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": self._image_to_data_url(p)},
                })
            return content

        if count != len(image_paths):
            raise ValueError(
                f"prompt has {count} <image> placeholder(s) "
                f"but {len(image_paths)} image path(s) provided"
            )

        parts = prompt.split(placeholder)
        content = []
        for i, part in enumerate(parts):
            if part:
                content.append({"type": "text", "text": part})
            if i < len(image_paths):
                content.append({
                    "type": "image_url",
                    "image_url": {"url": self._image_to_data_url(image_paths[i])},
                })
        return content

    def _build_messages(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        image_paths: Optional[list[str]] = None,
    ) -> list[dict]:
        content = self._build_content(prompt, image_paths or [])
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": content})
        return messages

    def chat(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        image_path: Optional[str] = None,
        image_paths: Optional[list[str]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stream: bool = False,
    ) -> Union[str, Iterator[str]]:
        if model is None:
            model = self._model

        all_paths: list[str] = []
        if image_paths:
            all_paths = image_paths
        elif image_path:
            all_paths = [image_path]

        messages = self._build_messages(prompt, system_prompt, all_paths)

        response = self._client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
        )

        if stream:
            return self._stream_text(response)

        return response.choices[0].message.content or ""

    def _stream_text(self, response) -> Iterator[str]:
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield content


def create_lmstudio_api(config_path: Optional[str] = None) -> LMStudioAPI:
    if config_path is None:
        config_path = str(Path(__file__).resolve().parent.parent.parent.parent.parent / "powermedia.config.json")

    config_file = Path(config_path)
    if not config_file.exists():
        warnings.warn(f"config file not found: {config_path}, using default (localhost:1234)")
        return LMStudioAPI({
            "host": "http://localhost:1234/v1",
            "model": "google/gemma-4-e4b",
        })

    config = json.loads(config_file.read_text(encoding="utf-8"))
    lmstudio_config = config.get("lmstudio", {})
    return LMStudioAPI(lmstudio_config)
