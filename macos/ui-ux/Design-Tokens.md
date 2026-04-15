# macOS 设计规范 (Design Tokens)

## 概要说明

本文档定义了 YakType 的视觉设计系统——“液态玻璃 (Liquid Glass)”。通过阅读本文档，您可以了解系统的核心调色盘（Cosmic Pulse）、深浅模式下的语义化色彩定义、毛玻璃材质的实现细节以及全局布局的间距标准。这些规范确保了应用在 macOS 平台上的视觉一致性与高端感。

## 核心调色盘 (Cosmic Pulse)

系统采用紫色与粉色构成的“宇宙脉冲”色调，展现现代与科技感。

| Token | Hex | 角色描述 |
| :--- | :--- | :--- |
| `CosmicDeep` | `#460076` | 深色背景重音、深层阴影。 |
| `CosmicVibrant` | `#910CB0` | 品牌主色、交互元素。 |
| `CosmicBright` | `#CA00BB` | 高亮、通知反馈、辅助色。 |
| `CosmicSoft` | `#E47CF4` | 柔和渐变、边框描边。 |
| `CosmicCloud` | `#F6EDFE` | 浅色模式背景色、光晕。 |

## 语义化色彩 (Semantic Colors)

系统支持 macOS 原生的深浅模式切换方案，通过 `Color.dynamic` 实现自动适配。

*   **Primary**：主操作色。浅色模式使用 `CosmicDeep`，深色模式使用 `C792FF`。
*   **Secondary**：次要操作色。深色模式下通过增加亮度确保可读性。
*   **反馈色**：
    *   `Success`：成功状态（例如润色完成）。
    *   `Warning`：警告状态（例如网络抖动）。
    *   `Danger`：错误状态（例如 API 异常）。

## 液态玻璃美学 (Liquid Glass)

YakType 广泛应用了进阶的毛玻璃效果（Glassmorphism）：

1.  **材质 (Material)**：使用 `.ultraThinMaterial` 或 `NSVisualEffectView` 实现高强度背景模糊。
2.  **边框 (Luminous Borders)**：使用极细（0.5pt）的线性渐变描边，模拟光线在玻璃边缘的折射。
3.  **分层 (Z-Index)**：通过 `ZStack` 和 `VisualEffectView` 的叠加，营造应用表面的深度感。

## 布局与间距 (Layout Tokens)

| 常量 | 数值 | 应用场景 |
| :--- | :--- | :--- |
| `pageSpacing` | 32pt | 页面大模块间的间距。 |
| `cardPadding` | 16pt | 卡片容器内部边距。 |
| `compactSpacing` | 8pt | 组件内部的小型间距。 |
| `cornerRadius` | 8pt / 16pt | 按钮与卡片的圆角标准。 |

## 排版规范 (Typography)
*   **标题**：SF Pro Rounded, Bold。
*   **正文**：SF Pro, Regular。
*   **特性**：关键数据使用 `.tracking()` 调整字间距，提升精致感。

## 交互与布局规范 (Interactive Standards)

为了确保 macOS 上的极致手感与视觉平衡，所有 UI 组件必须遵循以下交互准则：

### 1. 命中测试一致性 (Hit Test Consistency)
*   **全区域点击**：交互组件（如 `CosmicSegmentPicker` 的分段）必须确保整个视觉矩形区域均可响应点击，而非仅限于文字像素。
*   **技术实现**：如果组件背景在某些状态下是透明的，**必须**添加一个近乎透明的垫层（例如 `.background(Color.black.opacity(0.001))`），以强制 SwiftUI 捕获该区域的点击事件。

### 2. 头部组件布局 (Header Element Sizing)
*   **紧凑对齐**：位于卡片标题栏右侧或工具栏中的小型控制组件（如日期切换、筛选器），严禁使用 `maxWidth: .infinity` 引起非预期的横向拉伸。
*   **技术实现**：组件本身应设置合理的 `minWidth`（例如每个分段 44pt），并在调用时应用 `.fixedSize(horizontal: true, vertical: false)`，以确保其紧凑地靠右侧对齐，维持页面的“呼吸感”。
