# YakType iOS UI 实施规约（SwiftUI Native / Liquid Glass）

## 概要说明

本文档基于当前代码实现（`yaktype/Sources/iOS` 与 `yaktype/Sources/Shared/UI`）提炼 iOS UI 的执行规约，目标是统一以下四个方向：
- SwiftUI 原生优先（Native-first）
- 液态玻璃视觉语言（Liquid Glass）
- 系统原生交互（iOS 标准组件与行为）
- 视觉风格一致性（色彩、排版、层级、反馈）

适用范围：YakType iOS 宿主 App 与 Keyboard Extension 的 UI 新增、重构与评审。

## 1. 代码基线与适用边界

本规约来源于以下代码事实：
- 宿主 App 入口：`yaktype/Sources/iOS/YakTypeApp_iOS.swift`
- 主题与玻璃组件：`yaktype/Sources/Shared/UI/SharedTheme.swift`、`yaktype/Sources/Shared/UI/SharedUIComponents.swift`
- App 页面分层：`yaktype/Sources/iOS/UI/App/*`
- 键盘扩展主界面：`yaktype/Sources/iOS/Keyboard/KeyboardDashboardView.swift`

边界说明：
- 本文档仅定义“当前仓库可落地”的 UI 规约，不引入尚未实现的 UI 框架迁移方案。
- 若后续设计稿与本规约冲突，以“可运行代码 + 本规约”先落地，再通过 ADR 或设计评审更新。

## 2. SwiftUI Native-first 结构规约

### 2.1 页面容器结构（宿主 App）

必须遵循当前已稳定的导航结构：
1. Root 使用 `TabView` 承载一级信息架构（记录、引擎、首页、提示词、设置）。
2. 每个 Tab 内使用独立 `NavigationStack`。
3. 页面内容容器按语义选型：阅读型内容优先 `SectionScrollView + Card`，配置/表单型内容优先 `List(.insetGrouped)`。

禁止事项：
- 禁止自定义整套导航容器替代 `TabView + NavigationStack`。
- 禁止在同一页面混用多套主导航范式（例如局部自制 Tab 与系统 Tab 并存）。

### 2.2 组件拆分与复用

组件组织遵循“页面组装 + 组件下沉”模式：
- 页面层：`HomeSectionView`、`EnginesSectionView`、`HistorySectionView`、`PromptsSectionView`、`SettingsSectionView`
- 复用层：`EnginePipelineCard`、`EngineStatusCards`、`sectionCard()`、`liquidGlass()`

约束：
- 同类视觉容器统一使用 `sectionCard()` 或 `.liquidGlass(cornerRadius: 16)`，避免散落的局部样式实现。
- Sheet 统一使用系统 `.sheet` + `.presentationDetents([.medium, .large])`（若业务只需单层可用 `.medium`）。

### 2.4 Card 与 List 场景边界（新增）

容器选择原则：
- `Card`：用于信息密度高、以阅读理解为主的独立内容块（说明、图示、结果片段）。
- `List`：用于并列信息项、配置项与表单项（选择/填写/开关/菜单）等行式结构。

页面映射建议（当前 iOS）：
- 建议使用 `Card`：
  - 当前处理链路图（Engine Pipeline）
  - 键盘安装指南中的步骤说明块
  - 历史详情中的长文本结果块
- 建议使用 `List`：
  - 系统配置页分组项
  - 密钥管理列表与密钥详情表单
  - 提示词列表与提示词编辑表单（均采用系统 `List(.insetGrouped)`）
  - 引擎配置页中的听写引擎库、后处理引擎库与连通状态分组
  - 引擎配置编辑表单（配置型字段）

### 2.3 键盘扩展结构

Keyboard Extension 采用 `UIInputViewController + UIHostingController` 的原生桥接：
- UIKit 负责系统键盘容器接入与输入法切换按钮桥接。
- SwiftUI 负责交互界面与动画状态。

