# 🐦 Flappy Bird (Python + Pygame)

A smooth and modern recreation of the classic **Flappy Bird**, built in Python using the [Pygame](https://www.pygame.org/) library.
This version includes fullscreen support, sound effects, clean code architecture, and PyInstaller compatibility for easy distribution.

---

## 🎮 Features!!!

* Classic flappy gameplay with smooth physics
* Real-time score display
* Animated bird and moving pipes
* Ground scrolling and collision detection
* Sound effects for wing, point, and hit
* Toggle **fullscreen** (`F` or `F11`)
* Mouse, Spacebar, or Arrow key control
* Safe startup when no audio device is available
* Packaged easily with PyInstaller (includes `resource_path` helper)

---

## 🧩 Requirements

* Python **3.9+** (tested on 3.11)
* `pygame` library (2.6.1+ recommended)

Install Pygame via pip:

```bash
pip install pygame
```

---

## 🚀 Getting Started

1. **Clone the repository**

   ```bash
   git clone https://github.com/Tr0nML/flappy-bird-pygame.git
   cd flappy-bird-pygame
   ```

2. **Run the game**

   ```bash
   python flappy.py
   ```

3. **Controls**

   * **Space / Up Arrow / Mouse Click** → Flap
   * **F / F11** → Toggle fullscreen
   * **R** → Restart after game over
   * **Q / Esc** → Quit game

---

## 📁 Project Structure

```
Flappy/
├── flappy.py                 # Main game script
├── assets/
│   ├── audio/
│   │   ├── hit.wav
│   │   ├── point.wav
│   │   └── wing.wav
│   └── sprites/
│       ├── background-day.png
│       ├── base.png
│       ├── bluebird-upflap.png
│       ├── bluebird-midflap.png
│       ├── bluebird-downflap.png
│       ├── message.png
│       ├── pipe-green.png
│       └── [0-9].png         # Number sprites for score display
└── README.md
```

---

## 🧱 Packaging to EXE / APP (Optional)

If you want to share it as a standalone executable:

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --add-data "assets:assets" flappy.py
```

The game uses a helper (`resource_path`) to locate assets correctly when bundled by PyInstaller.

---

## 💡 Notes

* The game runs windowed by default at **400×600** resolution.
* Fullscreen mode stretches the scene to fill your monitor.
* Works smoothly on macOS, Windows, and Linux.
* Audio is optional — it automatically disables if no device is detected.

---

## 🧑‍💻 Author

**Aryan Garg**

Built for fun, practice, and nostalgia.
Feel free to fork, play, and improve the game!

---

## 📜 License

This project is licensed under the **MIT License** — you’re free to use, modify, and distribute it with attribution.

---
