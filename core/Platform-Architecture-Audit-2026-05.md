# YakType 项目分层梳理（2026-05）

## 目标

本次梳理聚焦两个问题：

1. 哪些能力已经是跨平台共性，适合继续下沉到 `Sources/Shared`。
2. 哪些能力虽然业务目标一致，但因为 macOS 与 iOS Keyboard 的“回填”机制不同，必须保留平台实现。

结论先行：

- `Shared` 当前已经承载了核心转写链路、引擎配置模型、Pipeline 解析、模型目录网络请求等真正的共性。
- “回填”不应该强行做成一套平台无差别实现，但“何时触发回填、如何保证幂等、如何表示完成态”可以进一步抽成共享域逻辑。
- 当前最值得优先抽离的是“引擎配置编辑规则”和“提示词/密钥管理规则”；最不该强行合并的是“macOS 注入实现”和 “iOS Keyboard 注入实现”。

## 当前结构概览

### 已经分层合理的部分

- 共享核心：
  - `Sources/Shared/Services/Transcription/*`
  - `Sources/Shared/Models/*`
  - `Sources/Shared/Engines/*`
- 平台实现：
  - macOS：`Sources/macOS/*`
  - iOS App + Keyboard：`Sources/iOS/*`

这说明项目在目录层面已经按“共享核心 + 平台外壳”设计过，主问题不在顶层目录，而在部分业务规则仍散落在平台 UI/ViewModel 里。

## 回填链路现状

### iOS Keyboard

当前 iOS 回填路径比较集中：

- 状态同步与完成态判定：`Sources/iOS/Keyboard/KeyboardDashboardModel+StatusSync.swift`
- 宿主状态发布：`Sources/iOS/AppShell/Bridge/TranscriptionBridge_iOS+SessionState.swift`
- 共享会话协议：`Sources/Shared/Services/KeyboardSharedBridge.swift`

特点：

- 宿主 App 发布 `KeyboardSyncSnapshot`
- Keyboard 侧根据 `completedSessionID`、`finalTranscriptID`、`localInstanceID` 做归属和幂等校验
- 真正注入文本时使用 `UITextDocumentProxy.insertText`

这套实现已经体现出“共享状态协议 + 平台注入执行”的正确方向。

### macOS

当前 macOS 回填路径是分散的：

- 完成事件来源：`Sources/Shared/Services/Transcription/TranscriptionTaskLifecycleCoordinator.swift`
- 接收完成通知并排队注入：`Sources/macOS/ViewModels/SpeechViewModel.swift`
- 真正执行注入：`Sources/macOS/Managers/AccessibilityManager.swift`

特点：

- `TranscriptionTaskLifecycleCoordinator` 通过 `NotificationCenter` 发出完成事件
- `SpeechViewModel` 监听 `.transcriptionCompleted`，维护 `pendingAutoInsertText`
- `AccessibilityManager` 通过“备份剪贴板 -> 写入文本 -> Cmd+V -> 恢复剪贴板”的方式注入

问题不在实现方式，而在职责分布：

- 回填触发逻辑在 `SpeechViewModel`
- 注入目标捕获也在 `SpeechViewModel`
- 注入执行在 `AccessibilityManager`
- 完成事件载荷使用字符串字典，而不是强类型共享结构

## 建议保留平台分离的部分

以下内容不建议强行合并：

### 1. 文本注入实现

- macOS：依赖辅助功能、前台 App 激活、剪贴板保护、模拟 `Cmd+V`
- iOS Keyboard：依赖 `UITextDocumentProxy.insertText`

两端注入手段完全不同，抽成一套统一实现没有收益，只会引入条件编译和弱抽象。

建议：

- 保留 `AccessibilityManager.injectText(_:)`
- 保留 Keyboard 侧 `proxyProvider()?.insertText(...)`
- 只抽“注入接口”或“回填命令”，不要抽“注入细节”

### 2. iOS Keyboard 会话协议

以下逻辑具有明显平台专属性，应继续保留在 iOS 侧：

- `KeyboardSyncSnapshot`
- `KeyboardSessionPolicy`
- `TranscriptionBridge_iOS`
- Keyboard owner / heartbeat / zombie session / command ack

这是 iOS App 与 Keyboard Extension 的跨进程问题，macOS 没有对应物。

### 3. 平台 UI 组合方式

- iOS 已经按 feature 拆分：`Features/Home`, `Features/History`, `Features/Prompts`, `Features/Engines`
- macOS 仍偏页面式组织：`HomeDashboardView`, `TasksListView`, `PromptsView`, `EngineManagementView`

即使未来统一命名，也不建议追求 UI 文件结构镜像。两端交互密度和组件形态不同，保持各自演化更合理。

## 建议优先抽到 Shared 的部分

### 1. 回填完成态与注入调度

当前 iOS 有比较完整的“完成态判断 + 幂等校验”，macOS 只有“收到完成通知后延迟注入”。

建议新增一个共享层概念，例如：

- `TranscriptionInsertionPayload`
- `TranscriptionInsertionDecision`
- `TranscriptionInsertionCoordinator`

共享层负责：

- 何时允许回填
- 如何表示完成文本
- 是否需要幂等 ID
- 是否应延迟执行

平台层负责：

- macOS：捕获目标、激活 App、粘贴、恢复剪贴板
- iOS：向 `UITextDocumentProxy` 插入文本

这样可以把“业务规则一致性”收口，同时保留平台执行差异。

### 2. 引擎配置编辑状态

