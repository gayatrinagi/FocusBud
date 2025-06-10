# 🎯 Focus Bud

**Focus Bud** is your real-time productivity partner that tracks your focus using your webcam, alerts you when you're distracted, and helps you stay on track during study or work sessions.

---

## 🚀 Features

- 🧠 **Real-Time Gaze-Based Tracking**: Uses your webcam to simulate gaze tracking and determine if you're focused or distracted.
- ⏳ **Live Session Timers**:
  - **Focused Time** increases as long as you're paying attention.
  - **Distraction Time** accumulates while you're off-task.
- 🔔 **Distraction Alerts**:
  - **Beep Alert** when distracted for more than 3 seconds.
  - **Pop-up Reminder** if distraction exceeds 7 seconds.
- 📸 **Live Camera Feed**:
  - Status and timers are displayed **on top of the camera feed** for constant feedback.
- 🎨 **Clean GUI** built with **Tkinter** featuring:
  - Aesthetic UI with centered layout
  - Scrollable interface for smaller screens

---

## 🧰 Tools & Technologies Used

| Tool/Library     | Purpose                                       |
|------------------|-----------------------------------------------|
| `OpenCV`         | Access and process webcam frames              |
| `Tkinter`        | Build the graphical user interface (GUI)      |
| `PIL` (Pillow)   | Convert OpenCV frames to a format usable in Tkinter |
| `winsound`       | Play alert sounds on distraction (Windows only) |
| `Python`         | Core programming language                     |

---

## 📝 How It Works

1. **Start Session**  
   Click "Start Session" to begin a 25-minute focus timer.

2. **Tracking Begins**  
   - Webcam opens and starts monitoring your focus.
   - It simulates focus detection by switching every few seconds.

3. **Stay Focused**  
   - A **beep** plays if you're distracted for 3+ seconds.
   - A **pop-up reminder** appears if you're distracted for 7+ seconds.
   - If you refocus, the session resumes without penalty.

4. **Live Stats Displayed**  
   - Status (FOCUSED / DISTRACTED)
   - Focused Time
   - Distraction Time
   - Time Remaining

5. **Stop Session**  
   You can manually stop the session anytime. Once the full 25-minute session is completed, you're notified with a pop-up.



## 📦 Requirements

- Python 3.x
- Required libraries:
  ```bash
  pip install opencv-python Pillow
