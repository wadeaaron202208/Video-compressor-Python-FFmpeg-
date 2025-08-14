import subprocess
import os
import json
import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox, ttk

def get_media_codecs(file_path):
    """用 ffprobe 获取视频和音频编码器"""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0", "-show_entries", "stream=codec_name",
                "-select_streams", "a:0", "-show_entries", "stream=codec_name",
                "-of", "json", file_path
            ],
            capture_output=True, text=True, check=True
        )
        data = json.loads(result.stdout)
        video_codec = None
        audio_codec = None
        for stream in data.get("streams", []):
            if stream.get("codec_type") == "video":
                video_codec = stream.get("codec_name")
            elif stream.get("codec_type") == "audio":
                audio_codec = stream.get("codec_name")
        return video_codec, audio_codec
    except subprocess.CalledProcessError:
        return None, None

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

    # 获取源文件编码信息
    src_video_codec, src_audio_codec = get_media_codecs(file_path)

    # 获取参数输入
    video_bitrate = simpledialog.askstring("输入", "请输入视频码率 (kbps，例如 1500)：")
    audio_bitrate = simpledialog.askstring("输入", "请输入音频码率 (kbps，例如 128)：")
    resolution = simpledialog.askstring("输入", "请输入分辨率（例如 1280x720，不改请留空）：")
    framerate = simpledialog.askstring("输入", "请输入帧率（例如 30，不改请留空）：")

    # 选择视频编码器
    codec_window = tk.Toplevel(root)
    codec_window.title("选择视频编码器")
    tk.Label(codec_window, text=f"请选择视频编码器（检测到原始: {src_video_codec or '未知'}）:").pack(padx=10, pady=5)

    codec_var = tk.StringVar()
    codec_options = {
        "H.264 / AVC (libx264)": "libx264",
        "H.265 / HEVC (libx265)": "libx265",
        "VP9 (libvpx-vp9)": "libvpx-vp9",
        "保持原编码器（copy）": "copy"
    }
    codec_menu = ttk.Combobox(codec_window, textvariable=codec_var, values=list(codec_options.keys()), state="readonly")
    codec_menu.pack(padx=10, pady=5)

    # 自动预选
    default_video = "保持原编码器（copy）"
    for name, value in codec_options.items():
        if src_video_codec and src_video_codec.lower() in value.lower():
            default_video = name
            break
    codec_var.set(default_video)

    def confirm_codec():
        codec_window.destroy()

    tk.Button(codec_window, text="确认", command=confirm_codec).pack(pady=10)
    codec_window.wait_window()
    selected_codec = codec_options[codec_var.get()]

    # 选择音频编码器
    audio_codec_window = tk.Toplevel(root)
    audio_codec_window.title("选择音频编码器")
    tk.Label(audio_codec_window, text=f"请选择音频编码器（检测到原始: {src_audio_codec or '未知'}）:").pack(padx=10, pady=5)

    audio_codec_var = tk.StringVar()
    audio_codec_options = {
        "AAC (aac)": "aac",
        "MP3 (libmp3lame)": "libmp3lame",
        "Opus (libopus)": "libopus",
        "保持原编码器（copy）": "copy"
    }
    audio_codec_menu = ttk.Combobox(audio_codec_window, textvariable=audio_codec_var, values=list(audio_codec_options.keys()), state="readonly")
    audio_codec_menu.pack(padx=10, pady=5)

    # 自动预选
    default_audio = "保持原编码器（copy）"
    for name, value in audio_codec_options.items():
        if src_audio_codec and src_audio_codec.lower() in value.lower():
            default_audio = name
            break
    audio_codec_var.set(default_audio)

    def confirm_audio_codec():
        audio_codec_window.destroy()

    tk.Button(audio_codec_window, text="确认", command=confirm_audio_codec).pack(pady=10)
    audio_codec_window.wait_window()
    selected_audio_codec = audio_codec_options[audio_codec_var.get()]

    # 构造 FFmpeg 命令
    output_path = os.path.splitext(file_path)[0] + "_optimized" + os.path.splitext(file_path)[1]
    cmd = ["ffmpeg", "-i", file_path]

    # 视频编码设置
    if selected_codec != "copy":
        cmd.extend(["-c:v", selected_codec])
    else:
        cmd.extend(["-c:v", "copy"])
    if video_bitrate and selected_codec != "copy":
        cmd.extend(["-b:v", f"{video_bitrate}k"])
    if resolution and selected_codec != "copy":
        cmd.extend(["-vf", f"scale={resolution}"])
    if framerate and selected_codec != "copy":
        cmd.extend(["-r", framerate])

    # 音频编码设置
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
