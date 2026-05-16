#!/usr/bin/env python3
"""
Intelligent launcher for Audio File Splitter
Handles display issues and provides fallbacks.
"""

import sys
import os
from pathlib import Path


def has_display():
    """Check if a display server is available."""
    # Check DISPLAY variable on Linux/Unix
    if os.environ.get('DISPLAY'):
        return True
    
    # Check for Wayland on Linux
    if os.environ.get('WAYLAND_DISPLAY'):
        return True
    
    # Check for X11 socket on Linux
    if sys.platform.startswith('linux') and os.path.exists('/tmp/.X11-unix'):
        return True
    
    # macOS and Windows usually have displays
    if sys.platform == 'darwin' or sys.platform == 'win32':
        return True
    
    return False


def main():
    """Main entry point - route to GUI or CLI based on environment."""
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check command line arguments
    force_cli = '--cli' in sys.argv
    force_gui = '--gui' in sys.argv
    
    # Remove our special flags from argv before passing to submodules
    clean_argv = [arg for arg in sys.argv if arg not in ['--cli', '--gui']]
    sys.argv = clean_argv
    
    display_available = has_display()
    use_cli = force_cli or (not display_available and not force_gui)
    
    # Route to appropriate launcher
    if use_cli:
        # Use CLI version - import and run
        from audio_splitter_cli import main as cli_main
        cli_main()
    else:
        # Use GUI version - import and run
        from audio_splitter import main as gui_main
        gui_main()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except SystemExit as e:
        # Re-raise SystemExit to maintain proper exit codes
        sys.exit(e.code if e.code is not None else 0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)



