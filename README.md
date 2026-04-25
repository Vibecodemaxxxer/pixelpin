```
  ██████╗ ██╗██╗  ██╗███████╗██╗     ██████╗ ██╗███╗   ██╗
  ██╔══██╗██║╚██╗██╔╝██╔════╝██║    ██╔══██╗██║████╗  ██║
  ██████╔╝██║ ╚███╔╝ █████╗  ██║     ██████╔╝██║██╔██╗ ██║
  ██╔═══╝ ██║ ██╔██╗ ██╔══╝  ██║     ██╔═══╝ ██║██║╚██╗██║
  ██║     ██║██╔╝ ██╗███████╗███████╗██║     ██║██║ ╚████║
  ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚═╝╚═╝  ╚═══╝
```

**screen coordinate picker — hover, right-click, paste**

<p align="left">
  <img src="https://img.shields.io/badge/python-3.8%2B-blue?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square"/>
  <img src="https://img.shields.io/badge/license-MIT-orange?style=flat-square"/>
</p>

---

PixelPin is a minimal always-on-top overlay that shows the current cursor position in real time. Right-click anywhere on the screen to copy the coordinates to your clipboard.

## Usage

```bash
git clone https://github.com/AzeriVibecoder/pixelpin
cd pixelpin
pip install pynput
python pixelpin.py
```

| Action | Result |
|---|---|
| Move mouse | Live `x, y` shown above the cursor |
| Right-click | Coordinates copied to clipboard |
| `Esc` or middle-click | Quit |

The copied format is plain `x, y`.

## How it works

A borderless, transparent window follows the cursor across the entire screen without interfering with anything underneath. Mouse and keyboard events are captured globally via [pynput](https://github.com/moses-palmer/pynput), so the tool works regardless of which window is in focus. The clipboard is handled through tkinter's built-in API — no additional dependencies.

## Requirements

- Python 3.8+
- `pynput`
- `tkinter` — included in standard Python. On some Linux systems: `sudo apt install python3-tk`

## Platform notes

Tested on Windows and Linux (X11). On macOS, the system will prompt for Accessibility permissions on first run — pynput requires them to read global mouse events. Wayland support depends on the compositor.

## License

Apache-2.0 license
