# Audio Splitter CLI

Use `python3 -m audiochop` when you want to split files from a terminal or batch script.
Use `python3 -m audiochop.merge_cli` when you want to combine split segments back into one file.

## Requirements

- Python 3.8+
- `ffmpeg` and `ffprobe` available in `PATH`

## Basic Usage

```bash
python3 -m audiochop FILE_OR_PATTERN --duration MINUTES
```

![AudioChop split CLI help](docs/cli_split_help.png)

Examples:

```bash
python3 -m audiochop song.mp3 --duration 5
python3 -m audiochop "*.mp3" --duration 10
python3 -m audiochop "/home/me/Music/*.flac" --duration 15
python3 -m audiochop song.mp3 --duration 5 --output split_output
python3 -m audiochop "*.m4a" --duration 20 --threads 4
python3 -m audiochop "*.wav" --duration 3 --quiet
```

## Options

- `--duration`, `-d`: Segment length in minutes. Valid range is `1` to `120`.
- `--output`, `-o`: Optional output folder. Relative paths are created beside each input file.
- `--threads`, `-t`: Number of files to process concurrently. Maximum is CPU cores minus 2.
- `--quiet`, `-q`: Suppresses progress messages.

## Output

By default, each input creates a folder beside the source file using the audio file stem.

For `song.mp3` split into 5-minute parts:

```text
song/
├── 01 - song.mp3
├── 02 - song.mp3
└── 03 - song.mp3
```

Prefix width is selected from the expected segment count:

- Less than 100 segments: `01`, `02`, ...
- 100 to 999 segments: `001`, `002`, ...
- 1000 or more segments: `0001`, `0002`, ...

Files shorter than or equal to twice the selected split duration are copied as `01 - original-name.ext` instead of split.

## Merge CLI

Merge files in the exact order you provide them:

```bash
python3 -m audiochop.merge_cli 1.m4a 2.m4a 3.m4a -o merged_song.m4a
```

![AudioChop merge CLI help](docs/cli_merge_help.png)

If `--output` is omitted, the output defaults to the first input file name with `_merged` added:

```bash
python3 -m audiochop.merge_cli 01.mp3 02.mp3 03.mp3
# writes 01_merged.mp3
```

Merge works best when the input files use the same format, codec, sample rate, and channel layout. This is the normal case for segments created by the splitter.
