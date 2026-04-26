import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import sys
import threading
from pynput import mouse as pmouse, keyboard as pkeyboard
import pystray
from PIL import Image, ImageDraw

if getattr(sys, 'frozen', False): 
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(BASE_DIR, "pixelpin_config.json")
# ----------------------------------------------------------

DEFAULT_CONFIG = {
    "copy_trigger": "mouse:right",
    "undo_trigger": "key:z",
    "autosave_enabled": False,
    "autosave_path": "",
    "onboarding_shown": False,
}

BANNER = r"""
  ██████╗ ██╗██╗  ██╗███████╗██╗     ██████╗ ██╗███╗   ██╗
  ██╔══██╗██║╚██╗██╔╝██╔════╝██║     ██╔══██╗██║████╗  ██║
  ██████╔╝██║ ╚███╔╝ █████╗  ██║     ██████╔╝██║██╔██╗ ██║
  ██╔═══╝ ██║ ██╔██╗ ██╔══╝  ██║     ██╔═══╝ ██║██║╚██╗██║
  ██║     ██║██╔╝ ██╗███████╗███████╗██║     ██║██║ ╚████║
  ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚═╝╚═╝  ╚═══╝
"""

MENU_HINT = """  ┌──────────────────────────────────────────────┐
  │   move mouse    →   live coordinates         │
  │   right-click   →   copy to clipboard        │
  │   Tab           →   settings                 │
  │   Esc           →   pause / resume           │
  └──────────────────────────────────────────────┘
"""

BG      = "#0a0a0a"
FG      = "#00ff88"
FG_DIM  = "#555555"
ACCENT  = "#ffff00"
ORANGE  = "#ff8800"
FONT    = ("Consolas", 10)
FONT_B  = ("Consolas", 10, "bold")

CYRILLIC_TO_LATIN = {
    'й':'q','ц':'w','у':'e','к':'r','е':'t','н':'y','г':'u','ш':'i','щ':'o','з':'p',
    'х':'[','ъ':']','ф':'a','ы':'s','в':'d','а':'f','п':'g','р':'h','о':'j','л':'k',
    'д':'l','ж':';','э':"'",'я':'z','ч':'x','с':'c','м':'v','и':'b','т':'n','ь':'m',
}

def normalize_char(ch):
    if not ch or len(ch) != 1: return ch
    return CYRILLIC_TO_LATIN.get(ch.lower(), ch.lower())

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                data = json.load(f)
            cfg = DEFAULT_CONFIG.copy()
            cfg.update(data)
            return cfg
        except: pass
    return DEFAULT_CONFIG.copy()

def save_config(config):
    try:
        with open(CONFIG_FILE, "w") as f: json.dump(config, f, indent=2)
    except: pass

def trigger_display(trigger):
    if not trigger: return "—"
    if trigger.startswith("mouse:"): return trigger.split(":")[1] + " click"
    if trigger.startswith("key:"):
        k = trigger.split(":")[1]
        return k.upper() if len(k) == 1 else k
    return trigger

def pynput_button_to_str(button):
    return {pmouse.Button.right: "right", pmouse.Button.left: "left", pmouse.Button.middle: "middle"}.get(button)

def pynput_key_to_str(key):
    try:
        if key.char: return normalize_char(key.char)
    except: pass
    try: return key.name.lower()
    except: pass
    return None

def create_tray_icon_image():
    image = Image.new('RGB', (64, 64), color=BG)
    dc = ImageDraw.Draw(image)
    dc.rectangle([16, 16, 48, 48], fill=FG)
    return image

