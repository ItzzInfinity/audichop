"""
Audio processing module for splitting audio files.

The implementation shells out to ffprobe/ffmpeg so large files are processed
segment by segment instead of being loaded into Python memory.
"""

import math
import shutil
import subprocess
from pathlib import Path
from typing import Callable, Optional


class AudioProcessor:
    """Handles audio file splitting functionality."""

    SUPPORTED_FORMATS = {".mp3", ".wav", ".m4a", ".flac"}

    def __init__(
        self,
        progress_callback: Optional[Callable[[str], None]] = None,
        segment_callback: Optional[Callable[[str, int, int], None]] = None,
        cancel_callback: Optional[Callable[[], bool]] = None,
    ):
        """
        Initialize the audio processor.

        Args:
            progress_callback: Optional callback function for progress updates.
            segment_callback: Optional callback called after each copied/split unit.
            cancel_callback: Optional callback returning True when processing should stop.
        """
        self.progress_callback = progress_callback
        self.segment_callback = segment_callback
        self.cancel_callback = cancel_callback

    def log_progress(self, message: str) -> None:
        """Log progress message."""
        if self.progress_callback:
            self.progress_callback(message)

    def _is_cancelled(self) -> bool:
        """Return True when the caller has requested cancellation."""
        return bool(self.cancel_callback and self.cancel_callback())

    def is_supported_format(self, filepath: str) -> bool:
        """Check if file format is supported."""
        return Path(filepath).suffix.lower() in self.SUPPORTED_FORMATS

    def calculate_prefix_format(self, total_segments: int) -> str:
        """
        Calculate the prefix format based on total segments.

        Args:
            total_segments: Total number of segments expected.

        Returns:
            Zero-padded format string (01, 001, 0001).
        """
        if total_segments < 100:
            return "02d"
        if total_segments < 1000:
            return "03d"
        return "04d"

    def get_duration_seconds(self, input_filepath: str) -> float:
        """Return audio duration in seconds using ffprobe."""
        command = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            input_filepath,
        ]
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        return float(result.stdout.strip())

    def planned_segment_count(self, input_filepath: str, split_duration_minutes: int) -> int:
        """Return how many progress units this file will produce."""
        duration_seconds = self.get_duration_seconds(input_filepath)
        split_duration_seconds = split_duration_minutes * 60
        if duration_seconds <= split_duration_seconds * 2:
            return 1
        return max(1, math.ceil(duration_seconds / split_duration_seconds))

    def _run_ffmpeg_segment(
        self,
        input_filepath: str,
        output_file: Path,
        start_seconds: int,
        duration_seconds: int,
    ) -> None:
        """Extract one segment using ffmpeg without decoding in Python."""
        command = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            str(start_seconds),
            "-t",
            str(duration_seconds),
            "-i",
            input_filepath,
            "-map",
            "0:a:0",
            "-vn",
            "-c:a",
            "copy",
            str(output_file),
        ]
        subprocess.run(command, check=True, capture_output=True, text=True)

    def split_audio_file(
        self,
        input_filepath: str,
        split_duration_minutes: int,
        output_folder: Optional[str] = None,
    ) -> bool:
        """
        Split an audio file into segments.

        Args:
            input_filepath: Path to the input audio file.
            split_duration_minutes: Duration of each segment in minutes.
            output_folder: Optional custom output folder path.

        Returns:
            True if successful, False otherwise.
        """
        input_path = Path(input_filepath)

        try:
            if not input_path.exists():
                self.log_progress(f"Error: File not found: {input_filepath}")
                return False

            if not self.is_supported_format(input_filepath):
                self.log_progress(f"Error: Unsupported format: {input_path.suffix}")
                return False

            if split_duration_minutes < 1:
                self.log_progress("Error: Split duration must be at least 1 minute")
                return False

            output_path = Path(output_folder) if output_folder else input_path.parent / input_path.stem
            output_path.mkdir(parents=True, exist_ok=True)

            self.log_progress(f"Inspecting audio file: {input_filepath}")
            duration_seconds = self.get_duration_seconds(str(input_path))
            duration_minutes = duration_seconds / 60
            split_duration_seconds = split_duration_minutes * 60
            self.log_progress(f"Audio duration: {duration_minutes:.2f} minutes")

            original_name = input_path.name

            if duration_seconds <= split_duration_seconds * 2:
                self.log_progress(
                    f"Audio duration is less than or equal to {split_duration_minutes * 2} minutes. "
                    "Copying original file..."
                )
                output_filename = f"01 - {original_name}"
                shutil.copy2(input_path, output_path / output_filename)
                self.log_progress(f"Saved: {output_filename}")
                if self.segment_callback:
                    self.segment_callback(str(input_path), 1, 1)
                return True

            total_segments = max(1, math.ceil(duration_seconds / split_duration_seconds))
            prefix_format = self.calculate_prefix_format(total_segments)
            self.log_progress(f"Splitting into {total_segments} segments...")

            for index in range(total_segments):
                if self._is_cancelled():
                    self.log_progress(f"Cancelled while processing {input_path.name}")
                    return False

                segment_number = index + 1
                start_seconds = index * split_duration_seconds
                remaining_seconds = max(1, math.ceil(duration_seconds - start_seconds))
                segment_seconds = min(split_duration_seconds, remaining_seconds)
                output_filename = f"{segment_number:{prefix_format}} - {original_name}"
                output_file = output_path / output_filename

                self.log_progress(f"Processing segment {segment_number}/{total_segments}...")
                self._run_ffmpeg_segment(
                    str(input_path),
                    output_file,
                    start_seconds,
                    segment_seconds,
                )
                self.log_progress(f"Saved: {output_filename}")
                if self.segment_callback:
                    self.segment_callback(str(input_path), segment_number, total_segments)

            self.log_progress(f"Successfully split {input_path.name} into {total_segments} segments!")
            return True

        except FileNotFoundError as exc:
            self.log_progress(f"Error: Required tool not found: {exc.filename}")
            return False
        except subprocess.CalledProcessError as exc:
            detail = (exc.stderr or exc.stdout or str(exc)).strip()
            self.log_progress(f"Error processing {input_path.name}: {detail}")
            return False
        except Exception as exc:
            self.log_progress(f"Error processing {input_path.name}: {exc}")
            return False

    def split_multiple_files(self, input_filepaths: list, split_duration_minutes: int) -> dict:
        """
        Split multiple audio files.

        Args:
            input_filepaths: List of input audio file paths.
            split_duration_minutes: Duration of each segment in minutes.

        Returns:
            Dictionary with results for each file.
        """
        results = {
            "total": len(input_filepaths),
            "successful": 0,
            "failed": 0,
            "details": [],
        }

        for index, filepath in enumerate(input_filepaths, 1):
            self.log_progress(f"\n--- Processing file {index}/{len(input_filepaths)} ---")
            success = self.split_audio_file(filepath, split_duration_minutes)

            if success:
                results["successful"] += 1
                results["details"].append({"file": filepath, "status": "success"})
            else:
                results["failed"] += 1
                results["details"].append({"file": filepath, "status": "failed"})

        return results
