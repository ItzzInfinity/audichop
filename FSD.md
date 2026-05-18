<!-- Functionality Specification Document (FSD) -->
# Audio File Splitter
1. need one script to split audio files into minutes defined by user a dropdown menu.
2. the script will check the path of the audio file and create a new folder with the same name as the audio file in the same directory.
3. the name will be same as the audio file but with a prefix
   1. for example, if the audio file is named "song.mp3" and the user selects to split it into 5-minute segments, the script will create a folder named "song" and save the split audio files as "01 - song.mp3", "02 - song.mp3", etc. in that folder.
   2. 01, 001, or 0001 can be used as the prefix depending on the total number of segments expected. For example, if the audio file is expected to be split into less than 100 segments, "01" can be used as the prefix. If it is expected to be split into more than 100 segments but less than 1000, "001" can be used. If it is expected to be split into more than 1000 segments, "0001" can be used.
4. the script will also handle cases where the audio file is shorter than the selected split duration, in which case it will simply copy the original file to the new folder without splitting.
5. the script will provide feedback to the user about the progress of the splitting process, such as displaying a progress bar or showing a message when the splitting is complete.
6. the script will also allow the user to select multiple audio files at once and split them all according to the same settings.
7. the script will be compatible with common audio file formats such as MP3, WAV, m4a and FLAC.
8. A GUI need to be created with pyqt6 to allow users to easily select audio files, choose the split duration from a dropdown menu, and start the splitting process. The GUI will also display the progress of the splitting process and any relevant messages to the user.
9. The script will use a reliable audio processing library, such as pydub or ffmpeg, to handle the splitting of audio files accurately and efficiently. The library will be chosen based on its compatibility with the supported audio formats and its ability to handle large audio files without significant performance issues.
10. The script will include error handling to manage potential issues such as unsupported file formats, read/write permissions, and other exceptions that may arise during the splitting process. The user will be informed of any errors through the GUI, and the script will attempt to continue processing other files if an error occurs with a specific file.
11. Script path "/home/itzzinfinity/Downloads/my_music/automation/split/"
12. Read `ssd_2_system.py` for QT GUI reference and implement the following features:
    1. create a textbox to show the selected audio file path which is editable and can be used to input the path directly and to the right of it a button to open the file dialog to select **folder** called *Browse*
    2. A Container area which will show the list of present audio files in the selected folder with a selection feature to select one or more files to split which can be implemented from `ssd_2_system.py`.
13. Implement Lower Memory Usage:
     1. Instead of loading the entire audio file into memory, the script will read and process the audio file in smaller chunks. This can be achieved by using a streaming approach or by utilizing libraries that support chunked processing of audio files.
     2. The script will also ensure that any temporary files created during the splitting process are properly managed and deleted after use to free up disk space.
     3. Additionally, the script will monitor memory usage during the splitting process and implement safeguards to prevent excessive memory consumption, such as limiting the number of concurrent processing threads or implementing a queue system for processing multiple files.
     4. Add one more button Select All and Deselect All to select or deselect all the audio files in the container area for splitting.
     5. Place the Log output All together to left side of the GUI 
     6. Make the Progress bar more Responsive as it currently does updated after the completion of each file, it should update after the completion of each segment to provide more real-time feedback to the user about the progress of the splitting process.
14. Implement Multithreading:
      1. The script will utilize multithreading to allow for concurrent processing of multiple audio files. This can be achieved by creating a thread pool and assigning each audio file to a separate thread for processing.
      2. The script will also implement synchronization mechanisms to ensure that shared resources, such as the progress bar or log messages, are properly managed across multiple threads.
      3. The user will have the option to enable or disable multithreading based on their system capabilities and preferences, allowing for flexibility in how the script is executed.
      4. In GUI please add a checkbox to enable or disable multithreading and based on the selection add a textbox to input the number of threads to be used for processing. The script will validate the user input to ensure that it is a positive integer and will provide feedback if the input is invalid. and also add a tooltip to the checkbox and the textbox to explain their functionality to the user. and also add a validation to ensure that the number of threads specified does not exceed n-2 where n is the total number of CPU cores available on the user's system. This will help prevent overloading the system and ensure optimal performance during the splitting process.
