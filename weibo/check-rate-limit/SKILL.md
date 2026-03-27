---
name: check-rate-limit
description: |
  检查微博 API 的限流状态。

  当用户说以下任何内容时触发此 skill：
  - "检查微博限流"
  - "查看 API 限制"
  - "检查还能发多少条微博"
  - "微博 API 状态"
  - "check weibo rate limit"
  - 任何涉及查询微博 API 限流状态的请求

  此 skill 返回：
  - IP 级别限流状态
  - 用户级别限流状态
  - 限流重置时间
  - 发布配额使用情况

  使用前必须配置微博开放平台凭据。

compatibility: |
  - Python 3.8+
  - 有效的 Access Token
  - 依赖：requests, python-dotenv
---

# 检查微博 API 限流状态

## 工作流程

1. 检查环境变量（WEIBO_ACCESS_TOKEN）
2. 调用微博 API 查询限流状态
3. 格式化并显示限流信息

## 输入参数

无

## 输出结果

```json
{
  "ip_limit": 15000,
  "ip_remaining": 14950,
  "ip_used": 50,
  "ip_usage_percent": 0.33,
  "user_limit": 30,
  "user_remaining": 25,
  "user_used": 5,
  "user_usage_percent": 16.67,
  "reset_time": "2026-03-27 11:00:00"
}
```

## 配置要求

必须设置环境变量：

```bash
export WEIBO_ACCESS_TOKEN="你的 Access Token"
```

## 限流说明

| 级别 | 限制 | 说明 |
|------|------|------|
| IP 级别 | 15,000 次/小时 | 同一 IP 的所有请求 |
| 用户级别 | 30 次/小时 | 同一用户的发布请求 |

## 使用示例

**示例 1：**
```
用户：检查微博限流状态
结果：
  IP 级别: 已使用 50/15000 (0.33%)
  用户级别: 已使用 5/30 (16.67%)
  还可以发布 25 条微博
```

**示例 2：**
```
用户：我还能发多少条微博？
结果：您还可以发布 25 条微博（用户级别限制）
```

## 注意事项

1. **IP 限流**：每小时 15,000 次请求
2. **用户限流**：每小时最多发布 30 条微博
3. **重置时间**：限流每小时重置一次

## 依赖安装

```bash
cd /mnt/d/08_tmp/02_media/power-media/weibo/check-rate-limit/scripts
pip3 install requests python-dotenv
```
