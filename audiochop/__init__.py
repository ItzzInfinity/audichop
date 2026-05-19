"""Public API for AudioChop."""

from audiochop.processor import AudioProcessor

__all__ = [
    "AudioProcessor",
    "merge_audio_files",
    "split_audio_file",
    "split_multiple_files",
]

__version__ = "0.1.0"


def split_audio_file(input_filepath, split_duration_minutes, output_folder=None, progress_callback=None):
    """Split one audio file and return True on success."""
    processor = AudioProcessor(progress_callback=progress_callback)
    return processor.split_audio_file(input_filepath, split_duration_minutes, output_folder)


def split_multiple_files(input_filepaths, split_duration_minutes, progress_callback=None):
    """Split multiple audio files and return the processing summary."""
    processor = AudioProcessor(progress_callback=progress_callback)
    return processor.split_multiple_files(input_filepaths, split_duration_minutes)


def merge_audio_files(input_files, output_file):
    """Merge audio files and return the output path."""
    from audiochop.merge_cli import merge_audio_files as _merge_audio_files

    return _merge_audio_files(input_files, output_file)
