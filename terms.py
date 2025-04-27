

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
    """Save that the terms were accepted."""
    with open(TERMS_FILE, "wb") as file:
        pickle.dump(True, file)

# Terms and Conditions Screen
class TermsApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window settings
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
            img = tk.PhotoImage(file="icons/pawfeeder.png")
            self.iconphoto(False, img)
        except Exception as e:
            print("Icon not found:", e)

        # Terms Title
        tk.Label(self, text="Terms and Conditions", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=HEADER_FONT).pack(pady=20)

        # Rounded frame for Terms Text
        rounded_frame = tk.Frame(self, bg=WHITE, bd=2, relief="groove")
        rounded_frame.pack(pady=10)

        inner_frame = tk.Frame(rounded_frame, bg=WHITE)
        inner_frame.pack(padx=10, pady=10)

        # Text widget inside rounded frame
        self.text = tk.Text(inner_frame,
                            wrap="word",
                            bg=WHITE,
                            fg="black",
                            font=SMALL_FONT,
                            relief="flat",
                            bd=0,
                            width=100,
                            height=22)
        self.text.insert("1.0", self.get_terms_text())
        self.text.configure(state="disabled")
        self.text.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        scrollbar = tk.Scrollbar(inner_frame, command=self.text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.text.config(yscrollcommand=scrollbar.set)

        # Accept Button
        accept_btn = tk.Button(self,
                               text="I Accept",
                               command=self.accept_terms,
                               bg=BUTTON_COLOR,
                               fg=WHITE,
                               font=BUTTON_FONT,
                               activebackground="#417882",
                               activeforeground=WHITE,
                               bd=0,
                               relief="groove",
                               padx=10,
                               pady=10,
                               cursor="hand2")
        accept_btn.pack(pady=20)

        # Hover effect
        accept_btn.bind("<Enter>", lambda e: accept_btn.config(bg="#417882"))
        accept_btn.bind("<Leave>", lambda e: accept_btn.config(bg=BUTTON_COLOR))

    def get_terms_text(self):
        return (
            "PawFeeder: Automatic Dog Food Dispenser\n\n"
        "Terms and Conditions\n\n"
        "Welcome to the PawFeeder. The terms and conditions will outline the rules and regulations for the use of the PawFeeder and by accessing this system, you accept these terms and conditions, and if you do not accept the terms and conditions, we advise you not to continue the use of the PawFeeder.\n\n"
        "The following statement is applied to the Terms and Conditions, Privacy Statement, and all the agreements. The \"user,\" \"you,\" and \"your\" refer to you as a person accessing and using the PawFeeder by accepting the PawFeeder’s terms and conditions. The \"PawFeeder team\" or \"we\" and \"our\" refer to the creators of PawFeeder, and \"party,\" \"parties,\" and \"us\" refer to both the user and ourselves.\n\n"
        "All terms refer to the offer, acceptance, and consideration undertaken in the process of our assistance to the user in the most appropriate manner, whether by formal meetings, fixed duration, or any other means, and for the express purpose of meeting the user’s needs in respect of the provision of the user’s stated services, in accordance with and subject to the prevailing law of the Philippines.\n\n"
        "Restrictions\n\n"
        "As a user of the PawFeeder system, you are specifically restricted from:\n"
        "- Using the system in any manner that may damage its operation, compromise its security, or interfere with the experience of other users.\n"
        "- Attempting to access areas of the system, data, or functionalities that are not intended for your use.\n"
        "- Extracting, sharing, reproducing, or distributing any information or content obtained from the PawFeeder without prior written authorization from the PawFeeder team.\n"
        "- Altering, modifying, decompiling, or creating secondary works based on any part of the PawFeeder system without permission from the PawFeeder team.\n"
        "- Using the system for any illegal activity or in violation of applicable laws and regulations.\n\n"
        "User Responsibility\n\n"
        "Any account credentials (e.g., data schedule, PIN code) associated with the PawFeeder system must be kept confidential. You are solely responsible for all activities conducted under your account and using your designated PIN. This includes, but is not limited to, the accuracy and appropriateness of feeding schedules, portion sizes, and any manual dispensing actions initiated through the system.\n\n"
        "It is your responsibility to ensure that only authorized individuals have access to the system's controls and any associated login information. PawFeeder is not responsible for any consequences resulting from the unauthorized access or misuse of your system or account credentials.\n\n"
        "Furthermore, you are responsible for regularly reviewing and verifying the system's settings and operation to ensure they align with your pet's needs and your intended use. This includes confirming the accuracy of scheduled feeding times and portion sizes.\n\n"
        "Your Privacy and Data\n\n"
        "Information\n\n"
        "PawFeeder values the user's privacy. The system will be collecting limited data, such as usage logs, feeding schedules, and device performance, for the purpose of improving the service. This data is not shared with third parties without your consent, except as required by law.\n\n"
        "Data Processing\n\n"
        "PawFeeder aims to operate and maintain the device in order to communicate updates regarding device safety and diagnosing technical issues. Users can personalize their data and feeding schedules.\n\n"
        "Rights\n\n"
        "Depending on your jurisdiction, you have the right to:\n"
        "- Access your data.\n"
        "- Withdraw consent at any time.\n"
        "- Request correction or deletion of data.\n\n"
        "Modifications to Terms\n\n"
        "The PawFeeder Team reserves the right, at its sole discretion, to amend, modify, update, or replace these Terms and Conditions at any time without prior notice. Such modifications shall become effective immediately upon being posted on our official platform or application or communicated through other reasonable means.\n\n"
        "It is your sole responsibility to review these Terms and Conditions periodically to remain informed of any updates. Your continued access to or use of the PawFeeder system following any modifications constitutes your binding acceptance of the updated Terms and Conditions. If you do not agree with any revised Terms, you must immediately cease all use of the PawFeeder system. Without liability to you or any third party, we may modify, suspend, or discontinue any aspect of the system, including features, functionality, or content, either temporarily or permanently, at any time and for any reason.\n\n"
        "Any changes to the dispute resolution provisions or governing law will not apply retroactively to disputes that arose before the effective date of such changes. The PawFeeder Team is not responsible for any failure to notify users individually about modifications, and any such failure shall not affect the enforceability of the updated Terms.\n\n"
        "Limitation of Liability\n\n"
        "We are not liable for:\n"
        "- Any direct or indirect damages arising from the use or misuse of the device.\n"
        "- Malfunctions due to improper handling or unauthorized modifications.\n"
        "- Feeding errors caused by external incidents such as power outages, Wi-Fi issues, or user input.\n"
        "- Any loss or corruption of data, including feeding schedules and system settings.\n"
        "- Any damages or losses resulting from unauthorized access to or use of your system or account credentials.\n\n"
        "Assignment\n\n"
        "We may assign, transfer, or subcontract our rights and obligations under these terms without notifying the user. Also, the users are not permitted to assign or transfer their rights without our consent.\n\n"
        "Entire Agreement\n\n"
        "These terms represent the comprehensive agreement between you and us regarding your utilization of this PawFeeder application, superseding all prior agreements and understandings.\n\n"
        "Governing Law and Jurisdiction\n\n"
        "This Agreement shall be governed by and construed in accordance with the laws of the Republic of the Philippines, without regard to its conflict of laws principles.\n\n"
        "Any dispute, controversy, or claim arising out of or in connection with this Agreement, including any question regarding its existence, validity, or termination, shall be submitted to the non-exclusive jurisdiction of the courts of Quezon City, Metropolitan Manila, Philippines.\n\n"
        "The parties hereby irrevocably consent to the personal jurisdiction and venue of such courts and waive any objection to such jurisdiction or venue on the grounds of inconvenient forum or otherwise.\n\n"
        )

    def accept_terms(self):
        """Handle acceptance of terms."""
        save_terms()
        self.destroy()
        self.show_pin_screen()

    def show_pin_screen(self):
        """Launch PIN app."""
        app = App()
        app.mainloop()

# Entry Point
if __name__ == "__main__":
    if load_terms():
        app = App()
        app.mainloop()
    else:
        app = TermsApp()
        app.mainloop()
