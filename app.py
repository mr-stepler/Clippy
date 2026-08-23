import fcntl
import importlib
import sys

from pynput import keyboard
from PySide6.QtCore import QMimeData, QObject, QPoint, QSize, QThread, QTimer, QUrl, Qt, Signal
from PySide6.QtGui import QCursor, QIcon, QImage, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Enforce single instance execution using a lock file
lock_file = "/tmp/Clippy.lock"
try:
    lock_file_fd = open(lock_file, "w")
    fcntl.lockf(lock_file_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
except (IOError, OSError):
    sys.exit(0)

# Hide application icon from the macOS Dock (Agent Application mode)
if sys.platform == "darwin":
    try:
        appkit = importlib.import_module("AppKit")
        ns_app = getattr(appkit, "NSApplication")
        ns_policy = getattr(appkit, "NSApplicationActivationPolicyAccessory")
        app_native = ns_app.sharedApplication()
        app_native.setActivationPolicy_(ns_policy)
    except (ImportError, AttributeError):
        pass


class HotkeySignal(QObject):
    """Signal emitter for thread-safe UI interactions from pynput listener."""
    triggered = Signal()


class HotkeyListenerThread(QThread):
    """Background thread listening for the global shortcut (Cmd + Shift + V)."""

    def __init__(self, hk_signal):
        super().__init__()
        self.signal = hk_signal
        self.listener = None

    def run(self):
        try:
            hotkeys = {'<cmd>+<shift>+v': self.on_triggered}
            with keyboard.GlobalHotKeys(hotkeys) as listener:
                self.listener = listener
                listener.join()
        except (KeyError, ValueError, RuntimeError) as e:
            print(f"[ERROR] pynput listener: {e}")

    def on_triggered(self):
        self.signal.triggered.emit()

    def stop(self):
        if self.listener:
            self.listener.stop()
        self.quit()
        self.wait()


class ClipboardApp(QWidget):
    """Main application window for managing clipboard history."""

    MAX_HISTORY = 100

    def __init__(self, thread_instance):
        super().__init__()
        self.listener_thread = thread_instance
        self.history = []
        self.last_clip_text = ""
        self.last_image_key = None
        self.drag_position = QPoint()

        # UI Widget declarations
        self.search_bar = None
        self.clear_btn = None
        self.close_btn = None
        self.list_widget = None
        self.toast_label = None

        # Native Qt clipboard instance
        self.clipboard = QApplication.clipboard()

        self.init_ui()

        # Timer polling for system clipboard changes
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_clipboard)
        self.timer.start(800)

        # Timer for hiding toast notifications
        self.toast_timer = QTimer(self)
        self.toast_timer.setSingleShot(True)
        self.toast_timer.timeout.connect(self.hide_toast)

    def init_ui(self):
        """Build and style the application interface."""
        self.setWindowTitle("Clippy")

        window_flags = (
                Qt.WindowType.Window
                | Qt.WindowType.FramelessWindowHint
                | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setWindowFlags(window_flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(340, 500)

        # Dark theme styling matching dark grey popup UI
        self.setStyleSheet("""
            QWidget#MainFrame { 
                background-color: #1e1e1e; 
                border-radius: 12px; 
                border: 1px solid #333333; 
            }
            QLineEdit { 
                background-color: #2d2d2d; 
                color: #ffffff; 
                border: 1px solid #3c3c3c; 
                border-radius: 6px; 
                padding: 6px 10px; 
                font-size: 13px; 
            }
            QLineEdit:focus { border: 1px solid #007acc; }
            QPushButton { 
                background-color: #2d2d2d; 
                color: #aaaaaa; 
                border: 1px solid #3c3c3c; 
                border-radius: 6px; 
                padding: 6px 12px; 
                font-size: 12px; 
            }
            QPushButton:hover { background-color: #383838; color: #ffffff; }
            QPushButton#CloseBtn {
                background-color: transparent;
                color: #888888;
                border: none;
                font-size: 16px;
                font-weight: bold;
                padding: 2px 6px;
            }
            QPushButton#CloseBtn:hover {
                color: #ff5555;
                background-color: #2d2d2d;
            }
            QListWidget { 
                background-color: #252526; 
                color: #cccccc; 
                border: 1px solid #333333; 
                border-radius: 6px; 
                outline: none; 
            }
            QListWidget::item { 
                padding: 8px; 
                border-bottom: 1px solid #2d2d2d; 
                border-radius: 4px; 
            }
            QListWidget::item:hover { 
                background-color: #2a2d2e; 
                color: #ffffff; 
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        container = QWidget(self)
        container.setObjectName("MainFrame")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(18, 18, 18, 18)

        # Top control bar
        top_layout = QHBoxLayout()
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.textChanged.connect(self.perform_search)
        top_layout.addWidget(self.search_bar)

        self.clear_btn = QPushButton("Clear", self)
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.clicked.connect(self.clear_history)
        top_layout.addWidget(self.clear_btn)

        # Close button to terminate the application
        self.close_btn = QPushButton("✕", self)
        self.close_btn.setObjectName("CloseBtn")
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setToolTip("Quit Clippy")
        self.close_btn.clicked.connect(QApplication.quit)
        top_layout.addWidget(self.close_btn)

        container_layout.addLayout(top_layout)

        # History list widget
        self.list_widget = QListWidget(self)
        self.list_widget.setIconSize(QSize(40, 40))
        self.list_widget.itemClicked.connect(self.paste_selected)
        self.list_widget.setVerticalScrollMode(
            QAbstractItemView.ScrollMode.ScrollPerPixel
        )
        self.list_widget.verticalScrollBar().setSingleStep(8)
        self.list_widget.setWordWrap(False)
        self.list_widget.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.list_widget.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        container_layout.addWidget(self.list_widget)
        main_layout.addWidget(container)
        self.setLayout(main_layout)

        # Small dark toast overlay next to cursor
        self.toast_label = QLabel("copied!", self)
        self.toast_label.setWindowFlags(
            Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.toast_label.setStyleSheet("""
            QLabel {
                background-color: #2d2d2d;
                color: #cccccc;
                border: 1px solid #3c3c3c;
                border-radius: 5px;
                padding: 4px 8px;
                font-size: 11px;
            }
        """)
        self.toast_label.hide()

    def show_toast(self, message="copied!"):
        """Show a small dark popup right next to the mouse cursor."""
        self.toast_label.setText(message)
        self.toast_label.adjustSize()

        cursor_pos = QCursor.pos()
        self.toast_label.move(cursor_pos.x() + 15, cursor_pos.y() + 15)
        self.toast_label.show()

        self.toast_timer.start(1000)

    def hide_toast(self):
        """Hide the mouse overlay popup."""
        self.toast_label.hide()

    def mousePressEvent(self, event):
        """Capture mouse position for window dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = (
                    event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event):
        """Drag window framelessly across the screen."""
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def check_clipboard(self):
        """Poll the clipboard to detect new text, rich text (HTML), or images."""
        mime_data = self.clipboard.mimeData()
        if mime_data is None:
            return

        # 1. Handle copied image files from Desktop or Finder
        if mime_data.hasUrls():
            urls = mime_data.urls()
            if urls and urls[0].isLocalFile():
                file_path = urls[0].toLocalFile()
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif')):
                    if file_path != self.last_image_key:
                        image = QImage(file_path)
                        if not image.isNull():
                            self.last_image_key = file_path
                            self.last_clip_text = ""

                            self.history = [
                                item for item in self.history
                                if item.get("path") != file_path
                            ]
                            self.history.insert(0, {"type": "image", "data": image, "path": file_path})

                            if len(self.history) > self.MAX_HISTORY:
                                self.history.pop()

                            if not self.search_bar.text().strip():
                                self.update_list()
                    return

        # 2. Handle screenshots from memory
        if mime_data.hasImage():
            image: QImage = self.clipboard.image()
            if not image.isNull():
                img_bytes = image.bits().tobytes()
                img_key = (image.width(), image.height(), len(img_bytes), hash(img_bytes[:1000]))

                if img_key != self.last_image_key:
                    self.last_image_key = img_key
                    self.last_clip_text = ""

                    self.history = [
                        item for item in self.history
                        if item["type"] != "image" or item.get("key") != img_key
                    ]
                    self.history.insert(0, {"type": "image", "data": image, "key": img_key})

                    if len(self.history) > self.MAX_HISTORY:
                        self.history.pop()

                    if not self.search_bar.text().strip():
                        self.update_list()

        # 3. Handle text with formatting (HTML + plain text fallback)
        elif mime_data.hasText():
            text = self.clipboard.text().strip()
            if not text:
                return

            html_text = mime_data.html() if mime_data.hasHtml() else ""

            # Use unique identifier based on text content to avoid duplicates
            if text != self.last_clip_text:
                self.last_clip_text = text
                self.last_image_key = None

                self.history = [
                    item for item in self.history
                    if item["type"] != "text" or item["data"] != text
                ]
                self.history.insert(0, {
                    "type": "text",
                    "data": text,
                    "html": html_text
                })

                if len(self.history) > self.MAX_HISTORY:
                    self.history.pop()

                if not self.search_bar.text().strip():
                    self.update_list()

    def _add_item_to_widget(self, item):
        """Helper to create and insert item into QListWidget."""
        if item["type"] == "text":
            text_data = item["data"]
            display_text = " ".join(text_data.split())
            widget_item = QListWidgetItem(display_text)
            widget_item.setData(Qt.ItemDataRole.UserRole, item)
            self.list_widget.addItem(widget_item)
        elif item["type"] == "image":
            image: QImage = item["data"]
            pixmap = QPixmap.fromImage(image)
            icon_pixmap = pixmap.scaled(
                80, 80,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            widget_item = QListWidgetItem(" [Image / Screenshot]")
            widget_item.setIcon(QIcon(icon_pixmap))
            widget_item.setData(Qt.ItemDataRole.UserRole, item)
            self.list_widget.addItem(widget_item)

    def update_list(self):
        """Rebuild list widget with current history."""
        self.list_widget.clear()
        for item in self.history:
            self._add_item_to_widget(item)

    def perform_search(self, text):
        """Filter list items dynamically based on search input."""
        self.list_widget.clear()
        text_clean = text.lower().strip()

        if not text_clean:
            self.update_list()
            return

        for item in self.history:
            if item["type"] == "text" and text_clean in item["data"].lower():
                self._add_item_to_widget(item)

    def clear_history(self):
        """Wipe saved history and clear current clipboard."""
        self.history.clear()
        self.last_clip_text = ""
        self.last_image_key = None
        self.clipboard.clear()
        self.list_widget.clear()

    def paste_selected(self, list_item):
        """Copy selected item back to system clipboard with preserved formatting."""
        item = list_item.data(Qt.ItemDataRole.UserRole)
        if not item:
            return

        if item["type"] == "text":
            text = item["data"]
            html = item.get("html", "")
            self.last_clip_text = text
            self.last_image_key = None

            # Restore both plain text and rich text formatting (HTML)
            mime = QMimeData()
            mime.setText(text)
            if html:
                mime.setHtml(html)
            self.clipboard.setMimeData(mime)

        elif item["type"] == "image":
            image: QImage = item["data"]
            if "path" in item:
                self.last_image_key = item["path"]
                new_mime = QMimeData()
                new_mime.setUrls([QUrl.fromLocalFile(item["path"])])
                new_mime.setImageData(image)
                self.clipboard.setMimeData(new_mime)
            else:
                self.last_image_key = item.get("key")
                self.clipboard.setImage(image)
            self.last_clip_text = ""

        self.show_toast("copied!")

    def toggle_window(self):
        """Toggle window visibility strictly on shortcut call."""
        if self.isVisible():
            self.hide()
        else:
            self.search_bar.clear()
            self.update_list()
            self.show()
            self.raise_()
            self.activateWindow()
            self.search_bar.setFocus()

    def keyPressEvent(self, event):
        """Hide window on Escape key press."""
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """Clean up background listener thread on app exit."""
        if self.listener_thread:
            self.listener_thread.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    hotkey_signal = HotkeySignal()
    listener_thread = HotkeyListenerThread(hotkey_signal)

    window = ClipboardApp(thread_instance=listener_thread)
    hotkey_signal.triggered.connect(window.toggle_window)

    listener_thread.start()
    app.aboutToQuit.connect(listener_thread.stop)

    sys.exit(app.exec())