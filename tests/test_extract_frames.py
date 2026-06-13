import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "extract_frames.py"
SPEC = importlib.util.spec_from_file_location("extract_frames", MODULE_PATH)
extract_frames = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(extract_frames)


class ExtractFramesTests(unittest.TestCase):
    def test_is_video_file(self):
        self.assertTrue(extract_frames.is_video_file("demo.MP4"))
        self.assertFalse(extract_frames.is_video_file("demo.txt"))

    def test_output_path(self):
        path = extract_frames.output_path(r"E:\video\sample.mp4", "首")
        self.assertTrue(path.endswith("sample（首）.png"))

    def test_find_local_ffmpeg_tools(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            ffmpeg = root / "ffmpeg.exe"
            ffprobe = root / "ffprobe.exe"
            ffmpeg.write_bytes(b"x")
            ffprobe.write_bytes(b"y")

            with mock.patch.object(extract_frames, "app_root", return_value=root):
                tools = extract_frames.find_ffmpeg_tools()

            self.assertEqual(tools, (str(ffmpeg), str(ffprobe)))

    def test_extract_frame_requires_ffmpeg(self):
        with mock.patch.object(extract_frames, "find_ffmpeg_tools", return_value=(None, None)):
            ok, msg = extract_frames.extract_frame("demo.mp4", "首")
        self.assertFalse(ok)
        self.assertIn("FFmpeg", msg)


if __name__ == "__main__":
    unittest.main()
