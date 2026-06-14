# YakType iOS 规约：“听写即输入法”

## 概要说明

本文档基于当前 `yaktype/Sources/iOS` 与 Shared Core 实现，说明 YakType iOS 端的真实产品结构、关键交互、热麦架构、键盘桥接方式和当前能力边界。它描述的是“当前工程已经落地的实现方向”，不是早期概念稿。

## 1. 产品结构

YakType iOS 当前由三部分组成：

1. 宿主 App：配置引擎、密钥、提示词、流水线、历史记录与热麦占用。
2. Keyboard Extension：在任意输入场景触发听写、停录、滑动选择流水线，并执行文本注入。
3. Shared Core：共享模型、引擎、桥接协议、音频与任务编排能力。

## 2. 平台架构

### 2.1 多目标职责划分

| 目标 | 当前职责 |
| :--- | :--- |
| `YakType-iOS` | 宿主 App、设置、历史、引擎与热麦控制 |
| `YakType-Keyboard` | 自定义键盘、命令发送、结果注入 |
| `AppCoreiOS` / `EngineKitiOS` / `Shared` | 共享模型、桥接与引擎能力 |

### 2.2 关键约束

- 键盘扩展不直接持有完整业务状态机。
- 热麦占用与真正的音频采集控制在宿主 App 一侧。
- 键盘通过 App Group + Darwin Notification 驱动宿主执行录音与处理。

## 3. 交互模型

### 3.1 当前核心心智模型

iOS 版 YakType 不是传统“打开 App 再录音”，而是：

1. 在宿主 App 中先打开 warm mic
2. 切到任意 App 的 YakType 键盘
3. 通过点击、左滑、右滑触发不同流水线
4. 宿主完成听写/后处理后，把最终文本回填到当前输入框

### 3.2 三条物理流水线

当前 iOS 已经采用三条物理流水线，而不是“一个后处理引擎 + 多 prompt slot”：

- 点击：默认流水线
- 左滑：第一条非默认流水线
- 右滑：第二条非默认流水线

每条流水线都可以绑定：

- 同一个听写引擎
- 不同的后处理引擎

## 4. 热麦（Warm Mic）架构

### 4.1 当前实现方式

热麦由 `MicrophoneSessionManager` 管理。宿主 App 负责：

- 激活 `AVAudioSession`
- 调用 `AudioManager.prepareWarmCapture()`
- 在指定时长内保持麦克风占用
- 在真正开始任务时暂停空闲倒计时

### 4.2 当前时长选项

当前 `SessionDuration` 为：

- `5 minutes`
- `30 minutes`
- `1 hour`

开发调试下还有 `1 minute` 选项。旧文档里提到的 “12 小时” 已不再是当前代码事实。

### 4.3 重要语义

- warm mic 占用并不等于已经开始听写任务
- 录音中的任务会挂起 idle timeout
- 任务结束后重新恢复 idle timeout

## 5. 键盘扩展职责

### 5.1 当前键盘侧负责的事情

- 展示宿主同步过来的状态与提示
- 响应点击/左滑/右滑/停止/取消
- 根据 `KeyboardSyncSnapshot` 更新 UI
- 仅在满足 owner 与幂等条件时执行最终文本注入

### 5.2 不负责的事情

- 不直接管理完整引擎实例生命周期
- 不承担热麦占用
- 不绕过宿主独立完成整条听写链路

## 6. 数据共享与桥接

### 6.1 App Group

当前共享容器标识：

- `group.com.yaktype.shared`

### 6.2 协议层

桥接协议位于：

- `yaktype/Sources/Shared/Services/KeyboardSharedBridge.swift`

当前桥接要点：

- `protocolVersion = 2`
- 命令支持队列模式
- 快照支持 `schemaVersion / snapshotID / generatedAt`
- stop/abort 需要严格 owner 校验

## 7. 文本注入策略

### 7.1 实时与最终文本

键盘侧会接收：

- `transcript`：过程中文本
- `finalTranscript`：最终稳定文本

但真正幂等注入的主依据是：

- `sessionState` 进入终态
- `completedSessionID == localInstanceID`
- `finalTranscriptID` 未消费

### 7.2 注入边界

YakType 的键盘目标是“最终可控地写回文本”，不是在每个阶段都强制覆盖系统输入框。

## 8. 引擎与配置页现状

### 8.1 引擎能力

当前 iOS 可见引擎能力与 Shared Core 保持一致：

- `Apple`
- `Gemini`
- `AliCloud QwenASR`
- `Xiaomi MiMo ASR`
- `OpenAI (Compatible)`

### 8.2 配置模型

iOS 侧已经收敛到：

- 统一密钥池（`ManagedKey`）
- 引擎实例（`EngineProfile`）
- 三条流水线选择
- 内置/订阅/用户提示词模板

### 8.3 连通性视图

当前引擎配置页的连通状态会按 4 个槽位展示：

- `Dictation`
- `Tap`
- `Left Swipe`
- `Right Swipe`

只展示实际配置过 profile 的槽位。

## 9. Onboarding 现状

iOS 首次引导不只是权限说明，还包含：

- 键盘启用确认
- Full Access 说明
- hot mic 使用练习
- 点击与左右滑手势练习

因此它不是一个单纯的“权限页 + API Key 表单”，而是围绕键盘真实交互链路的功能引导。

## 10. 实施与维护要求

1. 修改键盘命令语义时，同时更新 `KeyboardSharedBridge`、键盘模型与 iOS 文档。
2. 修改流水线结构时，同时检查 `PipelineResolver`、`TranscriptionPipelineResolver` 与引擎配置页文案。
3. 任何“键盘直接接管音频采集”的设计提议都应视为架构级变更，而不是局部优化。

