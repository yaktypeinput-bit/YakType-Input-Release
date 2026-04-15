# Gemini 集成指南 (Shared Core)

## 概要说明

本文档详述了 Gemini 引擎在 YakType 中的实现细节。Gemini 引擎是系统默认的多模态处理方案，同时承担语音转录（Speech-to-Text）与文本润色（Text-to-Text）两项核心任务。通过阅读本文档，您可以了解 Gemini REST API 的接入流程、音频分段处理策略、以及针对 ASR 场景的 Prompt 优化方法。

## 工作原理

Gemini 引擎通过 Google Generative Language REST API 实现，采用 `v1beta` 版本的 `generateContent` 接口。

### 1. 语音转录 (Transcription)
*   **实时编码**：捕捉到的 PCM Float32 音频流会被实时编码为 AAC (M4A) 格式，以 Base64 形式嵌入 JSON 载荷发送。
*   **分段策略**：
    *   **最大时长**：单段音频限制为 150 秒（`maxSegmentDuration`）。
    *   **速率限制缓冲**：段与段之间设置有 10 秒的延迟（`delayBetweenSegments`），以避免触发 API 的频率限制（Rate Limit）。
*   **多段拼接**：系统会自动维护 `finalizedTranscript` 缓冲区，将按序返回的段落文本自动拼接。

### 2. 文本润色 (Polishing)
*   **系统指令**：利用 `system_instruction` 传入用户定义的 Prompt 模板。
*   **参数控制**：固定 `temperature` 为 0.1，以确保生成结果的客观性与确定性，减少 AI 的随机发挥。

## 配置参数 (Configuration)

| 参数名 | 说明 | 推荐值 |
| :--- | :--- | :--- |
| `apiKey` | Google AI Studio 申请的 API 密钥。 | - |
| `modelName` | 调用的模型版本。 | `gemini-3.1-flash-lite-preview` |

## 优化逻辑

### AI 幻听与废话过滤
由于 Gemini 是通用大模型，在处理空音频或静音片段时可能会产生引导性对话（如“你好，请问有什么可以帮您？”）。引擎内部实现了 `aiChatterPhrases` 过滤列表，在文本交付业务层前会自动剔除这些已知干扰项。

### MIME 类型适配
根据音频来源不同，引擎会自动匹配特定的 MIME 类型：
*   **实时流**：`audio/mp4` (AAC)。
*   **离线文件**：`audio/ogg` (Opus)。

## 常见问题与排障 (Troubleshooting)
*   **503 Error**：通常表示当前模型请求量过大，系统状态机捕获此错误后会在 HUD 显示“发生错误”，建议用户稍后重试。
*   **API Key 验证失败**：请检查 `EngineProfile` 中的密钥是否包含多余的空格。
