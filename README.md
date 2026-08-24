# 👻 Clippy for macOS

A lightweight, minimal, and fast clipboard manager for macOS built with Python and PySide6.

---

## ✨ Features

* **Global Hotkey:** Press `Cmd + Shift + V` anytime to toggle the clipboard window.
* **Smart Text & Image Capture:** Automatically saves copied text snippets, screenshot images, and image files from Finder/Desktop.
* **Instant Search:** Filter your text clipboard history in real-time.
* **Cursor Feedback:** Subtle dark popup notification next to your mouse when copying items back.
* **Minimalist UI:** Borderless dark-mode design that stays out of your way.
* **No Dock Icon:** Operates quietly in the background without cluttering your Dock.

---

## 💻 System Requirements & Compatibility

* **Pre-built Binary (`.dmg`):** macOS 11.0+ (Apple Silicon: M1 or newer)
* **From Source:** macOS (Apple Silicon & Intel), Windows, Linux

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

The pre-built `.dmg` release is packaged using **PyInstaller**. You can inspect the build configuration in the [`Clippy.spec`](./Clippy.spec) file included in the repository.

To build the executable yourself:
pip install pyinstaller
pyinstaller Clippy.spec

---

## 🗑 Uninstallation

To completely remove Clippy and clear all its cached data, configurations, and system permissions:

1. Open the downloaded `.dmg` image (or locate `uninstall.command` in the project folder).
2. Double-click **`uninstall.command`**.

---

## 🛠 Built With

* **Python 3**
* **PySide6** (Qt for Python)
* **pynput** (Global hotkey listener)

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).