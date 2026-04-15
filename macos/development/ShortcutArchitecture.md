# Shortcut Virtualization Architecture (快捷键虚拟化架构)

为了解决多引擎实例间的快捷键冲突、删除后的“幽灵锁定”（Ghost Locking）以及非活跃引擎占用系统按键的问题，YakType macOS 版采用了**“快捷键虚拟化”**架构。该架构的核心思想是将**快捷键配置**与其在系统层面的**全局监听器**进行物理隔离与动态解耦。

## 1. 存储机制 (Binary Storage)

不同于传统的将快捷键名（Name）作为字符串存储的方式，新版本直接将 `KeyboardShortcuts.Shortcut` 对象序列化为二进制数据（`Data?`）存储在 SwiftData 模型中：

- **EngineProfile**：存储 `mainShortcutData`（主功能键）。
- **PolishingShortcut**：存储 `shortcutData`（自定义指令键）。

**优势**：
- **方案独立性**：数据库中可以同时存在多个具有相同快捷键的引擎方案而不会产生 `UserDefaults` 键值冲突。
- **生命周期同步**：快捷键不再是全局散落的配置，而是随 Profile 实例的删除而自动清理。

## 2. 槽位虚拟化 (Slot Virtualization)

系统不再为每一个 Profile 的主键或指令主键分配唯一的监听器名称，而是预定义了一组名为**“活跃槽位（Active Slots）”**的固定标识符：

| 槽位名称 | 映射目标 | 触发动作 |
| :--- | :--- | :--- |
| `active_dictation_main` | 当前 Pipeline 的听写引擎主快捷键 | 开启/停止听写 |
| `active_polishing_main` | 当前 Pipeline 的后处理引擎主快捷键 | 开启/停止后期润色 |
| `active_polishing_instruction_n` | 当前 Pipeline 后处理引擎的指令 N (0-9) | 触发特定的 Prompt 执行 |

## 3. 动态升级与同步 (Promotion & Sync)

每当流水线（`ProcessingPipeline`）发生变化时（如用户切换了默认引擎），`SpeechViewModel` 会启动同步流程：

1.  **按需读取**：仅从当前流水线标记为 `Default` 的 Profile 中提取二进制快捷键。
2.  **槽位升级 (Promote)**：通过 `ShortcutManager.promote` 方法，将提取出的二进制数据“注入”到上述预定义的固定槽位中。
3.  **原子化同步**：`ShortcutManager.sync` 负责原子化地更新底层 `KeyboardShortcuts` 的处理器绑定，确保旧引擎的监听器被移除，新引擎的监听器生效。

## 4. 录制逻辑与静默保护 (Recording & Suspension)

录制流程被设计为一套隔离的事务流，并通过“动态注销”确保录制过程无干扰：

- **隔离录制**：配置窗口（`EngineConfigView`）中的录制器绑定到一个专用的 `temp_editing_slot`。
- **动态注销 (Dynamic Deactivation)**：当录制界面打开时，系统会**暂时清空所有正在生效的活跃槽位**（`active_...`）中的按键绑定。
- **全局静默 (Global Suspension)**：`ShortcutManager.shared.isSuspended` 被设为 `true`，防止任何意外触发。
- **冲突规避逻辑**：由于活跃按键已被暂时清空，Recorder 不会因为按键被“已生效的引擎”占用而报错或显示冲突。这允许用户将引擎 B 的按键设置为与引擎 A 相同（只要它们不同时激活）。
- **提交持久化**：只有当用户点击“Save”按钮时，`temp_editing_slot` 中的数据才会被持久化。退出界面时，系统通过 `refreshShortcuts` 重新恢复流水线所需的按键绑定。

## 5. 冲突检测逻辑 (Conflict Detection)

为了辅助用户配置，系统集成了非强制性的冲突检测，遵循“仅对活跃集检测”原则：

- **工具类支持**：`ShortcutManager` 提供静态工具函数用于比对两个二进制 Data 是否代表物理意义上的相同按键。
- **冲突检测范围**：
    - **实例内验证**：检查当前正在编辑的引擎中，“主快捷键”是否与其内部的“指令列表”冲突。
    - **流水线验证**：主界面仅针对**当前流水线中同时活跃**的步骤（听写、后处理及其指令）进行检测。
- **非活跃豁免**：处于非活跃状态的引擎（即未选入 Pipeline 的引擎）即使设置了重复的快捷键，也不会被误报为冲突。
- **UI 展示**：通过黄色警告图标（⚠️）进行提示，但不硬性阻断保存逻辑。

---

> [!NOTE]
> **设计思想总结**：通过将“配置状态”转化为“冷数据”存储，仅在“运行时”将其激活到“热槽位”中，实现了系统资源的最优占用和按键冲突的逻辑规避。
