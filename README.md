视频首尾帧提取

从本地视频中提取**首帧**或**尾帧**，保存为 PNG 图片。支持中文路径与中文文件名。

功能
- 图形界面选择视频，支持批量处理
- 输出与原视频同目录：`原文件名（首）.png` / `原文件名（尾）.png`
- Windows 下中文路径读写兼容

目录结构
.
├── README.md
├── requirements.txt      # Python 依赖
├── src/
│   └── extract_frames.py # 主程序
└── scripts/
    └── 启动.bat          # Windows 一键启动


环境要求
- Windows 10 / 11（推荐）
- Python 3.8+
- 安装时勾选 **Add Python to PATH**

使用

# 方式一：批处理（推荐）

双击 `scripts/启动.bat`，首次会自动安装 `opencv-python`。

# 方式二：命令行

```bash
pip install -r requirements.txt
python src/extract_frames.py
```
# 依赖

- [opencv-python](https://pypi.org/project/opencv-python/)

## License

MIT（可按需修改）
