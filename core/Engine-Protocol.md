# 引擎协议接口 (Shared Core)

## 概要说明

本文档详述了 `SpeechRecognitionEngine` 协议的设计规范。该协议是 YakType 实现多引擎支持（包括 Apple 原生与 Gemini）的核心抽象层。通过阅读本文档，您可以了解如何为系统增加新的转录或润色引擎，以及引擎在运行时的状态转换与数据处理要求。

## 协议定义 (SpeechRecognitionEngine)

所有 AI 引擎必须实现 `SpeechRecognitionEngine` 协议，以确保能被 `TranscriptionService` 统一调度。

### 核心属性
*   **`status`**: 引擎当前的运行状态（详见下文状态说明）。
*   **`transcript`**: 引擎当前已识别/生成的文本内容。
*   **`statusMessage`**: 面向用户的状态描述语。
*   **`selectedLanguage`**: 识别语言（如 "zh-CN", "en-US" 或 "auto"）。

### 核心方法
1.  **`process(audioChunk: [Float])`**：处理来自音频捕获器的实时 PCM 数据块。
2.  **`process(fileURL: URL)`**：处理离线音频文件。
3.  **`polish(text: String, prompt: String)`**：可选方法。接收原始文本与 Prompt，返回润色后的文本。
4.  **`apply(config: EngineProfileConfig)`**：将持久化的 `EngineProfile` 配置应用到引擎实例。
5.  **`cancel() / reset()`**：任务取消与缓冲区清理。

## 引擎状态 (SpeechEngineStatus)

引擎必须在处理过程中准确报告以下状态：

| 状态 | 说明 |
| :--- | :--- |
| `idle` | 初始状态，未加载任务。 |
| `processing` | 正在进行网络请求或本地推理。 |
| `ready` | 任务处理完成，结果已准备就绪。 |
| `error(String)` | 处理发生异常，携带具体错误信息。 |

## 接入新引擎的步骤

1.  **实现协议**：在 `Sources/Shared/Engines` 下创建新目录并实现 `SpeechRecognitionEngine`。
2.  **扩展配置**：在 `EngineProfileConfig` 枚举中增加对应的配置子项，并定义 `ConfigFieldDescriptor` 以渲染 UI。
3.  **注册工厂**：在 `SpeechEngineFactory` 中增加新引擎的创建逻辑。
4.  **UI 适配**：在 `EngineType` 枚举中增加类型定义，以供用户在设置界面选择。

## 异常处理规范
*   引擎内部应自行处理网络超时与重试逻辑。
*   严重的 API 错误（如 Credential 无效、配额超限）应通过 `.error` 状态向上抛出，并由 Service 层反馈给用户。
