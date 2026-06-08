# -*- coding: utf-8 -*-
"""视频首尾帧提取工具"""

import ctypes
import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


def _repo_root() -> str:
    """项目根目录（requirements.txt 所在位置）"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


try:
    import cv2
except ImportError:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "缺少依赖",
        "未安装 opencv-python。\n\n请在项目根目录执行：\n"
        f'pip install -r "{_repo_root()}\\requirements.txt"',
    )
    sys.exit(1)

VIDEO_EXTENSIONS = {
    ".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm",
    ".m4v", ".mpeg", ".mpg", ".3gp", ".ts", ".m2ts",
}


def is_video_file(path: str) -> bool:
    return os.path.splitext(path)[1].lower() in VIDEO_EXTENSIONS


def get_short_path(path: str) -> str:
    """Windows short path (8.3), helps OpenCV when path has non-ASCII chars."""
    if os.name != "nt":
        return ""
    buf = ctypes.create_unicode_buffer(32768)
    if ctypes.windll.kernel32.GetShortPathNameW(path, buf, len(buf)):
        return buf.value
    return ""


def open_video(path: str) -> cv2.VideoCapture:
    cap = cv2.VideoCapture(path, cv2.CAP_FFMPEG)
    if cap.isOpened():
        return cap
    short = get_short_path(os.path.abspath(path))
    if short:
        cap = cv2.VideoCapture(short, cv2.CAP_FFMPEG)
    return cap


def imwrite_unicode(path: str, image) -> bool:
    """cv2.imwrite fails on Unicode paths on Windows; use imencode + tofile."""
    ext = os.path.splitext(path)[1] or ".png"
    ok, buf = cv2.imencode(ext, image)
    if not ok:
        return False
    try:
        buf.tofile(path)
    except OSError:
        return False
    return os.path.isfile(path)


def output_path(video_path: str, frame_type: str) -> str:
    """frame_type: '首' 或 '尾'"""
    folder = os.path.dirname(os.path.abspath(video_path))
    stem = os.path.splitext(os.path.basename(video_path))[0]
    return os.path.join(folder, f"{stem}（{frame_type}）.png")


def read_first_frame(cap: cv2.VideoCapture):
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    ok, frame = cap.read()
    return ok, frame


def read_last_frame(cap: cv2.VideoCapture):
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total > 1:
        for pos in (total - 1, total - 2, max(0, total - 10)):
            cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
            ok, frame = cap.read()
            if ok and frame is not None:
                return True, frame

    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    last = None
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        last = frame
    if last is not None:
        return True, last
    return False, None


def extract_frame(video_path: str, frame_type: str):
    cap = open_video(video_path)
    if not cap.isOpened():
        return False, "无法打开视频文件（路径含中文时请确认视频可正常播放）"

    try:
        if frame_type == "首":
            ok, frame = read_first_frame(cap)
        else:
            ok, frame = read_last_frame(cap)

        if not ok or frame is None:
            return False, "未能读取到有效帧"

        out = output_path(video_path, frame_type)
        if not imwrite_unicode(out, frame):
            return False, f"保存图片失败: {out}"

        return True, out
    finally:
        if cap is not None:
            cap.release()


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
        ttk.Button(btn_row, text="添加视频文件…", command=self._pick_files).pack(
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
            text="输出：与原视频同目录，文件名为「原文件名（首/尾）.png」",
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
            self.after(0, lambda n=name, t=frame_type: self._log(f"处理中: {n}（{t}帧）…"))

            ok, result = extract_frame(path, frame_type)
            if ok:
                ok_count += 1
                self.after(0, lambda r=result: self._log(f"  ✓ 已保存: {r}"))
            else:
                fail_count += 1
                self.after(0, lambda r=result, n=name: self._log(f"  ✗ {n}: {r}"))

        summary = f"完成：成功 {ok_count} 个，失败 {fail_count} 个"
        self.after(0, lambda: self._log(summary))
        self.after(0, lambda: self._set_busy(False))
        self.after(
            0,
            lambda: messagebox.showinfo("提取完成", summary) if ok_count or fail_count else None,
        )


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
