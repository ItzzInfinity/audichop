# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AudioChop is a Python package (`audiochop/`) that splits audio files (MP3, WAV, M4A, FLAC) into fixed-duration segments and merges them back. It has no audio-processing dependencies in Python — **all audio work shells out to `ffmpeg`/`ffprobe`**, which must be on `PATH`. The only Python dependency is PyQt6, and only for the GUI.

The behavior is specified in `FSD.md` (Functionality Specification Document). When changing behavior, keep it consistent with the FSD, and update the FSD when the spec itself changes.

## Commands

There are no tests or linters configured. Verify changes by byte-compiling and running the CLIs:

```bash
python3 -m py_compile audiochop/*.py     # syntax check
python3 -m audiochop --help              # splitter CLI (via audiochop/__main__.py)
python3 -m audiochop.merge_cli --help    # merge CLI
python3 -m audiochop.launch              # GUI (falls back to CLI when no display)
pip install -e .                         # editable install; also provides audiochop / audiochop-gui / audiochop-merge scripts
```

`run.sh` is a user-facing bootstrap (installs requirements, launches the app) — not needed for development.

## Architecture

- `audiochop/processor.py` — core logic, UI-agnostic. `AudioProcessor` computes duration with `ffprobe`, then extracts each segment with one `ffmpeg -ss/-t -c:a copy` subprocess call (stream copy, no re-encode, low memory). It communicates with callers exclusively through three optional callbacks: `progress_callback(str)` for log lines, `segment_callback(file, n, total)` for progress-bar units, `cancel_callback() -> bool` for cooperative cancellation. Keep this module free of Qt and argparse imports.
- `audiochop/cli.py` — argparse front end; expands wildcards itself (quoted globs like `"*.mp3"`), optional `ThreadPoolExecutor` for file-level parallelism (`--threads`, capped at CPU cores − 2).
- `audiochop/gui.py` — PyQt6 window. `WorkerThread(QThread)` runs processing off the UI thread and bridges the processor callbacks to Qt signals (`progress_signal`, `progress_update_signal`, `finished_signal`); never touch widgets from the worker. Optional multithreading uses a `ThreadPoolExecutor` *inside* the QThread. Known issue (FSD "ISSUES"): enabling multithreading can crash the GUI.
- `audiochop/merge_cli.py` — standalone merge tool using ffmpeg's concat demuxer with stream copy; also exports `merge_audio_files()`.
- `audiochop/__init__.py` — public API re-exports (`AudioProcessor`, `split_audio_file`, `split_multiple_files`, `merge_audio_files`). Keep this in sync with the "Python API" section of README.md.
- `audiochop/__main__.py` / `audiochop/launch.py` — entry points: `python3 -m audiochop` → splitter CLI; `python3 -m audiochop.launch` → auto-detects a display and routes to GUI or CLI (`--gui`/`--cli` to force).

## Domain rules (from FSD.md — preserve these)

- Output goes to a folder named after the input file's stem, beside the source; segments are named `NN - <original name>.<ext>` where the zero-padding adapts to segment count (`01` < 100, `001` < 1000, `0001` otherwise).
- Files with duration ≤ 2× the split duration are **copied** (as `01 - name.ext`), not split. This rule is shared by GUI and CLI.
- Errors on one file must not abort the batch — log and continue.
- Merging preserves the user-supplied input order; default output is `<first-input-stem>_merged<ext>`.
- Cross-platform (Linux/macOS/Windows): use `pathlib`, no shell=True, no platform-specific paths.
