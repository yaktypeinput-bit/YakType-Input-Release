# YakType 文档库

YakType 是一款面向速度与隐私的多平台语音输入与文本润色产品，当前覆盖 `macOS` 桌面主应用，以及 `iOS` 宿主 App + Keyboard Extension。

本目录现承载发布资料与提示词资料。代码与行为的**事实来源不在本目录**：

- 客户端行为、架构、API 契约与 UI 约定：[`yaktype/spec/`](../yaktype/spec/README.md)（iOS UI 见 [`spec/ios/ui/`](../yaktype/spec/ios/ui/README.md)，macOS UI 见 [`spec/macos/ui/`](../yaktype/spec/macos/ui/README.md)）
- 服务端行为与 HTTP 合约：[`asr-server/spec/`](../asr-server/spec/README.md)

2026-09 文档迁移说明：原 `core/` 技术文档、iOS 行为类文档与 `macos/` 目录已迁出或删除——iOS/macOS UI 规约分别迁入 `yaktype/spec/ios/ui/` 与 `yaktype/spec/macos/ui/`；macOS 环境搭建与使用说明迁入 `yaktype/docs/dev/` 与 `yaktype/docs/guides/macos/`；简约引擎模式设计稿归档至 `yaktype/docs/archive/`；其余过时文档以 Git 历史留存。

用户关注的提示词文档入口见 [prompt-hub/README.md](prompt-hub/README.md)。  
发布说明见 [RELEASE.md](RELEASE.md)（v1.0 存档）。

## 文档地图

### Prompt 资料与发布

- [prompt-hub/](prompt-hub/README.md)：提示词资料入口；`prompt-package.json` 与 `.github/workflows/release-prompts.yml` 是发布管线的产物与配置
- [App 图标素材](images/)

## 服务端工作区

服务端代码与规范位于工作区根目录：

- `asr-server/`：托管听写服务端代码与权威 `spec/`
- `asr-server-doc/`：已退役的早期设计仓库，仅保留迁移说明与 Git 历史
