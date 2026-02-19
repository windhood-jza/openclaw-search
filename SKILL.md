---
name: openclaw-search
description: 搜索 OpenClaw 相关文档和用例
metadata: {"openclaw": {"trigger": "openclaw"}}
---

# OpenClaw Search 技能

从 OpenClaw 相关的 GitHub 仓库中查询信息。

## 触发词

必须包含 `openclaw`，可选 `搜索`、`查一下`、`用例`、`技能`

## 使用方式

```
openclaw 有什么编程相关的用例？
openclaw 搜索 skill 创建
openclaw 用例
openclaw 文档
```

## 依赖

- curl（系统已有）

## 输出格式

返回结构化信息：
- 匹配的仓库（名称、描述、星数）
- 相关文件（README 等）
- 链接
