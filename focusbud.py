import cv2
import numpy as np
import time
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import winsound

def beep_sound():
    winsound.MessageBeep()

class FocusTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Focus Bud")
        self.root.configure(bg="#FFFDD0")  # Cream background
        self.root.geometry("950x700")

        # Timers and state
        self.focused_time = 0
        self.distraction_time = 0
        self.is_focused = True
        self.distraction_start = None
        self.distraction_beep_triggered = False
        self.alert_triggered = False
        self.last_popup_time = 0

        # Config
        self.popup_delay = 7
        self.popup_cooldown = 10
        self.study_goal = 25 * 60  # 25 minutes
        self.session_active = False

        self.cap = None
        self.frame_duration = int(1000 / 30)
        self.session_start = None

        self.setup_scrollable_ui()

    def setup_scrollable_ui(self):
        # Scrollable Canvas Setup
        self.canvas = tk.Canvas(self.root, bg="#FFFDD0", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollable_frame = tk.Frame(self.canvas, bg="#FFFDD0")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="n")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.root.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=self.canvas.winfo_width()))

        # UI inside the scrollable area
        heading = tk.Label(
            self.scrollable_frame, text="Focus Bud",
            font=("Segoe UI", 26, "bold"),
            bg="#FFFDD0", fg="#00CED1"
        )
        heading.pack(pady=(10, 0))

        byline = tk.Label(
            self.scrollable_frame, text="Your Productivity Partner 🧠",
            font=("Segoe UI", 16),
            bg="#FFFDD0", fg="#555"
        )
        byline.pack(pady=(0, 10))

        self.video_label = tk.Label(self.scrollable_frame, bg="#FFFDD0")
        self.video_label.pack()

        # Buttons
        btn_frame = tk.Frame(self.scrollable_frame, bg="#FFFDD0")
        btn_frame.pack(pady=15)

        self.start_button = tk.Button(
            btn_frame, text="Start Session",
            font=("Segoe UI", 14, "bold"),
            bg="#007acc", fg="#fff",
            activebackground="#005f99", activeforeground="#fff",
            command=self.start_session
        )
        self.start_button.grid(row=0, column=0, padx=20, ipadx=10, ipady=5)

        self.stop_button = tk.Button(
            btn_frame, text="Stop Session",
            font=("Segoe UI", 14, "bold"),
            bg="#d9534f", fg="#fff",
            activebackground="#c9302c", activeforeground="#fff",
            command=self.stop_session
        )
        self.stop_button.grid(row=0, column=1, padx=20, ipadx=10, ipady=5)

    def start_session(self):
        if self.session_active:
            messagebox.showinfo("Info", "Session already running!")
            return

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Cannot access webcam!")
            return

        self.session_active = True
        self.session_start = time.time()

        self.focused_time = 0
        self.distraction_time = 0
        self.is_focused = True
        self.distraction_start = None
        self.distraction_beep_triggered = False
        self.alert_triggered = False
        self.last_popup_time = 0

        self.update_frame()

    def stop_session(self):
        self.session_active = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.video_label.config(image='')

    def update_frame(self):
        if not self.session_active:
            return

        now = time.time()
        elapsed_time = now - self.session_start

        if elapsed_time >= self.study_goal:
            self.session_active = False
            self.stop_session()
            messagebox.showinfo("Session Complete", "Study session completed!")
            return

        ret, frame = self.cap.read()
        if not ret:
            self.stop_session()
            return

        gaze_status = "focused" if int(elapsed_time) % 10 < 5 else "distracted"

        if gaze_status == "focused":
            if not self.is_focused and self.distraction_start:
                self.distraction_time += (now - self.distraction_start)
                self.distraction_start = None
            self.focused_time += 1 / 30
            self.is_focused = True
            self.distraction_beep_triggered = False
            self.alert_triggered = False
        else:
            if self.is_focused:
                self.distraction_start = now
            self.is_focused = False
            current_distraction = now - self.distraction_start if self.distraction_start else 0

            if current_distraction > 3 and not self.distraction_beep_triggered:
                beep_sound()
                self.distraction_beep_triggered = True

            if current_distraction > self.popup_delay and not self.alert_triggered:
                if now - self.last_popup_time > self.popup_cooldown:
                    beep_sound()
                    self.last_popup_time = now
                    self.alert_triggered = True

        total_distraction_display = self.distraction_time
        if self.distraction_start and not self.is_focused:
            total_distraction_display += (now - self.distraction_start)

        time_remaining = max(0, int(self.study_goal - self.focused_time))

        overlay_text = [
            f"Status: {gaze_status.upper()}",
            f"Focused Time: {int(self.focused_time)}s",
            f"Distraction Time: {int(total_distraction_display)}s",
            f"Time Remaining: {time_remaining}s"
        ]

        h, w, _ = frame.shape
        y0 = 30
        for i, line in enumerate(overlay_text):
            color = (0, 255, 0) if "Focused" in line else (0, 0, 255) if "Distraction" in line else (255, 255, 0) if "Time Remaining" in line else (255, 255, 255)
            x = 10  # Left-aligned
            y = y0 + i * 35
            cv2.putText(frame, line, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_frame)
        imgtk = ImageTk.PhotoImage(image=img)

        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)

        self.root.after(self.frame_duration, self.update_frame)

    def on_closing(self):
        self.stop_session()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FocusTrackerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
