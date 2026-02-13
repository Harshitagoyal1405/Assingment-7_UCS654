import sys
import os
from yt_dlp import YoutubeDL
import subprocess
import shutil

def download_videos(singer_name, num_videos):
    """Download videos from YouTube"""
    print(f"Searching for {singer_name} videos...")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': False,
        'no_warnings': False,
        'default_search': 'ytsearch' + str(num_videos),
    }
    
    # Create downloads directory
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    
    search_query = f"{singer_name} songs"
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([search_query])
        print(f"Successfully downloaded {num_videos} videos")
    except Exception as e:
        print(f"Error downloading videos: {e}")
        sys.exit(1)

def cut_audio_files(duration):
    """Cut first Y seconds from all audio files using FFmpeg"""
    print(f"Cutting first {duration} seconds from each audio...")
    
    downloads_dir = 'downloads'
    cut_dir = 'cut_files'
    
    if not os.path.exists(cut_dir):
        os.makedirs(cut_dir)
    
    cut_files = []
    file_count = 0
    
    for filename in os.listdir(downloads_dir):
        if filename.endswith('.mp3'):
            input_path = os.path.join(downloads_dir, filename)
            output_path = os.path.join(cut_dir, f"cut_{file_count}.mp3")
            
            try:
                # Use FFmpeg to cut the audio
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
                print(f"Processed: {filename}")
            except subprocess.CalledProcessError as e:
                print(f"Error processing {filename}: {e}")
    
    return cut_files

def merge_audios(audio_files, output_filename):
    """Merge all audio files using FFmpeg"""
    print("Merging all audio files...")
    
    if not audio_files:
        print("No audio files to merge!")
        sys.exit(1)
    
    # Create a file list for FFmpeg
    list_file = 'filelist.txt'
    with open(list_file, 'w', encoding='utf-8') as f:
        for audio_file in audio_files:
            # Use absolute path and escape special characters
            abs_path = os.path.abspath(audio_file).replace('\\', '/')
            f.write(f"file '{abs_path}'\n")
    
    try:
        # Use FFmpeg concat demuxer to merge files
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
        print(f"Mashup created successfully: {output_filename}")
    except subprocess.CalledProcessError as e:
        print(f"Error merging audios: {e}")
        sys.exit(1)
    finally:
        # Clean up list file
        if os.path.exists(list_file):
            os.remove(list_file)

def cleanup():
    """Remove temporary directories"""
    for directory in ['downloads', 'cut_files']:
        if os.path.exists(directory):
            shutil.rmtree(directory)
    print("Cleaned up temporary files")

def main():
    # Check number of arguments
    if len(sys.argv) != 5:
        print("Error: Incorrect number of parameters")
        print("Usage: python <program.py> <SingerName> <NumberOfVideos> <AudioDuration> <OutputFileName>")
        print('Example: python 102303491.py "Sharry Maan" 20 20 102303491-output.mp3')
        sys.exit(1)
    
    # Get command line arguments
    singer_name = sys.argv[1]
    num_videos = sys.argv[2]
    audio_duration = sys.argv[3]
    output_filename = sys.argv[4]
    
    # Validate inputs
    try:
        num_videos = int(num_videos)
        audio_duration = int(audio_duration)
    except ValueError:
        print("Error: NumberOfVideos and AudioDuration must be positive numbers")
        sys.exit(1)
    
    if num_videos < 10:
        print("Error: NumberOfVideos must be greater than 10")
        sys.exit(1)
    
    if audio_duration < 20:
        print("Error: AudioDuration must be greater than 20 seconds")
        sys.exit(1)
    
    if not output_filename.endswith('.mp3'):
        print("Error: OutputFileName must end with .mp3")
        sys.exit(1)
    
    try:
        # Step 1: Download videos
        download_videos(singer_name, num_videos)
        
        # Step 2: Cut audios
        audio_files = cut_audio_files(audio_duration)
        
        # Step 3: Merge all audios
        merge_audios(audio_files, output_filename)
        
        # Step 4: Cleanup
        cleanup()
        
        print("\n✓ Mashup completed successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()