15. CLI Support:
       1. In addition to the GUI, the script will also support command-line interface (CLI) for users who prefer to use the terminal. The CLI will allow users to specify the audio file(s) to be split, the split duration, and other relevant options through command-line arguments.
       2. The CLI will provide clear instructions and feedback to the user, similar to the GUI, and will also include error handling to manage potential issues that may arise during the splitting process.
       3. The CLI will be designed to be user-friendly and accessible, allowing users of all levels of technical expertise to utilize the audio file splitter effectively.
       4. add a wildcard 
          1. where users can specify a pattern to match multiple audio files in the CLI. For example, users can use a pattern like `*.mp3` to select all MP3 files in a directory for splitting. The script will then process all files that match the specified pattern, providing feedback on the progress and results of the splitting process for each file.
          2. where one can check if the duration of the audio file is less than the 2x of the split duration, then it will simply copy the original file to the new folder without splitting. This can be implemented in both the GUI and CLI versions of the script, allowing for consistent behavior regardless of how the user chooses to interact with the audio file splitter.
16. GUI Redesign:
    1. Place Log Output to the left side of the GUI and make it resizable with dragging the divider between the log output and the file selection area. 
    2. Make the Selection area resizeable too.
17. Make a README_CLI.md file to explain how to use the CLI version of the script, including examples of command-line arguments and usage scenarios.
18. Make a README_GUI.md file to explain how to use the GUI version of the script, including step-by-step instructions and screenshots of the interface.
19. write a file audio_merge_cli.py to merge audio files from the command line, similar to the splitting functionality but in reverse, allowing users to combine multiple audio segments back into a single file.
    1.  It will combine multiple audio segments with the arguments provided by the user, such as the input files, output file name
    2.  merge_cli.py 1.m4a 2.m4a 3.m4a -o merged_song.m4a merge will be done in the order of the input files provided by the user and if no output file name is provided, it will default to the name of the first input file with a suffix "_merged" (e.g., "1_merged.m4a").
20. Finally The ultimate task :
    1. Make this a module / package that can be easily installed and imported into other projects. This will involve organizing the code into a structured format, creating setup files for installation, and ensuring that the module can be easily imported and used in other Python projects.
    2. Provide clear documentation for the module, including usage examples and API references, to help other developers understand how to use the functionality provided by the audio file splitter in their own projects. This documentation can be included in the README files or as separate documentation files within the package.
    3. For GUI `python3 -m audiochop.launch` and for CLI `python3 -m audiochop` can be used to launch the respective interfaces after the package is installed.
    4. Usage will look like `python3 -m audiochop.launch` opens GUI whereas `python3 -m audiochop ~/Downloads/1.m4a -d 20 -t 4` 
    5. want the shorter `python3 -m audiochop` (no .cli), so add a `__main__.py`:
       ```python
         # audiochop/__main__.py
         from audiochop.cli import main
         main()
       ```
21. Move all python files to audiochop/ directory.
22. Make it compatible with Windows, macOS, and Linux operating systems by ensuring that the script uses cross-platform libraries and handles file paths and system-specific features appropriately. This may involve using libraries like `os` and `pathlib` to manage file paths in a way that is compatible with different operating systems, as well as testing the script on multiple platforms to identify and address any compatibility issues that may arise. So I can add it to PyPI and make it available for installation via pip, allowing users on different operating systems to easily install and use the audio file splitter without worrying about compatibility issues.
# ISSUES
1. Enabling Multithreading is causing the GUI to crash - Need to implement proper thread management and synchronization to prevent crashes when multithreading is enabled. 