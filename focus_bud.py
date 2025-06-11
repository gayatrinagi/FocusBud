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
        self.calibrated_eye_distance = None

    def calibrate(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0]
            left_eye = [landmarks.landmark[33], landmarks.landmark[133]]
            right_eye = [landmarks.landmark[362], landmarks.landmark[263]]
            left_dx = abs(left_eye[0].x - left_eye[1].x)
            right_dx = abs(right_eye[0].x - right_eye[1].x)
            self.calibrated_eye_distance = (left_dx + right_dx) / 2
            return True
        return False

    def is_focused(self, frame):
        if self.calibrated_eye_distance is None:
            return True  # Assume focused before calibration

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0]
            left_eye = [landmarks.landmark[33], landmarks.landmark[133]]
            right_eye = [landmarks.landmark[362], landmarks.landmark[263]]
            left_dx = abs(left_eye[0].x - left_eye[1].x)
            right_dx = abs(right_eye[0].x - right_eye[1].x)
            current_eye_distance = (left_dx + right_dx) / 2

            return abs(current_eye_distance - self.calibrated_eye_distance) < 0.01
        return False

class FocusTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Focus Bud")
        self.root.geometry("950x780")
        self.root.configure(bg="#FFFDD0")

        self.focused_time = 0
        self.distraction_time = 0
        self.is_focused = True
        self.distraction_start = None
        self.session_active = False
        self.study_goal = 25 * 60
        self.session_start = None
        self.cap = None
        self.frame_duration = int(1000 / 30)

        self.gaze_detector = GazeDetector()
        self.setup_ui()

    def setup_ui(self):
        outer_frame = tk.Frame(self.root, bg="#FFFDD0")
        outer_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(outer_frame, bg="#FFFDD0", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(outer_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.scrollable_frame = tk.Frame(self.canvas, bg="#FFFDD0")
        self.frame_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="n")
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)

        heading = tk.Label(self.scrollable_frame, text="Focus Bud", font=("Segoe UI", 26, "bold"), bg="#FFFDD0", fg="#00CED1")
        heading.pack(pady=(10, 0))

        byline = tk.Label(self.scrollable_frame, text="Your Productivity Partner 🧠", font=("Segoe UI", 16), bg="#FFFDD0", fg="#555")
        byline.pack(pady=(0, 10))

        self.video_label = tk.Label(self.scrollable_frame, bg="#FFFDD0")
        self.video_label.pack()

        self.progress_canvas = tk.Canvas(self.scrollable_frame, width=200, height=200, bg="#FFFDD0", highlightthickness=0)
        self.progress_canvas.pack(pady=(10, 0))

        btn_frame = tk.Frame(self.scrollable_frame, bg="#FFFDD0")
        btn_frame.pack(pady=10)

        self.calibrate_button = tk.Button(btn_frame, text="Calibrate", font=("Segoe UI", 14, "bold"), bg="#FFA500", fg="#fff", command=self.calibrate_screen)
        self.calibrate_button.grid(row=0, column=0, padx=10)

        self.start_button = tk.Button(btn_frame, text="Start Session", font=("Segoe UI", 14, "bold"), bg="#007acc", fg="#fff", command=self.start_session)
        self.start_button.grid(row=0, column=1, padx=10)

        self.stop_button = tk.Button(btn_frame, text="Stop Session", font=("Segoe UI", 14, "bold"), bg="#d9534f", fg="#fff", command=self.stop_session)
        self.stop_button.grid(row=0, column=2, padx=10)

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.frame_window, width=event.width)

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    def calibrate_screen(self):
        if not self.cap:
            self.cap = cv2.VideoCapture(0)
        ret, frame = self.cap.read()
        if not ret:
            messagebox.showerror("Error", "Webcam not accessible for calibration.")
            return
        success = self.gaze_detector.calibrate(frame)
        if success:
            messagebox.showinfo("Calibrated", "Calibration successful!")
        else:
            messagebox.showwarning("Calibration Failed", "Face not detected. Please try again.")

    def start_session(self):
        if self.session_active:
            messagebox.showinfo("Info", "Session already running!")
            return
        if self.gaze_detector.calibrated_eye_distance is None:
            messagebox.showwarning("Calibration Required", "Please calibrate before starting the session.")
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
        self.progress_canvas.delete("all")
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

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)

        self.update_circular_progress()
        self.root.after(self.frame_duration, self.update_frame)

    def update_circular_progress(self):
        self.progress_canvas.delete("all")
        if not self.session_active or self.study_goal == 0:
            return
        elapsed = time.time() - self.session_start
        percent = min(100, (elapsed / self.study_goal) * 100)
        angle = (percent / 100) * 360
        self.progress_canvas.create_oval(20, 20, 180, 180, fill="#eee", outline="")
        self.progress_canvas.create_arc(20, 20, 180, 180, start=90, extent=-angle, fill="#00CED1")
        self.progress_canvas.create_text(100, 100, text=f"{int(percent)}%", font=("Segoe UI", 16, "bold"), fill="#333")

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
