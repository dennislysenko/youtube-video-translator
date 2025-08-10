import subprocess
import requests
from dotenv import load_dotenv
import os
import argparse
import time
import yt_dlp

def send_to_elevenlabs(video_path, api_key, target_lang="ru"):
    # Get the file extension to determine content type
    file_ext = os.path.splitext(video_path)[1].lower()
    
    # Map file extensions to content types
    content_types = {
        '.mp4': 'video/mp4',
        '.mov': 'video/quicktime',
        '.avi': 'video/x-msvideo',
        '.mkv': 'video/x-matroska',
        '.webm': 'video/webm'
    }
    
    content_type = content_types.get(file_ext, 'video/mp4')  # Default to mp4
    filename = os.path.basename(video_path)
    
    with open(video_path, "rb") as f:
        response = requests.post(
            "https://api.elevenlabs.io/v1/dubbing",
            headers={"xi-api-key": api_key},
            files={"file": (filename, f, content_type)},
            data={"source_lang": "en", "target_lang": target_lang, "watermark": "false"}
        )
    return response

def check_dubbing_status(dubbing_id, api_key):
    """Check the status of a dubbing project"""
    response = requests.get(
        f"https://api.elevenlabs.io/v1/dubbing/{dubbing_id}",
        headers={"xi-api-key": api_key}
    )
    return response

def download_dubbed_file(dubbing_id, api_key, target_lang="ru", output_dir="downloads"):
    """Download the completed dubbed file"""
    os.makedirs(output_dir, exist_ok=True)
    
    response = requests.get(
        f"https://api.elevenlabs.io/v1/dubbing/{dubbing_id}/audio/{target_lang}",
        headers={"xi-api-key": api_key},
        stream=True
    )
    
    if response.status_code == 200:
        file_path = os.path.join(output_dir, f"dubbed_{dubbing_id}_{target_lang}.mp4")
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return file_path
    else:
        print(f"Error downloading file: {response.status_code}")
        print("Response:", response.text)
        return None

def wait_and_download(dubbing_id, api_key, target_lang="ru", max_attempts=120, check_interval=10):
    """Wait for dubbing to complete and automatically download"""
    print(f"Waiting for dubbing {dubbing_id} to complete...")
    
    for attempt in range(max_attempts):
        status_response = check_dubbing_status(dubbing_id, api_key)
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            status = status_data.get("status", "unknown")
            
            print(f"Attempt {attempt + 1}: Status = {status}")
            
            if status == "dubbed":
                print("Dubbing completed! Downloading file...")
                file_path = download_dubbed_file(dubbing_id, api_key, target_lang)
                if file_path:
                    print(f"File downloaded successfully: {file_path}")
                    return file_path
                else:
                    print("Failed to download file")
                    return None
            elif status == "dubbing":
                print(f"Still processing... Will check again in {check_interval} seconds.")
                time.sleep(check_interval)
            else:
                print(f"Dubbing failed with status: {status}")
                if "error_message" in status_data:
                    print(f"Error: {status_data['error_message']}")
                return None
        else:
            print(f"Error checking status: {status_response.status_code}")
            print("Response:", status_response.text)
            return None
    
    print("Dubbing timed out")
    return None

