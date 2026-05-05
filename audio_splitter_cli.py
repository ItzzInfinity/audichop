#!/usr/bin/env python3
"""
Command-line interface for Audio File Splitter
Useful for batch processing and automation.
"""

import sys
import os
import argparse
from pathlib import Path
from audio_processor import AudioProcessor


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Split audio files into segments of specified duration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
FEATURES:
  - Supports MP3, WAV, M4A, and FLAC formats
  - Wildcard support for batch processing
  - If audio duration is less than 2x the split duration, the file is copied without splitting
  - Automatic output folder creation with numbered segment naming
  - Prefix format adapts to number of segments (01, 001, or 0001)

EXAMPLES:
  # Split a single file into 5-minute segments
  %(prog)s song.mp3 --duration 5
  
  # Split all MP3 files in current directory into 10-minute segments
  %(prog)s *.mp3 --duration 10
  
  # Split files to custom output folder
  %(prog)s song.mp3 --duration 5 --output /path/to/output
  
  # Split files matching a pattern with quiet mode
  %(prog)s /path/to/music/*.flac --duration 15 --quiet
  
  # Split all audio files in a directory
  %(prog)s /path/to/audio/*.{mp3,wav,m4a,flac} --duration 3
        """
    )
    
    parser.add_argument(
        "files",
        nargs="+",
        help="Audio file(s) to split (supports wildcards like *.mp3)"
    )
    parser.add_argument(
        "--duration", "-d",
        type=int,
        default=5,
        help="Split duration in minutes (default: 5, range: 1-120)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Custom output folder path (optional, default: creates folder next to input file)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress output"
    )
    
    args = parser.parse_args()
    
    # Expand file patterns
    input_files = []
    for pattern in args.files:
        path_obj = Path(pattern)
        
        # Handle absolute paths
        if path_obj.is_absolute():
            if path_obj.exists() and path_obj.is_file():
                input_files.append(pattern)
            else:
                print(f"Warning: File not found: {pattern}")
        else:
            # Handle relative patterns and globs
            try:
                matches = list(Path().glob(pattern))
                if matches:
                    input_files.extend([str(f) for f in matches if f.is_file()])
                else:
                    # Try as literal relative path
                    if path_obj.exists():
                        input_files.append(pattern)
                    else:
                        print(f"Warning: No files matching '{pattern}'")
            except Exception as e:
                print(f"Warning: Error processing pattern '{pattern}': {e}")
    
    if not input_files:
        print("Error: No files found to process")
        sys.exit(1)
    
    # Validate duration
    if args.duration < 1 or args.duration > 120:
        print("Error: Duration must be between 1 and 120 minutes")
        sys.exit(1)
    
    # Create processor
    def progress_callback(msg):
        if not args.quiet:
            print(msg)
    
    processor = AudioProcessor(progress_callback=progress_callback)
    
    # Process files
    print(f"Processing {len(input_files)} file(s)...")
    print(f"Split duration: {args.duration} minutes")
    print(f"Note: Files shorter than {args.duration * 2} minutes will be copied without splitting")
    print("-" * 50)
    
    if args.output:
        # Single output folder for all files
        for i, filepath in enumerate(input_files, 1):
            # Extract output base path from file if it's an absolute path
            if Path(filepath).is_absolute():
                output_dir = args.output if Path(args.output).is_absolute() else str(Path(filepath).parent / args.output)
            else:
                output_dir = args.output
            processor.split_audio_file(filepath, args.duration, output_dir)
    else:
        # Individual output folders - extract base path for absolute paths
        processed_files = []
        for filepath in input_files:
            if Path(filepath).is_absolute():
                # Use parent directory of the absolute path for output
                base_dir = Path(filepath).parent
                processed_files.append((str(filepath), base_dir))
            else:
                processed_files.append((str(filepath), None))
        
        # Process with working directory aware of input file locations
        results = {'total': len(input_files), 'successful': 0, 'failed': 0, 'details': []}
        for i, (filepath, base_dir) in enumerate(processed_files, 1):
            processor.log_progress(f"\n--- Processing file {i}/{len(input_files)} ---")
            if base_dir:
                original_cwd = os.getcwd()
                os.chdir(base_dir)
                success = processor.split_audio_file(filepath, args.duration)
                os.chdir(original_cwd)
            else:
                success = processor.split_audio_file(filepath, args.duration)
            
            if success:
                results['successful'] += 1
                results['details'].append({'file': filepath, 'status': 'success'})
            else:
                results['failed'] += 1
                results['details'].append({'file': filepath, 'status': 'failed'})
        
        print("-" * 50)
        print(f"Processing complete!")
        print(f"Results: {results['successful']} successful, {results['failed']} failed out of {results['total']} file(s)")
        
        if results['failed'] > 0:
            print(f"⚠ {results['failed']} file(s) failed to process")
            sys.exit(1)
        else:
            print("✓ All files processed successfully!")


if __name__ == "__main__":
    main()
