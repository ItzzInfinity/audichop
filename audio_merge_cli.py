#!/usr/bin/env python3
"""
Command-line interface for merging audio files.

Inputs are merged in the order provided by the user. The implementation uses
ffmpeg's concat demuxer and stream copy for low memory usage.
"""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


SUPPORTED_FORMATS = {".mp3", ".wav", ".m4a", ".flac"}


def _escape_concat_path(path):
    """Escape a path for ffmpeg concat demuxer file lines."""
    return str(path).replace("'", "'\\''")


def _default_output_path(first_input):
    """Build the default output filename from the first input."""
    first_path = Path(first_input)
    return first_path.with_name(f"{first_path.stem}_merged{first_path.suffix}")


def _validate_inputs(files):
    """Validate input paths and supported extensions."""
    valid_files = []
    for filepath in files:
        path = Path(filepath)
        if not path.exists():
            raise ValueError(f"Input file not found: {filepath}")
        if not path.is_file():
            raise ValueError(f"Input path is not a file: {filepath}")
        if path.suffix.lower() not in SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported input format: {path.suffix}")
        valid_files.append(path.resolve())
    return valid_files


def merge_audio_files(input_files, output_file):
    """Merge input audio files into output_file using ffmpeg."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=True) as concat_file:
        for input_path in input_files:
            concat_file.write(f"file '{_escape_concat_path(input_path)}'\n")
        concat_file.flush()

        command = [
                "ffmpeg",
                "-y", 
                "-hide_banner", 
                "-loglevel", "error", 
                "-f", 
                "concat", 
                "-safe", 
                "0", 
                "-i", 
                concat_file.name,
                "-map",
                "0:a",          # ← audio streams only, drop mjpeg thumbnail
                "-c", 
                "copy",
                str(output_path),
                ]
        subprocess.run(command, check=True, capture_output=True, text=True)

    return output_path


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Merge multiple audio files into a single output file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Merge files in the listed order
  %(prog)s 1.m4a 2.m4a 3.m4a -o merged_song.m4a

  # Default output: first input name plus _merged
  %(prog)s 01.mp3 02.mp3 03.mp3

NOTES:
  Inputs are merged in the exact order provided.
  Best results come from segments with matching format, codec, sample rate, and channels.
        """,
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="Audio files to merge in order.",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file name. Defaults to first input stem plus '_merged'.",
    )

    args = parser.parse_args()

    if len(args.files) < 2:
        print("Error: Provide at least two input files to merge", file=sys.stderr)
        sys.exit(1)

    try:
        input_files = _validate_inputs(args.files)
        output_file = Path(args.output) if args.output else _default_output_path(input_files[0])

        print(f"Merging {len(input_files)} file(s)...")
        for index, input_path in enumerate(input_files, 1):
            print(f"{index}. {input_path}")
        print(f"Output: {output_file}")

        merged_path = merge_audio_files(input_files, output_file)
        print(f"Merge complete: {merged_path}")
    except FileNotFoundError as exc:
        print(f"Error: Required tool not found: {exc.filename}", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or str(exc)).strip()
        print(f"Error: ffmpeg merge failed: {detail}", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
