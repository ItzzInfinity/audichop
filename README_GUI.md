# Audio Splitter GUI

Run the PyQt6 interface when you want to select files visually and monitor progress.

```bash
python3 -m audiochop.launch
```

## Screenshot

![Audio Splitter GUI](docs/gui_screenshot.png)

The log panel is on the left. Drag the vertical divider to resize it against the file selection and controls. Drag the horizontal divider in the right panel to resize the audio file selection area.

## Workflow

1. Choose an audio folder.
   - Type the folder path directly into the editable path box, or use `Browse`.
   - The file list loads supported audio files from that folder.

2. Select audio files.
   - Click one or more files in the list.
   - Use `Select All` or `Deselect All` for quick batch selection.

3. Choose the split duration.
   - Use the duration dropdown to select the segment length in minutes.

4. Optional: enable multithreading.
   - Check `Enable Multithreading` to process multiple files at once.
   - Enter a thread count from `1` through CPU cores minus 2.

5. Start processing.
   - Click `Start Splitting`.
   - The log panel on the left shows file and segment messages.
   - The progress bar updates after each segment or copied short file.

## Supported Formats

- MP3
- WAV
- M4A
- FLAC

## Output

Each input file creates an output folder beside the source file with the same base name.

For `song.mp3` split into 5-minute parts:

```text
song/
├── 01 - song.mp3
├── 02 - song.mp3
└── 03 - song.mp3
```

Files shorter than or equal to twice the selected split duration are copied as `01 - original-name.ext` instead of split.

## Notes

The splitter uses `ffprobe` to inspect duration and `ffmpeg` to write each segment. This keeps memory usage lower than loading the complete audio file into Python memory.
