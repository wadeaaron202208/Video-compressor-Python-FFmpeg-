import subprocess
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import re


class VideoOptimizerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("视频优化工具")
        self.master.geometry("520x580")

        self.file_path = ""
        self.output_folder = ""
        self.process = None
        self.cancel_flag = False

        # 输入文件选择
        tk.Label(master, text="输入视频文件:").pack(pady=5, anchor="w", padx=10)
        self.file_var = tk.StringVar()
        file_frame = tk.Frame(master)
        file_frame.pack(pady=5, fill="x", padx=10)
        tk.Entry(file_frame, textvariable=self.file_var, width=40).pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="浏览...", command=self.select_file).pack(side=tk.LEFT)

        # 输出文件夹选择
        tk.Label(master, text="输出文件夹:").pack(pady=5, anchor="w", padx=10)
        self.output_var = tk.StringVar()
        output_frame = tk.Frame(master)
        output_frame.pack(pady=5, fill="x", padx=10)
        tk.Entry(output_frame, textvariable=self.output_var, width=40).pack(side=tk.LEFT, padx=5)
        tk.Button(output_frame, text="浏览...", command=self.select_output).pack(side=tk.LEFT)

        # 视频码率
        tk.Label(master, text="视频码率 (kbps，例如 1500):").pack(pady=5)
        self.video_bitrate_entry = tk.Entry(master)
        self.video_bitrate_entry.pack()

        # 音频码率
        tk.Label(master, text="音频码率 (kbps，例如 128):").pack(pady=5)
        self.audio_bitrate_entry = tk.Entry(master)
        self.audio_bitrate_entry.pack()

        # 分辨率
        tk.Label(master, text="分辨率 (例如 1280x720，不改请留空):").pack(pady=5)
        res_frame = tk.Frame(master)
        res_frame.pack()
        self.width_entry = tk.Entry(res_frame, width=6)
        self.width_entry.pack(side=tk.LEFT)
        tk.Label(res_frame, text=" × ").pack(side=tk.LEFT)
        self.height_entry = tk.Entry(res_frame, width=6)
        self.height_entry.pack(side=tk.LEFT)

        # 帧率
        tk.Label(master, text="帧率 (fps，例如 30):").pack(pady=5)
        self.framerate_entry = tk.Entry(master)
        self.framerate_entry.pack()

        # 视频编码器选择
        tk.Label(master, text="视频编码器:").pack(pady=5)
        self.video_codec_var = tk.StringVar(value="H.264 / AVC (libx264)")
        self.video_codec_options = {
            "H.264 / AVC (libx264)": "libx264",
            "H.265 / HEVC (libx265)": "libx265",
            "VP9 (libvpx-vp9)": "libvpx-vp9",
            "保持原编码器（copy）": "copy"
        }
        video_codec_menu = ttk.Combobox(master, textvariable=self.video_codec_var, values=list(self.video_codec_options.keys()), state="readonly")
        video_codec_menu.pack()

        # 音频编码器选择
        tk.Label(master, text="音频编码器:").pack(pady=5)
        self.audio_codec_var = tk.StringVar(value="AAC")
        self.audio_codec_options = {
            "AAC": "aac",
            "MP3": "libmp3lame",
            "Opus": "libopus",
            "保持原编码器（copy）": "copy"
        }
        audio_codec_menu = ttk.Combobox(master, textvariable=self.audio_codec_var, values=list(self.audio_codec_options.keys()), state="readonly")
        audio_codec_menu.pack()

        # 开始按钮
        self.start_button = tk.Button(master, text="开始转换", command=self.start_conversion, font=("Arial", 12), width=12, height=2)
        self.start_button.pack(pady=15)

        # 进度条
        self.progress_label = tk.Label(master, text="", anchor="w")
        self.progress_label.pack(fill="x", padx=10, pady=5)
        self.progress = ttk.Progressbar(master, length=400, mode="determinate")
        self.progress.pack(pady=5)

        # 取消按钮
        self.cancel_button = tk.Button(master, text="取消转换", command=self.cancel_conversion, state="disabled")
        self.cancel_button.pack(pady=5)

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=[("视频文件", "*.mp4 *.mkv *.avi *.mov *.flv")]
        )
        if file_path:
            self.file_path = file_path
            self.file_var.set(file_path)

    def select_output(self):
        folder = filedialog.askdirectory(title="选择输出文件夹")
        if folder:
            self.output_folder = folder
            self.output_var.set(folder)

    def cancel_conversion(self):
        if self.process:
            self.cancel_flag = True
            self.process.terminate()
            self.progress_label.config(text="已取消转换")
            self.cancel_button.config(state="disabled")
            self.start_button.config(state="normal")
            messagebox.showinfo("取消", "视频转换已取消")

    def start_conversion(self):
        if not self.file_var.get():
            messagebox.showwarning("提示", "请选择输入文件！")
            return
        if not self.output_var.get():
            messagebox.showwarning("提示", "请选择输出文件夹！")
            return

        # 构造输出路径
        output_path = os.path.join(
            self.output_var.get(),
            os.path.splitext(os.path.basename(self.file_var.get()))[0] + "_optimized" + os.path.splitext(self.file_var.get())[1]
        )

        # 构造 FFmpeg 命令
        cmd = ["ffmpeg", "-y", "-i", self.file_var.get()]

        selected_video_codec = self.video_codec_options[self.video_codec_var.get()]
        selected_audio_codec = self.audio_codec_options[self.audio_codec_var.get()]
        video_bitrate = self.video_bitrate_entry.get()
        audio_bitrate = self.audio_bitrate_entry.get()
        width = self.width_entry.get()
        height = self.height_entry.get()
        resolution = f"{width}x{height}" if width and height else ""
        framerate = self.framerate_entry.get()

        # 视频参数
        if selected_video_codec != "copy":
            cmd.extend(["-c:v", selected_video_codec])
        else:
            cmd.extend(["-c:v", "copy"])
        if video_bitrate and selected_video_codec != "copy":
            cmd.extend(["-b:v", f"{video_bitrate}k"])
        if resolution and selected_video_codec != "copy":
            cmd.extend(["-vf", f"scale={resolution}"])
        if framerate and selected_video_codec != "copy":
            cmd.extend(["-r", framerate])

        # 音频参数
        if selected_audio_codec != "copy":
            cmd.extend(["-c:a", selected_audio_codec])
        else:
            cmd.extend(["-c:a", "copy"])
        if audio_bitrate and selected_audio_codec != "copy":
            cmd.extend(["-b:a", f"{audio_bitrate}k"])

        cmd.append(output_path)

        # 启动转换线程
        self.cancel_flag = False
        self.start_button.config(state="disabled")
        self.cancel_button.config(state="normal")
        threading.Thread(target=self.run_ffmpeg, args=(cmd, output_path), daemon=True).start()

    def run_ffmpeg(self, cmd, output_path):
        try:
            # 获取视频时长
            probe = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", self.file_var.get()],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore'
            )
            try:
                total_duration = float(probe.stdout.strip())
            except:
                total_duration = None

            self.progress["value"] = 0
            self.progress["maximum"] = 100

            self.process = subprocess.Popen(
                cmd, stderr=subprocess.PIPE, universal_newlines=True, encoding='utf-8', errors='ignore'
            )

            for line in self.process.stderr:
                if self.cancel_flag:
                    break
                match = re.search(r"time=(\d+):(\d+):(\d+\.\d+)", line)
                if match and total_duration:
                    h, m, s = match.groups()
                    seconds = int(h) * 3600 + int(m) * 60 + float(s)
                    percent = seconds / total_duration * 100
                    self.progress["value"] = percent
                    self.progress_label.config(text=f"进度: {percent:.2f}%")
                    self.master.update_idletasks()

            self.process.wait()

            if not self.cancel_flag and self.process.returncode == 0:
                self.progress["value"] = 100
                self.progress_label.config(text="转换完成！")
                messagebox.showinfo("完成", f"视频优化完成！新文件已保存到：\n{output_path}")
            elif not self.cancel_flag:
                messagebox.showerror("错误", "视频处理失败！")

        except Exception as e:
            messagebox.showerror("错误", f"执行过程中出错:\n{e}")
        finally:
            self.start_button.config(state="normal")
            self.cancel_button.config(state="disabled")
            self.process = None


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoOptimizerApp(root)
    root.mainloop()
