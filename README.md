# Music Mashup Generator

A Python application that creates audio mashups from YouTube videos.

## Requirements

- Python 3.13
- FFmpeg

## Installation

1. Install required packages:
```bash
pip install yt-dlp flask flask-mail
```

2. Install FFmpeg:
   - Download from https://ffmpeg.org/
   - Add to system PATH

## Program 1: Command Line

**Usage:**
```bash
python 102303491.py "Singer Name" NumberOfVideos Duration OutputFile.mp3
```

**Example:**
```bash
python 102303491.py "Arijit Singh" 15 25 output.mp3
```

## Program 2: Web Application

1. Configure email in `app.py`:
```python
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-app-password'
```

2. Run the server:
```bash
python app.py
```

3. Open browser: `http://127.0.0.1:5000`

4. Fill the form and submit

5. Receive mashup via email as zip file

## Features

- Downloads videos from YouTube
- Converts to MP3 audio
- Cuts specified duration from each audio
- Merges all clips into single file
- Sends result via email (Web App)
