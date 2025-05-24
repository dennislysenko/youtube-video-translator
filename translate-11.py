import subprocess
import requests
from dotenv import load_dotenv
import os
import argparse
import time

def send_to_elevenlabs(video_path, api_key):
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
            data={"source_lang": "en", "target_lang": "ru", "watermark": "true"}
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

def main():
    parser = argparse.ArgumentParser(description="YouTube Video Translator using ElevenLabs")
    parser.add_argument("--check-dubbing", type=str, help="Check status of dubbing with given ID")
    parser.add_argument("--download-dubbing", type=str, help="Download completed dubbing with given ID")
    parser.add_argument("--wait-and-download", type=str, help="Wait for dubbing to complete and download automatically")
    parser.add_argument("--input-file", type=str, help="Path to input video file")
    parser.add_argument("--target-lang", type=str, default="ru", help="Target language code (default: ru)")
    
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

    # Original video upload functionality
    input_file = args.input_file or "/Users/dennis/Downloads/german.mov"
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"{input_file} not found")

    print("Sending video to ElevenLabs for dubbing...")
    response = send_to_elevenlabs(input_file, api_key)

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
