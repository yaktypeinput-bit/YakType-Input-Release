# Xiaomi MiMo ASR 集成指南 (Shared Core)

## 概要说明

本文档说明 YakType 当前对 Xiaomi MiMo ASR 的集成方式。MiMo 在工程中被实现为一个仅承担听写角色的云端引擎，接口风格与 OpenAI 兼容后端相近，但配置、默认模型和错误语义独立维护。

## 1. 代码位置

- 引擎实现：`yaktype/Sources/Shared/Engines/Mimo/MimoSpeechEngine.swift`
- 配置模型：`yaktype/Sources/Shared/Models/EngineConfigs/MimoEngineConfig.swift`
- 引擎类型：`yaktype/Sources/Shared/Models/EngineType.swift`

## 2. 能力边界

当前 MiMo 仅支持：

- `dictation`

不支持：

- `polishing`

因此：

- `EngineType.mimo.supportedRoles == [.dictation]`
- 不应把 MiMo 绑定为后处理 profile

## 3. 默认配置

当前默认值：

| 字段 | 默认值 |
| :--- | :--- |
| `modelName` | `mimo-v2.5-asr` |
| `endpoint` | `https://api.xiaomimimo.com/v1` |
| `apiKey` | 空 |
| `managedKeyID` | 空 |

## 4. 配置字段

MiMo 当前暴露的可编辑字段：

- `apiKey`
- `modelName`
- `endpoint`

与其他云端引擎一致，也支持通过 `managedKeyID` 间接引用统一密钥池。

## 5. 处理链路

MiMo 当前走的是“文件/分段上传 -> 云端识别 -> 文本拼接”模式，整体语义与 Aliyun 近似：

- 长音频可切分成多个 segment
- segment 通过内部队列串行处理
- 每段结果回流后累加到最终文本

这意味着：

- 它适合当前 YakType 的分段听写管线
- 但不应被文档误写成“本地离线引擎”或“后处理模型”

## 6. 接入注意事项

1. 若扩展 MiMo 的模型目录，需要同步更新 `MimoEngineConfig.default.modelName` 及相关连接性检查逻辑。
2. 若调整 endpoint 规范，应同时检查 `UnifiedEngineModelCatalogService` 和 iOS 端连接性探测逻辑。
3. 在 UI 中，MiMo 目前展示名为 `Xiaomi MiMo ASR`。

