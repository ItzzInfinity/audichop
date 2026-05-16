"""
Audio File Splitter GUI Application
Uses PyQt6 for the user interface and pydub for audio processing.
"""

import sys
import os
import gc
import threading
from pathlib import Path

# Set Qt platform to use offscreen rendering if needed
if not os.environ.get('DISPLAY') and sys.platform.startswith('linux'):
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QComboBox, QListWidget, QListWidgetItem,
        QFileDialog, QProgressBar, QTextEdit, QSpinBox, QGroupBox, QLineEdit
    )
    from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject
    from PyQt6.QtGui import QFont, QColor
except ImportError as e:
    print(f"Error importing PyQt6: {e}")
    print("Try: pip install --upgrade PyQt6")
    sys.exit(1)

from audio_processor import AudioProcessor
from PyQt6.QtWidgets import QAbstractItemView


class WorkerThread(QThread):
    """Worker thread for audio processing to prevent UI freeze."""
    
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(dict)
    progress_update_signal = pyqtSignal(int)  # New signal for progress bar
    
    def __init__(self, files, duration):
        super().__init__()
        self.files = files
        self.duration = duration
        self.processed_count = 0
        # Create a fresh processor whose callback emits the signal (thread-safe)
        self.processor = AudioProcessor(progress_callback=self._safe_log)
    
    def _safe_log(self, message: str) -> None:
        """Emit signal instead of touching UI directly (thread-safe)."""
        self.progress_signal.emit(message)
    
    def run(self):
        """Run audio splitting in background thread."""
        try:
            results = {
                'total': len(self.files),
                'successful': 0,
                'failed': 0,
                'details': []
            }
            
            for i, filepath in enumerate(self.files, 1):
                self.progress_signal.emit(f"\n--- Processing file {i}/{len(self.files)} ---")
                success = self.processor.split_audio_file(filepath, self.duration)
                print("Finished processing file:", filepath, "Success:", success)  # Debug print
                
                if success:
                    results['successful'] += 1
                    results['details'].append({'file': filepath, 'status': 'success'})
                else:
                    results['failed'] += 1
                    results['details'].append({'file': filepath, 'status': 'failed'})
                
                # Update progress bar
                progress_percent = int((i / len(self.files)) * 100)
                self.progress_update_signal.emit(progress_percent)
                
                # Force garbage collection to prevent memory issues
                gc.collect()
            
            self.finished_signal.emit(results)
        except Exception as e:
            self.progress_signal.emit(f"Error in worker thread: {str(e)}")
            error_results = {
                'total': len(self.files),
                'successful': 0,
                'failed': len(self.files),
                'details': []
            }
            self.finished_signal.emit(error_results)


