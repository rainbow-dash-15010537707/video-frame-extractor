@echo off
setlocal EnableDelayedExpansion

set "ROOT="
for %%A in ("%~dp0..") do set "ROOT=%%~sA"
if not defined ROOT set "ROOT=%~dp0.."
pushd "!ROOT!" 2>nul
if errorlevel 1 (
    echo [ERROR] Cannot open project folder.
    pause
    exit /b 1
)

if exist "dist\视频首尾帧提取.exe" (
    start "" "dist\视频首尾帧提取.exe"
) else (
    where python >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python not found. Install Python 3.8+ and add to PATH.
        pause
        exit /b 1
    )

    python -c "import cv2" >nul 2>&1
    if errorlevel 1 (
        echo Installing dependencies...
        python -m pip install -r requirements.txt -q
    )

    start "" pythonw src\extract_frames.py
    if errorlevel 1 python src\extract_frames.py
)

popd
endlocal
exit /b 0