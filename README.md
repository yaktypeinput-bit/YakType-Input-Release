# 欢迎来到 YakType Wiki

YakType 是一款专为速度和隐私设计的 **多平台 (macOS/iOS)** 高级转录与 AI 润色工具。本文档库已被划分为 **跨平台核心 (Shared Core)** 与 **各平台具体实现**。

用户关注的 prompt 文档在这里：[Prompts](prompt-hub/README.md)
最新发布说明：[v1.0 Release Notes](RELEASE.md)

# 再往下的都是废话，不用看

## 文档地图 (Document Map)

### 📂 [跨平台核心 (Shared Core)](core/Architecture-Overview.md)

- **[架构概览 (Shared Core)](core/Architecture-Overview.md)** — 系统设计原则、多平台数据流与模块职责。
- **[数据模型 (Shared Core)](core/Data-Models.md)** — 跨平台共享的 SwiftData 实体定义规格说明书。
- **[核心状态机 (Shared Core)](core/State-Machines.md)** — 全生命周期 (Recording, Transcribing, Polishing) 的流程控制逻辑。
- **[引擎协议接口 (Shared Core)](core/Engine-Protocol.md)** — `SpeechEngine` 跨平台抽象协议设计。
- **[集成听写引擎 (Shared Core)](core/Adding-Dictation-Engine.md)** — 如何实现一个新的音频转录引擎规范。
- **[集成后处理引擎 (Shared Core)](core/Adding-Polishing-Engine.md)** — 如何实现一个新的文本润色/大模型引擎规范。
- **[Gemini 集成 (Shared Core)](core/Gemini-Integration.md)** — Gemini API 接入、OGG/AAC 编解码与长语音切分策略。
- **[OpenAI / 兼容集成 (Shared Core)](core/OpenAI-Integration.md)** — 接入 OpenAI、DeepSeek 等兼容 Chat API 的通用后处理方案。
- **[阿里云 ASR 集成 (Shared Core)](core/Aliyun-Integration.md)** — 阿里云 ASR 引擎在核心层的集成模型。
- **[听写音频格式架构 (Shared Core)](core/Dictation-Audio-Format-Architecture.md)** — 听写管道音频格式约定、引擎上传格式偏好与转码分工。
- **[平台分层审计报告 (Shared Core)](core/Platform-Architecture-Audit-2026-05.md)** — macOS 与 iOS Keyboard 共享核心下沉方案、回填机制与重构推荐顺序。

---

### 📂 [macOS 平台实现 (macOS Implementation)](macos/ui-ux/Layout-Architecture.md)

#### 开发与部署

- **[macOS 环境搭建](macos/development/Setup.md)** — XcodeGen 动态生成项目及 macOS 本地编译指南。

#### UI / UX 设计

- **[macOS 设计规范](macos/ui-ux/Design-Tokens.md)** — 液态玻璃 (Liquid Glass) 风格、Cosmic Pulse 配色系统。
- **[macOS UI 设计指南（当前基线）](macos/ui-ux/UI-Design-Guidelines.md)** — 首页、引擎编排与管理页布局设计目标、视觉与交互规范基线。
- **[macOS 局部布局架构](macos/ui-ux/Layout-Architecture.md)** — 窗口 Z-Index 堆叠、侧边栏及主内容区布局。
- **[macOS 页面蓝图](macos/ui-ux/Page-Blueprints.md)** — 核心视图的交互原型 (ASCII) 与界面分布详述。
- **[macOS 悬浮窗详情](macos/ui-ux/HUD-Interactions.md)** — HUD 生命周期管理与键盘交互细节规格。

#### 用户手册

- **[macOS 初始化与引导流程](macos/user-guide/Onboarding.md)** — 新手 4 步 Wizard 引导、权限申请与“净地”初始化逻辑。
- **[macOS 全局快捷键指南](macos/user-guide/Shortcuts.md)** — macOS 任务触发路径、PTT 交互模式与 HUD 原子化中断。
- **[macOS 引擎架构与执行流水线](macos/user-guide/Engines-and-Pipelines.md)** — ASR 与 LLM 双引擎协作逻辑、原子化 Pipeline 序列说明。
- **[macOS 进阶功能与系统维护](macos/user-guide/Advanced-Usage.md)** — 提示词工程、非实时音频导入机制及存储持久化策略。

---

### 📂 iOS 平台实现 (iOS Implementation)

- **[iOS 规约：听写即输入法](ios/Spec.md)** — iOS 平台的系统架构、UI 交互（键盘扩展）及技术规约详情。
- **[iOS UI 实施规约（SwiftUI Native / Liquid Glass）](ios/UI-SwiftUI-Native-LiquidGlass-Spec.md)** — 基于当前代码的 UI 统一规范，重点覆盖原生组件优先、液态玻璃风格和视觉一致性。
- **[iOS 主 App 与键盘扩展通信与状态机](ios/Host-Keyboard-Communication-StateMachine.md)** — 说明跨进程通信协议、状态同步与容错机制（心跳、看门狗、幂等注入）。
- **[iOS 键盘/宿主会话策略](ios/iOS-Keyboard-Host-Session-Policy.md)** — 跨进程 App Group 共享的会话阶段语义、所有权规则与看门狗判定。
- _iOS 开发指南与 UI 规范详述稍后补充。_
