# 🐦 Flappy Bird (Python + Pygame)

A smooth, modern recreation of the classic Flappy Bird, built with [Pygame](https://www.pygame.org/).
This version features a persistent leaderboard, fullscreen scaling, sound effects, and clean code architecture — perfect for learning or sharing.

## 🎮 Features

- Classic gameplay with smooth physics and animations
- Persistent leaderboard — your top scores are saved across runs and reinstalls
- Responsive fullscreen toggle (F or F11)
- Dynamic viewport resizing — see more of the world when expanding the window
- Sound effects for wing, point, and hit events
- Clean, modular codebase with classes for Bird, Pipe, and Ground
- Safe startup when no audio device is available
- PyInstaller-ready — build a single .exe or .app with all assets included

## 🧩 Requirements

- Python 3.9+ (tested on 3.11)
- pygame library (2.6.1+ recommended)

Install dependencies:
```bash
pip install pygame
```

## 🚀 Getting Started

Clone the repository
```bash
git clone https://github.com/Tr0nML/flappy-bird-pygame.git
cd flappy-bird-pygame
```

Run the game
```bash
python flappy.py
```

## Controls

| Action                   | Key / Button                |
|--------------------------|-----------------------------|
| Flap                     | Space, ↑, or Mouse Click    |
| Toggle Fullscreen        | F or F11                    |
| Restart after Game Over  | R or Space                  |
| Show / Hide Leaderboard  | L                           |
| Quit                     | Q or Esc                    |

## 🏆 Leaderboard Persistence

Your high scores are automatically saved in a user-specific data folder, so they persist even after creating or reinstalling the .exe build.

| Platform | Save Path                                              |
|----------|-------------------------------------------------------|
| Windows  | %APPDATA%\FlappyBird\flappy_scores.json                 |
| macOS    | ~/Library/Application Support/FlappyBird/flappy_scores.json |
| Linux    | ~/.local/share/FlappyBird/flappy_scores.json            |

Each time you play, new scores are recorded and ranked locally.

## 📁 Project Structure
```
Flappy/
├── flappy.py                 # Main game script
├── assets/
│   ├── icon.ico
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
│       └── [0-9].png         # Score number sprites
└── README.md
```

## 🧱 Building a Standalone Executable

To distribute your game easily:

Install PyInstaller:
```bash
pip install pyinstaller
```
Build the executable:
```bash
pyinstaller --noconsole --onefile --add-data "assets:assets" --icon "assets/icon.ico" flappy.py
```
The build output will appear in the dist/ folder:
```
dist/
└── flappy.exe   # or flappy (macOS/Linux)
```
The included resource_path() helper ensures that assets load correctly in both development and packaged builds.

## 🪶 Technical Highlights

- Written entirely in Python (Pygame)
- Smooth 60 FPS animation
- Resource-safe asset loading compatible with PyInstaller
- Uses mask collision detection for pixel-perfect gameplay
- Dynamic background and ground tiling based on viewport size

## 💡 Tips

- Default window size: 400×600 px
- Works seamlessly across Windows, macOS, and Linux
- Fullscreen stretches to monitor resolution but maintains proportion
- Audio gracefully disables if no sound device is found

## 🧑‍💻 Author

Aryan Garg

Built for fun, nostalgia, and hands-on learning in Python game development.
Feel free to fork, play, and improve it!

## 📜 License

Released under the MIT License — you're free to use, modify, and distribute this project with attribution.
