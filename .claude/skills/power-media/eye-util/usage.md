# eye-util 快速开始

## 前置条件

- Python >= 3.12
- 根据后端选择安装对应 Python 包

| 后端 | 安装命令 |
|------|---------|
| Ollama | `pip install ollama` |
| LMStudio | `pip install openai` |

## 选择后端

### Ollama 后端

#### 本地模式（Ollama 本地服务）

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

#### 云端模式（ollama.com）

需要注册 ollama.com 账号并获取 API Key：

1. 访问 https://ollama.com 注册账号
2. 进入 Settings → API Keys，生成一个 Key
3. 设置环境变量：`set OLLAMA_API_KEY=sk-xxxx`

配置文件参考：`eye-util/references/powermedia.config.cloud.template.json`

### LMStudio 后端

需要安装并运行 LMStudio 桌面端：

1. 从 https://lmstudio.ai 下载安装 LMStudio
2. 在 LMStudio 中下载模型（如 `google/gemma-4-e4b`）
3. 启动 LMStudio 本地推理服务：
   - 打开 LMStudio → 选择模型 → 点击 "Start Server"
   - 默认监听 `http://localhost:1234`
4. 确认服务运行中：访问 http://localhost:1234/v1/models 应返回模型列表

```bash
# 验证 LMStudio 服务
curl http://localhost:1234/v1/models
```

## 第二步：创建配置文件

选择对应模板，复制到项目根目录并重命名为 `powermedia.config.json`：

```bash
# Ollama 本地模式
cp .claude/skills/power-media/eye-util/references/powermedia.config.local.template.json powermedia.config.json

# 或 Ollama 云端模式
cp .claude/skills/power-media/eye-util/references/powermedia.config.cloud.template.json powermedia.config.json
```

配置文件中可同时包含 `ollama` 和 `lmstudio` 两个节：

```json
{
  "ollama": {
    "mode": "local",
    "model": "gemma4:e4b",
    "host": "http://localhost:11434"
  },
  "lmstudio": {
    "model": "google/gemma-4-e4b",
    "host": "http://localhost:1234/v1"
  }
}
```

## 第三步：验证配置

### Ollama 验证
```python
from eye_util.scripts.ollama_wrapper import create_ollama_api

api = create_ollama_api()
result = api.chat(prompt="回复'连接成功'四个字")
print(result)
```

### LMStudio 验证
```python
from eye_util.scripts.lmstudio_wrapper import create_lmstudio_api

api = create_lmstudio_api()
result = api.chat(prompt="回复'连接成功'四个字")
print(result)
```

输出 `连接成功` 即表示配置生效。

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `OLLAMA_API_KEY` 未设置 | Ollama 云端模式需要 API Key | `set OLLAMA_API_KEY=sk-xxx` |
| `Connection refused` | 服务未启动 | 启动对应后端服务 |
| `model not found` | 模型未下载 | 在对应平台下载模型 |
| `FileNotFoundError: powermedia.config.json` | 缺少配置文件 | 从模板复制一份 |
| LMStudio `Connection refused` | LMStudio Server 未启动 | 在 LMStudio 中点击 Start Server |
| `openai` 未安装 | LMStudio 后端依赖 openai 包 | `pip install openai` |
