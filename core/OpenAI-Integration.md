# OpenAI / 自定义 API 集成指南 (Shared Core)

## 概要说明

本文档详述了 YakType 中 **OpenAI 兼容引擎** 的实现细节。该引擎是一个通用的后处理（Polishing）工具，通过标准的 OpenAI Chat Completions 协议，支持接入包括 OpenAI 官方、DeepSeek、Groq、以及任何符合该协议的自建或第三方大模型后端。

## 工作原理

引擎调用 `v1/chat/completions` 接口，将转录结果作为用户消息发送给 AI。

### 1. 技术实现
*   **接口版本**：采用 `v1` 版本的 Chat Completions 接口。
*   **请求模式**：非流式（Non-streaming）请求，确保润色结果的一次性完整输出。
*   **上下文处理**：
    *   **系统消息 (System Message)**：传入用户配置的 `PromptTemplate`。
    *   **用户消息 (User Message)**：传入待处理的原始转录文本。

### 2. 核心参数
*   **Temperature**：默认设置为 `0.1`。保持较低的温度可以确保润色后的文本逻辑严谨，减少 AI 的随意发挥。
*   **Base URL**：支持自定义，从而实现对各类兼容厂商的无缝切换。

## 配置参考 (Configuration)

| 参数名 | 说明 | 示例值 |
| :--- | :--- | :--- |
| `apiKey` | API 密钥。 | `sk-xxxx...` |
| `baseURL` | API 的根地址。 | `https://api.openai.com/v1` |
| `modelName` | 调用的模型标识符。 | `gpt-4o`, `deepseek-chat` |
| `temperature` | 生成温度（0.0 - 1.0）。 | `0.1` |

## 典型配置场景

### 场景 A：OpenAI 官方
*   **Base URL**: `https://api.openai.com/v1`
*   **Model Name**: `gpt-4o`

### 场景 B：DeepSeek (国产高性能方案)
*   **Base URL**: `https://api.deepseek.com`
*   **Model Name**: `deepseek-chat`

### 场景 C：本地端 (Ollama / LocalAI)
*   **Base URL**: `http://localhost:11434/v1`
*   **Model Name**: `llama3`

## 注意事项 (Important)

*   **URL 格式**：请确保 Base URL **不包含** `/chat/completions` 后缀，引擎内部会自动拼接。
*   **角色限制**：该引擎目前仅作为 **后处理（Polishing）** 角色设计。若尝试将其用于语音转录任务（Dictation），将返回功能未实现的错误。