class AudioSplitterApp(QMainWindow):
    """Main application window for Audio Splitter."""
    
    def __init__(self):
        super().__init__()
        self.worker_thread = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Audio File Splitter")
        self.setGeometry(100, 100, 900, 700)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title_label = QLabel("Audio File Splitter")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # Folder Selection Group
        folder_group = QGroupBox("Step 1: Select Folder & Audio Files")
        folder_layout = QVBoxLayout()
        
        # Folder path input with browse button
        folder_row = QHBoxLayout()
        folder_row.addWidget(QLabel("Audio folder:"))
        self.folder_path_input = QLineEdit()
        self.folder_path_input.setPlaceholderText("Enter folder path or use Browse button")
        self.browse_folder_btn = QPushButton("Browse…")
        self.browse_folder_btn.clicked.connect(self._browse_folder)
        self.folder_path_input.editingFinished.connect(self._load_folder_contents)
        folder_row.addWidget(self.folder_path_input, 1)
        folder_row.addWidget(self.browse_folder_btn)
        folder_layout.addLayout(folder_row)
        
        # File list with multi-select
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.file_list.setMaximumHeight(150)
        folder_layout.addWidget(QLabel("Audio files in folder (select one or more):"))
        folder_layout.addWidget(self.file_list)
        
        folder_group.setLayout(folder_layout)
        main_layout.addWidget(folder_group)
        
        # Settings Group
        settings_group = QGroupBox("Step 2: Configure Settings")
        settings_layout = QVBoxLayout()
        
        # Duration selector with spinbox
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Split Duration (minutes):"))
        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setMinimum(1)
        self.duration_spinbox.setMaximum(120)
        self.duration_spinbox.setValue(5)
        duration_layout.addWidget(self.duration_spinbox)
        duration_layout.addStretch()
        settings_layout.addLayout(duration_layout)
        
        settings_layout.addWidget(QLabel("Supported formats: MP3, WAV, M4A, FLAC"))
        
        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)
        
        # Progress Group
        progress_group = QGroupBox("Step 3: Process & Results")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(QLabel("Progress:"))
        progress_layout.addWidget(self.progress_bar)
        
        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)
        
        # Log/Output Group
        log_group = QGroupBox("Log Output")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
        # Control buttons
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Splitting")
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px; border-radius: 4px;")
        self.start_btn.clicked.connect(self.start_splitting)
        self.start_btn.setMinimumHeight(40)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_splitting)
        self.stop_btn.setMinimumHeight(40)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        main_layout.addLayout(control_layout)
        
        # Add stretch at the end
        main_layout.addStretch()
    
    def _browse_folder(self):
        """Open folder dialog to select folder containing audio files."""
        start = str(Path.home())
        chosen = QFileDialog.getExistingDirectory(
            self,
            "Choose folder with audio files",
            start
        )
        if chosen:
            self.folder_path_input.setText(chosen)
            self._load_folder_contents()
    
    def _load_folder_contents(self):
        """Load and list audio files from the selected folder."""
        folder_path = self.folder_path_input.text().strip()
        self.file_list.clear()
        
        if not folder_path or not Path(folder_path).is_dir():
            return
        
        try:
            # List all audio files in the folder
            audio_extensions = {'.mp3', '.wav', '.m4a', '.flac'}
            audio_files = []
            
            for item in Path(folder_path).iterdir():
                if item.is_file() and item.suffix.lower() in audio_extensions:
                    audio_files.append(item.name)
            
            # Sort and add to list
            for filename in sorted(audio_files):
                full_path = Path(folder_path) / filename
                item = QListWidgetItem(filename)
                item.setData(Qt.ItemDataRole.UserRole, str(full_path))
                self.file_list.addItem(item)
            
            if audio_files:
                self.update_log(f"✓ Loaded {len(audio_files)} audio file(s) from {folder_path}")
            else:
                self.update_log(f"⚠ No audio files found in {folder_path}")
        except Exception as e:
            self.update_log(f"❌ Error loading folder: {str(e)}")
    
    def add_files(self):
        """Legacy method - use folder browser instead."""
        pass
    
    def clear_files(self):
        """Legacy method - use folder browser instead."""
        pass
    
    def update_log(self, message: str):
        """Update the log output."""
        self.log_text.append(message)
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def start_splitting(self):
        """Start the audio splitting process."""
        # Get selected files from the file list
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            self.update_log("❌ Error: No files selected!")
            return
        
        # Extract full paths from selected items
        selected_files = [
            item.data(Qt.ItemDataRole.UserRole) 
            for item in selected_items
        ]
        
        duration = self.duration_spinbox.value()
        
        self.log_text.clear()
        self.update_log(f"Starting audio splitting process...")
        self.update_log(f"Files to process: {len(selected_files)}")
        self.update_log(f"Split duration: {duration} minutes")
        self.update_log("-" * 50)
        
        # Disable buttons during processing
        self.start_btn.setEnabled(False)
        self.browse_folder_btn.setEnabled(False)
        self.folder_path_input.setEnabled(False)
        self.file_list.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # Create and start worker thread (thread creates its own processor)
        self.worker_thread = WorkerThread(selected_files, duration)
        self.worker_thread.progress_signal.connect(self.update_log)
        self.worker_thread.progress_update_signal.connect(self.progress_bar.setValue)  # Connect progress bar
        self.worker_thread.finished_signal.connect(self.on_splitting_finished)
        self.worker_thread.start()
    
    def on_splitting_finished(self, results: dict):
        """Handle completion of splitting process."""
        self.update_log("-" * 50)
        self.update_log(f"Processing complete!")
        self.update_log(f"Total files: {results['total']}")
        self.update_log(f"Successful: {results['successful']}")
        self.update_log(f"Failed: {results['failed']}")
        
        # Re-enable buttons
        self.start_btn.setEnabled(True)
        self.browse_folder_btn.setEnabled(True)
        self.folder_path_input.setEnabled(True)
        self.file_list.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        # Ensure progress bar is at 100
        self.progress_bar.setValue(100)
        
        # Clean up worker thread and force garbage collection
        self.worker_thread = None
        gc.collect()
    
    def stop_splitting(self):
        """Stop the splitting process."""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.update_log("⚠ Splitting process stopped by user.")
            
            # Re-enable buttons
            self.start_btn.setEnabled(True)
            self.browse_folder_btn.setEnabled(True)
            self.folder_path_input.setEnabled(True)
            self.file_list.setEnabled(True)
            self.stop_btn.setEnabled(False)


def main():
    """Main entry point for the application."""
    try:
        # Suppress warnings and potential debug output
        os.environ['QT_LOGGING_RULES'] = '*=false'
        
        # Try to create application
        try:
            app = QApplication(sys.argv)
        except Exception as app_err:
            print(f"Error creating QApplication: {app_err}", file=sys.stderr)
            print("This typically means there's a graphics/display issue.", file=sys.stderr)
            print("Try: export QT_QPA_PLATFORM=offscreen", file=sys.stderr)
            raise
        
        window = AudioSplitterApp()
        window.show()
        return_code = app.exec()
        
        if return_code != 0:
            print(f"Application exited with code {return_code}", file=sys.stderr)
        
        sys.exit(return_code)
        
    except Exception as e:
        print(f"\nError starting GUI application: {e}", file=sys.stderr)
        print(f"Error type: {type(e).__name__}", file=sys.stderr)
        
        # Print full traceback
        import traceback
        print("\nFull traceback:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        
        # Provide helpful suggestions
        print("\n" + "="*50, file=sys.stderr)
        print("SOLUTIONS:", file=sys.stderr)
        print("="*50, file=sys.stderr)
        print("1. Install Qt libraries (Ubuntu/Debian):", file=sys.stderr)
        print("   sudo apt-get install libqt6gui6 libqt6core6", file=sys.stderr)
        print("\n2. Try with environment variable:", file=sys.stderr)
        print("   export QT_QPA_PLATFORM=offscreen", file=sys.stderr)
        print("   python3 audio_splitter.py", file=sys.stderr)
        print("\n3. Use CLI version instead:", file=sys.stderr)
        print("   python3 audio_splitter_cli.py --help", file=sys.stderr)
        print("="*50 + "\n", file=sys.stderr)
        
        sys.exit(1)


if __name__ == "__main__":
    main()
