"""
Audio processing module for splitting audio files.
Handles MP3, WAV, m4a, and FLAC formats using pydub.
"""

import os
from pathlib import Path
from pydub import AudioSegment
from typing import Callable, Optional


class AudioProcessor:
    """Handles audio file splitting functionality."""
    
    SUPPORTED_FORMATS = {'.mp3', '.wav', '.m4a', '.flac'}
    
    def __init__(self, progress_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize the audio processor.
        
        Args:
            progress_callback: Optional callback function for progress updates
        """
        self.progress_callback = progress_callback
    
    def log_progress(self, message: str) -> None:
        """Log progress message."""
        if self.progress_callback:
            self.progress_callback(message)
    
    def is_supported_format(self, filepath: str) -> bool:
        """Check if file format is supported."""
        return Path(filepath).suffix.lower() in self.SUPPORTED_FORMATS
    
    def get_format_from_extension(self, filepath: str) -> str:
        """Get audio format from file extension."""
        ext = Path(filepath).suffix.lower().lstrip('.')
        if ext == 'm4a':
            return 'mp4'
        return ext
    
    def calculate_prefix_format(self, total_segments: int) -> str:
        """
        Calculate the prefix format based on total segments.
        
        Args:
            total_segments: Total number of segments expected
            
        Returns:
            Zero-padded format string (01, 001, 0001)
        """
        if total_segments < 100:
            return '02d'  # 01, 02, etc.
        elif total_segments < 1000:
            return '03d'  # 001, 002, etc.
        else:
            return '04d'  # 0001, 0002, etc.
    
    def split_audio_file(
        self,
        input_filepath: str,
        split_duration_minutes: int,
        output_folder: Optional[str] = None
    ) -> bool:
        """
        Split an audio file into segments.
        
        Args:
            input_filepath: Path to the input audio file
            split_duration_minutes: Duration of each segment in minutes
            output_folder: Optional custom output folder path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            input_path = Path(input_filepath)
            
            # Validate input file
            if not input_path.exists():
                self.log_progress(f"Error: File not found: {input_filepath}")
                return False
            
            if not self.is_supported_format(input_filepath):
                self.log_progress(f"Error: Unsupported format: {input_path.suffix}")
                return False
            
            # Create output folder
            if output_folder is None:
                output_folder = str(input_path.parent / input_path.stem)
            
            output_path = Path(output_folder)
            output_path.mkdir(parents=True, exist_ok=True)
            
            self.log_progress(f"Loading audio file: {input_filepath}")
            
            # Load audio file
            audio_format = self.get_format_from_extension(input_filepath)
            audio = AudioSegment.from_file(input_filepath, format=audio_format)
            
            # Get audio duration in milliseconds and convert to minutes
            duration_minutes = len(audio) / (1000 * 60)
            self.log_progress(f"Audio duration: {duration_minutes:.2f} minutes")
            
            # If audio is shorter than 2x the split duration, just copy it
            if duration_minutes <= split_duration_minutes * 2:
                self.log_progress(f"Audio duration is less than {split_duration_minutes * 2} minutes. Copying original file...")
                segment_number = 1
                prefix_format = '02d'
                original_name = input_path.name
                output_filename = f"{segment_number:{prefix_format}} - {original_name}"
                output_file = output_path / output_filename
                
                audio.export(str(output_file), format=audio_format)
                self.log_progress(f"Saved: {output_filename}")
                return True
            
            # Calculate number of segments
            split_duration_ms = split_duration_minutes * 60 * 1000
            total_segments = (len(audio) + split_duration_ms - 1) // split_duration_ms
            
            self.log_progress(f"Splitting into {total_segments} segments...")
            
            # Calculate prefix format
            prefix_format = self.calculate_prefix_format(total_segments)
            
            # Split audio
            original_name = input_path.name
            for i in range(total_segments):
                start_ms = i * split_duration_ms
                end_ms = min((i + 1) * split_duration_ms, len(audio))
                
                segment = audio[start_ms:end_ms]
                segment_number = i + 1
                
                # Create output filename with prefix
                output_filename = f"{segment_number:{prefix_format}} - {original_name}"
                output_file = output_path / output_filename
                
                self.log_progress(f"Processing segment {segment_number}/{total_segments}...")
                segment.export(str(output_file), format=audio_format)
                self.log_progress(f"Saved: {output_filename}")
            
            self.log_progress(f"✓ Successfully split {input_path.name} into {total_segments} segments!")
            return True
            
        except Exception as e:
            self.log_progress(f"Error processing {input_path.name}: {str(e)}")
            return False
    
    def split_multiple_files(
        self,
        input_filepaths: list,
        split_duration_minutes: int
    ) -> dict:
        """
        Split multiple audio files.
        
        Args:
            input_filepaths: List of input audio file paths
            split_duration_minutes: Duration of each segment in minutes
            
        Returns:
            Dictionary with results for each file
        """
        results = {
            'total': len(input_filepaths),
            'successful': 0,
            'failed': 0,
            'details': []
        }
        
        for i, filepath in enumerate(input_filepaths, 1):
            self.log_progress(f"\n--- Processing file {i}/{len(input_filepaths)} ---")
            success = self.split_audio_file(filepath, split_duration_minutes)
            
            if success:
                results['successful'] += 1
                results['details'].append({'file': filepath, 'status': 'success'})
            else:
                results['failed'] += 1
                results['details'].append({'file': filepath, 'status': 'failed'})
        
        return results
