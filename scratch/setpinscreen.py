import tkinter as tk
from tkinter import messagebox
import pickle
import os
import random
import smtplib
import subprocess 
from email.message import EmailMessage
from dotenv import load_dotenv
import time
from tkinter import PhotoImage

load_dotenv()

try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except ImportError:
    pass

# Constants
PIN_FILE = "pkl/pin_code.pkl"
OTP_FILE = "pkl/otp.pkl"
EMAIL_FILE = "pkl/email.pkl"
OTP_EXPIRY = 120  # 2 minutes

EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    print("Error: EMAIL_ADDRESS and EMAIL_PASSWORD environment variables not set.")

# UI Constants
APP_WIDTH, APP_HEIGHT = 500, 600
BACKGROUND_COLOR = "#F0F4F8"
BUTTON_COLOR = "#134B70"
WHITE = "#ffffff"
TEXT_COLOR = "#2A3B5A"
HEADER_FONT = ("Segoe UI", 20, "bold")
LABEL_FONT = ("Segoe UI", 12)
ENTRY_FONT = ("Segoe UI", 12)
BUTTON_FONT = ("Segoe UI", 10, "bold")
SMALL_FONT = ("Segoe UI", 12)


# --- Data Handling ---
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, "rb") as file:
            return pickle.load(file)
    return None

def save_data(data, filename):
    with open(filename, "wb") as file:
        pickle.dump(data, file)


# --- Email Sending ---
def send_otp_email(to_email, otp):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        messagebox.showerror("Error", "Email configuration not found.")
        return

    subject = 'PawFeeder: OTP Verification'
    body = f'Your One-Time Password (OTP) is: {otp}\n\nThis OTP will expire in 2 minutes.'

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg.set_content(body)

        server.send_message(msg)
        messagebox.showinfo("Success", "OTP sent to your email address.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send OTP email: {e}")
    finally:
        if 'server' in locals():
            server.quit()


# --- App Launcher ---
def show_pin_verification():
    root = tk.Tk()
    app = App(root)
    root.mainloop()
    return app.login_success


# --- App ---
class App:
    def __init__(self, master):
        self.master = master
        self.master.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.master.title("PawFeeder: Access")
        self.master.configure(bg=BACKGROUND_COLOR)
        self.master.resizable(False, False)
        self.center_window()

        try:
            img = tk.PhotoImage(file='icons/pawfeeder.png')
            self.master.iconphoto(False, img)
        except Exception as e:
            print("Icon not found:", e)

        self.current_frame = None
        self.login_success = False
        self.show_login_or_set_pin()

    def center_window(self):
        self.master.update_idletasks()
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width - APP_WIDTH) // 2
        y = (screen_height - APP_HEIGHT) // 2
        self.master.geometry(f"{APP_WIDTH}x{APP_HEIGHT}+{x}+{y}")

    def show_frame(self, frame_class):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = frame_class(self.master, self)
        self.current_frame.pack(expand=True, fill="both")


    def show_login_or_set_pin(self):
        stored_email = load_data(EMAIL_FILE)
        stored_pin = load_data(PIN_FILE)
        if stored_email is None:
            self.show_frame(ResetPinScreen)
        elif stored_pin is None:
            self.show_frame(ResetPinScreen)
        else:
            self.show_frame(ResetPinScreen)

    def login_successful(self):
        self.login_success = True
        self.master.destroy()
        subprocess.Popen(["python", "testsystem.py"]) 


# --- Base Frame ---
class BaseFrame(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=BACKGROUND_COLOR)
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        # A centered container frame inside BaseFrame
        self.container = tk.Frame(self, bg=BACKGROUND_COLOR)
        self.container.pack(expand=True, fill="both", padx=40)

    def create_label(self, text, font=None, pady=10):
        return tk.Label(
            self.container,
            text=text,
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            font=font or LABEL_FONT,
            pady=pady
        )

    def create_entry(self, show=None):
        return tk.Entry(
            self.container,
            show=show,
            font=ENTRY_FONT,
            bd=1,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#ccc",
            highlightcolor="#3AA6B9",
            justify='left'
        )

    def create_button(self, text, command):
        return tk.Button(
            self.container,
            text=text,
            command=command,
            bg=BUTTON_COLOR,
            fg=WHITE,
            font=BUTTON_FONT,
            activebackground="#2E8C9B",
            activeforeground=WHITE,
            bd=0,
            relief="flat",
            padx=10,
            pady=5,
            cursor="hand2",
            width=10
        )








