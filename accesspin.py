import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
import pickle
import os
import random
import smtplib
import subprocess
from email.message import EmailMessage
from dotenv import load_dotenv
import time
import re
import hashlib


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
RECOVERY_WAIT_TIME = 120 # 2 minutes

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

def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()


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
        
        if self.login_success:
            try:
                subprocess.Popen(["python", "Pawfeeder.py"])
            except Exception as e:
                print(f"Failed to start Pawfeeder.py: {e}")



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

    def create_entry(self, show=None, **kwargs):
        return tk.Entry(
            self.container,
            show=show,
            font=ENTRY_FONT,
            bd=1,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#ccc",
            highlightcolor="#3AA6B9",
            justify='left',
            **kwargs
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
            width=15
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

        self.otp_label.pack_forget()
        self.otp_entry.pack_forget()
        self.verify_otp_button.pack_forget()

        self.resend_timer = None  # To store the timer ID

    def register_email(self):
        email = self.email_entry.get()
        if not email:
            messagebox.showerror("Error", "Please enter your email address.")
            return

        otp = "".join(str(random.randint(0, 9)) for _ in range(6))
        expiry_time = time.time() + OTP_EXPIRY
        save_data({"otp": otp, "expiry": expiry_time, "email": email}, OTP_FILE)
        try:
            send_otp_email(email, otp)
            self.otp_label.pack(pady=5, ipadx=0, ipady=0, anchor=tk.W)
            self.otp_entry.pack(fill="x", pady=5, anchor=tk.W)
            self.verify_otp_button.pack(pady=10, anchor=tk.CENTER)
            self.register_button.config(state="disabled", text="Resend OTP (2:00)")
            self.start_resend_timer(RECOVERY_WAIT_TIME) # Start timer
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send OTP. Please check your internet connection or try again later. Error: {e}")
            self.enable_resend_button() #re-enable button

    def verify_email(self):
        entered_otp = self.otp_entry.get()
        stored_otp_data = load_data(OTP_FILE)

        if not stored_otp_data:
            messagebox.showerror("Error", "No OTP found. Please register again.")
            self.enable_resend_button()
            return

        if time.time() > stored_otp_data["expiry"]:
            messagebox.showerror("Error", "OTP expired. Please register again.")
            os.remove(OTP_FILE)
            self.enable_resend_button()
            return

        if entered_otp == stored_otp_data["otp"]:
            save_data(stored_otp_data["email"], EMAIL_FILE)
            messagebox.showinfo("Success", "Email verified!")
            self.app.show_login_or_set_pin()
        else:
            messagebox.showerror("Error", "Incorrect OTP.")

    def start_resend_timer(self, duration):
        self.remaining_time = duration
        self.update_resend_button_text()
        self.resend_timer = self.master.after(1000, self.update_timer)

    def update_timer(self):
        self.remaining_time -= 1
        self.update_resend_button_text()
        if self.remaining_time <= 0:
            self.enable_resend_button()
        else:
            self.resend_timer = self.master.after(1000, self.update_timer)

    def update_resend_button_text(self):
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.register_button.config(text=f"Resend OTP ({minutes}:{seconds:02d})")

    def enable_resend_button(self):
        self.register_button.config(state="normal", text="Resend OTP", command=self.register_email)
        if self.resend_timer:
            self.master.after_cancel(self.resend_timer)
            self.resend_timer = None

    def is_valid_email(email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)



class SetPinScreen(BaseFrame):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.create_label("Set Your New PIN", font=HEADER_FONT, pady=40).pack(anchor=tk.W)
        vcmd = (self.register(self.validate_pin_input), "%P")

        # PIN Label and Entry
        self.pin_label = self.create_label("Enter New 6-digit PIN:")
        self.pin_label.pack(pady=5, ipadx=0, ipady=0, anchor=tk.W)

        # Frame for PIN Entry
        pin_frame = tk.Frame(self.container, bg="#F0F4F8")
        pin_frame.pack(fill="x", pady=5, anchor=tk.W)

        self.pin_entry = tk.Entry(pin_frame, show="*", font=ENTRY_FONT, bd=1, relief="flat",
                                  highlightthickness=1, highlightbackground="#ccc", highlightcolor="#3AA6B9", justify='center', validate="key", validatecommand=vcmd)
        self.pin_entry.pack(side="left", fill="x", expand=True, pady=10, padx=10)

        self.eye_icon = PhotoImage(file="icons/visibility_off.png")
        self.eye_icon_open = PhotoImage(file="icons/visibility.png")

        self.eye_button = tk.Button(pin_frame, image=self.eye_icon, command=self.toggle_password, bd=0, bg="#F0F4F8", activebackground="#F0F4F8")
        self.eye_button.pack(side="right", padx=5)

        # Confirm PIN Label and Entry
        self.cpin_label = self.create_label("Confirm New PIN")
        self.cpin_label.pack(pady=5, ipadx=0, ipady=0, anchor=tk.W)

        # Frame for Confirm PIN Entry
        cpin_frame = tk.Frame(self.container, bg="#F0F4F8")
        cpin_frame.pack(fill="x", pady=5, anchor=tk.W)

        self.confirm_entry = tk.Entry(cpin_frame, show="*", font=ENTRY_FONT, bd=1, relief="flat",
                                      highlightthickness=1, highlightbackground="#ccc", highlightcolor="#3AA6B9", justify='center', validate="key", validatecommand=vcmd)
        self.confirm_entry.pack(side="left", fill="x", expand=True, pady=10, padx=10)

        self.ceye_button = tk.Button(cpin_frame, image=self.eye_icon, command=self.toggle_confirm_password, bd=0, bg="#F0F4F8", activebackground="#F0F4F8")
        self.ceye_button.pack(side="right", padx=5)

        # Save Button
        self.create_button("Save PIN", self.save_new_pin).pack(pady=10, anchor=tk.CENTER)

    def toggle_password(self):
        if self.pin_entry.cget("show") == "*":
            self.pin_entry.config(show="")
            self.eye_button.config(image=self.eye_icon_open)
        else:
            self.pin_entry.config(show="*")
            self.eye_button.config(image=self.eye_icon)

    def toggle_confirm_password(self):
        if self.confirm_entry.cget("show") == "*":
            self.confirm_entry.config(show="")
            self.ceye_button.config(image=self.eye_icon_open)
        else:
            self.confirm_entry.config(show="*")
            self.ceye_button.config(image=self.eye_icon)

    def save_new_pin(self):
        pin = self.pin_entry.get()
        confirm = self.confirm_entry.get()

        if not (pin.isdigit() and len(pin) == 6):
            messagebox.showwarning("Invalid PIN", "PIN must be exactly 6 digits.")
            return
        if pin != confirm:
            messagebox.showerror("Mismatch", "PIN entries do not match.")
            return

        save_data(pin, PIN_FILE)
        messagebox.showinfo("Success", "PIN set successfully!")
        self.app.show_login_or_set_pin()

    def validate_pin_input(self, new_value):
        return new_value.isdigit() and len(new_value) <= 6 or new_value == ""

class LoginScreen(BaseFrame):
    def setup_ui(self):
        super().setup_ui()
        
        # Title label for the screen
        self.title = self.create_label("Enter Your PIN", font=HEADER_FONT)
        self.title.pack(pady=40, anchor=tk.W)

        # Validation: Only allow digits and up to 6 characters
        vcmd = (self.register(self.validate_pin_input), "%P")
        
        # Frame for PIN Entry
        pin_frame = tk.Frame(self.container, bg="#F0F4F8")
        pin_frame.pack(fill="x", pady=5, anchor=tk.W)
        
        # PIN entry field
        self.pin_entry = tk.Entry(pin_frame, show="*", font=ENTRY_FONT, bd=1, relief="flat",
                                   highlightthickness=1, highlightbackground="#ccc", highlightcolor="#3AA6B9", 
                                   justify='center', validate="key", validatecommand=vcmd)
        self.pin_entry.pack(side="left", fill="x", expand=True, pady=10, padx=10)
        
        # Eye icon images for show/hide toggle
        self.eye_icon = PhotoImage(file="icons/visibility_off.png")
        self.eye_icon_open = PhotoImage(file="icons/visibility.png")
        
        # Eye toggle button to show/hide PIN
        self.eye_button = tk.Button(pin_frame, image=self.eye_icon, command=self.toggle_password, bd=0, 
                                    bg="#F0F4F8", activebackground="#F0F4F8")
        self.eye_button.pack(side="right", padx=5)

        # Login button
        self.login_button = self.create_button("Login", self.check_pin)
        self.login_button.pack(pady=20)
        
        # Forgot PIN button
        self.forgot_button = self.create_button("Forgot PIN?", self.show_forgot_pin)
        self.forgot_button.pack()

    def toggle_password(self):
        """Toggle the visibility of the PIN entered."""
        if self.pin_entry.cget('show') == "*":
            self.pin_entry.config(show="")
            self.eye_button.config(image=self.eye_icon_open)  # Change icon to open
        else:
            self.pin_entry.config(show="*")
            self.eye_button.config(image=self.eye_icon)  # Change icon to closed

    def validate_pin_input(self, new_value):
        """Allow only digits and max 6 characters, and allow deletion (backspace)."""
        # Check if the new value is empty (allow deletion)
        if new_value == "":
            return True
        # Check if the new value consists only of digits and is at most 6 characters long
        return new_value.isdigit() and len(new_value) <= 6

    def check_pin(self):
        if load_data(PIN_FILE) == self.pin_entry.get():
            self.app.login_successful()
        else:
            messagebox.showerror("Incorrect", "Wrong PIN.")

    def show_forgot_pin(self):
        self.app.show_frame(ForgotPasswordScreen)


# --- Forgot PIN ---
class ForgotPasswordScreen(BaseFrame):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.create_label("Verify Your Email", font=HEADER_FONT, pady=40).pack(anchor=tk.W)
        self.create_label("Enter your registered email:").pack(pady=5, ipadx=0, ipady=0, anchor=tk.W)
        self.email_entry = self.create_entry()
        self.email_entry.pack(fill="x", pady=5, anchor=tk.W)

        self.send_otp_button = self.create_button("Send OTP", self.send_verification_otp)
        self.send_otp_button.pack(pady=10)

        self.otp_label = self.create_label("Enter OTP:")
        self.otp_entry = self.create_entry()
        self.verify_otp_button = self.create_button("Verify OTP", self.verify_otp)

        # Back Button
        self.back_button = self.create_button("Back", self.go_back)
        self.back_button.pack(pady=10)

        self.otp_label.pack_forget()
        self.otp_entry.pack_forget()
        self.verify_otp_button.pack_forget()

        self.resend_timer = None

    def send_verification_otp(self):
        email = self.email_entry.get()
        stored_email = load_data(EMAIL_FILE)
        if email != stored_email:
            messagebox.showerror("Error", "Email does not match registered.")
            return
        otp = "".join(str(random.randint(0, 9)) for _ in range(6))
        save_data({"otp": otp, "expiry": time.time() + OTP_EXPIRY}, OTP_FILE)
        try:
            send_otp_email(email, otp)
            self.otp_label.pack(pady=5, ipadx=0, ipady=0, anchor=tk.W)
            self.otp_entry.pack(fill="x", pady=5, anchor=tk.W)
            self.verify_otp_button.pack(pady=10)
            self.send_otp_button.config(state="disabled", text="Resend OTP (2:00)")
            self.start_resend_timer(RECOVERY_WAIT_TIME)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send OTP. Please check your internet connection or try again later. Error: {e}")
            self.enable_resend_button()  # Enable the button if sending fails

    def start_resend_timer(self, duration):
        self.remaining_time = duration
        self.update_resend_button_text()
        self.resend_timer = self.master.after(1000, self.update_timer)

    def update_timer(self):
        self.remaining_time -= 1
        self.update_resend_button_text()
        if self.remaining_time <= 0:
            self.enable_resend_button()
        else:
            self.resend_timer = self.master.after(1000, self.update_timer)

    def update_resend_button_text(self):
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.send_otp_button.config(text=f"Resend OTP ({minutes}:{seconds:02d})")

    def enable_resend_button(self):
        self.send_otp_button.config(state="normal", text="Resend OTP", command=self.send_verification_otp)
        if self.resend_timer:
            self.master.after_cancel(self.resend_timer)
            self.resend_timer = None

    def verify_otp(self):
        entered_otp = self.otp_entry.get()
        otp_data = load_data(OTP_FILE)
        if not otp_data or "otp" not in otp_data or "expiry" not in otp_data:
            messagebox.showerror("Error", "No OTP found or OTP expired.")
            self.enable_resend_button()
            return

        stored_otp = otp_data["otp"]
        expiry_time = otp_data["expiry"]

        if time.time() > expiry_time:
            messagebox.showerror("Error", "OTP has expired.")
            self.enable_resend_button()
            return

        if entered_otp == stored_otp:
            messagebox.showinfo("Success", "Email verified successfully!")
            self.app.show_frame(ResetPinScreen)
        else:
            messagebox.showerror("Error", "Invalid OTP.")

    def go_back(self):
        self.app.show_login_or_set_pin()


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
        print("PawFeeder System Launched!")
    else:
        print("Access denied or cancelled.")
