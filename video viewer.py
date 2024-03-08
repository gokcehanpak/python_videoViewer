import cv2
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageTk
import threading

class VideoViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Viewer")

        self.video_path = None
        self.cap = None
        self.total_frames = 0
        self.current_frame = 0
        self.is_playing = False

        self.video_label = tk.Label(root)
        self.video_label.pack(padx=10, pady=10)

        self.control_frame = tk.Frame(root)
        self.control_frame.pack(pady=10)

        self.btn_open = tk.Button(self.control_frame, text="Open Video", command=self.open_video)
        self.btn_open.grid(row=0, column=0, padx=5)

        self.btn_play = tk.Button(self.control_frame, text="Play", command=self.toggle_play)
        self.btn_play.grid(row=0, column=1, padx=5)

        self.btn_stop = tk.Button(self.control_frame, text="Stop", command=self.stop_video)
        self.btn_stop.grid(row=0, column=2, padx=5)

        self.seek_slider = ttk.Scale(self.control_frame, from_=0, to=100, orient="horizontal", length=300, command=self.seek_video)
        self.seek_slider.grid(row=0, column=3, padx=5)

        self.time_label = tk.Label(self.control_frame, text="00:00 / 00:00")
        self.time_label.grid(row=0, column=4, padx=5)

    def open_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.mkv")])
        if file_path:
            self.video_path = file_path
            self.cap = cv2.VideoCapture(file_path)
            self.cap.set(cv2.CAP_PROP_FPS, 60)  # Set the frame rate to 60 fps
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.seek_slider.config(to=self.total_frames)

            self.play_video()

    def play_video(self):
        self.is_playing = True
        self.btn_play.configure(text="Pause", command=self.toggle_play)
        threading.Thread(target=self.update_frame).start()

    def stop_video(self):
        self.is_playing = False
        self.btn_play.configure(text="Play", command=self.toggle_play)
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
            self.video_label.configure(image=None)
        self.current_frame = 0
        self.seek_slider.set(0)
        self.update_time_label()

    def toggle_play(self):
        if self.is_playing:
            self.is_playing = False
            self.btn_play.configure(text="Play", command=self.toggle_play)
        else:
            if self.current_frame == self.total_frames:
                self.current_frame = 0
                self.seek_slider.set(0)
            self.is_playing = True
            self.btn_play.configure(text="Pause", command=self.toggle_play)
            threading.Thread(target=self.update_frame).start()

    def update_frame(self):
        while self.is_playing and self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.display_frame(frame)
                self.current_frame += 1
                self.seek_slider.set(self.current_frame)
                self.update_time_label()
            else:
                self.stop_video()
                break

    def seek_video(self, value):
        value = int(value)
        if self.cap is not None and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, value)
            self.current_frame = value
            ret, frame = self.cap.read()
            if ret:
                self.display_frame(frame)
                self.update_time_label()

    def display_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, _ = frame.shape
        frame = cv2.resize(frame, (width, height))
        photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
        self.video_label.configure(image=photo)
        self.video_label.image = photo

    def update_time_label(self):
        current_time = self.format_time(self.current_frame)
        total_time = self.format_time(self.total_frames)
        self.time_label.config(text=f"{current_time} / {total_time}")

    @staticmethod
    def format_time(frames):
        total_seconds = int(frames / 60)  # Assuming 60 frames per second
        minutes, seconds = divmod(total_seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoViewer(root)
    root.mainloop()
