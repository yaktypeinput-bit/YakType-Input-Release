# 引擎协议接口 (Shared Core)

## 概要说明

本文档说明 YakType 当前用于统一听写与后处理引擎的协议层：`SpeechRecognitionEngine`。它描述的是当前代码中的真实协议，而不是抽象化的旧版本说明。

## 1. 协议定位

`SpeechRecognitionEngine` 是所有引擎实现的统一入口，负责：

- 接收音频 segment 或整段文件进行听写
- 对文本执行可选的后处理
- 对外暴露状态、转写结果、提示语与配置能力

该协议位于：

- `yaktype/Sources/Shared/Engines/SpeechRecognitionEngine.swift`

## 2. 当前协议定义

### 2.1 必备属性

| 属性 | 类型 | 说明 |
| :--- | :--- | :--- |
| `configuration` | `EngineConfiguration` | 引擎的分段与重试参数 |
| `status` | `SpeechEngineStatus` | 当前运行状态 |
| `transcript` | `String` | 当前引擎输出文本 |
| `statusMessage` | `String` | 面向 UI 的提示信息 |
| `selectedLanguage` | `String` | 当前识别语言 |
| `currentPrompt` | `String` | 当前绑定的提示词 |
| `hasPendingRealtimeRequest` | `Bool` | 是否仍有实时请求在途 |
| `preferredDictationAudioFormat` | `DictationAudioFormat` | 听写上传偏好的音频格式 |

### 2.2 必备方法

```swift
func process(audioChunk: [Float])
func process(fileURL: URL)
func cancel()
func reset()
func requestAuthorization()
func polish(text: String, prompt: String) async throws -> String
func apply(config: EngineProfileConfig, resolvedAPIKey: String)
```

与旧文档相比，当前协议有两个必须注意的差异：

1. `apply` 现在接收的是“已解析后的最终 API Key”，而不是要求引擎自行查找密钥池。
2. 协议显式声明了 `preferredDictationAudioFormat` 和 `hasPendingRealtimeRequest`，供音频上传与桥接层判断。

## 3. 相关支持类型

### 3.1 `SpeechEngineStatus`

当前状态枚举：

- `idle`
- `processing`
- `ready`
- `error(String)`

### 3.2 `EngineConfiguration`

当前字段：

- `maxSegmentDuration`
- `delayBetweenSegments`
- `minRealtimeSegmentDuration`
- `realtimeSegmentRetryLimit`

说明：

- 这组参数直接影响 `RealtimeTranscriptionCoordinator` 的切段与节流行为。
- 引擎实现不能只关心 `maxSegmentDuration`，还应考虑实时 segment 的最小时长和重试上限。

### 3.3 `DictationAudioFormat`

当前支持：

- `.oggOpus`
- `.wav16kMonoPcm16`

通过 `mimeType` 提供上传时的 MIME 映射。

## 4. 当前引擎能力边界

| 引擎 | 角色 | 说明 |
| :--- | :--- | :--- |
| `Apple` | `dictation` | 原生听写 |
| `Gemini` | `dictation` + `polishing` | 双能力引擎 |
| `AliCloud QwenASR` | `dictation` | 云端听写 |
| `Xiaomi MiMo ASR` | `dictation` | 云端听写 |
| `OpenAI (Compatible)` | `polishing` | 仅文本后处理 |

## 5. 引擎实现要求

### 5.1 听写类引擎

必须正确处理：

- `process(audioChunk:)`
- `process(fileURL:)`
- 分段状态回写
- 取消与 reset 清理

如果引擎存在实时请求队列，应准确返回 `hasPendingRealtimeRequest = true`，避免桥接层误判任务已结束。

### 5.2 后处理类引擎

至少要可靠实现：

- `polish(text:prompt:)`
- `apply(config:resolvedAPIKey:)`

对不支持音频处理的引擎，可以让 `process(audioChunk:)` / `process(fileURL:)` 保持空实现或直接失败，但不能破坏协议一致性。

## 6. 配置应用规范

### 6.1 统一密钥解析

密钥解析责任在 `EngineProfile.resolveAPIKey(in:)` 与 service 层，而不是散落在各引擎内部。

因此：

- 引擎实现不要依赖自己再去查 `ManagedKey`
- `apply(config:resolvedAPIKey:)` 应把 `resolvedAPIKey` 视为最终可用值

### 6.2 提示词绑定

引擎收到的 prompt 可能来自：

- `EngineProfile.promptTemplateID`
- 内置模板本地化正文
- 运行时 `repolish` 传入的显式 prompt

引擎不需要关心 prompt 的来源，只需按最终字符串执行。

## 7. 接入新引擎的最小步骤

1. 在 `EngineType` 中新增 case，并声明 `supportedRoles`
2. 在 `EngineProfileConfig` 中新增配置 case
3. 增加对应 `*EngineConfig` 与 `fields`
4. 在 `EngineProfile.defaultConfig(for:)` 与 `fromDictionary` 中注册
5. 在 `SpeechEngineFactory` 中接入实例化逻辑
6. 校正平台 UI 中的穷举分支和展示文案

