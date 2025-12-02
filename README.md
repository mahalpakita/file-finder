## File Finder (AmeJump Edition)

A fast, multi-threaded file search desktop app built with **Python + PySide6**.  
You can search by filename (with optional extension filters), highlight matches in the results, and package it as a standalone Windows `.exe` with a custom AmeJump icon.

---

### Features

- **Instant filename search**
  - Type a filename (or part of it) and press **Enter** or click **Search**.
  - Optionally search the **entire PC** or a specific folder.
- **Case sensitivity toggle**
  - Switch between case-insensitive and case-sensitive matching.
- **Extension filters / presets**
  - Quick presets: **All**, **Images**, **Documents**, **Code**.
  - Or manually specify extensions (e.g. `py,txt,pdf`).
- **Highlighted matches**
  - The matching part of each filename is highlighted in yellow.
- **Selectable / copyable results**
  - Result lines are selectable text, so you can easily copy full paths.
- **Modern dark UI**
  - Custom-styled dark theme with accent colors.
- **Packaged EXE**
  - Can be built into a single-file `.exe` with a custom `AmeJump.ico` icon.

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
- `AmeJump.ico` – app icon (place this in the same folder as `main.py`).
- `amelia-watson.gif` *(optional)* – animated GIF used by the loading overlay if present.

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

Make sure `AmeJump.ico` is in the same folder as `main.py`, then from that folder run:

```bash
pyinstaller --noconsole --onefile --name "FileFinder" --icon "AmeJump.ico" ^
  --add-data "AmeJump.ico;." main.py
```

Notes:

- `--noconsole` hides the console window.
- `--onefile` creates a single `FileFinder.exe`.
- `--icon "AmeJump.ico"` sets the **file icon** in Explorer.
- `--add-data "AmeJump.ico;."` bundles the icon so it can be used at runtime.

After the build completes, the EXE will be in:

```text
dist\FileFinder.exe
```

Double-click `FileFinder.exe` to run the app like a normal Windows program.

If you also use an animated GIF (e.g. `amelia-watson.gif`) for the loading overlay, add it as data too:

```bash
pyinstaller --noconsole --onefile --name "FileFinder" --icon "AmeJump.ico" ^
  --add-data "AmeJump.ico;." --add-data "amelia-watson.gif;." main.py
```

---

### Usage Tips

- **Enter to search**: Press **Enter** in the filename box to start searching.
- **Whole PC vs folder**:
  - Check **“Search entire PC”** to scan all available drives.
  - Or uncheck it and choose a specific directory.
- **Extensions**:
  - Use presets for quick filtering, or type your own list like `py,txt,md`.
- **Copy results**:
  - Click into a result line, drag to select text, and press **Ctrl+C**.

---

### Troubleshooting

- **Imports not resolved in IDE**  
  Ensure your editor is using the same Python interpreter where you ran:

  ```bash
  pip install PySide6
  ```

- **Icon not visible in EXE**  
  - Confirm `AmeJump.ico` exists next to `main.py`.
  - Rebuild the EXE with `--icon` **and** `--add-data "AmeJump.ico;."`.

---

### License

This project is provided as-is for personal / educational use.  
Replace this section with your preferred license if you intend to distribute it.


