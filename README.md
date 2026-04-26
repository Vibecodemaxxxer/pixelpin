```
  ██████╗ ██╗██╗  ██╗███████╗██╗      ██████╗ ██╗███╗   ██╗
  ██╔══██╗██║╚██╗██╔╝██╔════╝██║     ██╔══██╗██║████╗  ██║
  ██████╔╝██║ ╚███╔╝ █████╗  ██║      ██████╔╝██║██╔██╗ ██║
  ██╔═══╝ ██║ ██╔██╗ ██╔══╝  ██║      ██╔═══╝ ██║██║╚██╗██║
  ██║     ██║██╔╝ ██╗███████╗███████╗██║     ██║██║ ╚████║
  ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚═╝╚═╝  ╚═══╝
```

**Screen coordinate picker — hover, right-click, paste**

<p align="left">
  <img src="https://img.shields.io/badge/python-3.8%2B-blue?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square"/>
  <img src="https://img.shields.io/badge/license-Apache%202.0-orange?style=flat-square"/>
</p>

---

PixelPin is a minimal always-on-top overlay that shows the current cursor position in real time. Right-click anywhere on the screen to copy the coordinates to your clipboard, and optionally auto-save them to a text file.

```shell
git clone https://github.com/Vibecodemaxxxer/pixelpin
cd pixelpin
pip install pynput pystray Pillow
python pixelpin.py
```
### Default Controls

| Action      | Result                                       |
| ----------- | -------------------------------------------- |
| Move mouse  | Live x, y shown above the cursor             |
| Right-click | Copy coordinates to clipboard                |
| Tab         | Open settings menu                           |
| Esc         | Pause / resume overlay                       |
| Z           | Undo (removes the last saved line from file) |

The copied format is plain `x, y`.

Note: Copy and Undo triggers can be remapped to any key or mouse button in the Settings (Tab). To quit the app, use the system tray icon or the Settings menu.

## 📥 Download & Usage

Download the standalone version for your operating system:

- [🖥️ **Download for Windows**](https://github.com/Vibecodemaxxxer/pixelpin/releases/latest/download/PixelPin-windows-latest.zip)
- [🍎 **Download for macOS**](https://github.com/Vibecodemaxxxer/pixelpin/releases/latest/download/PixelPin-macos-latest.zip)
- [🐧 **Download for Linux**](https://github.com/Vibecodemaxxxer/pixelpin/releases/latest/download/PixelPin-ubuntu-latest.zip)

## Features

- **Live Tracking:** A borderless, transparent tooltip follows the cursor without interfering with windows underneath.
- **Auto-save & Undo:** Automatically append every copied coordinate to a .txt file. Make a mistake? Press Z to instantly delete the last entry.
- **Customizable Triggers:** Bind the copy and undo actions to any keyboard key or mouse button.
- **Pause Mode:** Hit Esc to freeze the overlay when you don't need it.
- **System Tray:** Runs quietly in the background. Right-click the tray icon to open settings or exit.
## How it works

Mouse and keyboard events are captured globally via [pynput](https://www.google.com/url?sa=E&q=https%3A%2F%2Fgithub.com%2Fmoses-palmer%2Fpynput), meaning the tool works regardless of which window is in focus. The clipboard and UI are handled through tkinter's built-in API. The system tray icon is managed via pystray and runs in a separate thread to ensure smooth performance.
## Requirements

- Python 3.8+
- pynput
- pystray
- Pillow
- tkinter — included in standard Python. On some Linux systems, you might need: sudo apt install python3-tk
## Platform notes

Tested on Windows and Linux (X11). On macOS, the system will prompt for Accessibility permissions on first run — pynput requires them to read global mouse events. Wayland support depends on the compositor.
## License

Apache-2.0 license
