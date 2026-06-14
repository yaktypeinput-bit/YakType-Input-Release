# 持久化架构与同步方案 (Persistence & Sync Schema)

## 概要说明

本文档说明 YakType 当前在代码中的持久化分层，包括 SwiftData、进程内 `UserDefaults`、iOS App Group 共享存储以及 iCloud JSON 同步。重点是“哪些数据存在哪里、为什么在那里、是否跨进程或跨设备同步”。

## 1. 持久化分层

| 存储层 | 访问范围 | 当前用途 |
| :--- | :--- | :--- |
| SwiftData | App 主进程 | 历史记录、引擎配置、流水线、提示词、密钥池 |
| `UserDefaults.standard` | 单进程本地 | 本地 UI 偏好、引导进度、时长选择等 |
| App Group `UserDefaults` | iOS 宿主 + 键盘扩展 | 键盘桥接快照、命令队列、心跳、共享状态 |
| iCloud JSON (`AppSyncProfile`) | 跨设备 | 配置与资料同步，不含任务历史音频 |

## 2. SwiftData 实体范围

当前会持久化到 SwiftData 的实体：

- `TranscriptionTask`
- `EngineProfile`
- `ProcessingPipeline`
- `PromptTemplate`
- `ManagedKey`

同步层面对这些实体的处理并不完全一致：

- `TranscriptionTask`：本地历史，不参与云同步
- 其他 4 类配置实体：可进入同步资料

## 3. 文件路径与容器

### 3.1 数据库文件

数据库路径由 `AppPaths.databaseURL` 统一计算：

- `macOS`：`Application Support/<bundle-like-folder>/default.sqlite`
- `iOS`：优先放入 App Group 容器内的 `default.sqlite`

### 3.2 录音与 segment

- `recordingsDirectory`：最终录音文件
- `segmentsDirectory`：处理中间 segment

当前实现中：

- `iOS` 使用 App Group 容器下的 `Recordings` / `Segments`
- `macOS` Release 使用 `Application Support` 和 `Caches`
- `macOS` Debug 使用更便于开发排查的本地目录

## 4. `UserDefaults` 分层语义

### 4.1 本地进程设置

由 `LocalAppSettings.defaults` 承载，典型字段包括：

- `onboardingCompleted`
- `selectedSessionDuration`
- `selectedAppLanguage`
- `autoDeletePolicy`
- `showDockIcon`

这些值默认不要求键盘扩展可见，因此不强制进入 App Group。

### 4.2 App Group 共享状态

当前 App Group 标识符：

- `group.com.yaktype.shared`

桥接层通过 `KeyboardSharedBridge.sharedDefaults` 访问，关键 key 包括：

- `keyboard.syncSnapshot`
- `keyboard.pendingRequest`
- `keyboard.pendingRequestQueue`
- `keyboard.debugLog`
- `keyboard.lastSeenTimestamp`
- `keyboard.reportedFullAccess`

注意：

- 这部分主要服务于 iOS 键盘桥接，不是通用配置仓库。
- 当容器不可用时，`SharedAppGroup.defaultsIfAvailable` 会返回 `nil`，以避免启动阻塞。

## 5. iCloud 同步资料：`AppSyncProfile`

当前同步载荷是一个版本化 JSON 容器，不是直接同步 SQLite。

### 5.1 当前版本

`AppSyncProfile.version` 当前默认为 `2`。

### 5.2 关键字段

- `sharedSettings`
- `iosSettings`
- `macSettings`
- `iosPipelines`
- `macPipelines`
- `managedKeys`
- `engineProfiles`
- `promptTemplates`
- `tombstones`

这意味着当前同步已经从早期“单一扁平 settings/pipelines”演进到带平台作用域的版本 2 结构。

### 5.3 Tombstone 机制

删除同步配置时，会通过 `SyncTombstoneDTO` 记录：

- `id`
- `entityType`
- `scope`
- `deletedAt`

其作用是避免“本地删掉、远端又被旧数据恢复”的回流问题。

## 6. 实体与同步策略

| 实体 / 数据 | 本地持久化 | 跨进程 | 跨设备同步 |
| :--- | :--- | :--- | :--- |
| `TranscriptionTask` | 是 | 否 | 否 |
| `EngineProfile` | 是 | 否 | 是 |
| `ProcessingPipeline` | 是 | 否 | 是 |
| `PromptTemplate` | 是 | 否 | 是 |
| `ManagedKey` | 是 | 否 | 是 |
| 键盘命令/快照 | 否（短期共享） | 是 | 否 |
| 引导状态 | 是 | 否 | 否 |

## 7. 当前重要语义

### 7.1 统一密钥池已进入 SwiftData

`ManagedKey` 不再是仅存于 `UserDefaults` 的临时数据。引擎配置通过 `managedKeyID` 引用它，运行时再解析出真实密钥。

### 7.2 内置提示词与订阅提示词是不同来源

`PromptTemplate.source` 当前至少有三类：

- `builtin`
- `subscription`
- `user`

同步与 UI 操作时要考虑只读约束，而不是把所有模板视作同一类型。

