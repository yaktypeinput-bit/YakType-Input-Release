# 后处理引擎接入指南 (Adding-Polishing-Engine.md)

## 概要说明

后处理引擎 (Polishing Engine / Post-processing Engine) 的核心职责是对已生成的文本进行重构。在 YakType 中，后处理引擎通常作为流水线的第二步，负责文本润色、格式修复或风格转换。本文档规定了实现一个新后处理引擎的技术要求。

## 核心职责

1.  **文本生成**：接收一段原始文本 (`text`) 与一段指令 (`prompt`)，通过 LLM 生成目标文本。
2.  **异步处理**：利用 Swift `async/await` 模式，确保大模型生成的长耗时操作不会阻塞 UI。
3.  **Prompt 注入**：能够解析来自 `EngineProfile` 的 `currentPrompt` 或独立传入的 `prompt` 参数。

## 实现步骤

### 1. 协议实现 (SpeechRecognitionEngine)

主要关注 `polish` 方法，这是后处理逻辑的核心：

```swift
public func polish(text: String, prompt: String) async throws -> String {
    // 1. 设置状态 self.status = .processing
    // 2. 构造从 apply(config:) 中获得的请求参数（如 API Key, Model ID, Temperature, Max Tokens 等）
    // 3. 调用 AI 接口（如 OpenAI, Gemini, etc.）
    // 4. 成功后更新 self.transcript 并返回最终文本
    // 5. 将 self.status 切换回 .ready
}
```

### 2. 补全协议属性

由于协议继承自 `ObservableObject`，所有状态相关属性必须标记为 `@Published`：

```swift
@Published public var status: SpeechEngineStatus = .idle
@Published public var transcript: String = ""
@Published public var statusMessage: String = ""
@Published public var selectedLanguage: String = "auto"
@Published public var currentPrompt: String = "" // 必须实现，即使不使用音频
public var configuration: EngineConfiguration { EngineConfiguration(maxSegmentDuration: 30, delayBetweenSegments: 0.5) } 
```

### 3. 配置与注册

1.  **配置扩展 (`Sources/Shared/Models/EngineProfile.swift`)**：
    *   在 `EngineProfileConfig` 枚举中增加新 Case。
    *   实现 `toDictionary()` 和 `fromDictionary()` 映射逻辑。
    *   在 `ConfigFieldDescriptor` 中定义模型 ID、API Key、Temperature、Timeout 等 UI 字段。
2.  **工厂注册 (`Sources/Shared/Engines/SpeechEngineFactory.swift`)**：
    *   在 `create(for:)` 中实例化新引擎。

### 4. UI 联动与角色限制

- **角色定义 (`Sources/Shared/Models/EngineType.swift`)**：
    *   必须在 `EngineType.swift` 的 `supportedRoles` 属性中注册新引擎支持的角色（`.dictation` 或 `.polishing`）。
    *   **Polishing-only** 引擎（如 OpenAI）应仅返回 `[.polishing]`。
- **Onboarding 过滤**：
    *   [**OnboardingView.swift**](file:///Users/pengyue/project/yaktype-workspace/yaktype/Sources/macOS/UI/OnboardingView.swift) 的 “New Instance” 菜单已配置为仅显示 `supportedRoles` 包含 `.dictation` 的引擎类型。如果是纯润色引擎，它不会出现在新手引导的听写设置中，这是预期的行为。
- **图标配对**：
    *   在 `OnboardingView` 的 `iconName(for:)` 中为新引擎配对 SF Symbol 系统图标（必须包含以防编译失败）。
- **其他 UI 开关**：
    *   **重要：** 必须更新以下文件的 **Exhaustive Switch**：
        *   [**EngineCard.swift**](file:///Users/pengyue/project/yaktype-workspace/yaktype/Sources/macOS/UI/Components/EngineCard.swift)：`description` 计算属性。
        *   [**TranscriptionService.swift**](file:///Users/pengyue/project/yaktype-workspace/yaktype/Sources/Shared/Services/TranscriptionService.swift)：`apply(profile:...)` 中的配置应用逻辑。

## 注意事项

- **无须音频处理**：纯润色引擎可以将 `process(audioChunk:)` 与 `process(fileURL:)` 置为空实现，或仅保留默认行为。
- **错误捕获**：在 `polish` 中，如果發生网络请求错误，应抛出具体的 `Error`。Service 层会捕获这些错误并向用户展示“润色失败，保留原稿”的提示。
- **响应速度**：建议在调用 LLM 时设置适当的超时时间（Timeout），并根据需要 provide `statusMessage`（如 "Generative AI is thinking..."）。
- **通用性**：对于 OpenAI 兼容引擎，建议允许 API Key 为空，以支持 Ollama 或 LM Studio 等本地 Provider。

## 参考实现
- [**OpenAISpeechEngine.swift**](file:///Users/pengyue/project/yaktype-workspace/yaktype/Sources/Shared/Engines/OpenAI/OpenAISpeechEngine.swift) - 标准的基于 OpenAI 兼容 API 的润色引擎实现，包含 Temperature、Max Tokens 和 Timeout 配置。
- [**GeminiSpeechEngine.swift**](file:///Users/pengyue/project/yaktype-workspace/yaktype/Sources/Shared/Engines/Gemini/GeminiSpeechEngine.swift) - 同时集成了听写与润色双重能力的复合引擎示例。