约束：
- 输入法地球键必须保留系统行为（`needsInputModeSwitchKey` + `handleInputModeList`）。
- 键盘高度管理由控制器统一控制，SwiftUI 页面不自行硬编码高度策略。

## 3. Liquid Glass 视觉规约

### 3.1 单一玻璃实现来源

液态玻璃样式以 `LiquidGlassModifier` 为唯一基线：
- iOS 26+：优先使用系统原生 `glassEffect`
- 低版本 fallback：`.ultraThinMaterial`（可带 opacity 参数）
- 描边：低强度渐变描边（0.5pt）
- 阴影：轻量外投影（避免重阴影导致“塑料感”）

禁止事项：
- 禁止在业务页面重复定义新的“玻璃卡”算法。
- 禁止混入不一致的高饱和描边、重高斯模糊和多层硬阴影。

### 3.2 背景层级

背景统一使用 `LiquidBackground`：
- 底色：`SharedTheme.Cosmic.backgroundLight/backgroundDark`
- 中层：Cosmic 渐变色散射圆形模糊
- 前层：业务卡片层（glass cards）

约束：
- 页面级背景由 Root 提供（当前位于 `ContentView`），子页面不重复铺全屏背景。
- 业务卡片优先使用“浅材质 + 低对比边界”，避免高对比色块破坏玻璃系统统一性。

## 4. 系统原生交互规约

### 4.1 系统组件优先级

优先使用 iOS 原生能力：
- 导航：`NavigationStack`
- 多页：`TabView`
- 弹层：`.sheet` + `.presentationDetents`
- 列表：`List`（在需要 swipeActions 的场景）
- 表单选择：`Picker(.menu)`
- 标准图标：SF Symbols

List 细则（分组列表）：
- 优先使用系统分隔线，不手动画分割线。
- 当出现 section 底部多余分隔线影响视觉时，优先使用原生修饰符：
  - `.listSectionSeparator(.hidden, edges: .bottom)`
- 避免通过覆盖层自绘线条替代系统分隔，除非有明确视觉特例评审结论。
- 全局统一参数（`ListDesignSpec`）：
  - 行高：`defaultMinListRowHeight = 52`
  - 分组头最小高度：`defaultMinListHeaderHeight = 30`
  - 分组间距：使用 `List(.insetGrouped)` 系统默认分组间距，不做页面级自定义
  - 详情图标：`info.circle`，尺寸 `16`，透明度 `0.65`
  - 引擎实例行：不使用前置图标，保持文本型列表一致性
- Header 实现统一：
  - 统一使用 `appSectionHeaderStyle()`（字体、颜色、`textCase(nil)`、最小高度）避免各页面标题到首行距离不一致

Icon 细则（iOS）：
- 所有 SF Symbols 优先通过公共 token 统一，不在业务页面散写 `.font(.system(size: ...))`
- 当前公共基线位于 `ContentViewShared.swift`：
  - `IconDesignSpec.toolbarSize = 17`
  - `IconDesignSpec.inlineSize = 12`
  - `IconDesignSpec.statusSize = 16`
  - `IconDesignSpec.emptyStateSize = 30`
  - `IconDesignSpec.menuChevronSize = 11`
  - `IconDesignSpec.tabSize = 15`
  - `IconDesignSpec.actionGlyphSize = 24`
  - `IconDesignSpec.toolbarBadgeSize = 10`
  - `IconDesignSpec.onboardingHeroSize = 80`
  - `IconDesignSpec.pipelineLargeSize = 22`
  - `IconDesignSpec.pipelineMediumSize = 18`
  - `IconDesignSpec.pipelineSmallSize = 14`
  - `IconDesignSpec.pipelineErrorSize = 12`
  - `IconDesignSpec.minimumTapSize = 44`
