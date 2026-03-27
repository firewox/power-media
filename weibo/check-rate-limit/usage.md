# check-rate-limit

检查微博 API 的限流状态。

## 功能

- 查询 IP 级别限流状态
- 查询用户级别限流状态
- 显示限流重置时间
- 可视化展示配额使用情况

## 安装

```bash
cd /mnt/d/08_tmp/02_media/power-media/weibo/check-rate-limit/scripts
pip3 install requests python-dotenv
```

## 配置

设置环境变量：

```bash
export WEIBO_ACCESS_TOKEN="你的 Access Token"
```

## 使用方法

### CLI 使用

```bash
python3 scripts/check-rate-limit.py
```

带选项：

```bash
python3 scripts/check-rate-limit.py --json    # JSON 格式输出
python3 scripts/check-rate-limit.py --raw     # 原始 API 响应
```

### 作为模块使用

```python
from scripts.check_rate_limit import RateLimitChecker

checker = RateLimitChecker(access_token)
info = checker.check_rate_limit()
print(info)
```

## 输出格式

**默认输出：**

```
============================================================
微博 API 限流状态
============================================================

【IP 级别限流】
  总配额: 15,000 次/小时
  已使用: 50 次 (0.33%)
  剩余:   14,950 次
  [█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 0.33%

【用户级别限流】
  总配额: 30 次/小时
  已使用: 5 次 (16.67%)
  剩余:   25 次
  [████░░░░░░░░░░░░░░░░░░░░░░░░░░] 16.67%

限流重置时间: 2026-03-27 11:00:00

【发布限制说明】
  - 每小时最多发布 30 条微博
  - 单张图片最大 5MB
  - 文本长度最多 140 个中文字符
============================================================
```

**JSON 格式：**

```json
{
  "ip_limit": 15000,
  "ip_remaining": 14950,
  "user_limit": 30,
  "user_remaining": 25,
  "reset_time": "2026-03-27 11:00:00"
}
```

## 限流规则

- IP 级别：15,000 次/小时
- 用户级别：30 次/小时（发布微博）
- 限流每小时重置
