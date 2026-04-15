# 听写引擎接入指南 (Adding-Dictation-Engine.md)

## 概要说明

听写引擎 (Dictation Engine) 的核心职责是将音频信号转换为文本。在 YakType 中，听写引擎通常作为流水线的第一步，负责实时捕获或文件转录。本文档规定了实现一个新听写引擎的技术要求。

## 核心职责

1.  **流式处理**：能够接收 16kHz 单声道 Float 格式的音频切片 (`audioChunk`)。
2.  **文件转录**：能够处理本地音频文件并返回完整文本。
3.  **状态反馈**：在处理过程中必须准确报告 `processing` 状态，并在完成时切换至 `ready`。

## 实现步骤

### 1. 协议实现 (SpeechRecognitionEngine)

在 `Sources/Shared/Engines` 下创建新目录，并实现核心方法：

```swift
public func process(audioChunk: [Float]) {
    // 1. 将音频推入内部缓冲区
    // 2. 如果满足发送条件（如静音检测或长度限制），发起 API 请求
    // 3. 更新 self.status = .processing
}

public func process(fileURL: URL) {
    // 1. 读取音频文件
    // 2. 发起离线转录请求
    // 3. 结果返回后更新 self.transcript 并设置 self.status = .ready
}
```

### 2. 补全协议属性

由于协议继承自 `ObservableObject`，所有状态相关属性必须标记为 `@Published`：

```swift
@Published public var status: SpeechEngineStatus = .idle
@Published public var transcript: String = ""
@Published public var statusMessage: String = ""
@Published public var selectedLanguage: String = "auto"
@Published public var currentPrompt: String = "" // 即使是听写引擎也必须保留此属性
public var configuration: EngineConfiguration { EngineConfiguration(maxSegmentDuration: 30, delayBetweenSegments: 0.5) } 
```

### 3. 配置定义 (`Sources/Shared/Models/EngineProfile.swift`)

- **配置结构**：在 `EngineProfileConfig` 枚举中增加新 Case。
- **序列化**：实现 `toDictionary()` 和 `fromDictionary()` 映射逻辑。
- **UI 描述符**：实现 `ConfigFieldDescriptor` 静态属性，定义 API Key、模型 ID 等 UI 输入项字段。

### 4. UI 联动与角色限制

- **角色定义 (`Sources/Shared/Models/EngineType.swift`)**：
    *   必须在 `EngineType.swift` 的 `supportedRoles` 属性中注册新引擎支持的角色（`.dictation` 或 `.polishing`）。
- **Onboarding 过滤**：
    *   [**OnboardingView.swift**](file:///Users/pengyue/project/yaktype-workspace/yaktype/Sources/macOS/UI/OnboardingView.swift) 的 “New Instance” 菜单已配置为仅显示 `supportedRoles` 包含 `.dictation` 的引擎类型。
- **图标配对**：
    *   在 `OnboardingView` 的 `iconName(for:)` 中为新引擎配对 SF Symbol 系统图标（必须包含以防编译失败）。
- **工厂与 UI 注册**：
    1.  **工厂注册 (`Sources/Shared/Engines/SpeechEngineFactory.swift`)**：在 `create(for:)` 方法中增加实例化逻辑。
    2.  **类型定义 (`Sources/Shared/Models/EngineType.swift`)**：增加新 Case 及 `rawValue`。
    3.  **重要：** 必须更新以下文件的 **Exhaustive Switch**：
        *   [**EngineCard.swift**](file:///Users/pengyue/project/yaktype-workspace/yaktype/Sources/macOS/UI/Components/EngineCard.swift)：`description` 计算属性。
        *   [**TranscriptionService.swift**](file:///Users/pengyue/project/yaktype-workspace/yaktype/Sources/Shared/Services/TranscriptionService.swift)：`apply(profile:...)` 中的配置应用逻辑。

## 注意事项

- **线程安全**：由于音频回调可能在非主线程，引擎内部的 UI 状态更新（如 `transcript`, `status`）必须通过 `@MainActor` 或 `DispatchQueue.main` 确保线程安全。
- **内存管理**：对于流式引擎，务必在 `reset()` 或 `cancel()` 时清空音频缓冲区。
- **错误抛出**：API 认证失败或网络断开应立即切换至 `.error(String)` 状态，以便 UI 能够及时提示。

## 参考实现
- [**GeminiSpeechEngine.swift**](file:///Users/pengyue/project/yaktype-workspace/yaktype/Sources/Shared/Engines/Gemini/GeminiSpeechEngine.swift) - 包含复杂的流式切分与队列管理逻辑。
- [**AliyunSpeechEngine.swift**](file:///Users/pengyue/project/yaktype-workspace/yaktype/Sources/Shared/Engines/Aliyun/AliyunSpeechEngine.swift) - 典型的离线文件转录实现。
