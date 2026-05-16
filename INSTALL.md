# Audio File Splitter - Installation & Quick Start Guide

## Overview
Audio File Splitter is a Python application with both GUI and CLI interfaces for splitting audio files into user-defined segments. It supports MP3, WAV, M4A, and FLAC formats.

## Quick Start (Recommended)

### Linux/macOS
```bash
chmod +x run.sh
./run.sh
```

### Windows
```bash
run.bat
```

## Manual Installation

### Prerequisites
1. **Python 3.8 or higher**
   - Check: `python3 --version`

2. **ffmpeg** (system dependency)
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install ffmpeg
   ```
   
   **macOS:**
   ```bash
   brew install ffmpeg
   ```
   
   **Windows:**
   - Download from https://ffmpeg.org/download.html
   - Add to system PATH or install via chocolatey:
     ```bash
     choco install ffmpeg
     ```

### Install Python Dependencies
```bash
pip install -r requirements.txt
```

## Usage

### GUI Application (Recommended for Users)
```bash
python3 audio_splitter.py
```

**How to use:**
1. Click "Add Audio Files" to select files
2. Set the split duration (1-120 minutes)
3. Click "Start Splitting"
4. Monitor progress in the log window

### Command-Line Interface (For Automation)
```bash
python3 audio_splitter_cli.py [options] FILES
```

**Examples:**
```bash
# Split single file into 5-minute segments
python3 audio_splitter_cli.py song.mp3 --duration 5

# Split all MP3 files into 10-minute segments
python3 audio_splitter_cli.py "*.mp3" --duration 10

# Split to custom output folder
python3 audio_splitter_cli.py song.mp3 --duration 5 --output ./output

# Quiet mode (suppress output)
python3 audio_splitter_cli.py song.mp3 --duration 5 --quiet
```

## File Structure

```
/split/
├── audio_splitter.py          # Main GUI application
├── audio_splitter_cli.py      # Command-line interface
├── audio_processor.py         # Core audio processing logic
├── requirements.txt           # Python dependencies
├── run.sh                      # Linux/macOS quick start
├── run.bat                     # Windows quick start
├── README.md                   # Usage documentation
├── INSTALL.md                  # This file
└── FSD.md                      # Original specification
```

## Output Format

When splitting `song.mp3` into 5-minute segments:

**Output Directory:** `song/` (created in same location as input file)

**Output Files:**
```
song/
├── 01 - song.mp3  (0:00 - 5:00)
├── 02 - song.mp3  (5:00 - 10:00)
├── 03 - song.mp3  (10:00 - 15:00)
└── ...
```

**Naming Convention:**
- Files numbered sequentially
- Prefix padding auto-adjusts:
  - `01-99` for < 100 segments
  - `001-999` for 100-999 segments
  - `0001-9999` for 1000+ segments

## Supported Audio Formats
- MP3 (.mp3)
- WAV (.wav)
- M4A (.m4a)
- FLAC (.flac)

## Troubleshooting

### "No module named 'PyQt6'"
```bash
pip install --upgrade PyQt6
```

### "No module named 'pydub'"
```bash
pip install --upgrade pydub
```

### "ffmpeg not found"
- Ensure ffmpeg is installed: `ffmpeg -version`
- On Windows, add ffmpeg to system PATH
- On macOS/Linux, verify installation: `which ffmpeg`

### GUI window doesn't appear
- Ensure you're running X11 on Linux (remote systems may need special setup)
- Try CLI version instead: `python3 audio_splitter_cli.py`

### Audio file processing is slow
- This is normal for large files
- Processing happens in background thread for GUI
- Estimated speed: ~1-3 minutes per GB depending on format and CPU

### "Permission denied" when running .sh files
```bash
chmod +x run.sh
./run.sh
```

## Features

✓ **Multi-file processing** - Process multiple files in one batch
✓ **Flexible duration** - 1-120 minute segments
✓ **Smart naming** - Auto-calculated prefix padding
✓ **Format support** - MP3, WAV, M4A, FLAC
✓ **Error handling** - Graceful failures with detailed messages
✓ **Progress tracking** - Real-time feedback and logging
✓ **Short file handling** - Auto-copies files shorter than split duration
✓ **Background processing** - Non-blocking operation in GUI
✓ **Batch automation** - CLI interface for scripting

## System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.8 | 3.10+ |
| RAM | 512 MB | 2 GB+ |
| Disk Space | 2x audio file size | 3x+ for overhead |
| ffmpeg | Latest | Latest |

## Performance Notes

- Processing speed depends on:
  - Audio file size
  - System CPU/storage speed
  - Audio format complexity
  
- Typical speeds:
  - MP3: ~5-10 min/GB
  - WAV: ~2-5 min/GB
  - FLAC: ~3-8 min/GB

## Advanced Usage

### Python API (For Developers)
```python
from audio_processor import AudioProcessor

def progress_callback(msg):
    print(msg)

processor = AudioProcessor(progress_callback=progress_callback)

# Process single file
processor.split_audio_file('song.mp3', split_duration_minutes=5)

# Process multiple files
results = processor.split_multiple_files(['file1.mp3', 'file2.wav'], duration=5)
```

## Support & Issues

For issues or feature requests, check:
1. This INSTALL.md file for common problems
2. README.md for usage documentation
3. FSD.md for original specifications

## License

As specified in FSD.md
