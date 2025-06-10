import cv2
import time
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import mediapipe as mp
import winsound

def beep_sound():
    winsound.MessageBeep()

class GazeDetector:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(max_num_faces=1)
        self.mp_drawing = mp.solutions.drawing_utils

    def is_focused(self, frame):
        # Convert to RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]

            # Get left and right eye landmark coordinates
            h, w, _ = frame.shape
            left_eye = [face_landmarks.landmark[33], face_landmarks.landmark[133]]  # eye corners
            right_eye = [face_landmarks.landmark[362], face_landmarks.landmark[263]]

            # Calculate eye direction vector
            left_dx = abs(left_eye[0].x - left_eye[1].x)
            right_dx = abs(right_eye[0].x - right_eye[1].x)

            # The larger the dx, the more likely user is looking sideways
            if left_dx < 0.03 or right_dx < 0.03:
                return False  # likely looking away

            return True
        return False  # No face detected

class FocusTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Focus Bud")
        self.root.geometry("950x700")
        self.root.configure(bg="#FFFDD0")

        self.focused_time = 0
        self.distraction_time = 0
        self.is_focused = True
        self.distraction_start = None
        self.session_active = False
        self.study_goal = 25 * 60

        self.cap = None
        self.frame_duration = int(1000 / 30)
        self.session_start = None

        self.gaze_detector = GazeDetector()
        self.setup_ui()

    def setup_ui(self):
        heading = tk.Label(self.root, text="Focus Bud", font=("Segoe UI", 26, "bold"), bg="#FFFDD0", fg="#00CED1")
        heading.pack(pady=(10, 0))

        byline = tk.Label(self.root, text="Your Productivity Partner 🧠", font=("Segoe UI", 16), bg="#FFFDD0", fg="#555")
        byline.pack(pady=(0, 10))

        self.video_label = tk.Label(self.root, bg="#FFFDD0")
        self.video_label.pack()

        btn_frame = tk.Frame(self.root, bg="#FFFDD0")
        btn_frame.pack(pady=10)

        self.start_button = tk.Button(
            btn_frame, text="Start Session", font=("Segoe UI", 14, "bold"),
            bg="#007acc", fg="#fff", command=self.start_session
        )
        self.start_button.grid(row=0, column=0, padx=20)

        self.stop_button = tk.Button(
            btn_frame, text="Stop Session", font=("Segoe UI", 14, "bold"),
            bg="#d9534f", fg="#fff", command=self.stop_session
        )
        self.stop_button.grid(row=0, column=1, padx=20)

    def start_session(self):
        if self.session_active:
            messagebox.showinfo("Info", "Session already running!")
            return

        duration = simpledialog.askinteger("Session Duration", "Enter duration in minutes (1-180):", minvalue=1, maxvalue=180)
        if duration is None:
            return
        self.study_goal = duration * 60

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Cannot access webcam!")
            return

        self.session_active = True
        self.session_start = time.time()
        self.focused_time = 0
        self.distraction_time = 0
        self.distraction_start = None
        self.update_frame()

    def stop_session(self):
        self.session_active = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.video_label.config(image='')
        self.show_report()

    def update_frame(self):
        if not self.session_active:
            return

        now = time.time()
        elapsed = now - self.session_start

        if elapsed >= self.study_goal:
            self.stop_session()
            return

        ret, frame = self.cap.read()
        if not ret:
            self.stop_session()
            return

        gaze_focused = self.gaze_detector.is_focused(frame)

        if gaze_focused:
            if self.distraction_start:
                self.distraction_time += (now - self.distraction_start)
                self.distraction_start = None
            self.focused_time += 1 / 30
            self.is_focused = True
        else:
            if not self.distraction_start:
                self.distraction_start = now
            self.is_focused = False

        # Draw info overlay
        info = [
            f"Status: {'FOCUSED' if self.is_focused else 'DISTRACTED'}",
            f"Focused Time: {int(self.focused_time)}s",
            f"Distraction Time: {int(self.distraction_time)}s",
            f"Time Remaining: {int(self.study_goal - elapsed)}s"
        ]

        y = 30
        for text in info:
            color = (0, 255, 0) if "FOCUSED" in text else (0, 0, 255) if "DISTRACTED" in text else (255, 255, 255)
            cv2.putText(frame, text, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            y += 30

        # Convert to Tkinter image
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)

        self.root.after(self.frame_duration, self.update_frame)

    def show_report(self):
        total_time = self.focused_time + self.distraction_time
        if total_time == 0:
            return

        productivity = (self.focused_time / total_time) * 100
        msg = (
            f"Session Complete!\n\n"
            f"Focused Time: {int(self.focused_time)} seconds\n"
            f"Distraction Time: {int(self.distraction_time)} seconds\n"
            f"Productivity Level: {productivity:.2f}%"
        )
        messagebox.showinfo("Session Report", msg)

    def on_closing(self):
        self.stop_session()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FocusTrackerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
