import tkinter as tk
from tkinter import messagebox
import pickle
import os

# Constants
PIN_FILE = "pkl/pin_code.pkl"

# Styles
APP_WIDTH, APP_HEIGHT = 400, 300
BACKGROUND_COLOR = "#134B70"
BUTTON_COLOR = "#508C9B"
WHITE = "#ffffff"
TEXT_COLOR = "#ffffff"
BUTTON_FONT = ("Arial", 12, "bold")
HEADER_FONT = ("Arial", 16, "bold")
SMALL_FONT = ("Arial", 12)

# --- Functions to Load and Save PIN ---

def load_pin():
    if os.path.exists(PIN_FILE):
        with open(PIN_FILE, "rb") as file:
            return pickle.load(file)
    return None

def save_pin(pin):
    with open(PIN_FILE, "wb") as file:
        pickle.dump(pin, file)

# --- Access PIN Window Logic ---

def show_pin_verification():
    """Shows the PIN entry window and returns True if successful, False otherwise."""
    root = tk.Tk()
    app = App(root)
    root.mainloop()
    return app.login_success

# --- App class ---

class App:
    def __init__(self, master):
        self.master = master
        self.master.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.master.title("PawFeeder: Access PIN")
        self.master.configure(bg=BACKGROUND_COLOR)
        self.master.resizable(False, False)

        # Center the window
        self.center_window()

        # Set Icon
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
        stored_pin = load_pin()
        if stored_pin is None:
            self.show_frame(SetPinScreen)
        else:
            self.show_frame(LoginScreen)

    def login_successful(self):
        self.login_success = True
        self.master.destroy()

# --- Base Frame ---

class BaseFrame(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=BACKGROUND_COLOR)
        self.app = app

    def create_label(self, text, font=SMALL_FONT, pady=5):
        return tk.Label(self, text=text, bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=font, pady=pady)

    def create_entry(self, show=None):
        return tk.Entry(self, show=show, font=SMALL_FONT, bd=2, relief="solid")

    def create_button(self, text, command):
        return tk.Button(self, text=text, command=command,
                         bg=BUTTON_COLOR, fg=WHITE, font=BUTTON_FONT,
                         activebackground="#417882", activeforeground=WHITE,
                         bd=0, relief="flat", padx=10, pady=5, cursor="hand2")

# --- Set PIN Screen ---

class SetPinScreen(BaseFrame):
    def __init__(self, master, app):
        super().__init__(master, app)

        self.create_label("Set a New 4-digit PIN", font=HEADER_FONT, pady=20).pack(pady=5, ipadx=0, ipady=0, anchor=tk.W)
        self.pin_entry = self.create_entry(show="*")
        self.pin_entry.pack(fill="x", pady=5, anchor=tk.W)

        self.create_label("Confirm PIN", font=HEADER_FONT, pady=10).pack(pady=5, ipadx=0, ipady=0, anchor=tk.W)
        self.confirm_entry = self.create_entry(show="*")
        self.confirm_entry.pack(fill="x", pady=5, anchor=tk.W)

        self.create_button("Save PIN", self.save_new_pin).pack(pady=10, anchor=tk.CENTER)

    def save_new_pin(self):
        new_pin = self.pin_entry.get()
        confirm_pin = self.confirm_entry.get()

        if not (new_pin.isdigit() and len(new_pin) == 4):
            messagebox.showwarning("Invalid PIN", "PIN must be exactly 4 digits.")
            return

        if new_pin != confirm_pin:
            messagebox.showerror("Mismatch", "PIN entries do not match.")
            return

        save_pin(new_pin)
        messagebox.showinfo("Success", "PIN set successfully!")
        self.app.show_login_or_set_pin()

# --- Login Screen ---

class LoginScreen(BaseFrame):
    def __init__(self, master, app):
        super().__init__(master, app)

        self.create_label("Enter PIN to Continue", font=HEADER_FONT, pady=30).pack()
        self.pin_entry = self.create_entry(show="*")
        self.pin_entry.pack(pady=10)

        self.create_button("Login", self.check_pin).pack(pady=10)
        self.create_button("Forgot PIN? Reset", self.reset_pin).pack(pady=10)

    def check_pin(self):
        entered_pin = self.pin_entry.get()
        stored_pin = load_pin()

        if stored_pin == entered_pin:
            self.app.login_successful()
        else:
            messagebox.showerror("Incorrect", "Wrong PIN. Try again.")

    def reset_pin(self):
        answer = messagebox.askyesno("Reset PIN", "Are you sure you want to reset your PIN?")
        if answer:
            save_pin(None)
            messagebox.showinfo("Reset", "PIN has been reset. Set a new PIN.")
            self.app.show_login_or_set_pin()

# --- Main Testing Entry Point (Only runs when this file is run directly) ---

if __name__ == "__main__":
    if show_pin_verification():
        print("PIN verified successfully!")
    else:
        print("PIN verification failed or cancelled.")
