import customtkinter as ctk
import pyautogui
import threading
import time
import random
from datetime import datetime
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import sys
import os

class TeamsStatusKeeper(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Teams Status Keeper")
        self.geometry("450x650") 
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Variables
        self.is_active = False
        self.next_activity_seconds = 0
        self.total_interval = 0
        self.running = True
        self.min_interval = ctk.IntVar(value=30)
        self.max_interval = ctk.IntVar(value=90)
        self.always_on_top = ctk.BooleanVar(value=False)

        # UI Components
        self.title_label = ctk.CTkLabel(self, text="Teams Status Keeper", font=ctk.CTkFont(size=26, weight="bold"))
        self.title_label.pack(pady=(20, 10))

        # Status indicator
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.pack(pady=5)
        self.status_indicator = ctk.CTkLabel(self.status_frame, text="●", font=ctk.CTkFont(size=30), text_color="#ff4d4d")
        self.status_indicator.pack(side="left", padx=5)
        self.status_text = ctk.CTkLabel(self.status_frame, text="Status: Inactive", font=ctk.CTkFont(size=16))
        self.status_text.pack(side="left", padx=5)

        # Progress Section
        self.timer_label = ctk.CTkLabel(self, text="Next activity: --:--", font=ctk.CTkFont(size=14), text_color="#777777")
        self.timer_label.pack(pady=(10, 0))
        self.progress_bar = ctk.CTkProgressBar(self, width=350)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

        # Main Controls
        self.toggle_button = ctk.CTkButton(self, text="START ACTIVATOR", command=self.toggle_activator, 
                                           height=50, font=ctk.CTkFont(size=16, weight="bold"),
                                           fg_color="#3e3e42", hover_color="#4e4e52")
        self.toggle_button.pack(pady=(10, 10), padx=40, fill="x")

        # Settings Section
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(self.settings_frame, text="Settings", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        
        # Interval inputs
        interval_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        interval_frame.pack(pady=5)
        ctk.CTkLabel(interval_frame, text="Min (s):").pack(side="left", padx=5)
        ctk.CTkEntry(interval_frame, textvariable=self.min_interval, width=60).pack(side="left", padx=5)
        ctk.CTkLabel(interval_frame, text="Max (s):").pack(side="left", padx=5)
        ctk.CTkEntry(interval_frame, textvariable=self.max_interval, width=60).pack(side="left", padx=5)

        # Always on top
        self.top_toggle = ctk.CTkSwitch(self.settings_frame, text="Always on Top", variable=self.always_on_top, command=self.update_topmost)
        self.top_toggle.pack(pady=10)

        # Log Section
        ctk.CTkLabel(self, text="Activity Log", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 0))
        self.log_textbox = ctk.CTkTextbox(self, height=120, width=400, font=ctk.CTkFont(size=11))
        self.log_textbox.pack(pady=10, padx=20)
        self.log_textbox.configure(state="disabled")

        # Tray setup
        self.tray_icon = None
        self.setup_tray()
        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

        # Start timer thread
        self.timer_thread = threading.Thread(target=self.activity_loop, daemon=True)
        self.timer_thread.start()

    def update_topmost(self):
        self.attributes("-topmost", self.always_on_top.get())

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"[{timestamp}] {message}\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def toggle_activator(self):
        self.is_active = not self.is_active
        if self.is_active:
            self.reset_timer()
            self.toggle_button.configure(text="STOP ACTIVATOR", fg_color="#e81123", hover_color="#ff1a1a")
            self.status_indicator.configure(text_color="#46d246")
            self.status_text.configure(text="Status: KEEPING ACTIVE", text_color="#46d246")
            self.log("Activator started")
        else:
            self.toggle_button.configure(text="START ACTIVATOR", fg_color="#3e3e42", hover_color="#4e4e52")
            self.status_indicator.configure(text_color="#ff4d4d")
            self.status_text.configure(text="Status: Inactive", text_color="white")
            self.timer_label.configure(text="Next activity: --:--")
            self.progress_bar.set(0)
            self.log("Activator stopped")

    def reset_timer(self):
        try:
            low = self.min_interval.get()
            high = self.max_interval.get()
            if low > high: low, high = high, low
        except:
            low, high = 30, 90
            
        self.next_activity_seconds = random.randint(low, high)
        self.total_interval = self.next_activity_seconds

    def activity_loop(self):
        while self.running:
            if self.is_active:
                if self.next_activity_seconds <= 0:
                    # 1. Simulate Keystrokes (Scroll Lock)
                    pyautogui.press('scrolllock')
                    time.sleep(0.1)
                    pyautogui.press('scrolllock')
                    
                    # 2. Simulate Mouse Movement (Subtle 1px move)
                    try:
                        curr_x, curr_y = pyautogui.position()
                        pyautogui.moveTo(curr_x + 1, curr_y, duration=0.1)
                        pyautogui.moveTo(curr_x, curr_y, duration=0.1)
                    except:
                        pass # Avoid crash if mouse is at screen edge
                        
                    self.log("Activity: Key + Mouse move")
                    self.reset_timer()
                
                self.next_activity_seconds -= 1
                
                # UI Updates
                minutes = max(0, self.next_activity_seconds // 60)
                seconds = max(0, self.next_activity_seconds % 60)
                self.timer_label.configure(text=f"Next activity in: {minutes:02d}:{seconds:02d}")
                
                if self.total_interval > 0:
                    progress = 1 - (self.next_activity_seconds / self.total_interval)
                    self.progress_bar.set(min(1, max(0, progress)))
            
            time.sleep(1)

    def setup_tray(self):
        # Create a simple icon
        image = Image.new('RGB', (64, 64), color=(30, 30, 30))
        d = ImageDraw.Draw(image)
        d.ellipse((10, 10, 54, 54), fill=(70, 210, 70))
        
        menu = (
            item('Show', self.show_window, default=True),
            item('Start/Stop', self.toggle_activator),
            item('Exit', self.exit_app)
        )
        self.tray_icon = pystray.Icon("Teams Status Keeper", image, "Teams Status Keeper", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def minimize_to_tray(self):
        self.withdraw()
        if self.tray_icon:
            self.tray_icon.visible = True

    def show_window(self):
        self.after(0, self.deiconify)

    def exit_app(self):
        self.running = False
        if self.tray_icon:
            self.tray_icon.stop()
        self.destroy()
        sys.exit()

if __name__ == "__main__":
    app = TeamsStatusKeeper()
    app.mainloop()
