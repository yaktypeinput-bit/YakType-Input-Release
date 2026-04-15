# 阿里云 ASR 引擎集成指南 (Shared Core)

## 概要说明

本文档详述了阿里云语音识别（ASR）引擎在 YakType 中的集成实现方案。该引擎基于阿里云 DashScope 的 OpenAI 兼容接口，专门用于音频采集后的原始文字转换。通过阅读本文档，您可以了解引擎的 OGG (Opus) 编码机制、OpenAI `input_audio` 接口的调用规范以及针对长语音的分布式切分策略。

## 工作原理

阿里云 ASR 引擎采用典型的“采集-编码-上传-识别”的全链路异步处理模式。

### 1. 音频编码 (OGG/Opus)
与 Gemini 直接使用 AAC 编码不同，阿里云引擎首选 **OGG (Opus)** 格式以获得极高的压缩比与音频质量平衡：
*   **重采样**：将输入的 44.1kHz/48kHz 音频下采样至 **16kHz** (单声道)，这是 ASR 模型的最佳识别频率。
*   **编码器**：利用 `SwiftOGG` 将 PCM 数据包装为符合阿里云识别规范的 OGG 二进制流。

### 2. API 调用规范
引擎对接阿里云 DashScope 的 OpenAI 兼容接口（`/chat/completions`）：
*   **内容类型**：使用 `input_audio` 负载，将音频数据以 Base64 Data URI 形式嵌入。
*   **模型指令**：虽然主要用于 ASR，但底层请求仍遵循对话模型格式，通过 `extra_body` 中的 `asr_options` 开启 **ITN (逆文本标准化)**，将口语中的日期、数字自动转为书面格式。

### 3. 长音频处理 (Segmentation)
针对超过 150 秒的长语音，系统会进入分布式切分模式：
*   **自动切分**：音频被逻辑切分为多个片段（Segments）。
*   **串行提交**：通过 `segmentQueue` 按序提交至云端，段落间隔 10 秒以规避 API 频率限制。
*   **文本累加**：由 `finalizedTranscript` 负责维护上下文稳定性，将识别出的各段文本按时间线动态拼接。

## 配置参数 (Configuration)

| 参数名 | 默认值 | 描述 |
| :--- | :--- | :--- |
| `apiKey` | (空) | 阿里云 DashScope 管理控制台申请的有效密钥。 |
| `modelName` | `qwen-asr-latest` | 调用的模型标识符。可选 `qwen-asr-v1` 或最新快照。 |
| `endpoint` | `https://dashscope.aliyuncs.com/compatible-mode/v1` | 兼容 OpenAI 协议的中转网关。 |

## 优化手段
*   **静音裁剪**：在调用 API 前，由 `AudioProcessor` 执行 VAD（语音激活检测），剔除首尾无效静音，降低 API 调用成本并提升响应速度。
*   **错误自愈**：当分段上传失败时，系统会尝试捕获 JSON 响应中的 `error.message` 并通过 HUD 实时反馈给用户。

## 常见问题
*   **API 响应慢**：请确认所选区域（Region）与网络环境。阿里云 ASR 服务端通常处理速度极快，延迟通常主要来自音频上行传输。
*   **识别乱码**：请检查 API Key 的有效性及账户余额。
