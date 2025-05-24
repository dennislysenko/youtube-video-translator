# YouTube Translator

**Break down language barriers. Share any English YouTube video with Russian-speaking family and friends.**

Ever found an amazing YouTube video you wanted to share with your Russian-speaking grandma, but couldn't because of the language barrier? This service automatically translates English YouTube videos into Russian with natural-sounding AI voiceover dubbing.

## How It Works

1. **Submit** - Paste any English YouTube video link
2. **Process** - AI extracts audio, translates to Russian, and generates dubbed voiceover  
3. **Share** - Get a direct playback link to share with anyone

No apps to download, no accounts to create. Just paste, process, and share.

## Key Features

- **Automatic Translation** - English to Russian with AI-powered transcription and translation
- **Natural Voiceover** - High-quality AI dubbing that sounds natural
- **Shareable Links** - Direct playback URLs that work in any browser
- **Mobile-Friendly** - Optimized for easy viewing on phones and tablets
- **No Registration** - Works immediately without any signup process

## Current Status

This project is in development. The current version supports direct video file processing via CLI using ElevenLabs AI dubbing service.

### Usage

```bash
# Process a video file
python translate-11.py --input-file path/to/video.mp4

# Check dubbing status
python translate-11.py --check-dubbing YOUR_DUBBING_ID

# Download completed dubbing
python translate-11.py --download-dubbing YOUR_DUBBING_ID
```

---

*Making the internet more accessible, one video at a time.* 