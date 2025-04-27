import tkinter as tk
from tkinter import messagebox
import pickle
import os
from access_pin import App  # Import App from access_pin.py

# Constants
TERMS_FILE = "terms_accepted.pkl"

# Styles
APP_WIDTH, APP_HEIGHT = 1000, 600
BACKGROUND_COLOR = "#134B70"
BUTTON_COLOR = "#508C9B"
WHITE = "#ffffff"
TEXT_COLOR = "#ffffff"
BUTTON_FONT = ("Arial", 12, "bold")
HEADER_FONT = ("Arial", 20, "bold")
SMALL_FONT = ("Arial", 12)

# Load and Save Terms Functions
def load_terms():
    """Load the terms accepted status."""
    if os.path.exists(TERMS_FILE):
        with open(TERMS_FILE, "rb") as file:
            return pickle.load(file)
    return False

def save_terms():
    """Save the terms accepted status."""
    with open(TERMS_FILE, "wb") as file:
        pickle.dump(True, file)

# Terms and Conditions Screen
class TermsApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window Settings
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.title("PawFeeder: Terms and Conditions")
        self.configure(bg=BACKGROUND_COLOR)
        self.resizable(False, False)

        # Center the window
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - APP_WIDTH) // 2
        y = (screen_height - APP_HEIGHT) // 2
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}+{x}+{y}")

        # Icon
        try:
            img = tk.PhotoImage(file='icons/pawfeeder.png')
            self.iconphoto(False, img)
        except Exception as e:
            print("Icon not found:", e)

        # Terms Title
        tk.Label(self, text="Terms and Conditions", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=HEADER_FONT).pack(pady=20)

        # Terms Text (make it scrollable)
        terms_frame = tk.Frame(self, bg=BACKGROUND_COLOR)
        terms_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.text = tk.Text(terms_frame, wrap="word", bg="white", fg="black", font=SMALL_FONT, relief="solid", bd=2)
        self.text.insert("1.0", self.get_terms_text())
        self.text.configure(state="disabled")
        self.text.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(terms_frame, command=self.text.yview)
        scrollbar.pack(side="right", fill="y")
        self.text.config(yscrollcommand=scrollbar.set)

        # Accept Button
        accept_btn = tk.Button(self, text="I Accept", command=self.accept_terms,
                               bg=BUTTON_COLOR, fg=WHITE, font=BUTTON_FONT,
                               activebackground="#417882", activeforeground=WHITE,
                               bd=0, relief="flat", padx=20, pady=10, cursor="hand2")
        accept_btn.pack(pady=20)

    def get_terms_text(self):
        # Replace with actual terms
        return (
            "Welcome to PawFeeder!\n\n"
            "Please read the following terms carefully before using this application.\n\n"
            "1. This system is intended for personal use only.\n"
            "2. The developers are not responsible for any damage to pets or property.\n"
            "3. Use at your own risk.\n"
            "4. By clicking 'I Accept', you agree to abide by all terms and conditions listed here.\n\n"
            "Thank you for choosing PawFeeder!"
        )

    def accept_terms(self):
        save_terms()  # Save terms as accepted
        self.destroy()  # Close Terms window
        self.show_pin_screen()

    def show_pin_screen(self):
        """Show the App (PIN screen) after accepting terms."""
        app = App()  # Open the App from access_pin.py
        app.mainloop()

if __name__ == "__main__":
    if load_terms():  # If terms are accepted, show the PIN screen
        app = App()  # Open the PIN setup screen
        app.mainloop()
    else:
        app = TermsApp()  # If terms are not accepted, show the Terms screen
        app.mainloop()