- 高频 modifier 统一：
  - `appToolbarIconStyle()`：顶部工具栏、新增/关闭/刷新等操作图标，默认使用 `Semantic.secondary`
  - `appInfoIconStyle()`：列表详情入口 `info.circle`，尺寸 16，透明度 0.65
  - `appInlineIconStyle()`：元信息、chip、时间等辅助小图标，尺寸 12，默认使用 `textSecondary`
  - `appStatusIconStyle()`：状态结果图标，如 `checkmark.circle.fill`、`exclamationmark.triangle.fill`
  - `appEmptyStateIconStyle()`：空状态图标，尺寸 30，低对比显示
  - `appMenuChevronStyle()`：Menu/Picker 右侧下拉箭头
- 展示型图标：
  - onboarding 主视觉图标使用 `onboardingHeroSize`
  - 处理链路图节点图标使用 `pipelineLarge/Medium/Small` 三档，不混入业务页面中的普通操作图标尺寸
- 颜色规则：
  - 导航/工具栏图标：默认 `Semantic.secondary`
  - 详情/尾随信息图标：`textSecondary`
  - 成功状态：`Semantic.success`
  - 处理中/品牌操作：`Semantic.secondary`
  - 危险操作：`Semantic.danger`
  - 空状态：`textSecondary` 降低透明度
- 点击热区：
  - 独立 icon 按钮点击区域不小于 `44x44`
  - 行内详情按钮保持轻量视觉，但必须保留独立触控区域，避免与整行点击冲突

Icon 语义规则（SF Symbols 选型）：
- `info.circle`
  - 仅用于“查看详情 / 打开配置详情 / 展示更多信息”的独立次级动作
  - 典型场景：引擎详情、提示词详情、密钥详情
- `chevron.right`
  - 用于“整行点击后跳转到下一级页面”的列表导航提示
  - 若使用系统 `NavigationLink`，优先复用系统默认 disclosure indicator，不额外再放一个 `info.circle`
- `checkmark.circle.fill`
  - 仅用于“已选中 / 已生效 / 连通成功”这类状态结果
  - 不用于顶部工具栏的保存确认
- `checkmark`
  - 仅用于工具栏确认、提交、保存
- `xmark`
  - 仅用于关闭 sheet / 取消当前编辑
- `xmark.circle.fill`
  - 仅用于“清除当前筛选 / 取消当前选择”这类就地清空动作
- `trash`
  - 仅用于删除
- `arrow.clockwise`
  - 仅用于刷新、重试、重新检测
- `doc.on.doc`
  - 仅用于复制
- `calendar`
  - 仅用于日期筛选或日期选择入口
- `gearshape.fill`
  - 仅用于设置入口
- `sparkles`
  - 统一表示提示词 / 后处理 / 润色能力
- `waveform.and.mic`
  - 统一表示听写结果、重新听写、听写域能力
- `waveform.badge.mic`
  - 仅用于处理链路图中的听写引擎节点
- `mic.fill` / `mic.slash.fill` / `stop.fill`
  - 仅用于首页热麦主按钮与键盘主录音动作状态
- `exclamationmark.triangle.fill`
  - 统一表示配置异常、网络异常、检测失败等 warning/error 状态

卡片内部分隔线细则：
- 凡是“同一张卡片内存在多行可读/可操作项”的结构，必须显式使用横向 `Divider` 分隔行。
- 不依赖 `VStack(spacing: 1)` 这类间距模拟分隔线。
- 推荐做法：`Divider().padding(.horizontal, 16)`，并使用系统分隔色（如 `Color(uiColor: .separator).opacity(...)`）控制强度。

### 4.2 触感与反馈

交互反馈使用系统 `UIImpactFeedbackGenerator`，并与状态绑定：
- 键盘主操作、滑动触发、工具按钮：轻/中/刚性反馈分层
- 失败或不可达状态：用状态文本与颜色提示，不用额外视觉噪音

### 4.3 系统行为一致性

- Toolbar 操作应保持 iOS 语义（关闭、确认、删除等动作位置固定）。
- 破坏性操作使用系统 `role: .destructive` 并走系统 Alert。
- 键盘扩展需兼容宿主前后台切换、心跳超时与不可用状态提示。

