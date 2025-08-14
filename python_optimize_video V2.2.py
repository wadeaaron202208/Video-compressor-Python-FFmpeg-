import subprocess
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

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

    # 创建主输入窗口
    param_window = tk.Toplevel(root)
    param_window.title("视频优化参数设置")
    param_window.geometry("450x500")

    # 视频码率
    tk.Label(param_window, text="视频码率 (kbps，例如 1500):").pack(pady=5)
    video_bitrate_entry = tk.Entry(param_window)
    video_bitrate_entry.pack()

    # 音频码率
    tk.Label(param_window, text="音频码率 (kbps，例如128):").pack(pady=5)
    audio_bitrate_entry = tk.Entry(param_window)
    audio_bitrate_entry.pack()

    # 分辨率输入（两个框）
    tk.Label(param_window, text="分辨率，例如1280x720，不改请留空:").pack(pady=5)
    res_frame = tk.Frame(param_window)
    res_frame.pack()
    width_entry = tk.Entry(res_frame, width=6)
    width_entry.pack(side=tk.LEFT)
    tk.Label(res_frame, text=" × ").pack(side=tk.LEFT)
    height_entry = tk.Entry(res_frame, width=6)
    height_entry.pack(side=tk.LEFT)

    # 帧率
    tk.Label(param_window, text="帧率 (fps，例如 30):").pack(pady=5)
    framerate_entry = tk.Entry(param_window)
    framerate_entry.pack()

    # 视频编码器选择
    tk.Label(param_window, text="视频编码器:").pack(pady=5)
    video_codec_var = tk.StringVar(value="libx264")
    video_codec_options = {
        "H.264 / AVC (libx264)": "libx264",
        "H.265 / HEVC (libx265)": "libx265",
        "VP9 (libvpx-vp9)": "libvpx-vp9",
        "保持原编码器（copy）": "copy"
    }
    video_codec_menu = ttk.Combobox(param_window, textvariable=video_codec_var, values=list(video_codec_options.keys()), state="readonly")
    video_codec_menu.pack()

    # 音频编码器选择
    tk.Label(param_window, text="音频编码器:").pack(pady=5)
    audio_codec_var = tk.StringVar(value="aac")
    audio_codec_options = {
        "AAC": "aac",
        "MP3": "libmp3lame",
        "Opus": "libopus",
        "保持原编码器（copy）": "copy"
    }
    audio_codec_menu = ttk.Combobox(param_window, textvariable=audio_codec_var, values=list(audio_codec_options.keys()), state="readonly")
    audio_codec_menu.pack()

    # 输出文件夹选择
    tk.Label(param_window, text="输出文件夹:").pack(pady=5)
    output_folder_var = tk.StringVar()
    def choose_output_folder():
        folder = filedialog.askdirectory(title="选择输出文件夹")
        if folder:
            output_folder_var.set(folder)
    output_frame = tk.Frame(param_window)
    output_frame.pack()
    tk.Entry(output_frame, textvariable=output_folder_var, width=30).pack(side=tk.LEFT, padx=5)
    tk.Button(output_frame, text="浏览...", command=choose_output_folder).pack(side=tk.LEFT)

    def confirm_params():
        if not output_folder_var.get():
            messagebox.showwarning("提示", "请选择输出文件夹！")
            return
        param_window.destroy()

    # 确认按钮（加大尺寸）
    tk.Button(param_window, text="确定", command=confirm_params, font=("Arial", 14), width=10, height=2).pack(pady=15)

    param_window.wait_window()

    # 获取参数值
    video_bitrate = video_bitrate_entry.get()
    audio_bitrate = audio_bitrate_entry.get()
    width = width_entry.get()
    height = height_entry.get()
    resolution = f"{width}x{height}" if width and height else ""
    framerate = framerate_entry.get()
    selected_video_codec = video_codec_options[video_codec_var.get()]
    selected_audio_codec = audio_codec_options[audio_codec_var.get()]
    output_folder = output_folder_var.get()

    # 构造输出路径
    output_path = os.path.join(output_folder, os.path.splitext(os.path.basename(file_path))[0] + "_optimized" + os.path.splitext(file_path)[1])

    # 构造 FFmpeg 命令
    cmd = ["ffmpeg", "-i", file_path]

    # 视频编码器
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

    # 音频编码器
    if selected_audio_codec != "copy":
        cmd.extend(["-c:a", selected_audio_codec])
    else:
        cmd.extend(["-c:a", "copy"])
    if audio_bitrate and selected_audio_codec != "copy":
        cmd.extend(["-b:a", f"{audio_bitrate}k"])

    cmd.append(output_path)

    # 执行 FFmpeg
    try:
        subprocess.run(cmd, check=True)
        messagebox.showinfo("完成", f"视频优化完成！新文件已保存到：\n{output_path}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("错误", f"视频处理失败：\n{e}")

if __name__ == "__main__":
    optimize_video()
