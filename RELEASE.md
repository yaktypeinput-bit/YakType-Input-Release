# YakType (macOS) v1.0 Release Notes

## 概要说明

YakType 1.0 是专为 macOS 14+ 设计的高性能语音转录与 AI 文本后处理工具。它通过“Liquid Glass”设计语言与强大的 AI 引擎集成，将语音录入、实时转录与即时文字润色整合为一套极简的生产力工作流。

## 核心特性 (Key Features)

### 💎 Liquid Glass 视觉系统
- **原生体验**：基于 macOS 14+ 视觉规范，采用全 SwiftView 原生开发。
- **层叠卡片布局**：多层级阴影与毛玻璃背景，确保在高对比度与深色模式下均有极佳表现。
- **Cosmic Pulse 配色**：以活力紫为核心的色谱系统，增强界面交互反馈的呼吸感。

### ⚡️ 全球首创：即时文本润色 (Polishing Shortcuts)
- **全局快捷键**：无论你在哪个 App 中，只需选中文字并按下预设快捷键，YakType 即可调用 AI 引擎进行润色。
- **自定义指令**：支持从 [Prompt Hub](prompt-hub/README.md) 动态加载提示词，实现一键翻译、修复口水词或改变语气。

### 🤖 多引擎协作流水线 (Multi-Engine Pipelines)
- **ASR 引擎支持**：集成 Apple 原生语音识别与阿里云实时语音处理，提供极速响应与极高准确率。
- **LLM 集成**：原生支持 Google Gemini (支持 20MB+ 长音频)、OpenAI (及 DeepSeek 等兼容 API) 协议，满足不同场景下的智能处理需求。

### 📁 Prompt Hub 提示词仓库
- **开源指令集**：内置 `dictation` 与 `translation` 优化提示词，专为语音转文字场景调优。
- **零配置启动**：支持 Markdown 格式的提示词管理，用户可随心所欲扩展自己的处理逻辑。

## 系统要求 (System Requirements)

- **操作系统**：macOS 14.0 (Sonoma) 或更高版本。
- **硬件**：支持 Apple Silicon 与 Intel 架构机型。
- **网络**：建议连接互联网以获得最佳的云端 ASR 与 LLM 处理速度。

## 隐私与安全 (Privacy & Security)

- **本地优先**：YakType 优先通过本地存储和配置管理，所有 API Key 均安全地存储在本地钥匙串/配置文件中。
- **无追踪**：应用不包含任何第三方追踪插件，用户的语音数据仅传输至用户自行配置的官方 API。

---
*YakType - Private, Secure, and Blazing Fast.*
