import time
from typing import Any


class ActionLogger:
    def __init__(self, log_file: str | None = "computer-mcp.log"):
        self.log_file = log_file
        self.entries: list[dict] = []

    def record(self, tool: str, params: dict[str, Any]) -> dict:
        safe_params = self._redact(params)
        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "tool": tool,
            "params": safe_params,
        }
        self.entries.append(entry)
        if self.log_file:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(str(entry) + "\n")
        return entry

    def _redact(self, params: dict[str, Any]) -> dict[str, Any]:
        if params.get("secret"):
            return {**params, "text": "[REDACTED]"}
        return params
