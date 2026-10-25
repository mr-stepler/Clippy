# 👻 Clippy for macOS

A lightweight, minimal, and fast clipboard manager for macOS built with Python and PySide6.

---

## ✨ Features

* **Global Hotkey:** Press `Cmd + Shift + V` anytime to toggle the clipboard window. Settings warn about common macOS shortcut conflicts.
* **Smart Text & Image Capture:** Automatically saves copied text snippets, screenshot images, and image files from Finder/Desktop.
* **Instant Search & Type Filters:** Search text and links in real time; link search includes the URL and domain, plus the page title when link previews are enabled. Filter by All, Text, Images, or Links.
* **Opt-in Link Previews:** Fetch a copied page's title and favicon to recognize links; network requests are off by default.
* **Click-to-copy, no auto-paste:** Clicking a history item restores it to the system clipboard. Switch to the target app and paste manually with `Cmd + V`.
* **Cursor Feedback:** Subtle dark popup notification next to your mouse when copying items back.
* **Minimalist UI:** Borderless dark-mode design that stays out of your way.
* **No Dock Icon:** Operates quietly in the background without cluttering your Dock.

---

## 💻 System Requirements & Compatibility

* **Pre-built Binary (`.dmg`):** macOS 13+ (Apple Silicon: M1 or newer)
* **From Source:** macOS 13+ (Apple Silicon & Intel), Windows, Linux

---

## 🚀 Installation

1. Download **`Clippy.dmg`** from the [Releases](../../releases) section.
2. Open the `.dmg` image and drag **`Clippy.app`** into your **Applications** folder.
3. Grant required permissions:
   * Go to **System Settings → Privacy & Security**.
   * Enable **Clippy** under both **Accessibility** and **Input Monitoring**.

---

## 🔧 Running from Source

If you want to run the project locally or build it on other platforms:

1. **Clone the repository:**
   git clone https://github.com/mr-stepler/Clippy.git
   cd Clippy

2. **Create and activate a virtual environment:**
   python3 -m venv venv
   source venv/bin/activate

3. **Install dependencies:**
   pip install PySide6 pynput

4. **Run the app:**
   python app.py

---

## 📦 Build Specifications

The macOS `.app` and `.dmg` installer are built with **PyInstaller**. The workflow and script create the required `.icns` from the checked-in `icon.JPG`, package the app, and add an Applications shortcut to the disk image.

On an Apple Silicon Mac, install the build dependencies and run:

```bash
python3 -m pip install PyInstaller "PySide6==6.11.2" "pynput==1.8.1"
bash scripts/build_macos_dmg.sh
```

The outputs are `dist/Clippy.app` and `dist/Clippy.dmg`. The underlying PyInstaller configuration is in [`Clippy.spec`](./Clippy.spec).

---

## 🗑 Uninstallation

The uninstaller closes Clippy, removes its app bundle from `/Applications` or `~/Applications`, and deletes Clippy's local settings, pinned items, caches, and lock files. Removing the app from `/Applications` may trigger a macOS administrator authorization prompt.

1. Open the downloaded `.dmg` image (or locate `uninstall.command` in the project folder).
2. Double-click **`uninstall.command`** and review its output for any paths it could not remove.
3. macOS privacy permissions are managed separately: if desired, remove Clippy manually from **System Settings → Privacy & Security → Accessibility** and **Input Monitoring**.

---

## 🛠 Built With

* **Python 3**
* **PySide6** (Qt for Python)
* **pynput** (Global hotkey listener)

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
