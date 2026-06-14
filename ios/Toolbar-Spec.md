# iOS Toolbar Spec

本规范用于 YakType iOS 顶部导航工具栏的统一实现，覆盖提示词、历史、引擎、设置、sheet 编辑页等常见场景。目标是让后续页面在不反复比对截图的情况下，直接按同一套 SwiftUI 结构与 token 落地。

## 1. 基线

- 图标尺寸统一使用 `IconDesignSpec.toolbarSize = 17`
- 单个图标按钮最小点击热区统一使用 `IconDesignSpec.minimumTapSize = 44`
- 工具栏图标样式统一通过 `appToolbarIconStyle(...)`
- 默认颜色：
  - 常规操作：`.primary`
  - 状态辅助或弱化表达：`.secondary` / `SharedTheme.Semantic.secondary`
  - 危险操作：仅在确认弹窗中使用 `role: .destructive`，不要在 toolbar 上直接做红色常驻

代码基线位于：
- `/Users/pengyue/project/yaktype-workspace/yaktype/Sources/iOS/UI/App/ContentViewShared.swift`

## 2. 结构规则

### 2.1 多操作按钮

当同一页面右上角存在多个操作按钮时，必须使用多个独立的：

```swift
ToolbarItem(placement: .topBarTrailing)
```

不要把多个按钮包进一个 `HStack` 再塞进单个 `ToolbarItem`。

原因：
- 系统会自动处理 toolbar 内部间距
- 系统会自动生成与提示词页一致的胶囊式分组外观
- 黑白模式、导航栏高度、大标题折叠过程中的排版更稳定

### 2.2 排序

- 所有右上角动作统一使用 `.topBarTrailing`
- 主要入口动作靠最右
- 次级动作按使用频率向左扩展
- 临时态动作（如“清除筛选”）只在状态存在时显示

历史页参考：
- 常驻：`trash`
- 条件出现：`xmark.circle.fill`
- 常驻：`calendar`

提示词页参考：
- 常驻：`arrow.clockwise`
- 常驻：`square.and.arrow.down`
- 常驻：`plus`

## 3. 交互规则

- 破坏性操作不能直接执行，必须先弹系统 `Alert`
- `Alert` 中使用 `role: .destructive`
- toolbar 本体只作为入口，不承担确认职责
- disabled 状态可直接使用 `.disabled(...)`，由系统接管对比度与可点击性

## 4. 图标语义

- `plus`：新增
- `square.and.arrow.down`：导入 / 订阅导入
- `arrow.clockwise`：恢复 / 刷新 / 重试
- `calendar`：日期筛选入口
- `xmark.circle.fill`：清除当前筛选或当前选择
- `trash`：删除入口
- `checkmark`：编辑页确认 / 保存
- `xmark`：关闭 sheet / 取消编辑

## 5. 代码模板

### 标准多按钮 toolbar

```swift
@ToolbarContentBuilder
var pageToolbar: some ToolbarContent {
    ToolbarItem(placement: .topBarTrailing) {
        Button {
            performSecondaryAction()
        } label: {
            Image(systemName: "trash")
                .appToolbarIconStyle(.secondary)
        }
    }

    if hasActiveFilter {
        ToolbarItem(placement: .topBarTrailing) {
            Button {
                clearFilter()
            } label: {
                Image(systemName: "xmark.circle.fill")
                    .appToolbarIconStyle(.secondary)
            }
        }
    }

    ToolbarItem(placement: .topBarTrailing) {
        Button {
            openPrimaryAction()
        } label: {
            Image(systemName: "calendar")
                .appToolbarIconStyle(hasActiveFilter ? SharedTheme.Semantic.secondary : .primary)
        }
    }
}
```

### 错误示例

```swift
ToolbarItem(placement: .topBarTrailing) {
    HStack {
        Button { ... } label: { ... }
        Button { ... } label: { ... }
        Button { ... } label: { ... }
    }
}
```

问题：
- 间距与提示词页不一致
- 系统胶囊分组表现不稳定
- 更容易出现截图中那种尺寸、密度不统一的问题

## 6. 当前项目约束

- 新页面如需 2 个及以上 toolbar 图标，默认先复用本规范
- 若视觉上需要偏离本规范，必须同步更新本文件与 `UI-SwiftUI-Native-LiquidGlass-Spec.md`
- 本规范优先服务“便于检索与落地”，因此要保持短、具体、可复制
