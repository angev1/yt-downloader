from PySide6.QtCore import QThread, Signal

import os
import yt_dlp
import json
import re

def create_download_thread(data, url, ydl_opts, project_root, directory):
    path = os.path.join(project_root, 'assets', 'config.json')
    save_settings(path, data)

    return DownloadThread(url, ydl_opts, directory)

def build_ydl_opts(format_file, project_root, video_quality, directory, url):
    if format_file == 'mp4':
        quality_map = {
            'The best': 'bestvideo+bestaudio/best',
            '1080': 'bestvideo[height<=1080]+bestaudio/best',
            '720': 'bestvideo[height<=720]+bestaudio/best',
            '480': 'bestvideo[height<=480]+bestaudio/best',
            '360': 'bestvideo[height<=360]+bestaudio/best',
            '144': 'bestvideo[height<=144]+bestaudio/best',
        }
        ydl_opts = {
            'format': quality_map.get(video_quality, quality_map['The best']),
            'merge_output_format': 'mp4',
            'noplaylist': True,
            'outtmpl': os.path.join(directory, '%(title)s.%(ext)s')
        }

    else:
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': format_file,
                    'preferredquality': '0',
                },
                {
                    'key': 'FFmpegMetadata',
                    'add_metadata': True,
                },
                {
                    'key': 'EmbedThumbnail',
                },
            ],
            'writethumbnail': True,
            'outtmpl': os.path.join(directory, '%(title)s.%(ext)s')
        }

    data = {
        "last_dir": directory,
        "format_file": format_file
    }

    return create_download_thread(data, url, ydl_opts, project_root, directory)

def save_settings(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def get_text_dir(project_root):
    data = load_settings(project_root)
    return data['last_dir']

def get_file_type(project_root):
    data = load_settings(project_root)
    if data['format_file'] == 'mp4':
        return ['mp4', 'mp3', 'flac']
    elif data['format_file'] == 'mp3':
        return ['mp3', 'mp4', 'flac']
    else:
        return ['flac' ,'mp3', 'mp4']

def get_video_quality(project_root):
    data =  load_settings(project_root)
    return data['video_quality']


def is_valid_youtube_url(url: str) -> bool:
    pattern = (
        r'^(https?://)?(www\.)?'
        r'(youtube\.com/(watch\?v=|shorts/|playlist\?list=)|youtu\.be/)'
        r'[\w\-]{10,}'
        r'(&.*)?$'
    )
    return re.match(pattern, url) is not None

def load_settings(project_root: str) -> dict:
    path = os.path.join(project_root, 'assets', 'config.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


class DownloadThread(QThread):
    error_signal = Signal(str)
    progress = Signal(int)

    def __init__(self, url, ydl_opts, directory):
        super().__init__()
        self.url = url
        self.ydl_opts = ydl_opts
        self.directory = directory

    def run(self):
        if not os.path.isdir(self.directory):
            self.error_signal.emit('The selected directory does not exist.')
            return

        def progress_hook(d):
            if self.isInterruptionRequested():
                raise RuntimeError("Download cancelled.")

            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded = d.get('downloaded_bytes', 0)

                if total:
                    progress_value = int(downloaded / total * 100)
                    self.progress.emit(progress_value)

            elif d['status'] == 'finished':
                self.progress.emit(100)
        try:
            self.ydl_opts['progress_hooks'] = [progress_hook]            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([self.url])
        except yt_dlp.utils.DownloadError as e:
            self.error_signal.emit(clean_error(str(e)))
        except RuntimeError as e:
            self.error_signal.emit(str(e))


def clean_error(message: str) -> str:
    ansi_escape = re.compile(r'\x1B\[[0-9;]*m')
    clean = ansi_escape.sub('', message)
    clean_lower = clean.lower()

    if 'getaddrinfo failed' in clean_lower or 'network' in clean_lower:
        return "No internet connection."
    if 'Video unavailable' in clean:
        return "The video is deleted or don't have access."
    if 'ffmpeg' in clean_lower or 'ffprobe' in clean_lower:
        return "FFmpeg is required for audio conversion. Install FFmpeg and add it to PATH."
    if 'mutagen' in clean_lower:
        return "Mutagen is required to embed thumbnails in FLAC files. Install it with: pip install mutagen"
    if (
        'sign in to confirm your age' in clean_lower
        or 'age-restricted' in clean_lower
        or 'age restricted' in clean_lower
        or 'inappropriate for some users' in clean_lower
    ):
        return "Videos have a limit age or require registration."
    if 'private video' in clean_lower:
        return "It is a private video."
    
    return clean