def download_youtube_video(url, output_dir="downloads"):
    """Download YouTube video and return the path to the downloaded file"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Configure yt-dlp options
    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'format': 'mp4/best[ext=mp4]',  # Prefer mp4 format
        'restrictfilenames': True,  # Avoid special characters in filename
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info first
            info = ydl.extract_info(url, download=False)
            
            # Get the filename that yt-dlp will actually use
            filename = ydl.prepare_filename(info)
            
            # Download the video
            ydl.download([url])
            
            # Return the actual path
            if os.path.exists(filename):
                return filename
            else:
                # Fallback: look for the most recently created file in downloads dir
                files = [os.path.join(output_dir, f) for f in os.listdir(output_dir)]
                if files:
                    most_recent = max(files, key=os.path.getctime)
                    return most_recent
                else:
                    return None
            
    except Exception as e:
        print(f"Error downloading YouTube video: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Video Translator using ElevenLabs - Supports local files and YouTube URLs")
    parser.add_argument("--check-dubbing", type=str, help="Check status of dubbing with given ID")
    parser.add_argument("--download-dubbing", type=str, help="Download completed dubbing with given ID")
    parser.add_argument("--wait-and-download", type=str, help="Wait for dubbing to complete and download automatically")
    parser.add_argument("--input-file", type=str, help="Path to local video file (supports .mp4, .mov, .avi, .mkv, .webm)")
    parser.add_argument("--target-lang", type=str, default="ru", help="Target language code (default: ru). Popular options: es (Spanish), fr (French), de (German), it (Italian), pt (Portuguese), zh (Chinese), ja (Japanese), ko (Korean), ar (Arabic), hi (Hindi), and 60+ more")
    parser.add_argument("--youtube-url", type=str, help="YouTube video URL to download and translate")
    
    args = parser.parse_args()
    
    load_dotenv()
    api_key = os.getenv("ELEVEN_API_KEY")
    if not api_key:
        raise ValueError("Missing ELEVEN_API_KEY in .env")

    # Check dubbing status
    if args.check_dubbing:
        print(f"Checking status for dubbing ID: {args.check_dubbing}")
        response = check_dubbing_status(args.check_dubbing, api_key)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            status_data = response.json()
            print(f"Dubbing Status: {status_data.get('status', 'unknown')}")
            print("Full Response:", response.text)
        else:
            print("Response:", response.text)
        return

    # Download completed dubbing
    if args.download_dubbing:
        print(f"Downloading dubbing ID: {args.download_dubbing}")
        file_path = download_dubbed_file(args.download_dubbing, api_key, args.target_lang)
        if file_path:
            print(f"Downloaded: {file_path}")
        return

    # Wait for dubbing to complete and download
    if args.wait_and_download:
        wait_and_download(args.wait_and_download, api_key, args.target_lang)
        return

    # YouTube video download functionality
    if args.youtube_url:
        print(f"Downloading YouTube video: {args.youtube_url}")
        video_path = download_youtube_video(args.youtube_url)
        if video_path:
            print(f"Downloaded: {video_path}")
            # Process the downloaded video
            print(f"Sending video to ElevenLabs for dubbing (English → {args.target_lang})...")
            response = send_to_elevenlabs(video_path, api_key, args.target_lang)
            print(f"Status: {response.status_code}")
            print("Response:", response.text)
            
            if response.status_code == 200:
                response_data = response.json()
                dubbing_id = response_data.get("dubbing_id")
                expected_duration = response_data.get("expected_duration_sec")
                
                print(f"\n🎬 Dubbing started successfully!")
                print(f"📋 Dubbing ID: {dubbing_id}")
                print(f"⏱️  Expected duration: {expected_duration:.1f} seconds")
                print(f"🎥 Original video: {video_path}")
                print(f"\n⏳ Automatically waiting for completion and downloading...")
                
                # Automatically wait and download
                downloaded_file = wait_and_download(dubbing_id, api_key, args.target_lang)
                if downloaded_file:
                    print(f"\n✅ Process complete! Dubbed video ({args.target_lang}) saved to: {downloaded_file}")
                else:
                    print(f"\n❌ Auto-download failed. You can manually check status and download with:")
                    print(f"   python {os.path.basename(__file__)} --check-dubbing={dubbing_id}")
                    print(f"   python {os.path.basename(__file__)} --download-dubbing={dubbing_id}")
            else:
                print(f"❌ Failed to start dubbing. Status: {response.status_code}")
                print("Response:", response.text)
        else:
            print("Failed to download YouTube video")
        return

    # Original video upload functionality
    # Default to the trimmed video file if no input specified
    default_file = "/Users/dennis/dev/youtube-translator/pain_workout_first10min.mp4"
    input_file = args.input_file or default_file
    
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        print("\n💡 Available options:")
        print("   • Specify a file: --input-file /path/to/your/video.mp4")
        print("   • Use YouTube URL: --youtube-url https://youtube.com/...")
        
        # Show some helpful file suggestions if they exist
        suggestions = [
            "/Users/dennis/dev/youtube-translator/pain_workout_first10min.mp4",
            "/Users/dennis/dev/youtube-translator/pain_workout_compatible.mp4",
            "/Users/dennis/Downloads/german.mov"
        ]
        
        existing_files = [f for f in suggestions if os.path.exists(f)]
        if existing_files:
            print("\n📁 Found these video files you might want to use:")
            for file in existing_files:
                size_mb = os.path.getsize(file) / (1024 * 1024)
                print(f"   • {file} ({size_mb:.1f} MB)")
                
        raise FileNotFoundError(f"Please specify a valid input file")
        
    # Show file info
    file_size_mb = os.path.getsize(input_file) / (1024 * 1024)
    print(f"📁 Using input file: {os.path.basename(input_file)} ({file_size_mb:.1f} MB)")

    print(f"Sending video to ElevenLabs for dubbing (English → {args.target_lang})...")
    response = send_to_elevenlabs(input_file, api_key, args.target_lang)

    print(f"Status: {response.status_code}")
    print("Response:", response.text)
    
    if response.status_code == 200:
        response_data = response.json()
        dubbing_id = response_data.get("dubbing_id")
        expected_duration = response_data.get("expected_duration_sec")
        
        print(f"\n🎬 Dubbing started successfully!")
        print(f"📋 Dubbing ID: {dubbing_id}")
        print(f"⏱️  Expected duration: {expected_duration:.1f} seconds")
        print(f"\n💡 To check status, run:")
        print(f"   python {os.path.basename(__file__)} --check-dubbing={dubbing_id}")
        print(f"\n📥 To download when ready, run:")
        print(f"   python {os.path.basename(__file__)} --download-dubbing={dubbing_id}")
        print(f"\n⏳ Or wait and auto-download, run:")
        print(f"   python {os.path.basename(__file__)} --wait-and-download={dubbing_id}")

if __name__ == "__main__":
    main()
