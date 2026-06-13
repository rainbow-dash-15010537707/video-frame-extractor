@echo off
setlocal
cd /d "%~dp0.."
python -m PyInstaller --noconfirm video_frame_tool.spec
endlocal
