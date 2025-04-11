# 🎈 Balloon Collection Game

This is an interactive **Balloon Collection Game** developed using OpenCV and MediaPipe. It uses real-time hand tracking via webcam to allow you to collect falling balloons using your left and right hands. ✋🫲🕹️

---

## 🚀 Features

- 🖐️ Real-time hand tracking using MediaPipe
- 🎯 Balloon collection mechanics (left and right hand tracking)
- 🧠 Game state management: Menu, Countdown, Playing, Paused, Game Over
- ⏱️ Timer-based gameplay with countdown
- 🖼️ Image-based balloons (or fallback to simple circles if images are missing)
- 🟢 Hand placement to start the game
- 🧪 On-screen buttons (start, pause, resume, etc.) controlled via finger tap

---

## 📦 Requirements

This project is built with Python 3 and depends on the following libraries:

- `opencv-python`
- `mediapipe`
- `numpy`

Install them with:

```bash
pip install opencv-python mediapipe numpy
```

---

## 🛠️ Installation & Running the Game

1. Clone the repository or download the ZIP:
   ```bash
   git clone https://github.com/your-username/balloon-collection-game.git
   cd balloon-collection-game
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the game:
   ```bash
   python main.py
   ```

> Replace `main.py` with your actual Python file name if different.

---

## 🖼️ Assets

The game expects a balloon image at:

```
images/ballon.png
```

If the image is missing, it will gracefully fall back to drawing a red circle instead.

Project folder structure:

```
balloon-collection-game/
├── images/
│   └── ballon.png
├── main.py
├── README.md
```

---

## 🎮 How to Play

1. Start the game — your webcam will activate.
2. Tap the **Play** button by pointing your index finger at it.
3. Place both your hands in the green circles to begin the countdown.
4. Once the game starts, use your left and right index fingers to "touch" the falling balloons.
5. Each successful collection scores 1 point.
6. After 60 seconds, the game ends and your final score is displayed.

**Keyboard Shortcut:**
- Press `Q` to quit the game anytime.

---

## 🧠 Behind the Scenes

- Hand detection is handled by **MediaPipe**.
- Balloons fall at random speeds and are removed when collected or off-screen.
- Only the correct hand (left/right) can collect the corresponding balloon.
- Interactive buttons on screen can be "clicked" using your finger tip.
- The game manages multiple states and transitions between them based on user actions.

---

## 🤝 Contributing

Contributions, feedback, and suggestions are welcome! Open an issue or submit a pull request. 🎉

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## ✨ Credits

- [OpenCV](https://opencv.org/)
- [MediaPipe](https://mediapipe.dev/)
- And the amazing Python community 💙

---

> Code games, play code. Have fun! 🎮💻
