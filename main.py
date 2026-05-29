import cv2
import customtkinter as ctk
from PIL import Image, ImageTk
import threading
import numpy as np
from tkinter import ttk

class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Camaki - bessere Kameraansicht")
        self.root.geometry("1280x820")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.cap = None
        self.running = False
        self.terminal_mode = False
        
        # Main frame
        self.main_frame = ctk.CTkFrame(root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="funktioner doch mal alter",
            font=("Helvetica", 24, "bold")
        )
        title_label.pack(pady=10)
        
        # Control frame
        control_frame = ctk.CTkFrame(self.main_frame)
        control_frame.pack(fill="x", pady=10)
        
        self.start_btn = ctk.CTkButton(
            control_frame,
            text="Cam an",
            command=self.start_camera,
            fg_color="#1f6aa5",
            hover_color="#0d47a1"
        )
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = ctk.CTkButton(
            control_frame,
            text="Cam kill",
            command=self.stop_camera,
            fg_color="#c41c3b",
            hover_color="#a01030",
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=5)
        
        self.toggle_terminal = ctk.CTkButton(
            control_frame,
            text="cmd view",
            command=self.toggle_terminal_view,
            fg_color="#00897b",
            hover_color="#004d40"
        )
        self.toggle_terminal.pack(side="left", padx=5)
        
        # Display frame
        self.display_frame = ctk.CTkFrame(self.main_frame)
        self.display_frame.pack(fill="both", expand=True, pady=10)
        
        # Image label
        self.image_label = ctk.CTkLabel(
            self.display_frame,
            text="Camera kaka nicht an du hs",
            fg_color="#2b2b2b"
        )
        self.image_label.pack(fill="both", expand=True)
        
        # Terminal text display
        self.terminal_text = ctk.CTkTextbox(
            self.display_frame,
            fg_color="#0d0d0d",
            text_color="#00ff00",
            font=("Courier", 7)
        )
        self.terminal_text.pack(fill="both", expand=True)
        self.terminal_text.pack_forget()
        
        # Status bar
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Status: Ready",
            text_color="#888888",
            font=("Helvetica", 10)
        )
        self.status_label.pack(pady=5)
    
    def start_camera(self):
        if not self.running:
            self.cap = cv2.VideoCapture(0)
            self.running = True
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.status_label.configure(text="Status: Camera running")
            
            thread = threading.Thread(target=self.camera_loop, daemon=True)
            thread.start()
    
    def stop_camera(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.image_label.configure(image="")
        self.terminal_text.delete("1.0", "end")
        self.status_label.configure(text="Status: Stopped")
    
    def toggle_terminal_view(self):
        self.terminal_mode = not self.terminal_mode
        if self.terminal_mode:
            self.image_label.pack_forget()
            self.terminal_text.pack(fill="both", expand=True)
            self.toggle_terminal.configure(text="Toggle Camera View")
            self.status_label.configure(text="Status: Terminal View ON")
        else:
            self.terminal_text.pack_forget()
            self.image_label.pack(fill="both", expand=True)
            self.toggle_terminal.configure(text="Toggle Terminal View")
            self.status_label.configure(text="Status: Camera View ON")
    
    def frame_to_ascii(self, frame, width=180, height=55):
        # Resize frame using higher-quality interpolation
        frame_resized = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LANCZOS4)
        frame_resized = cv2.detailEnhance(frame_resized, sigma_s=15, sigma_r=0.3)
        
        # Convert to grayscale and boost contrast
        gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        
        # ASCII characters from dark to light
        ascii_chars = "@%#*+=-:.~ `"
        
        # Convert pixels to ASCII
        ascii_art = ""
        for row in gray:
            for pixel in row:
                ascii_art += ascii_chars[int((pixel / 255) * (len(ascii_chars) - 1))]
            ascii_art += "\n"
        
        return ascii_art
    
    def enhance_frame(self, frame):
        # Detail enhancement and color improvement
        enhanced = cv2.detailEnhance(frame, sigma_s=10, sigma_r=0.15)
        lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        lab = cv2.merge((l, a, b))
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        hsv = cv2.cvtColor(enhanced, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        s = np.clip(s.astype(np.int16) + 20, 0, 255).astype(np.uint8)
        v = np.clip(v.astype(np.int16) + 10, 0, 255).astype(np.uint8)
        hsv = cv2.merge((h, s, v))
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    def camera_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            
            if ret:
                # Flip frame horizontally
                frame = cv2.flip(frame, 1)
                
                if self.terminal_mode:
                    # ASCII art mode
                    ascii_art = self.frame_to_ascii(frame, 180, 55)
                    self.terminal_text.delete("1.0", "end")
                    self.terminal_text.insert("1.0", ascii_art)
                else:
                    # Normal camera mode
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    img = img.resize((1160, 680), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    
                    self.image_label.configure(image=photo)
                    self.image_label.image = photo
                
                self.root.after(0)  # ~60 FPS

if __name__ == "__main__":
    root = ctk.CTk()
    app = CameraApp(root)
    root.mainloop()