当前两端存在明显重复：

- macOS：`Sources/macOS/UI/Components/EngineConfigDraftState.swift`
- iOS：`Sources/iOS/Features/Engines/EngineProfileEditorDraftState.swift`

重复点包括：

- 字段分组
- `managedKeyID` 解析
- API Key / Base URL / Model Name 的显示条件
- 模型建议过滤规则

差异主要只有：

- iOS 允许 legacy `apiKey` fallback
- macOS 当前完全走 `ManagedKey`

建议：

- 抽出共享 `EngineProfileDraftState`
- 平台层只传入策略参数，例如 `allowsLegacyInlineAPIKey`

这部分抽离收益高，风险低。

### 3. 引擎模型建议协调器

当前也有重复：

- macOS：`Sources/macOS/UI/Components/EngineConfigSuggestionCoordinator.swift`
- iOS：`Sources/iOS/Features/Engines/EngineProfileEditorSuggestionCoordinator.swift`

两者都只是对共享网络服务的薄封装，而共享服务已经存在：

- `Sources/Shared/Services/UnifiedEngineModelCatalogService.swift`

其中 iOS 还保留了额外 shim：

- `Sources/iOS/Features/Engines/EngineModelCatalogService.swift`

建议：

- 删除 iOS `EngineModelCatalogService` 这层 shim
- 统一用 `UnifiedEngineModelCatalogRequest`
- 合并两端 suggestion coordinator

这是当前最容易直接落地的合并点。

### 4. 提示词管理规则

当前“提示词引用校验 / 删除保护 / clone / 订阅导入”有重复实现：

- iOS：`Sources/iOS/Features/Prompts/PromptsFeatureStore.swift`
- macOS：`Sources/macOS/UI/PromptsView.swift`

其中重复业务包括：

- 删除前检查 `EngineProfile.referencedPromptTemplateIDs`
- clone 命名规则
- 订阅导入映射逻辑

建议抽成共享 domain service，例如：

- `PromptTemplateDomainService`
- `PromptTemplateDeletionPolicy`
- `PromptSubscriptionImportService`

UI 只消费结果 and 错误文案。

### 5. 密钥管理规则

当前“密钥引用检查 / 删除保护”也重复：

- iOS：`Sources/iOS/UI/App/APIKeyManagerView.swift`
- macOS：`Sources/macOS/UI/EngineManagementView.swift`

而 `EngineProfile` 已经提供共享访问点：

- `EngineProfile.managedKeyID`

这说明引用判断其实已经有共享抽象基础，不需要各端继续自己遍历不同 config case。

建议抽成共享规则：

- `ManagedKeyDomainService.referencingProfiles(...)`
- `ManagedKeyDeletionPolicy`

这样两端都不再直接写删除保护逻辑。

## 建议继续拆小的 macOS 模块

### `SpeechViewModel` 过重

`Sources/macOS/ViewModels/SpeechViewModel.swift` 当前同时承担：

- 权限检查
- HUD 状态
- 快捷键刷新
- Pipeline 同步
- 回填调度
- 录音入口
- 历史操作

建议至少拆成以下协作者：

- `MacOSAutoInsertCoordinator`
- `MacOSHUDCoordinator`
- `MacOSShortcutCoordinator`
- `MacOSPipelineSelectionCoordinator`

这里不是“跨平台抽 shared”，而是先把 macOS 自己的聚合类拆散，否则后续公共能力下沉会持续受阻。

## 建议保留但需要明确边界的历史遗留

### `EngineProfile` 里的 legacy prompt slot 字段

`EngineProfile` 仍保留：

- `promptTemplateIDString1`
- `promptTemplateIDString2`
- `polishingShortcuts`

这些字段当前主要服务迁移兼容，不适合继续扩散到新代码。

建议：

- Shared 层保留迁移兼容
- 平台 UI 不再新增任何对 legacy slot 的直接读写
- 后续在迁移窗口结束后集中移除

## 推荐重构顺序

建议按风险从低到高推进：

1. 合并引擎模型建议相关薄层
   - `EngineModelCatalogService`
   - `EngineConfigSuggestionCoordinator`
   - `EngineProfileEditorSuggestionCoordinator`

2. 合并引擎配置 DraftState
   - 抽共享 `EngineProfileDraftState`

3. 抽提示词/密钥 domain service
   - 删除保护
   - 引用查询
   - clone 规则

4. 拆 macOS `SpeechViewModel`
   - 先把回填调度拆出去

5. 最后再抽共享“回填决策层”
   - 不碰平台注入实现
   - 只统一完成事件和幂等策略

## 最终判断

### 应该拆出来的

- 引擎配置 DraftState
- 模型建议协调器
- Prompt 管理 domain 规则
- ManagedKey 管理 domain 规则
- macOS `SpeechViewModel` 的 auto-insert / HUD / shortcut 协调职责

### 应该合并的

- iOS `EngineModelCatalogService` 与 Shared `UnifiedEngineModelCatalogService` 的重复薄层
- 两端引擎编辑器上层的 suggestion state / draft state

### 不该合并的

- macOS 文本注入实现
- iOS Keyboard 文本注入实现
- iOS Keyboard 宿主同步协议
- 平台 UI 结构

## 一句话边界

建议采用这个边界继续整理：

- `Shared` 负责“转写、完成、选择、校验、引用关系、删除策略、建议拉取、回填决策”
- `macOS/iOS` 只负责“平台输入注入、平台会话壳、平台 UI 组织”
