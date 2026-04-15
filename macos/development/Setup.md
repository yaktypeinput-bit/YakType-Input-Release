# macOS 环境搭建与编译 (Setup)

## 概要说明

本文档旨在通过标准化的步骤引导开发者完成 **YakType macOS 版本** 的本地开发环境搭建。内容涵盖基础系统要求、核心开发工具（如 XcodeGen）、依赖包管理（SPM）以及如何生成 `.xcodeproj` 并进行本地调试。

## 开发环境要求

*   **操作系统**：macOS 14.0 (Sonoma) 或更高版本。
*   **开发工具**：Xcode 15.3+ (Swift 5.10+)。
*   **项目生成器**：XcodeGen (必需，用于动态生成项目文件，包括 XcodeGen 命令行工具)。
*   **架构支持**：本项目原生支持 Apple Silicon (arm64)。

## 快速开始

### 1. 安装基础工具
确保您的系统中已安装 Homebrew，并执行以下命令安装项目生成工具：
```bash
brew install xcodegen
```

### 2. 克隆项目并初始化
```bash
git clone https://github.com/your-username/yaktype.git
cd yaktype
```

### 3. 生成 Xcode 项目
YakType 使用 `project.yml` 管理项目结构，**请勿直接修改 `.xcodeproj`**。每次新增源代码文件或修改资源配置后，必须运行：
```bash
xcodegen generate
```
生成成功后，直接通过 `open yaktype.xcodeproj` 即可开始开发。

## 依赖管理说明

### Swift Package Manager (SPM)
项目大部分依赖通过 SPM 自动获取，关键三方库包括：
*   **`swift-ogg`**：负责 OGG/Opus 音频格式的编解码。
*   **`KeyboardShortcuts`**：用于处理 macOS 系统级的全局快捷键监听。

### 本地库 (Local Libraries)
*   **`WebRTCCore`**：静态库文件位于 `Sources/WebRTCCore` 下，集成在主 target 中，用于处理回声消除与音频预处理逻辑。

## 常用开发命令

*   **项目生成**：`xcodegen generate`
*   **构建 Release 版本**：`xcodebuild build`
*   **打包镜像**：
    运行 `scripts/make_dmg.sh` 脚本可将 `.app` 打包为分发所需的 `.dmg` 文件（需配合有效的 Developer ID 进行签名）。

## 注意事项 (Important)
*   **沙盒设置**：项目开启了 App Sandbox，开发调试时若需调整网络或文件访问权限，请通过 `yaktype.entitlements` 配置文件进行修改。
*   **权限授予**：由于涉及麦克风采集与辅助功能（文本注入），调试时需在“系统设置 -> 隐私与安全性”中手动授予开发版应用的相应权限。