class OnboardingWindow:
    def __init__(self, parent_root, on_close, on_never_show):
        self.on_close = on_close
        self.on_never_show = on_never_show
        self.win = tk.Toplevel(parent_root)
        self.win.title("PixelPin")
        self.win.configure(bg=BG, padx=32, pady=24)
        self.win.attributes("-topmost", True)
        self.win.resizable(False, False)
        self._build()
        self.win.update_idletasks()
        self.win.geometry(f"+{(self.win.winfo_screenwidth() - self.win.winfo_width()) // 2}+{(self.win.winfo_screenheight() - self.win.winfo_height()) // 2}")

    def _row(self, parent, row, key, desc, key_fg=None):
        tk.Label(parent, text=key, bg=BG, fg=key_fg or FG, font=FONT_B, width=14, anchor="w").grid(row=row, column=0, sticky="w", pady=2)
        tk.Label(parent, text=desc, bg=BG, fg=FG_DIM, font=FONT, anchor="w").grid(row=row, column=1, sticky="w", pady=2, padx=(8, 0))

    def _build(self):
        tk.Label(self.win, text=BANNER, bg=BG, fg=FG, font=("Consolas", 6), justify="left").pack(anchor="w", pady=(0, 10))
        tk.Label(self.win, text="Welcome to PixelPin", bg=BG, fg=FG, font=("Consolas", 14, "bold")).pack(anchor="w")
        tk.Label(self.win, text="Hover anywhere on screen, copy coordinates in one click.", bg=BG, fg=FG_DIM, font=FONT).pack(anchor="w", pady=(2, 15))

        grid = tk.Frame(self.win, bg=BG)
        grid.pack(fill="x")

        self._row(grid, 0, "move mouse",   "live coordinates above cursor")
        self._row(grid, 1, "right-click",  "copy to clipboard")
        self._row(grid, 2, "Tab",          "open settings")
        self._row(grid, 3, "Esc",          "pause / resume")

        tk.Label(grid, text="You can rebind and customize these in Settings (Tab):", 
                 bg=BG, fg=ACCENT, font=FONT_B).grid(row=4, column=0, columnspan=2, sticky="w", pady=(20, 5))

        tk.Frame(grid, bg="#1c1c1c", height=1).grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        self._row(grid, 6, "Auto-save",    "appends every copy to a .txt file")
        self._row(grid, 7, "Undo",         "removes the last saved line from file")
        self._row(grid, 8, "Rebind",       "assign any key or mouse button")

        bottom = tk.Frame(self.win, bg=BG)
        bottom.pack(fill="x", pady=(20, 0))

        self._no_show_var = tk.BooleanVar(value=False)
        tk.Checkbutton(bottom, text="Don't show again", variable=self._no_show_var, bg=BG, fg=FG_DIM, selectcolor="#1c1c1c", 
                       activebackground=BG, activeforeground=FG_DIM, font=FONT, bd=0, highlightthickness=0).pack(side="left")

        tk.Button(bottom, text="  Let's go  ", command=self._close, bg=FG, fg=BG, font=FONT_B, relief="flat", padx=10, pady=4, bd=0).pack(side="right")

    def _close(self):
        if self._no_show_var.get(): self.on_never_show()
        self.win.destroy()
        self.on_close()

