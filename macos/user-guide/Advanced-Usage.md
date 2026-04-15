# 进阶功能与系统维护 (Advanced Usage)

## 概要说明

本文档详述了 YakType 的进阶操作模式，包括如何通过提示词模板（Prompt Templates）自定义 AI 处理逻辑、非实时音频文件的导入转录机制，以及系统存储的自动清理与维护策略。

---

## 1. 提示词模板工程 (Prompt Template Engineering)

提示词模板是驱动润色引擎的核心指令。系统支持为不同的工作流绑定专属模板。

### 1.1 系统预设模板
*   **默认 (Standard ASR)**：专注于修正 ASR 噪音、同音字纠错及标点符号。
*   **指令化操作**：用户可利用提示词实现特定垂直场景的转换（如翻译为英文、提取代码段）。

### 1.2 注入占位符 (Context Injection)
应用在执行润色请求时，会将听写草案通过以下上下文格式化：

```text
[System Instruction]
Draft Input: {RawText}
Output:
```

*   **原则**：提示词应遵循“零对话 (Zero-Shot)”模式，强制 AI 仅输出处理后的纯文本，不包含任何解释性描述。

---

## 2. 非实时音频处理 (External Audio Import)

除了实时语音捕获，系统提供独立的文件处理路径：

*   **触发入口**：主窗口 (Main Window) -> 导入文件 (Import)。
*   **支持格式**：`.ogg`, `.wav`, `.m4a`, `.mp3` (取决于系统受限的支持范围)。
*   **处理机制**：利用 `TranscriptionService.processImportedFile` 接口。导入后，任务会被加入后台异步队列，完成后用户可通过历史记录进行维护。

---

## 3. 任务生命周期与自动清理 (Persistence Policy)

系统产生的所有数据（音频切片、转录任务、API 调用日志）均受限于本地持久化策略。

### 3.1 自动清理规则 (Auto-Delete Policy)
为了保护隐私并控制磁盘占用，支持以下过期删除策略：
*   **Never**：永久保留。
*   **After 7 / 30 / 90 Days**：根据 `task.date` 自动判断并移除对应的音频物理文件及其数据库条目。

### 3.2 手动维护 (Manual Management)
用户可随时在“历史记录 (History)”面板中执行以下原子操作：
*   **Re-Transcribe**：保留原音频，使用新选定的听写引擎重试。
*   **Re-Polish**：对现有的转录稿，使用不同的 Prompt 模板重新润色。
*   **Export**：将原始音频切片导出为 `.ogg` 文件。

---

## 数据存储路径 (File System)

| 数据类型 | 物理路径 | 备注 |
| :--- | :--- | :--- |
| **音频源文件** | `~/Library/Application Support/com.yaktype.yak-mac/recordings/` | `.ogg` 格式存储。 |
| **数据库** | `~/Library/Application Support/com.yaktype.yak-mac/default.store` | SwiftData 持久化层。 |
| **临时缓存** | `~/Library/Caches/com.yaktype.yak-mac/` | 用于音频切片的流式缓冲。 |

*注意：调试模式（DEBUG）下的存储路径会带有 `-debug` 后缀，以防止开发测试数据对生产环境产生干扰。*
