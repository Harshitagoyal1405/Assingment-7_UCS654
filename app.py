from flask import Flask, render_template, request, flash, redirect, url_for
from flask_mail import Mail, Message
import os
import zipfile
import threading
from yt_dlp import YoutubeDL
import subprocess
import shutil
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'hgoyal_be23@thapar.edu'  # Change this
app.config['MAIL_PASSWORD'] = 'pxfb dwyn zagt hjxx'      # Change this
app.config['MAIL_DEFAULT_SENDER'] = 'hgoyal_be23@thapar.edu'   # Change this

mail = Mail(app)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def download_videos(singer_name, num_videos, output_dir):
    """Download videos from YouTube"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch' + str(num_videos),
    }
    
    search_query = f"{singer_name} songs"
    
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([search_query])

def cut_audio_files(duration, input_dir, output_dir):
    """Cut first Y seconds from all audio files using FFmpeg"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    cut_files = []
    file_count = 0
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.mp3'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"cut_{file_count}.mp3")
            
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-t', str(duration),
                '-acodec', 'copy',
                '-y',
                output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            cut_files.append(output_path)
            file_count += 1
    
    return cut_files

def merge_audios(audio_files, output_filename, work_dir):
    """Merge all audio files using FFmpeg"""
    list_file = os.path.join(work_dir, 'filelist.txt')
    with open(list_file, 'w', encoding='utf-8') as f:
        for audio_file in audio_files:
            abs_path = os.path.abspath(audio_file).replace('\\', '/')
            f.write(f"file '{abs_path}'\n")
    
    cmd = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', list_file,
        '-c', 'copy',
        '-y',
        output_filename
    ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    os.remove(list_file)

def create_mashup(singer_name, num_videos, duration, email):
    """Create mashup and send via email"""
    work_dir = f"temp_{email.split('@')[0]}"
    downloads_dir = os.path.join(work_dir, 'downloads')
    cut_dir = os.path.join(work_dir, 'cut_files')
    output_file = os.path.join(work_dir, 'mashup.mp3')
    zip_file = os.path.join(work_dir, 'mashup.zip')
    
    try:
        # Create working directory
        os.makedirs(downloads_dir, exist_ok=True)
        
        # Step 1: Download videos
        download_videos(singer_name, num_videos, downloads_dir)
        
        # Step 2: Cut audios
        audio_files = cut_audio_files(duration, downloads_dir, cut_dir)
        
        # Step 3: Merge audios
        merge_audios(audio_files, output_file, work_dir)
        
        # Step 4: Create zip file
        with zipfile.ZipFile(zip_file, 'w') as zipf:
            zipf.write(output_file, 'mashup.mp3')
        
        # Step 5: Send email
        msg = Message(
            subject=f'Your {singer_name} Mashup is Ready!',
            recipients=[email]
        )
        msg.body = f'''Hello,

Your mashup for {singer_name} has been created successfully!

Details:
- Singer: {singer_name}
- Number of videos: {num_videos}
- Duration per video: {duration} seconds

Please find the mashup attached as a zip file.

Enjoy your music!

Best regards,
Mashup Service
'''
        
        with open(zip_file, 'rb') as f:
            msg.attach('mashup.zip', 'application/zip', f.read())
        
        try:
            with app.app_context():
                mail.send(msg)
            print(f"✓ Email sent successfully to {email}")
        except Exception as e:
            print(f"✗ Email sending failed: {e}")
            import traceback
            traceback.print_exc()
        
    finally:
        # Cleanup
        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        singer_name = request.form.get('singer_name')
        num_videos = request.form.get('num_videos')
        duration = request.form.get('duration')
        email = request.form.get('email')
        
        # Validate inputs
        errors = []
        
        if not singer_name or not singer_name.strip():
            errors.append('Singer name is required')
        
        try:
            num_videos = int(num_videos)
            if num_videos <= 1:
                errors.append('Number of videos must be greater than 0')
        except (ValueError, TypeError):
            errors.append('Number of videos must be a valid number')
        
        try:
            duration = int(duration)
            if duration <= 1:
                errors.append('Duration must be in seconds')
        except (ValueError, TypeError):
            errors.append('Duration must be a valid number')
        
        if not email or not validate_email(email):
            errors.append('Please enter a valid email address')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('index'))
        
        # Process in background thread
        flash(f'Processing your request! Mashup will be sent to {email} shortly.', 'success')
        
        thread = threading.Thread(
            target=create_mashup,
            args=(singer_name, num_videos, duration, email)
        )
        thread.start()
        
        return redirect(url_for('index'))
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)