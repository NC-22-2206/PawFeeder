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
            self.show_frame(RegisterEmailScreen)
        elif stored_pin is None:
            self.show_frame(SetPinScreen)
        else:
            self.show_frame(LoginScreen)

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


# --- Register Email ---
class RegisterEmailScreen(BaseFrame):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.create_label("Register Your Email", font=HEADER_FONT, pady=40).pack(anchor=tk.W)
        self.email_label = self.create_label("Enter your email address:")
        self.email_label.pack(pady=5, ipadx=0, ipady=0, anchor=tk.W)
        self.email_entry = self.create_entry()
        self.email_entry.pack(fill="x", pady=5, anchor=tk.W)

        self.register_button = self.create_button("Register", self.register_email)
        self.register_button.pack(pady=10, anchor=tk.CENTER)

        self.otp_label = self.create_label("Enter OTP:")
        self.otp_entry = self.create_entry()
        self.verify_otp_button = self.create_button("Verify OTP", self.verify_email)

    def register_email(self):
        email = self.email_entry.get()
        if not email:
            messagebox.showerror("Error", "Please enter your email address.")
            return

        otp = "".join(str(random.randint(0, 9)) for _ in range(6))
        expiry_time = time.time() + OTP_EXPIRY
        save_data({"otp": otp, "expiry": expiry_time, "email": email}, OTP_FILE)
        send_otp_email(email, otp)

        self.otp_label.pack(pady=5, ipadx=0, ipady=0, anchor=tk.W)
        self.otp_entry.pack(fill="x", pady=5, anchor=tk.W)
        self.verify_otp_button.pack(pady=10, anchor=tk.CENTER)
        self.register_button.config(state="disabled")

    def verify_email(self):
        entered_otp = self.otp_entry.get()
        stored_otp_data = load_data(OTP_FILE)

        if not stored_otp_data:
            messagebox.showerror("Error", "No OTP found. Please register again.")
            return

        if time.time() > stored_otp_data["expiry"]:
            messagebox.showerror("Error", "OTP expired. Please register again.")
            os.remove(OTP_FILE)
            return

        if entered_otp == stored_otp_data["otp"]:
            save_data(stored_otp_data["email"], EMAIL_FILE)
            messagebox.showinfo("Success", "Email verified!")
            self.app.show_login_or_set_pin()
        else:
            messagebox.showerror("Error", "Incorrect OTP.")


# --- Set PIN ---
class SetPinScreen(BaseFrame):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.create_label("Set a New 6-digit PIN", font=HEADER_FONT, pady=20).pack()
        self.pin_entry = self.create_entry(show="*")
        self.pin_entry.pack(pady=10)

        self.create_label("Confirm PIN", font=HEADER_FONT, pady=10).pack()
        self.confirm_entry = self.create_entry(show="*")
        self.confirm_entry.pack(pady=10)

        self.create_button("Save PIN", self.save_new_pin).pack(pady=20)

    def save_new_pin(self):
        pin, confirm = self.pin_entry.get(), self.confirm_entry.get()
        if not (pin.isdigit() and len(pin) == 6):
            messagebox.showwarning("Invalid PIN", "PIN must be exactly 6 digits.")
            return
        if pin != confirm:
            messagebox.showerror("Mismatch", "PIN entries do not match.")
            return
        save_data(pin, PIN_FILE)
        messagebox.showinfo("Success", "PIN set successfully!")
        self.app.show_login_or_set_pin()


# --- Login ---
class LoginScreen(BaseFrame):
    def setup_ui(self):
        super().setup_ui()
        self.title = self.create_label("Enter Your PIN", font=HEADER_FONT)
        self.title.pack(pady=(0, 30))

        self.pin_entry = self.create_entry(show="*")
        self.pin_entry.pack(pady=10, ipadx=10, ipady=6)

        self.login_button = self.create_button("Login", self.check_pin)
        self.login_button.pack(pady=20)

        self.forgot_button = self.create_button("Forgot PIN?", self.show_forgot_pin)
        self.forgot_button.pack()
    
    def check_pin(self):
        if load_data(PIN_FILE) == self.pin_entry.get():
            self.app.login_successful()
        else:
            messagebox.showerror("Incorrect", "Wrong PIN.")


# --- Forgot PIN ---
class ForgotPasswordScreen(BaseFrame):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.create_label("Verify Your Email", font=HEADER_FONT, pady=20).pack()
        self.create_label("Enter your registered email:").pack()
        self.email_entry = self.create_entry()
        self.email_entry.pack(pady=5)

        self.send_otp_button = self.create_button("Send OTP", self.send_verification_otp)
        self.send_otp_button.pack(pady=10)

        self.otp_label = self.create_label("Enter OTP:")
        self.otp_entry = self.create_entry()
        self.verify_otp_button = self.create_button("Verify OTP", self.verify_otp)

    def send_verification_otp(self):
        email = self.email_entry.get()
        stored_email = load_data(EMAIL_FILE)
        if email != stored_email:
            messagebox.showerror("Error", "Email does not match registered.")
            return
        otp = "".join(str(random.randint(0, 9)) for _ in range(6))
        save_data({"otp": otp, "expiry": time.time() + OTP_EXPIRY}, OTP_FILE)
        send_otp_email(email, otp)
        self.otp_label.pack()
        self.otp_entry.pack(pady=5)
        self.verify_otp_button.pack(pady=10)
        self.send_otp_button.config(state="disabled")

    def verify_otp(self):
        entered = self.otp_entry.get()
        data = load_data(OTP_FILE)
        if not data or time.time() > data["expiry"]:
            messagebox.showerror("Error", "OTP expired or not found.")
            return
        if entered == data["otp"]:
            messagebox.showinfo("Success", "Email verified. Reset your PIN.")
            self.app.show_frame(ResetPinScreen)
        else:
            messagebox.showerror("Error", "Incorrect OTP.")


# --- Reset PIN ---
class ResetPinScreen(BaseFrame):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.create_label("Reset Your PIN", font=HEADER_FONT, pady=20).pack()
        self.create_label("New 6-digit PIN:").pack()
        self.new_pin_entry = self.create_entry(show="*")
        self.new_pin_entry.pack()

        self.create_label("Confirm PIN:").pack()
        self.confirm_entry = self.create_entry(show="*")
        self.confirm_entry.pack()

        self.create_button("Reset PIN", self.reset_pin).pack(pady=20)

    def reset_pin(self):
        new, confirm = self.new_pin_entry.get(), self.confirm_entry.get()
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


# --- Entry Point ---
if __name__ == "__main__":
    if show_pin_verification():
        print("Access granted!")
    else:
        print("Access denied or cancelled.")
