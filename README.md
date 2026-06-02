# 🎬 YouTube Downloader

A program for downloading video and audio from YouTube with a beautiful graphical interface.

---

##  System Requirements

- **Python 3.10+**
- **FFmpeg** (for video/audio processing)

---

## 📦 Dependencies

- [PySide6](https://pypi.org/project/PySide6/) - GUI
- [yt-dlp](https://pypi.org/project/yt-dlp/) - video download
- [mutagen](https://pypi.org/project/mutagen/) - audio metadata

All dependencies are installed automatically via `pip install -r requirements.txt`.

##  Installation

### Step 1: Install FFmpeg

#### Windows:
```bash
winget install FFmpeg
```
Or download manually from [ffmpeg.org](https://ffmpeg.org/download.html)

#### macOS:
```bash
brew install ffmpeg
```

#### Linux:
```bash
# Debian/Ubuntu
sudo apt install ffmpeg

# Fedora
sudo dnf install ffmpeg
```

---

### Step 2: Download the Program

# Clone the code
```bash
git clone https://github.com/angev1/youtube_downloader
cd youtube_downloader
```

---

### Step 3: Create a Virtual Environment

Open terminal/command prompt in the program folder and execute:

```bash
python -m venv .venv
```

---

### Step 4: Activate the Virtual Environment

#### Windows:
```bash
.venv\Scripts\activate
```

#### macOS / Linux:
```bash
source .venv/bin/activate
```

> 💡 After activation, you'll see `(.venv)` at the beginning of your command line

---

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Step 6: Run the Program

```bash
python main.py
```

---

## ✨ Program Features

✅ **Video download** in various qualities (Best, 1080p, 720p, 480p)
✅ **Audio download** in mp3, flac format

---

## ❓ Troubleshooting

### Error: "FFmpeg not found"
Make sure FFmpeg is installed and added to system PATH.