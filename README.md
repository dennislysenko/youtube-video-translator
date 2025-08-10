# YouTube Translator

**Break down language barriers. Share any video with non-English speaking family and friends.**

Ever found an amazing video you wanted to share with your Russian-speaking grandma, but couldn't because of the language barrier? This service automatically translates English videos into Russian (or any other language) with natural-sounding AI voiceover dubbing.

## How It Works

1. **Submit** - Paste any English YouTube video link or provide a local video file
2. **Process** - AI extracts audio, translates it, and generates dubbed voiceover  
3. **Share** - Get a direct playback link to share with anyone

No apps to download, no accounts to create. Just paste, process, and share.

## Key Features

- **Automatic Translation** - English to 70+ languages with AI-powered transcription and translation
- **Natural Voiceover** - High-quality AI dubbing that sounds natural
- **Multiple Languages** - Spanish, French, German, Italian, Portuguese, Chinese, Japanese, Korean, Arabic, Hindi, and many more
- **Shareable Links** - Direct playback URLs that work in any browser
- **Mobile-Friendly** - Optimized for easy viewing on phones and tablets
- **No Registration** - Works immediately without any signup process

## Current Status

This project is in development. The current version supports processing of both local video files and YouTube videos via CLI using ElevenLabs AI dubbing service.

### Usage

```bash
# Process a local video file (defaults to Russian)
python translate-11.py --input-file path/to/video.mp4

# Process a local video file in another language (example: Spanish)
python translate-11.py --input-file path/to/video.mp4 --target-lang es

# Process a YouTube video in Korean
python translate-11.py --youtube-url https://youtube.com/watch?v=VIDEO_ID --target-lang ko

# Check dubbing status
python translate-11.py --check-dubbing YOUR_DUBBING_ID

# Download completed dubbing
python translate-11.py --download-dubbing YOUR_DUBBING_ID
```

---

*Making the internet more accessible, one video at a time.* 