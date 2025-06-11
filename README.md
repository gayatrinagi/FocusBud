# 🎯 Focus Bud - Gaze-Based Productivity Tracker

**Focus Bud** is a desktop application built with Python that helps users monitor and improve their productivity using real-time gaze detection. It uses computer vision and facial landmark analysis to track whether a user is focused on their screen during a study or work session.

![Focus Bud Screenshot](screenshot.png) <!-- Replace with your actual screenshot file -->

---

## 🔍 Features

- 🔁 **Real-Time Gaze Tracking** using MediaPipe and OpenCV
- 🎯 **Calibration** to adjust for individual face measurements
- 🧠 **Focus Detection** based on eye landmark distances
- 📊 **Live Productivity Stats** (Focused Time, Distraction Time, Remaining Time)
- 🔁 **Circular Progress Visualization**
- 🧾 **Session Report** with productivity percentage
- 📦 **Scroll-friendly UI** using Tkinter

---

## 🛠 Technologies Used

- Python 3.x
- OpenCV
- MediaPipe
- Pillow
- Tkinter (GUI)
- Winsound (for system beeps)

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/focus-bud.git
cd focus-bud
````

### 2. Install Dependencies

```bash
pip install opencv-python mediapipe pillow
```

---

## 🚀 Usage

1. Run the application:

```bash
python focus_bud.py
```

2. Click **"Calibrate"** to adjust the system based on your face.
3. Set your desired session duration (e.g., 25 minutes).
4. Click **"Start Session"** to begin.
5. Track your focus with the live video and progress ring.
6. Once done, click **"Stop Session"** to see your focus report.

---

## 📸 How It Works

* The app uses **MediaPipe Face Mesh** to detect key eye landmarks.
* During calibration, it records the average horizontal distance between specific eye points.
* During the session, if the distance changes significantly, the app considers the user distracted.
* Time spent in focus and distraction is tracked and displayed.

---

## 📁 Project Structure

```
focus_bud/
│
├── focus_bud.py         # Main application file
├── README.md            # This file
├── requirements.txt     # List of dependencies
└── screenshot.png       # UI screenshot
```

---

## 📊 Example Output

```
Session Complete!

Focused Time: 1320 seconds
Distraction Time: 180 seconds
Productivity Level: 88.0%
```

---

## 🧠 Inspiration

Built to help students and remote workers stay accountable and minimize distractions during work/study sessions.

---

## 🛡️ Disclaimer

This tool is a prototype and may not be perfectly accurate in every lighting or facial orientation. It is designed for basic productivity awareness.

---

## 👩‍💻 Author

**Gayatri Nagi**
[LinkedIn](https://www.linkedin.com/in/gayatri-nagi-2a586325a/) • [GitHub](https://github.com/gayatrinagi)

---

## 📃 License

This project is licensed under the MIT License. See `LICENSE` for more information.


