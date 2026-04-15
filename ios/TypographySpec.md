# YakType iOS Typography Specification

## 概要说明

本规范定义了 YakType iOS 应用程序中各级文字的大小与字重 (Typography Tokens)，旨在确保所有核心页面（记录、引擎、提示词、设置）在视觉传达上保持一致。

## 字号与字重规范 (iOS Tokens)

所有 Token 均已集成在 `SharedTheme.Typography` 枚举中。开发时应优先调用 Token，而非硬编码数值。

| 等级        | 会员 / 属性     | 语义 Token (Style) | 字重 (Weight) | 设计 (Design) | 适用场景                                          |
| :---------- | :-------------- | :----------------- | :------------ | :------------ | :------------------------------------------------ |
| **Level 1** | `sectionHeader` | **`.title3`**      | Bold          | Rounded       | 页面分块标题 (推荐颜色: `.secondary`)             |
| **Level 2** | `itemTitle`     | **`.headline`**    | Bold          | Rounded       | 核心条目名称、设置项标题、历史日期                |
| **Level 3** | `itemBody`      | **`.body`**        | Regular       | Default       | 转写文本正文、详细指令预览、表单标签              |
| **Level 4** | `itemSecondary` | **`.subheadline`** | Regular       | Default       | 设置项当前值、引擎模型 ID、副标题说明             |
| **Level 5** | `caption`       | **`.footnote`**    | Medium        | Default       | 时间戳、记录时长、状态标签 (如“已完成”)           |

## 实现指南

### 1. 调用方式

在 SwiftUI View 中使用：

```swift
Text("设置项标题")
    .font(SharedTheme.Typography.itemTitle)
```

### 2. 局部加粗

如果需要在指定 Token 基础上进一步加粗（例如表单中的 Section Label），应使用 `.fontWeight()` 修饰符：

```swift
Text("模板名称")
    .font(SharedTheme.Typography.itemBody)
    .fontWeight(.bold)
```

### 3. 图标比例

顶部工具栏 (Toolbar) 的图标应统一设定为 `16pt` 或 `18pt` 以匹配文字张力：

- 功能性按钮 (如“恢复内置”、“日期过滤器”): 16pt Semibold
- 主操作按钮 (如“新增提示词”): 18pt