### 4.4 列表双动作交互（选中 + 详情）

当同一行同时存在“选中”和“查看详情”两个动作时，遵循：
- 行点击：仅触发“选中”
- 详情入口：使用独立 `info.circle` 按钮，点击热区不小于 `44x44`
- 视觉上可保持轻量（可无背景），但触控区域必须独立，避免与行点击冲突
- 若项已选中，重复点击不再触发二次处理（避免重复状态切换与冗余触感反馈）

## 5. 视觉风格统一规约

### 5.1 色彩 Token

必须优先使用 `SharedTheme`：
- 品牌色：`SharedTheme.Cosmic.*`
- 语义色：`SharedTheme.Semantic.primary/secondary/tertiary/success/danger`
- 文本色：`SharedTheme.Semantic.textPrimary/textSecondary`

约束：
- 业务代码禁止新增散装品牌色常量。
- 状态色（成功/错误/处理中）使用语义色，不直接写魔法值。

### 5.2 字体 Token

宿主 App 统一按 `SharedTheme.Typography`：
- `sectionHeader`：分区标题
- `itemTitle` / `itemBody` / `itemSecondary` / `caption`：分层文字信息

约束：
- 标题与关键按钮优先 rounded 设计，正文使用默认 body/subheadline。
- 禁止同层级信息出现多套字号体系并存。

### 5.3 间距与圆角

当前稳定参数：
- 主卡片圆角：16
- 卡片内边距：12~20（按内容密度）
- Section 垂直间距：12~24

约束：
- 新页面优先复用既有间距阶梯，避免出现 13、17、23 这类离散值。

## 6. 宿主 App 页面一致性规则

### 6.1 首页 / 引擎 / 记录 / 提示词 / 设置

统一模式：
- `Section` 标题（`sectionHeader`）
- 玻璃容器（`sectionCard` / `liquidGlass`）
- 状态胶囊（Capsule）
- SF Symbol + 文本的结构化信息块

记录与首页展示规则：
- 首页“最近一次结果”与记录列表都统一展示两枚引擎信息 chip：
  - 听写引擎：使用听写域图标
  - 后处理引擎：使用后处理域图标；未启用时显示 `未启用后处理`
- 记录类页面不再展示 prompt 归属信息，避免将“运行时引擎上下文”和“可编辑提示词资产”混为一谈
- 图标只承担语义区分，不额外引入高饱和强调色；文本颜色遵循正文/次级正文 token

### 6.2 详情与编辑页（Sheet）

统一模式：
- `NavigationStack` 内部承载表单或详情
- 顶部左关闭、右确认/删除
- 中间为卡片化编辑区，避免满屏纯文本输入
- List/Form 场景优先 `List(.insetGrouped)`，保证系统留白与层级一致性
- 可编辑输入项建议支持“整行点击聚焦”以降低误触
- 不可编辑值（只读项）使用灰色语义色（如 `textSecondary`）区分可编辑内容
- 引擎配置编辑页（`EngineProfileEditorSheet`）使用 `List + Section`，保留系统分隔线，并通过 `.listSectionSeparator(.hidden, edges: .bottom)` 去除分组尾部冗余线
- 后处理引擎编辑采用“单引擎单提示词”规则：每个后处理引擎只配置一个 prompt，点击 / 左滑 / 右滑分别在链路图中选择要使用的引擎实例
- 记录详情页的正文区域按“引擎输出”组织：
  - 第一段优先展示后处理引擎输出，分组首行显示引擎名称，右侧保留复制操作
  - 第二段展示听写引擎原始输出，分组首行同样显示引擎名称与复制操作
  - 不再在详情页首要位置展示 prompt 名称或 slot 信息

### 6.3 引擎配置页规则

