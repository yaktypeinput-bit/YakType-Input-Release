# YakType 文档库

YakType 是一款面向速度与隐私的多平台语音输入与文本润色产品，当前覆盖 `macOS` 桌面主应用，以及 `iOS` 宿主 App + Keyboard Extension。

本目录用于存放与当前工程代码对齐的长期技术文档、平台实现说明、用户手册与提示词资料。代码事实以 `yaktype/` 为准，本文档库负责解释实现语义、设计边界与维护约定。

用户关注的提示词文档入口见 [prompt-hub/README.md](prompt-hub/README.md)。  
发布说明见 [RELEASE.md](RELEASE.md)。

## 文档地图

### 跨平台核心

- [架构概览](core/Architecture-Overview.md)：Shared Core、平台分层、运行时主链路与默认种子数据。
- [数据模型](core/Data-Models.md)：SwiftData 实体、关系、字段语义与当前 schema 事实。
- [核心状态机](core/State-Machines.md)：任务状态、桥接状态与 UI 阶段映射。
- [引擎协议接口](core/Engine-Protocol.md)：`SpeechRecognitionEngine` 协议、能力边界与接入要求。
- [持久化架构与同步方案](core/Persistence-Schema.md)：SwiftData、UserDefaults、App Group、iCloud 同步范围。
- [听写音频格式架构](core/Dictation-Audio-Format-Architecture.md)：音频格式、转码职责与引擎上传偏好。
- [平台分层审计报告](core/Platform-Architecture-Audit-2026-05.md)：Shared Core 下沉与双端差异梳理。

### 引擎集成

- [新增听写引擎接入指南](core/Adding-Dictation-Engine.md)
- [新增后处理引擎接入指南](core/Adding-Polishing-Engine.md)
- [Gemini 集成指南](core/Gemini-Integration.md)
- [OpenAI / 自定义 API 集成指南](core/OpenAI-Integration.md)
- [阿里云 ASR 集成指南](core/Aliyun-Integration.md)
- [Xiaomi MiMo ASR 集成指南](core/Mimo-Integration.md)

### macOS

- [环境搭建](macos/development/Setup.md)
- [全局快捷键架构](macos/development/ShortcutArchitecture.md)
- [设计 Tokens](macos/ui-ux/Design-Tokens.md)
- [HUD 交互](macos/ui-ux/HUD-Interactions.md)
- [布局架构](macos/ui-ux/Layout-Architecture.md)
- [页面蓝图](macos/ui-ux/Page-Blueprints.md)
- [UI 设计指南](macos/ui-ux/UI-Design-Guidelines.md)
- [初始化与引导流程](macos/user-guide/Onboarding.md)
- [引擎架构与执行流水线](macos/user-guide/Engines-and-Pipelines.md)
- [进阶功能与系统维护](macos/user-guide/Advanced-Usage.md)
- [快捷键用户指南](macos/user-guide/Shortcuts.md)

### iOS

- [iOS 规约：听写即输入法](ios/Spec.md)
- [iOS UI 实施规约（SwiftUI Native / Liquid Glass）](ios/UI-SwiftUI-Native-LiquidGlass-Spec.md)
- [iOS Toolbar 规范](ios/Toolbar-Spec.md)
- [主 App 与键盘扩展通信机制与状态机](ios/Host-Keyboard-Communication-StateMachine.md)
- [键盘/宿主会话策略](ios/iOS-Keyboard-Host-Session-Policy.md)
- [Typography Spec](ios/TypographySpec.md)