class ResetPinScreen(BaseFrame):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.create_label("Reset Your PIN", font=HEADER_FONT, pady=40).pack(anchor=tk.W)

        vcmd = (self.register(self.validate_pin_input), "%P")

        # Label for New PIN
        self.resetpin_label = self.create_label("Enter New 6-digit PIN:")
        self.resetpin_label.pack(pady=5, anchor=tk.W)

        # Frame for New PIN Entry
        resetpin_frame = tk.Frame(self.container, bg="#F0F4F8")
        resetpin_frame.pack(fill="x", pady=5, anchor=tk.W)

        self.resetpin_entry = tk.Entry(resetpin_frame, show="*", font=ENTRY_FONT, bd=1, relief="flat",
                                       highlightthickness=1, highlightbackground="#ccc", highlightcolor="#3AA6B9",
                                       justify='center', validate="key", validatecommand=vcmd)
        self.resetpin_entry.pack(side="left", fill="x", expand=True, pady=10, padx=10)

        self.eye_icon = PhotoImage(file="icons/visibility_off.png")
        self.eye_icon_open = PhotoImage(file="icons/visibility.png")

        self.eye_button = tk.Button(resetpin_frame, image=self.eye_icon, command=self.toggle_password,
                                    bd=0, bg="#F0F4F8", activebackground="#F0F4F8")
        self.eye_button.pack(side="right", padx=5)

        # Label for Confirm PIN
        self.crpin_label = self.create_label("Confirm New PIN")
        self.crpin_label.pack(pady=5, anchor=tk.W)

        # Frame for Confirm PIN Entry
        crpin_frame = tk.Frame(self.container, bg="#F0F4F8")
        crpin_frame.pack(fill="x", pady=5, anchor=tk.W)

        self.confirmr_entry = tk.Entry(crpin_frame, show="*", font=ENTRY_FONT, bd=1, relief="flat",
                                       highlightthickness=1, highlightbackground="#ccc", highlightcolor="#3AA6B9",
                                       justify='center', validate="key", validatecommand=vcmd)
        self.confirmr_entry.pack(side="left", fill="x", expand=True, pady=10, padx=10)

        self.ceye_button = tk.Button(crpin_frame, image=self.eye_icon, command=self.toggle_confirm_password,
                                     bd=0, bg="#F0F4F8", activebackground="#F0F4F8")
        self.ceye_button.pack(side="right", padx=5)

        # Reset Button
        self.create_button("Reset PIN", self.reset_pin).pack(pady=20)

    def toggle_password(self):
        if self.resetpin_entry.cget("show") == "*":
            self.resetpin_entry.config(show="")
            self.eye_button.config(image=self.eye_icon_open)
        else:
            self.resetpin_entry.config(show="*")
            self.eye_button.config(image=self.eye_icon)

    def toggle_confirm_password(self):
        if self.confirmr_entry.cget("show") == "*":
            self.confirmr_entry.config(show="")
            self.ceye_button.config(image=self.eye_icon_open)
        else:
            self.confirmr_entry.config(show="*")
            self.ceye_button.config(image=self.eye_icon)

    def reset_pin(self):
        new = self.resetpin_entry.get()
        confirm = self.confirmr_entry.get()

        if not (new.isdigit() and len(new) == 6):
            messagebox.showwarning("Invalid PIN", "PIN must be 6 digits.")
            return
        if new != confirm:
            messagebox.showerror("Mismatch", "PINs do not match.")
            return

        save_data(new, PIN_FILE)

        if os.path.exists(OTP_FILE):
            os.remove(OTP_FILE)

        messagebox.showinfo("Success", "PIN reset successfully!")
        self.app.show_login_or_set_pin()

    def validate_pin_input(self, new_value):
        return new_value.isdigit() and len(new_value) <= 6 or new_value == ""

# --- Entry Point ---
if __name__ == "__main__":
    if show_pin_verification():
        print("Access granted!")
    else:
        print("Access denied or cancelled.")
