#!/usr/bin/env python3
"""
Command-line interface for Audio File Splitter.
Useful for batch processing and automation.
"""

import argparse
import glob
import multiprocessing
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from audio_processor import AudioProcessor


def _expand_input_files(patterns):
    """Expand literal paths and wildcard patterns into a stable file list."""
    input_files = []
    for pattern in patterns:
        matches = [Path(match) for match in glob.glob(pattern)]
        if matches:
            input_files.extend(str(match) for match in matches if match.is_file())
            continue

        path_obj = Path(pattern)
        if path_obj.exists() and path_obj.is_file():
            input_files.append(str(path_obj))
        elif any(char in pattern for char in "*?[]"):
            print(f"Warning: No files matching '{pattern}'")
        else:
            print(f"Warning: File not found: {pattern}")

    return list(dict.fromkeys(input_files))


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Split audio files into segments of specified duration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
FEATURES:
  - Supports MP3, WAV, M4A, and FLAC formats
  - Wildcard support for batch processing
  - Files shorter than or equal to 2x the split duration are copied without splitting
  - Automatic output folder creation with numbered segment naming
  - Prefix format adapts to number of segments (01, 001, or 0001)

EXAMPLES:
  # Split a single file into 5-minute segments
  %(prog)s song.mp3 --duration 5

  # Split all MP3 files in current directory into 10-minute segments
  %(prog)s "*.mp3" --duration 10

  # Split files to a custom output folder next to each input
  %(prog)s song.mp3 --duration 5 --output split_output

  # Split files matching a pattern with quiet mode
  %(prog)s "/path/to/music/*.flac" --duration 15 --quiet

  # Process matching files concurrently using up to 4 worker threads
  %(prog)s "/path/to/music/*.mp3" --duration 5 --threads 4
        """,
    )

    parser.add_argument(
        "files",
        nargs="+",
        help="Audio file(s) to split. Supports wildcards like '*.mp3'.",
    )
    parser.add_argument(
        "--duration",
        "-d",
        type=int,
        default=5,
        help="Split duration in minutes (default: 5, range: 1-120).",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Custom output folder. Relative paths are created next to each input file.",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress progress output.",
    )
    parser.add_argument(
        "--threads",
        "-t",
        type=int,
        default=1,
        help="Number of files to process concurrently (default: 1, max: CPU cores - 2).",
    )

    args = parser.parse_args()

    input_files = _expand_input_files(args.files)
    if not input_files:
        print("Error: No files found to process")
        sys.exit(1)

    if args.duration < 1 or args.duration > 120:
        print("Error: Duration must be between 1 and 120 minutes")
        sys.exit(1)

    max_threads = max(1, multiprocessing.cpu_count() - 2)
    if args.threads < 1 or args.threads > max_threads:
        print(f"Error: Threads must be between 1 and {max_threads} (CPU cores - 2)")
        sys.exit(1)

    def progress_callback(message):
        if not args.quiet:
            print(message)

    def process_one(filepath):
        processor = AudioProcessor(progress_callback=progress_callback)
        output_dir = None
        if args.output:
            output_dir = args.output
            if not Path(args.output).is_absolute():
                output_dir = str(Path(filepath).parent / args.output)

        success = processor.split_audio_file(filepath, args.duration, output_dir)
        return filepath, success

    print(f"Processing {len(input_files)} file(s)...")
    print(f"Split duration: {args.duration} minutes")
    print(f"Threads: {args.threads}")
    print(f"Note: Files shorter than or equal to {args.duration * 2} minutes will be copied without splitting")
    print("-" * 50)

    results = {"total": len(input_files), "successful": 0, "failed": 0, "details": []}

    if args.threads > 1 and len(input_files) > 1:
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            futures = {}
            for index, filepath in enumerate(input_files, 1):
                progress_callback(f"\n--- Queued file {index}/{len(input_files)}: {filepath} ---")
                futures[executor.submit(process_one, filepath)] = filepath

            for future in as_completed(futures):
                filepath, success = future.result()
                if success:
                    results["successful"] += 1
                    results["details"].append({"file": filepath, "status": "success"})
                else:
                    results["failed"] += 1
                    results["details"].append({"file": filepath, "status": "failed"})
    else:
        for index, filepath in enumerate(input_files, 1):
            progress_callback(f"\n--- Processing file {index}/{len(input_files)} ---")
            filepath, success = process_one(filepath)
            if success:
                results["successful"] += 1
                results["details"].append({"file": filepath, "status": "success"})
            else:
                results["failed"] += 1
                results["details"].append({"file": filepath, "status": "failed"})

    print("-" * 50)
    print("Processing complete!")
    print(f"Results: {results['successful']} successful, {results['failed']} failed out of {results['total']} file(s)")

    if results["failed"] > 0:
        print(f"Warning: {results['failed']} file(s) failed to process")
        sys.exit(1)

    print("All files processed successfully!")


if __name__ == "__main__":
    main()