class SettingsWindow:
    def __init__(self, parent_root, config, on_save, on_close, on_quit):
        self.parent = parent_root
        self.config = config.copy()
        self.on_save, self.on_close, self.on_quit = on_save, on_close, on_quit
        self._capturing = None
        self.win = tk.Toplevel(parent_root)
        self.win.title("PixelPin — Settings")
        self.win.configure(bg=BG, padx=24, pady=20)
        self.win.attributes("-topmost", True)
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self._close)
        self._build()

    def _btn(self, parent, text, cmd, fg=None, bg=None):
        return tk.Button(parent, text=text, command=cmd, bg=bg or "#1c1c1c", fg=fg or FG, font=FONT, relief="flat", padx=8, pady=3, bd=0)

    def _build(self):
        p = {"pady": 5}
        tk.Label(self.win, text="Copy trigger", bg=BG, fg=FG_DIM, font=FONT).grid(row=0, column=0, sticky="w", **p)
        f1 = tk.Frame(self.win, bg=BG); f1.grid(row=0, column=1, sticky="w", padx=(12, 0), **p)
        self._copy_var = tk.StringVar(value=trigger_display(self.config["copy_trigger"]))
        self._copy_lbl = tk.Label(f1, textvariable=self._copy_var, bg="#1c1c1c", fg=FG, font=FONT_B, width=16, padx=6, pady=3)
        self._copy_lbl.pack(side="left")
        self._btn(f1, "Rebind", lambda: self._start_capture("copy")).pack(side="left", padx=(6, 0))

        tk.Frame(self.win, bg="#1c1c1c", height=1).grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)

        tk.Label(self.win, text="Auto-save", bg=BG, fg=FG_DIM, font=FONT).grid(row=2, column=0, sticky="w", **p)
        self._autosave_var = tk.BooleanVar(value=self.config["autosave_enabled"])
        self._toggle_btn = self._btn(self.win, "", self._toggle_autosave); self._toggle_btn.grid(row=2, column=1, sticky="w", padx=(12, 0), **p)
        self._update_toggle()

        tk.Label(self.win, text="File path", bg=BG, fg=FG_DIM, font=FONT).grid(row=3, column=0, sticky="w", **p)
        f2 = tk.Frame(self.win, bg=BG); f2.grid(row=3, column=1, sticky="w", padx=(12, 0), **p)
        self._path_var = tk.StringVar(value=self.config["autosave_path"])
        tk.Entry(f2, textvariable=self._path_var, bg="#1c1c1c", fg=FG, font=FONT, width=24, bd=4, relief="flat").pack(side="left")
        self._btn(f2, "Browse", self._browse).pack(side="left", padx=(6, 0))

        tk.Frame(self.win, bg="#1c1c1c", height=1).grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)

        tk.Label(self.win, text="Undo trigger", bg=BG, fg=FG_DIM, font=FONT).grid(row=5, column=0, sticky="w", **p)
        f3 = tk.Frame(self.win, bg=BG); f3.grid(row=5, column=1, sticky="w", padx=(12, 0), **p)
        self._undo_var = tk.StringVar(value=trigger_display(self.config["undo_trigger"]))
        self._undo_lbl = tk.Label(f3, textvariable=self._undo_var, bg="#1c1c1c", fg=FG, font=FONT_B, width=16, padx=6, pady=3)
        self._undo_lbl.pack(side="left")
        self._btn(f3, "Rebind", lambda: self._start_capture("undo")).pack(side="left", padx=(6, 0))

        btns = tk.Frame(self.win, bg=BG); btns.grid(row=6, column=0, columnspan=2, pady=(15, 0))
        self._btn(btns, "  Save  ", self._save, fg=BG, bg=FG).pack(side="left", padx=5)
        self._btn(btns, " Cancel ", self._close).pack(side="left", padx=5)
        self._btn(btns, "  Quit  ", self._do_quit, fg="#ff4444").pack(side="right", padx=15)

    def _toggle_autosave(self): self._autosave_var.set(not self._autosave_var.get()); self._update_toggle()
    def _update_toggle(self):
        txt, bg, fg = ("  ON  ", "#003322", FG) if self._autosave_var.get() else (" OFF  ", "#1c1c1c", FG_DIM)
        self._toggle_btn.config(text=txt, bg=bg, fg=fg)

    def _browse(self):
        p = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt")])
        if p: self._path_var.set(p)

    def _start_capture(self, field):
        self._capturing = field
        var = self._copy_var if field == "copy" else self._undo_var
        lbl = self._copy_lbl if field == "copy" else self._undo_lbl
        var.set("[ press... ]")
        lbl.config(fg=ACCENT)
        self.win.focus_set()
        self.win.bind("<Key>", self._cap_key)
        self.win.bind("<ButtonRelease-1>", lambda e: self._apply("mouse:left"))
        self.win.bind("<ButtonRelease-2>", lambda e: self._apply("mouse:middle"))
        self.win.bind("<ButtonRelease-3>", lambda e: self._apply("mouse:right"))

    def _cap_key(self, e): 
        if e.keysym == "Escape":
            self._cancel_capture()
            return
        key_str = normalize_char(e.char) if e.char and e.char.isprintable() and len(e.char) == 1 else e.keysym.lower()
        self._apply(f"key:{key_str}")

    def _apply(self, trig):
        f = self._capturing
        if not f: return
        self._capturing = None
        self.win.unbind("<Key>"); self.win.unbind("<ButtonRelease-1>"); self.win.unbind("<ButtonRelease-2>"); self.win.unbind("<ButtonRelease-3>")
        self.config["copy_trigger" if f=="copy" else "undo_trigger"] = trig
        (self._copy_var if f=="copy" else self._undo_var).set(trigger_display(trig))
        (self._copy_lbl if f=="copy" else self._undo_lbl).config(fg=FG)

    def _cancel_capture(self):
        f = self._capturing
        self._capturing = None
        self.win.unbind("<Key>"); self.win.unbind("<ButtonRelease-1>"); self.win.unbind("<ButtonRelease-2>"); self.win.unbind("<ButtonRelease-3>")
        if not f: return
        key = "copy_trigger" if f == "copy" else "undo_trigger"
        (self._copy_var if f == "copy" else self._undo_var).set(trigger_display(self.config[key]))
        (self._copy_lbl if f == "copy" else self._undo_lbl).config(fg=FG)

    def _save(self):
        self.config.update({"autosave_enabled": self._autosave_var.get(), "autosave_path": self._path_var.get()})
        save_config(self.config)
        self.on_save(self.config)
        self._close()

    def _do_quit(self):
        self.win.destroy()
        self.on_quit()

    def _close(self):
        if self._capturing: self._cancel_capture()
        self.win.destroy()
        self.on_close()

