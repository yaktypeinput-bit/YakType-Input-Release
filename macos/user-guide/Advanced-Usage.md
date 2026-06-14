# 进阶功能与系统维护 (Advanced Usage)

## 概要说明

本文档说明当前工程代码已经具备的进阶能力，包括提示词模板体系、统一密钥池、音频/任务持久化路径以及若干维护语义。内容以现有实现为准，不延伸未落地功能。

## 1. 提示词模板体系

### 1.1 模板来源

当前 `PromptTemplate.source` 至少有三类：

- `builtin`
- `subscription`
- `user`

这三类在当前代码里不是同一语义：

- `builtin`：系统内置，只读，可按语言本地化
- `subscription`：远端订阅导入，只读
- `user`：用户可编辑模板

### 1.2 当前内置模板

当前代码内置两个系统模板：

1. `Dictation Polishing`
2. `Chinese-to-English Translation`

它们通过稳定的 `externalUUID` 和 `systemPresetKey` 管理，而不是只靠名字匹配。

### 1.3 模板与引擎的关系

Prompt 当前绑定在 `EngineProfile.promptTemplateID` 上，而不是绑定在任务记录上。

这意味着：

- 一个后处理引擎实例可以代表一种固定的 prompt 语义
- 历史任务不再以 prompt 名称作为主要上下文主键

## 2. 统一密钥池

### 2.1 当前模型

云端引擎配置支持两种密钥方式：

- `apiKey`
- `managedKeyID`

`managedKeyID` 指向 `ManagedKey` 实体，后者保存：

- `name`
- `secret`
- `createdAt`
- `updatedAt`

### 2.2 删除约束

若某个 `ManagedKey` 正被引擎实例引用，当前 UI 会阻止删除，并给出引用说明。这不是前端层面的静态校验，而是基于 `ManagedKeyDomainService.referencingProfiles` 的运行时判断。

## 3. 任务与文件持久化

### 3.1 历史记录

任务历史由 `TranscriptionTask` 保存，包含：

- 音频路径
- 原始文本
- 后处理文本
- 引擎 profile 引用
- 时长/错误等元数据

### 3.2 存储路径

由 `AppPaths` 统一计算：

- 录音文件：`recordingsDirectory`
- 中间 segment：`segmentsDirectory`
- 数据库：`databaseURL`

说明：

- `macOS` Release 主要使用 `Application Support` / `Caches`
- `macOS` Debug 为便于开发排查，会使用更直接的本地路径

## 4. 自动种子与恢复

### 4.1 内置提示词恢复

当前初始化逻辑不是“插入单条默认 prompt”，而是统一走 `restoreBuiltInPrompts()`：

- 若内置模板存在，则按 `externalUUID` 精确更新
- 若不存在，则插入
- 不再按名字宽松合并，避免污染订阅模板

### 4.2 默认引擎与流水线

`AppInitializer` 还会确保：

- 至少存在一条默认流水线
- 至少存在一个 Apple 听写实例
- 至少存在一个 Gemini 后处理实例

## 5. 当前维护建议

1. 如果修改提示词导入逻辑，优先检查 `PromptTemplate.externalUUID`、`source` 与 `systemPresetKey` 的兼容性。
2. 如果修改密钥模型，不要把“密钥明文”重新散落回 `EngineProfile` 顶层字段。
3. 如果修改任务展示或重试逻辑，先确认 `TranscriptionTask` 的兼容字段是否仍被依赖。

