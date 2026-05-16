# Audio File Splitter

A PyQt6-based GUI and CLI application for splitting audio files into user-defined segments.

## Features

- **Multi-file Support**: Select and process multiple audio files at once
- **Flexible Duration**: Choose split duration from 1-120 minutes via dropdown
- **Format Support**: MP3, WAV, M4A, and FLAC audio formats
- **Smart Naming**: Auto-calculates prefix padding (01, 001, 0001) based on segment count
- **Error Handling**: Graceful error messages and continues processing on failures
- **Progress Feedback**: Real-time log output showing processing status
- **Short File Handling**: Automatically copies audio files shorter than or equal to 2x the split duration
- **Background Processing**: Audio processing runs in separate thread to prevent UI freeze
- **Lower Memory Usage**: Uses ffprobe/ffmpeg per segment instead of loading full files into Python memory
- **CLI Support**: Batch processing, wildcard input, quiet mode, and optional worker threads

## Installation

### Requirements
- Python 3.8+
- ffmpeg (required by pydub for audio processing)

### Setup

1. Install ffmpeg (if not already installed):
   ```bash
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   
   # macOS
   brew install ffmpeg
   
   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Modes

### GUI — Visual Interface

A PyQt6 desktop application for selecting files, configuring settings, and watching live progress.

```bash
python3 audio_splitter.py
```

![Audio Splitter GUI](docs/gui_screenshot.png)

The log panel sits on the left. Drag the vertical divider to resize it. Drag the horizontal divider in the right panel to resize the file browser area independently.

→ Full GUI guide: [README_GUI.md](README_GUI.md)

---

### CLI — Terminal & Batch Processing

A command-line interface for scripting, wildcards, and automated pipelines. Also includes a merge tool to combine segments back into one file.

```bash
# Split a single file
python3 audio_splitter_cli.py song.mp3 --duration 20

# Split all m4a files with 4 parallel threads
python3 audio_splitter_cli.py "*.m4a" --duration 20 --threads 4

# Merge segments back together
python3 audio_merge_cli.py 01.m4a 02.m4a 03.m4a -o merged.m4a
```

→ Full CLI guide: [README_CLI.md](README_CLI.md)

---

### Output

Each input file creates a folder beside the source with numbered segments:

```
song/
├── 01 - song.mp3   (0:00 - 5:00)
├── 02 - song.mp3   (5:00 - 10:00)
└── 03 - song.mp3   (10:00 - 15:00)
```

Files shorter than or equal to twice the split duration are copied as `01 - original-name.ext` without splitting.

## File Structure

```
/split/
├── audio_splitter.py      # Main GUI application
├── audio_processor.py     # Audio processing logic
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── FSD.md                # Functionality Specification Document
```

## Error Handling

The application handles various error scenarios:
- **Unsupported Format**: Notifies user and skips the file
- **File Not Found**: Displays error message in log
- **Permission Issues**: Shows error and continues with other files
- **Audio Processing Errors**: Logs detailed error information

## Dependencies

- **PyQt6**: GUI framework
- **ffmpeg/ffprobe**: Audio codec and duration support (system requirement)

## Troubleshooting

### ffmpeg not found
Make sure ffmpeg is installed and in your system PATH.

### Audio format not supported
Ensure your audio file is in one of the supported formats: MP3, WAV, M4A, or FLAC.

## Performance Notes

- Processing large files (>500MB) may take several minutes
- The application runs audio processing in a background thread
- UI remains responsive during processing
- Progress is logged in real-time

## License
This project is licensed under the [MIT License](https://opensource.org/licenses/MIT). See the LICENSE file for details.