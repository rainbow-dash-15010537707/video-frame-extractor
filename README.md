# 视频首尾帧提取

一个 Windows 桌面工具，用于从本地视频中批量提取首帧或尾帧，并保存为 PNG 图片。

## 功能

- 批量选择多个视频文件
- 提取首帧或尾帧
- 结果保存到原视频同目录
- 自动生成文件名：`原文件名（首）.png` / `原文件名（尾）.png`
- 支持中文路径和中文文件名

## 当前版本

- 当前版本：`v1.1.0`
- 提取后端：`ffmpeg` / `ffprobe`
- 发布目录体积约：`25.4 MB`
- EXE 本体体积约：`2.11 MB`

## 运行依赖

程序运行时需要 `ffmpeg` 和 `ffprobe`。

优先级如下：

1. 优先使用 EXE 同目录下的 `ffmpeg.exe` 和 `ffprobe.exe`
2. 如果同目录没有，再使用系统 `PATH` 中已有的 `ffmpeg` 和 `ffprobe`

如果两者都不存在，程序会提示缺少依赖。

## 发布文件

- `dist/视频首尾帧提取/视频首尾帧提取.exe`：主程序
- `scripts/启动.bat`：启动脚本
- `scripts/build_exe.bat`：重新打包脚本
- `src/extract_frames.py`：源码入口

## 使用方式

### 方式一：直接运行 EXE

双击：

```text
dist/视频首尾帧提取/视频首尾帧提取.exe
```

### 方式二：通过启动脚本

双击：

```text
scripts/启动.bat
```

### 方式三：运行源码

```bash
python src/extract_frames.py
```

## 构建

```bat
scripts\build_exe.bat
```

## 环境要求

- Windows 10 / 11
- 运行源码时需要 Python 3.8+
- 运行发布包时不需要单独安装 Python

## 更新日志

见 [CHANGELOG.md](./CHANGELOG.md)
