import subprocess
import os
import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox, ttk

def optimize_video():
    root = tk.Tk()
    root.withdraw()

    # 选择视频文件
    file_path = filedialog.askopenfilename(
        title="选择视频文件",
        filetypes=[("视频文件", "*.mp4 *.mkv *.avi *.mov *.flv")]
    )
    if not file_path:
        messagebox.showinfo("提示", "未选择文件，程序结束。")
        return

    # 获取参数输入
    video_bitrate = simpledialog.askstring("输入", "请输入视频码率 (kbps，例如 1500)：")
    audio_bitrate = simpledialog.askstring("输入", "请输入音频码率 (kbps，例如 128)：")
    resolution = simpledialog.askstring("输入", "请输入分辨率（例如 1280x720，不改请留空）：")
    framerate = simpledialog.askstring("输入", "请输入帧率（例如 30，不改请留空）：")

    # 选择视频编码器
    codec_window = tk.Toplevel(root)
    codec_window.title("选择视频编码器")
    tk.Label(codec_window, text="请选择视频编码器:").pack(padx=10, pady=5)

    codec_var = tk.StringVar(value="libx264")
    codec_options = {
        "H.264 / AVC (libx264)": "libx264",
        "H.265 / HEVC (libx265)": "libx265",
        "VP9 (libvpx-vp9)": "libvpx-vp9",
        "保持原编码器（copy）": "copy"
    }

    codec_menu = ttk.Combobox(codec_window, textvariable=codec_var, values=list(codec_options.keys()), state="readonly")
    codec_menu.pack(padx=10, pady=5)

    def confirm_codec():
        codec_window.destroy()

    tk.Button(codec_window, text="确认", command=confirm_codec).pack(pady=10)
    codec_window.wait_window()

    selected_codec = codec_options[codec_var.get()]

    # 构造 FFmpeg 命令
    output_path = os.path.splitext(file_path)[0] + "_optimized" + os.path.splitext(file_path)[1]
    cmd = ["ffmpeg", "-i", file_path]

    if selected_codec != "copy":
        cmd.extend(["-c:v", selected_codec])
    else:
        cmd.extend(["-c:v", "copy"])  # 保留原视频编码
    if video_bitrate and selected_codec != "copy":
        cmd.extend(["-b:v", f"{video_bitrate}k"])
    if audio_bitrate:
        cmd.extend(["-b:a", f"{audio_bitrate}k"])
    if resolution and selected_codec != "copy":
        cmd.extend(["-vf", f"scale={resolution}"])
    if framerate and selected_codec != "copy":
        cmd.extend(["-r", framerate])

    cmd.append(output_path)

    # 执行 FFmpeg
    try:
        subprocess.run(cmd, check=True)
        messagebox.showinfo("完成", f"视频优化完成！新文件已保存到：\n{output_path}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("错误", f"视频处理失败：\n{e}")

if __name__ == "__main__":
    optimize_video()
