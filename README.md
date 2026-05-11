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

## Usage

### Running the Application

```bash
python audio_splitter.py
```

### Steps to Split Audio Files

1. **Step 1: Select Audio Files**
   - Click "Add Audio Files" to select one or more audio files
   - Supported formats: MP3, WAV, M4A, FLAC
   - Click "Clear Selection" to remove all selected files

2. **Step 2: Configure Settings**
   - Set the split duration in minutes (1-120 minutes)
   - Default is 5 minutes

3. **Step 3: Process & Results**
   - Click "Start Splitting" to begin processing
   - Monitor progress in the log output window
   - Processing runs in the background to keep the UI responsive

### Output

For each audio file processed:
- A new folder is created with the same name as the audio file
- Split segments are saved as: `01 - filename.mp3`, `02 - filename.mp3`, etc.
- Numbering prefix adjusts based on total segments:
  - `< 100 segments`: 01, 02, ..., 99
  - `100-999 segments`: 001, 002, ..., 999
  - `≥ 1000 segments`: 0001, 0002, ...., 9999

### Example

**Input**: `song.mp3` (15 minutes)
**Split Duration**: 5 minutes
**Output Folder**: `song/`
**Output Files**:
```
song/
├── 01 - song.mp3   (0:00 - 5:00)
├── 02 - song.mp3   (5:00 - 10:00)
└── 03 - song.mp3   (10:00 - 15:00)
```

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

This project is created as per the specifications in FSD.md
