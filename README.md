# 视频首尾帧提取

一个 Windows 桌面工具，用于从本地视频中批量提取首帧或尾帧，并保存为 PNG 图片。

## 功能

- 批量选择多个视频文件
- 提取首帧或尾帧
- 结果保存到原视频同目录
- 自动生成文件名：`原文件名（首）.png` / `原文件名（尾）.png`
- 支持中文路径和中文文件名

## 发布文件

- `dist/视频首尾帧提取.exe`：独立可执行版本，双击即可运行
- `scripts/启动.bat`：兼容启动脚本，优先调用 exe
- `src/extract_frames.py`：源码入口

## 使用方式

### 方式一：直接运行 exe

双击 `dist/视频首尾帧提取.exe`。

### 方式二：通过启动脚本

双击 `scripts/启动.bat`。

### 方式三：运行源码

```bash
pip install -r requirements.txt
python src/extract_frames.py
```

## 环境要求

- Windows 10 / 11
- `dist/视频首尾帧提取.exe` 无需额外安装 Python
- 运行源码时需要 Python 3.8+

## 依赖

- `opencv-python`