class CoordPicker:
    def __init__(self):
        self.mx = self.my = 0
        self._running = True
        self._paused = False
        self._settings_open = False
        self._onboard_open = False
        self._is_flashing = False
        self.config = load_config()

        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True, "-alpha", 0.9)
        self.root.config(bg=BG, highlightbackground=FG, highlightthickness=1)
        self.label = tk.Label(self.root, text="0, 0", bg=BG, fg=FG, font=("Consolas", 12, "bold"), padx=8, pady=4)
        self.label.pack()

        self.m_ltn = pmouse.Listener(on_move=self._on_m, on_click=self._on_c)
        self.m_ltn.start()
        self.k_ltn = pkeyboard.Listener(on_press=self._on_k)
        self.k_ltn.start()

        self._setup_tray()
        self.root.after(10, self._tick)

        if not self.config.get("onboarding_shown"):
            self.root.after(200, self._show_onboarding)

        self.root.mainloop()

    def _setup_tray(self):
        m = pystray.Menu(
            pystray.MenuItem("Settings", lambda icon, item: self.root.after(0, self._open_settings)),
            pystray.MenuItem("Quit", lambda icon, item: self.root.after(0, self._quit))
        )
        self.tray = pystray.Icon("pixelpin", create_tray_icon_image(), "PixelPin", m)
        threading.Thread(target=self.tray.run, daemon=True).start()

    def _on_m(self, x, y):
        self.mx, self.my = x, y

    def _on_c(self, x, y, b, p):
        if not p or self._settings_open or self._paused: return
        s = pynput_button_to_str(b)
        if not s: return
        if self.config.get("copy_trigger") == f"mouse:{s}":
            self.root.after(0, lambda: self._copy(f"{x}, {y}"))
        elif self.config.get("undo_trigger") == f"mouse:{s}":
            self.root.after(0, self._undo)

    def _on_k(self, k):
        if k == pkeyboard.Key.esc:
            self.root.after(0, self._toggle_p)
            return
        if k == pkeyboard.Key.tab:
            self.root.after(0, self._open_settings)
            return
        if self._settings_open or self._paused:
            return
        
        s = pynput_key_to_str(k)
        if not s: return
        
        if self.config.get("copy_trigger") == f"key:{s}":
            self.root.after(0, lambda: self._copy(f"{self.mx}, {self.my}"))
        elif self.config.get("undo_trigger") == f"key:{s}":
            self.root.after(0, self._undo)

    def _tick(self):
        if not self._running: return
        
        if self._paused:
            if self.label.cget("text") != "⏸  paused":
                self.label.config(text="⏸  paused", fg=FG_DIM, bg=BG)
                self.root.config(highlightbackground=FG_DIM)
        elif not self._is_flashing:
            current_text = f"{self.mx}, {self.my}"
            if self.label.cget("text") != current_text:
                self.label.config(text=current_text)
                
        w = self.label.winfo_reqwidth() + 16
        nx, ny = self.mx + 14, self.my - 36
        sw = self.root.winfo_screenwidth()
        
        if nx + w > sw: nx = self.mx - w - 6
        if ny < 0: ny = self.my + 20
        
        self.root.geometry(f"+{nx}+{ny}")
        self.root.after(10, self._tick)

    def _copy(self, c):
        self.root.clipboard_clear()
        self.root.clipboard_append(c)
        if self.config.get("autosave_enabled") and self.config.get("autosave_path"):
            try: 
                with open(self.config["autosave_path"], "a", encoding="utf-8") as f: f.write(c + "\n")
            except: pass
        self._is_flashing = True
        self.label.config(text=f"✓  {c}", fg=ACCENT, bg="#1a3a1a")
        self.root.config(highlightbackground=ACCENT)
        self.root.after(700, self._reset)

    def _undo(self):
        p = self.config.get("autosave_path", "")
        if not self.config.get("autosave_enabled") or not os.path.exists(p): return
        try:
            with open(p, "r", encoding="utf-8") as f: lines = f.readlines()
            while lines and lines[-1].strip() == "": lines.pop()
            if lines: lines.pop()
            with open(p, "w", encoding="utf-8") as f: f.writelines(lines)
            
            self._is_flashing = True
            self.label.config(text="↩  undone", fg=ORANGE, bg="#1a1200")
            self.root.config(highlightbackground=ORANGE)
            self.root.after(700, self._reset)
        except: pass

    def _toggle_p(self):
        self._paused = not self._paused
        self._reset()

    def _reset(self):
        self._is_flashing = False
        if not self._paused:
            self.label.config(fg=FG, bg=BG)
            self.root.config(highlightbackground=FG)
            self.label.config(text=f"{self.mx}, {self.my}")

    def _show_onboarding(self):
        if not self._onboard_open: 
            self._onboard_open = True
            OnboardingWindow(self.root, lambda: setattr(self, "_onboard_open", False), lambda: save_config({**self.config, "onboarding_shown": True}))

    def _open_settings(self):
        if not self._settings_open:
            self._settings_open = True
            SettingsWindow(self.root, self.config, lambda c: setattr(self, "config", c), lambda: setattr(self, "_settings_open", False), self._quit)

    def _quit(self):
        self._running = False
        self.m_ltn.stop()
        self.k_ltn.stop()
        if hasattr(self, 'tray'): self.tray.stop()
        self.root.destroy()

if __name__ == "__main__":
    print(BANNER)
    print(MENU_HINT)
    CoordPicker()
