import base64
import mimetypes
from pathlib import Path
from typing import Iterator, Optional, Union

from openai import OpenAI


class LMStudioAPI:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        base_url: str = "http://localhost:1234/v1",
        model: str = "google/gemma-4-e4b",
    ):
        if self._initialized:
            return
        self._client = OpenAI(base_url=base_url, api_key="lm-studio")
        self._model = model
        self._warmed_up = False
        self._initialized = True

    def warm_up(self):
        if not self._warmed_up:
            try:
                self._client.chat.completions.create(
                    model=self._model,
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=1,
                )
                self._warmed_up = True
            except Exception:
                pass

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

    def chat(
        self,
        prompt: str,
        image_path: Optional[str] = None,
        image_paths: Optional[list[str]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stream: bool = False,
    ) -> Union[str, Iterator[str]]:
        #self.warm_up()

        all_paths: list[str] = []
        if image_paths:
            all_paths = image_paths
        elif image_path:
            all_paths = [image_path]

        content = self._build_content(prompt, all_paths)

        response = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": content}],
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
