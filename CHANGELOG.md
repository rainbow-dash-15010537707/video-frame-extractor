# Changelog

## v1.1.0 - 2026-06-13

### Changed
- 将首尾帧提取实现从 `OpenCV` 改为 `ffmpeg` / `ffprobe`
- 保留原有 GUI、批量处理、首帧/尾帧选择、PNG 输出和原目录保存行为
- 程序启动时优先使用 EXE 同目录下的 `ffmpeg.exe` / `ffprobe.exe`，否则回退到系统 `PATH`

### Added
- 新增回归测试，覆盖视频扩展名判断、输出命名、FFmpeg 探测和依赖缺失提示
- 新增 `scripts/build_exe.bat` 便于重新构建发布包

### Removed
- 移除 `opencv-python` 运行依赖和相关打包残留

### Packaging
- 发布目录体积从约 `167.59 MB` 降至约 `25.4 MB`
- EXE 本体体积降至约 `2.11 MB`

### Notes
- 如需直接运行发布包，需保证系统已安装 `ffmpeg` / `ffprobe`，或将这两个文件放在 EXE 同目录
