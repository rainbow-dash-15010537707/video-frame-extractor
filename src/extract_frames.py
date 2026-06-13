# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


VIDEO_EXTENSIONS = {
    ".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm",
    ".m4v", ".mpeg", ".mpg", ".3gp", ".ts", ".m2ts",
}


def app_root() -> Path:
    if getattr(__import__("sys"), "frozen", False):
        return Path(__import__("sys").executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def is_video_file(path: str) -> bool:
    return os.path.splitext(path)[1].lower() in VIDEO_EXTENSIONS


def output_path(video_path: str, frame_type: str) -> str:
    folder = os.path.dirname(os.path.abspath(video_path))
    stem = os.path.splitext(os.path.basename(video_path))[0]
    return os.path.join(folder, f"{stem}（{frame_type}）.png")


def find_ffmpeg_tools():
    root = app_root()
    local_ffmpeg = root / "ffmpeg.exe"
    local_ffprobe = root / "ffprobe.exe"
    if local_ffmpeg.is_file() and local_ffprobe.is_file():
        return str(local_ffmpeg), str(local_ffprobe)

    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if ffmpeg and ffprobe:
        return ffmpeg, ffprobe

    return None, None


def run_command(args):
    return subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def probe_duration(ffprobe_path: str, video_path: str):
    result = run_command([
        ffprobe_path,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        video_path,
    ])
    if result.returncode != 0:
        return None
    try:
        duration = float(result.stdout.strip())
    except ValueError:
        return None
    return duration if duration > 0 else None


def extract_first_frame(ffmpeg_path: str, video_path: str, out_path: str):
    return run_command([
        ffmpeg_path,
        "-y",
        "-i",
        video_path,
        "-frames:v",
        "1",
        out_path,
    ])


def extract_last_frame(ffmpeg_path: str, ffprobe_path: str, video_path: str, out_path: str):
    duration = probe_duration(ffprobe_path, video_path)
    if duration is None:
        return None
    seek_time = max(duration - 0.04, 0)
    return run_command([
        ffmpeg_path,
        "-y",
        "-ss",
        f"{seek_time:.3f}",
        "-i",
        video_path,
        "-frames:v",
        "1",
        out_path,
    ])


def extract_frame(video_path: str, frame_type: str):
    ffmpeg_path, ffprobe_path = find_ffmpeg_tools()
    if not ffmpeg_path or not ffprobe_path:
        return False, "缺少 FFmpeg 依赖，请提供 ffmpeg.exe 和 ffprobe.exe，或安装到系统 PATH"

    out = output_path(video_path, frame_type)
    if frame_type == "首":
        result = extract_first_frame(ffmpeg_path, video_path, out)
    else:
        result = extract_last_frame(ffmpeg_path, ffprobe_path, video_path, out)
        if result is None:
            return False, "无法获取视频时长"

    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        return False, detail or "提取失败"

    if not os.path.isfile(out):
        return False, f"保存图片失败: {out}"

    return True, out


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("视频首尾帧提取")
        self.resizable(True, True)
        self.minsize(520, 380)

        self.video_paths: list[str] = []
        self.frame_choice = tk.StringVar(value="首")

        self._build_ui()
        self._center_window()

    def _center_window(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        pad = {"padx": 12, "pady": 6}

        frm_top = ttk.LabelFrame(self, text="选择视频", padding=10)
        frm_top.pack(fill=tk.BOTH, expand=False, **pad)

        btn_row = ttk.Frame(frm_top)
        btn_row.pack(fill=tk.X)
        ttk.Button(btn_row, text="添加视频文件...", command=self._pick_files).pack(
            side=tk.LEFT, padx=(0, 8)
        )
        ttk.Button(btn_row, text="清空列表", command=self._clear_list).pack(side=tk.LEFT)

        list_frm = ttk.Frame(frm_top)
        list_frm.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        scroll = ttk.Scrollbar(list_frm)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox = tk.Listbox(
            list_frm, height=8, yscrollcommand=scroll.set, selectmode=tk.EXTENDED
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.config(command=self.listbox.yview)

        frm_mode = ttk.LabelFrame(self, text="提取类型", padding=10)
        frm_mode.pack(fill=tk.X, **pad)
        ttk.Radiobutton(
            frm_mode, text="首帧", variable=self.frame_choice, value="首"
        ).pack(side=tk.LEFT, padx=16)
        ttk.Radiobutton(
            frm_mode, text="尾帧", variable=self.frame_choice, value="尾"
        ).pack(side=tk.LEFT, padx=16)

        ttk.Label(
            self,
            text="输出：与原视频同目录，文件名为“原文件名（首/尾）.png”",
            foreground="#555",
        ).pack(anchor=tk.W, padx=12)

        frm_act = ttk.Frame(self)
        frm_act.pack(fill=tk.X, **pad)
        self.btn_run = ttk.Button(
            frm_act, text="开始提取", command=self._start_extract, width=16
        )
        self.btn_run.pack(side=tk.LEFT)
        self.progress = ttk.Progressbar(frm_act, mode="indeterminate", length=200)
        self.progress.pack(side=tk.LEFT, padx=12, fill=tk.X, expand=True)

        frm_log = ttk.LabelFrame(self, text="处理日志", padding=8)
        frm_log.pack(fill=tk.BOTH, expand=True, **pad)
        log_scroll = ttk.Scrollbar(frm_log)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log = tk.Text(frm_log, height=8, state=tk.DISABLED, wrap=tk.WORD)
        self.log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.log.config(yscrollcommand=log_scroll.set)
        log_scroll.config(command=self.log.yview)

    def _log(self, msg: str):
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)

    def _pick_files(self):
        paths = filedialog.askopenfilenames(
            title="选择视频文件",
            filetypes=[
                ("视频文件", "*.mp4;*.avi;*.mov;*.mkv;*.wmv;*.flv;*.webm;*.m4v"),
                ("所有文件", "*.*"),
            ],
        )
        if not paths:
            return
        added = 0
        for p in paths:
            if not is_video_file(p):
                self._log(f"[跳过] 非视频格式: {os.path.basename(p)}")
                continue
            if p not in self.video_paths:
                self.video_paths.append(p)
                self.listbox.insert(tk.END, p)
                added += 1
        if added:
            self._log(f"已添加 {added} 个视频")

    def _clear_list(self):
        self.video_paths.clear()
        self.listbox.delete(0, tk.END)
        self._log("已清空视频列表")

    def _set_busy(self, busy: bool):
        state = tk.DISABLED if busy else tk.NORMAL
        self.btn_run.config(state=state)
        if busy:
            self.progress.start(12)
        else:
            self.progress.stop()

    def _start_extract(self):
        if not self.video_paths:
            messagebox.showwarning("提示", "请先添加至少一个视频文件")
            return
        frame_type = self.frame_choice.get()
        threading.Thread(
            target=self._run_extract, args=(list(self.video_paths), frame_type), daemon=True
        ).start()

    def _run_extract(self, paths: list[str], frame_type: str):
        self.after(0, lambda: self._set_busy(True))
        ok_count = 0
        fail_count = 0

        for path in paths:
            name = os.path.basename(path)
            self.after(0, lambda n=name, t=frame_type: self._log(f"处理中: {n}（{t}帧）..."))

            ok, result = extract_frame(path, frame_type)
            if ok:
                ok_count += 1
                self.after(0, lambda r=result: self._log(f"  成功: {r}"))
            else:
                fail_count += 1
                self.after(0, lambda r=result, n=name: self._log(f"  失败: {n}: {r}"))

        summary = f"完成：成功 {ok_count} 个，失败 {fail_count} 个"
        self.after(0, lambda: self._log(summary))
        self.after(0, lambda: self._set_busy(False))
        self.after(0, lambda: messagebox.showinfo("提取完成", summary))


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
