import sys
from pathlib import Path
from PySide6.QtCore import QThread, Signal, Qt
import os
import time
import queue
import concurrent.futures
import threading
import re
import html

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QListWidget, QListWidgetItem, QLabel,
    QFileDialog, QCheckBox, QMessageBox, QComboBox, QSizePolicy
)
from PySide6.QtGui import QFont, QColor, QPainter
from PySide6.QtCore import QTimer, QRect
from design import generate_stylesheet

# LoadingOverlay and stylesheet generation live in `design.py`.

class FileSearchThread(QThread):
    found_file = Signal(str)
    finished = Signal()

    def __init__(self, search_path, filename, case_sensitive=False, allowed_exts=None):
        super().__init__()
        self.search_path = search_path
        self.filename = filename
        self._stop_event = threading.Event()
        self.case_sensitive = bool(case_sensitive)
        # allowed_exts: set of normalized extensions without dot (e.g. {'py', 'txt'}) or None
        if allowed_exts:
            try:
                self.allowed_exts = set(e.strip().lstrip('.').lower() for e in allowed_exts if e and e.strip())
            except Exception:
                self.allowed_exts = None
        else:
            self.allowed_exts = None

    def run(self):
        # normalize search_path to a list of roots
        if isinstance(self.search_path, (list, tuple)):
            roots = list(self.search_path)
        else:
            roots = [self.search_path]

        try:
            # Prepare target according to case-sensitivity
            target = self.filename if self.case_sensitive else self.filename.lower()

            # Use a thread-pool with a shared queue for directories.
            dir_queue = queue.Queue()
            # enqueue all provided roots
            for root in roots:
                try:
                    dir_queue.put(root)
                except Exception:
                    continue

            def worker():
                while True:
                    # Check cancellation first
                    if self._stop_event.is_set():
                        break
                    try:
                        # Use timeout so we can react to cancellation
                        dirpath = dir_queue.get(timeout=0.5)
                        if dirpath is None:
                            dir_queue.task_done()
                            break
                        try:
                            with os.scandir(dirpath) as it:
                                for entry in it:
                                    try:
                                        if entry.is_dir(follow_symlinks=False):
                                            # schedule directory for scanning
                                            dir_queue.put(entry.path)
                                        elif entry.is_file(follow_symlinks=False):
                                            name_to_check = entry.name if self.case_sensitive else entry.name.lower()
                                            if target and (target in name_to_check):
                                                # apply extension filter if provided
                                                if self.allowed_exts:
                                                    ext = os.path.splitext(entry.name)[1].lower().lstrip('.')
                                                    if ext not in self.allowed_exts:
                                                        continue
                                                self.found_file.emit(entry.path)
                                    except PermissionError:
                                        continue
                        except (PermissionError, FileNotFoundError):
                            # skip directories that can't be accessed or vanish
                            pass
                        finally:
                            try:
                                dir_queue.task_done()
                            except Exception:
                                pass
                    except queue.Empty:
                        # Timeout allows loop to re-check stop event
                        continue
                    except Exception:
                        # Guard worker loop from unexpected exceptions
                        try:
                            dir_queue.task_done()
                        except Exception:
                            pass

            max_workers = min(32, (os.cpu_count() or 1) * 2)
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # start worker tasks
                futures = [executor.submit(worker) for _ in range(max_workers)]

                # Wait until queue appears idle or cancellation requested
                while True:
                    if self._stop_event.is_set():
                        break
                    # give workers a moment to enqueue more directories
                    if dir_queue.empty():
                        time.sleep(0.5)
                        if dir_queue.empty():
                            break
                    else:
                        time.sleep(0.1)

                # stop workers
                for _ in range(max_workers):
                    dir_queue.put(None)
                # ensure workers finish
                concurrent.futures.wait(futures)

        except Exception as e:
            self.found_file.emit(f"Error: {e}")
        finally:
            self.finished.emit()

    def request_cancel(self):
        """Signal the running search to stop as soon as possible."""
        try:
            self._stop_event.set()
        except Exception:
            pass


class FileFinderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Finder")
        self.setGeometry(100, 100, 820, 560)
        self.search_thread = None
        self._result_count = 0
        self._search_start_time = None
        # keep attribute to avoid AttributeError when referenced elsewhere
        self.loading_overlay = None

        # Theme colors
        self.accent1 = '#F8DB92'
        self.accent2 = '#F7DA91'

        # Apply initial stylesheet (light mode)
        self.apply_theme()

        # Layout
        widget = QWidget()
        layout = QVBoxLayout()

        # Top bar (dark theme only)
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(8, 8, 8, 4)
        top_bar.setSpacing(8)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        # Search input
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(8, 8, 8, 8)
        search_layout.setSpacing(6)
        search_layout.addWidget(QLabel("File name:"))
        self.search_input = QLineEdit()
        self.search_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        search_layout.addWidget(self.search_input)
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.start_search)

        # Folder selector + Browse
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Select folder or leave blank for C:\\")
        self.path_input.setMinimumWidth(300)
        self.path_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        search_layout.addWidget(self.path_input)

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_folder)
        search_layout.addWidget(self.browse_button)

        # Checkbox to search whole PC
        self.entire_pc_checkbox = QCheckBox("Search entire PC")
        self.entire_pc_checkbox.stateChanged.connect(self.on_entire_pc_toggled)
        search_layout.addWidget(self.entire_pc_checkbox)
        
        # Case sensitivity option
        self.case_sensitive_checkbox = QCheckBox("Case sensitive")
        self.case_sensitive_checkbox.setChecked(False)
        search_layout.addWidget(self.case_sensitive_checkbox)
        
        # Preset filter dropdown (All / Images / Documents / Code)
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["All", "Images", "Documents", "Code"])
        self.preset_combo.currentIndexChanged.connect(self.on_preset_changed)
        search_layout.addWidget(self.preset_combo)

        # File type filter (extensions)
        self.ext_input = QLineEdit()
        self.ext_input.setPlaceholderText("(e.g. py,txt) - leave blank for all")
        self.ext_input.setMaximumWidth(180)
        self.ext_input.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        search_layout.addWidget(self.ext_input)
        search_layout.addWidget(self.search_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_search)
        search_layout.addWidget(self.cancel_button)
        layout.addLayout(search_layout)
        # make the results list expand to fill available space
        layout.setStretchFactor(search_layout, 0)

        # Results list
        self.results_label = QLabel("Results:")
        self.results_label.setStyleSheet("font-weight: bold; color: #333333;")
        layout.addWidget(self.results_label)
        self.results_list = QListWidget()
        self.results_list.setAlternatingRowColors(True)
        layout.addWidget(self.results_list)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #555555; font-size: 10pt; padding: 4px;")
        layout.addWidget(self.status_label)

        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
        # Loading overlay removed — no animation while searching.

    def start_search(self):
        filename = self.search_input.text().strip()
        if not filename:
            return

        # Validate extensions input (if any) before starting
        ext_text = self.ext_input.text().strip() if getattr(self, 'ext_input', None) else ''
        try:
            allowed_exts = self.parse_extensions(ext_text) if ext_text else None
        except ValueError as e:
            QMessageBox.warning(self, "Invalid extensions", str(e))
            return

        self.results_list.clear()
        self.search_button.setEnabled(False)
        self.search_button.setText("Searching...")
        self._result_count = 0
        self._search_start_time = time.time()
        self.status_label.setText("Searching...")

        # Determine search roots: either user-selected folder or whole PC
        # Remember case sensitivity for the UI/highlighting
        case_sensitive = bool(self.case_sensitive_checkbox.isChecked())

        if self.entire_pc_checkbox.isChecked():
            # enumerate existing drive roots A:\ .. Z:\
            roots = []
            for letter in map(chr, range(ord('A'), ord('Z') + 1)):
                root = f"{letter}:\\"
                if os.path.exists(root):
                    roots.append(root)
            if not roots:
                # fallback to C:\ if nothing found
                roots = ["C:\\"]
            self.search_thread = FileSearchThread(roots, filename, case_sensitive=case_sensitive, allowed_exts=allowed_exts)
        else:
            path_text = self.path_input.text().strip()
            if path_text:
                root = path_text
            else:
                root = "C:\\"
            self.search_thread = FileSearchThread(str(root), filename, case_sensitive=case_sensitive, allowed_exts=allowed_exts)
        self.search_thread.found_file.connect(self.add_result)
        self.search_thread.finished.connect(self.on_search_finished)
        self.search_thread.start()
        self.cancel_button.setEnabled(True)
        
        # Show loading overlay
        if self.loading_overlay:
            self.loading_overlay.setGeometry(self.rect())
            self.loading_overlay.show()
            self.loading_overlay.raise_()

    def browse_folder(self):
        try:
            folder = QFileDialog.getExistingDirectory(self, "Select folder", str(Path.home()))
            if folder:
                self.path_input.setText(folder)
        except Exception:
            # ignore dialog errors
            pass

    def on_entire_pc_toggled(self, state):
        # When searching entire PC, disable manual path selection
        try:
            checked = bool(state)
        except Exception:
            checked = False
        self.path_input.setEnabled(not checked)
        self.browse_button.setEnabled(not checked)

    def on_preset_changed(self, index):
        # Populate ext_input based on preset selection
        try:
            preset = self.preset_combo.currentText()
            if preset == "All":
                self.ext_input.setText("")
            elif preset == "Images":
                self.ext_input.setText("png,jpg,jpeg,gif,bmp,webp")
            elif preset == "Documents":
                self.ext_input.setText("pdf,doc,docx,xls,xlsx,txt,odt")
            elif preset == "Code":
                self.ext_input.setText("py,js,java,cpp,c,h,cs,ts,rb,go,rs,html,css")
        except Exception:
            pass

    def parse_extensions(self, text: str):
        """Parse and validate a comma-separated extensions string.

        Returns a list of normalized extensions (without dots) or raises ValueError.
        """
        if not text:
            return None
        parts = [p.strip().lstrip('.') for p in text.split(',') if p.strip()]
        if not parts:
            return None
        invalid = []
        for p in parts:
            # allow alphanumeric extensions only
            if not re.fullmatch(r'[A-Za-z0-9]+', p):
                invalid.append(p)
        if invalid:
            raise ValueError(f"Invalid extension(s): {', '.join(invalid)}\nUse comma-separated alphanumeric extensions, e.g. 'py,txt'")
        return parts

    def add_result(self, filepath):
        # Create a rich-text label with highlighted matches and add as an item widget
        try:
            orig = filepath
            esc = html.escape(orig)
            search_text = self.search_input.text()
            html_text = esc

            if search_text:
                pattern = re.escape(search_text)
                flags = 0 if (getattr(self, 'case_sensitive_checkbox', None) and self.case_sensitive_checkbox.isChecked()) else re.IGNORECASE
                try:
                    if flags & re.IGNORECASE:
                        matches = list(re.finditer(pattern, orig, flags=re.IGNORECASE))
                    else:
                        matches = list(re.finditer(pattern, orig))

                    if matches:
                        parts = []
                        last = 0
                        for m in matches:
                            s, e = m.start(), m.end()
                            parts.append(html.escape(orig[last:s]))
                            parts.append(f"<span class=\"match\">{html.escape(orig[s:e])}</span>")
                            last = e
                        parts.append(html.escape(orig[last:]))
                        html_text = "".join(parts)
                    else:
                        html_text = esc
                except re.error:
                    html_text = esc

            item = QListWidgetItem()
            label = QLabel()
            label.setTextFormat(Qt.RichText)
            label.setText(html_text)
            label.setToolTip(filepath)
            label.setWordWrap(False)
            self.results_list.addItem(item)
            self.results_list.setItemWidget(item, label)

            # Keep a running count and update status so user sees progress
            self._result_count += 1
            self.status_label.setText(f"Found: {self._result_count}")
        except Exception:
            # fallback to plain item if anything goes wrong
            try:
                self.results_list.addItem(QListWidgetItem(filepath))
            except Exception:
                pass

    def on_search_finished(self):
        self.search_button.setEnabled(True)
        self.search_button.setText("Search")
        self.cancel_button.setEnabled(False)
        # Hide loading overlay
        if self.loading_overlay:
            self.loading_overlay.stop()
            self.loading_overlay.hide()
        # Show final status with elapsed time and total results
        try:
            elapsed = time.time() - (self._search_start_time or time.time())
            self.status_label.setText(f"Search finished: {self._result_count} result(s) in {elapsed:.1f}s")
        except Exception:
            self.status_label.setText("Search finished")

    def cancel_search(self):
        # Cooperative cancellation: signal the search thread to stop
        if self.search_thread:
            try:
                self.search_thread.request_cancel()
                self.status_label.setText("Cancelling...")
                self.cancel_button.setEnabled(False)
                # Hide loading overlay on cancel
                if self.loading_overlay:
                    self.loading_overlay.stop()
                    self.loading_overlay.hide()
            except Exception:
                pass

    def apply_theme(self):
        """Apply light or dark theme based on self.dark_mode flag."""
        app_css, label_color = generate_stylesheet(self.accent1, self.accent2)
        self.setStyleSheet(app_css)
        # Update label colors dynamically
        try:
            self.results_label.setStyleSheet(f"color: {label_color};")
            self.status_label.setStyleSheet(f"color: {label_color};")
        except Exception:
            pass

    def toggle_dark_mode(self):
        """Toggle between light and dark mode."""
        # Theme toggling removed; only dark theme supported now.
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FileFinderApp()
    window.show()
    sys.exit(app.exec())