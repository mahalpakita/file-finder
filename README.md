## File Finder 

A fast, multi-threaded file search desktop app built with **Python + PySide6**.  
You can search by file  (with optional extension filters), highlight matches in the results, and package it as a standalone Windows .exe.

---

### Features

- **Instant file  search**
  - Type a file  (or part of it) and press **Enter** or click **Search**.
  - Optionally search the **entire PC** or a specific folder.
- **Case sensitivity toggle**
  - Switch between case-insensitive and case-sensitive matching.
- **Extension filters / presets**
  - Quick presets: **All**, **Images**, **Documents**, **Code**.
  - Or manually specify extensions 
- **Highlighted matches**
  - The matching part of each file  is highlighted in yellow.
- **Selectable/copyable results**
  - Result lines are selectable text, so you can easily copy full paths.
- **Modern dark UI**
  - Custom-styled dark theme with accent colors.

---

### Requirements

- **Python** 3.9+ (recommended)
- **Packages**:
  - `PySide6`

Install dependencies with:

```bash
pip install PySide6
```

If you prefer a virtual environment:

```bash
python -m venv .venv
.\.venv\Scripts\activate  # on Windows
pip install PySide6
```

---

### Project Structure

- `main.py` – main application window and search logic (threads, UI wiring).
- `design.py` – styling and loading overlay implementation.
- ` Jump.ico` – app icon (place this in the s  folder as `main.py`).
- ` lia-watson.gif` *(optional)* – animated GIF used by the loading overlay if present.

---

### Running from Source

1. Clone or download the project into a folder, e.g.  
   `C:\Users\My PC\Desktop\file finder`
2. Make sure `PySide6` is installed in your active Python environment.
3. From that folder, run:

```bash
python main.py
```

The File Finder window should open.

---

### Building a Windows EXE with PyInstaller

First, install **PyInstaller**:

```bash
pip install pyinstaller
```

Make sure ` Jump.ico` is in the s  folder as `main.py`, then from that folder run:

```bash
pyinstaller --noconsole --onefile --n  "FileFinder" --icon " Jump.ico" ^
  --add-data " Jump.ico;." main.py
```

Notes:

- `--noconsole` hides the console window.
- `--onefile` creates a single `FileFinder.exe`.
- `--icon " Jump.ico"` sets the **file icon** in Explorer.
- `--add-data " Jump.ico;."` bundles the icon so it can be used at runtime.

After the build completes, the EXE will be in:

```text
dist\FileFinder.exe
```

Double-click `FileFinder.exe` to run the app like a normal Windows program.

If you also use an animated GIF (e.g. ` lia-watson.gif`) for the loading overlay, add it as data too:

```bash
pyinstaller --noconsole --onefile --n  "FileFinder" --icon " Jump.ico" ^
  --add-data " Jump.ico;." --add-data " lia-watson.gif;." main.py
```

---

### Usage Tips

- **Enter to search**: Press **Enter** in the filen  box to start searching.
- **Whole PC vs folder**:
  - Check **“Search entire PC”** to scan all available drives.
  - Or uncheck it and choose a specific directory.
- **Extensions**:
  - Use presets for quick filtering, or type your own list like `py,txt,md`.
- **Copy results**:
  - Click into a result line, drag to select text, and press **Ctrl+C**.

---


### License

This project is provided as-is for personal / educational use.  
Replace this section with your preferred license if you intend to distribute it.


