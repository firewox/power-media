# eye-util 快速开始

## 前置条件

- Python >= 3.12
- 已安装 `ollama` Python 包（`uv add ollama` 或 `pip install ollama`）

## 第一步：选择运行模式

### 本地模式（Ollama 本地服务）

需要先在本机启动 Ollama 服务：

```bash
# 安装 Ollama（如果还没装）
# 从 https://ollama.com 下载安装

# 拉取模型
ollama pull gemma4:e4b

# 确认服务运行中
ollama list
```

配置文件参考：`eye-util/references/powermedia.config.local.template.json`

### 云端模式（ollama.com）

需要注册 ollama.com 账号并获取 API Key：

1. 访问 https://ollama.com 注册账号
2. 进入 Settings → API Keys，生成一个 Key
3. 设置环境变量：`set OLLAMA_API_KEY=sk-xxxx`

配置文件参考：`eye-util/references/powermedia.config.cloud.template.json`

## 第二步：创建配置文件

选择对应模板，复制到项目根目录并重命名为 `powermedia.config.json`：

```bash
# 本地模式
cp .claude/skills/power-media/eye-util/references/powermedia.config.local.template.json powermedia.config.json

# 或云端模式
cp .claude/skills/power-media/eye-util/references/powermedia.config.cloud.template.json powermedia.config.json
```

## 第三步：验证配置

```python
# test_connection.py
from ollama_wrapper import create_ollama_api

api = create_ollama_api()
result = api.chat(prompt="回复'连接成功'四个字")
print(result)
```

输出 `连接成功` 即表示配置生效。

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `OLLAMA_API_KEY` 未设置 | 云端模式需要 API Key | `set OLLAMA_API_KEY=sk-xxx` |
| `Connection refused` | Ollama 本地服务未启动 | `ollama serve` 或启动 Ollama 桌面端 |
| `model not found` | 模型未下载 | `ollama pull <模型名>` |
| `FileNotFoundError: powermedia.config.json` | 缺少配置文件 | 从模板复制一份 |