- 当前处理链路图是唯一的引擎选择入口
- 听写引擎：点击顶部节点弹出原生 `Menu`
- 后处理引擎：点击中间 / 左侧 / 右侧节点，分别弹出对应链路的原生 `Menu`
- 听写引擎库、后处理引擎库退回为“管理库”，用于查看与编辑，不承担选中职责
- 链路节点文案优先展示引擎实例名；若有 prompt，可在副文案展示 prompt 名称
- 连通状态区最多显示 4 行，且必须与当前链路图中的实际选中引擎保持一致：
  - `听写`
  - `点击`
  - `左滑`
  - `右滑`
- 当链路中的引擎实例发生变化时，连通状态行需要自动重建并自动触发检测
- 每一行仍保留独立刷新入口，允许用户手动重测单个引擎

## 7. 键盘扩展 UI 规则

### 7.1 信息层级

键盘面板按三层组织：
1. 顶部工具层：品牌入口、地球键、输入辅助键
2. 中央主交互层：录音/停止主按钮 + 滑动触发轨道
3. 底部状态层：提示文本 + 录音波形

### 7.2 手势与状态机映射

- 单击：默认 pipeline 启停
- 左滑/右滑：切换到配置好的快捷 pipeline
- 长按停留：进入 ghost hints（可发现性提示）

链路配置约束：
- 默认点击、左滑、右滑对应三条独立物理流水线
- 键盘侧交互不区分“slot prompt”，只区分当前手势落到哪条流水线
- 手势文案允许显示该流水线的 prompt 名称，但运行时选择的是该流水线绑定的后处理引擎

约束：
- 手势触发阈值和状态反馈保持一致，不在局部页面单独改阈值。
- 不可用状态（宿主不可达、未热麦）必须优先给出文本诊断。

## 8. 当前代码中的统一性风险与修正策略

### 8.1 已识别风险

1. 存在部分 `Color.white/Color.black` 直接写值，未完全走语义 token。
2. `selectedTheme` 已存在设置项，但主题切换尚未形成完整全局应用链路。
3. 局部组件有重复的“状态胶囊/卡片”样式实现，长期会造成视觉漂移。

### 8.2 修正优先级

1. **P0**：新增页面必须只使用 `SharedTheme` + `liquidGlass/sectionCard`。
2. **P1**：抽取统一 `StatusPill` 与 `MetaChip` 组件，替代重复实现。
3. **P1**：补齐 `selectedTheme` 到全局 `preferredColorScheme` 与 token 分发链路。
4. **P2**：清理散落硬编码色值，收敛到语义色。

## 9. 评审清单（PR Checklist）

提交 iOS UI 变更时，必须逐项自检：

1. 是否仍使用 `TabView + NavigationStack + SectionScrollView` 主结构？
2. 卡片是否统一使用 `sectionCard()` / `.liquidGlass()`？
3. 色彩和字体是否来自 `SharedTheme` token？
4. 是否优先使用系统原生组件（Sheet/Picker/List/Toolbar）？
5. 键盘扩展是否保留地球键与系统输入法切换行为？
6. 状态反馈（文案、颜色、触感）是否与状态机一致？

## 10. 参考文件

- `yaktype/Sources/Shared/UI/SharedTheme.swift`
- `yaktype/Sources/Shared/UI/SharedUIComponents.swift`
- `yaktype/Sources/iOS/YakTypeApp_iOS.swift`
- `yaktype/Sources/iOS/UI/App/ContentViewShared.swift`
- `yaktype/Sources/iOS/UI/App/HomeSectionView.swift`
- `yaktype/Sources/iOS/UI/App/EnginesSectionView.swift`
- `yaktype/Sources/iOS/UI/App/HistorySectionView.swift`
- `yaktype/Sources/iOS/UI/App/PromptsSectionView.swift`
- `yaktype/Sources/iOS/UI/App/SettingsSectionView.swift`
- `yaktype/Sources/iOS/Keyboard/KeyboardDashboardView.swift`
