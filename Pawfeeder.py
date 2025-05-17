import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
import time
import threading
import serial
import subprocess
import sys
import os
import pickle
from datetime import datetime


# --- Serial Setup ---
try:
    arduino = serial.Serial('COM3', 9600, timeout=1)
    time.sleep(2)  # Allow Arduino to reset
except serial.SerialException:
    print("[ERROR] Cannot connect to Arduino on COM5")
    exit()


# --- Ask Arduino for current RTC time ---
arduino.reset_input_buffer()
arduino.write(b'GETTIME\n')
time.sleep(0.5)


while arduino.in_waiting:
    line = arduino.readline().decode(errors='ignore').strip()
    print("[ARDUINO RTC]:", line)




# --- Convert to 24h Format for RTC Schedule ---
def convert_to_24h_format(t):
    t = t.strip().upper().replace(" ", "")
    try:
        dt = datetime.strptime(t, "%I:%M%p")
        return dt.strftime("%H:%M:%S")
    except ValueError:
        print(f"[ERROR] Invalid time format: {t}")
        return None

# --- Confirm and Send Scheduled Times to Arduino ---
def confirm_schedule(event):
    selected = table.focus()
    if not selected:
        return


    values = table.item(selected, 'values')
    dog_type, age_size, meal_frequency, portion_per_meal, times_str = values


    response = messagebox.askyesno(
        "Confirm Schedule",
        f"Dog Type: {dog_type}\nAge/Size: {age_size}\nMeal Frequency: {meal_frequency}\n"
        f"Portion per Meal: {portion_per_meal}\nTime of Feeding: {times_str}\n\n"
        "Do you want to activate this schedule?"
    )


    if not response:
        return


    times_list = [t.strip() for t in times_str.split(',')]
    formatted_times = []


    for t in times_list:
        converted = convert_to_24h_format(t)
        if converted:
            formatted_times.append(converted)
        else:
            print(f"[WARN] Skipping invalid time: {t}")


    if formatted_times:
        command = "SCHEDULE:" + ",".join(formatted_times) + "\n"
        try:
            arduino.write(command.encode())
            print("[INFO] Sent to Arduino:", command.strip())
            schedule_label.config(text=", ".join(times_list))
            messagebox.showinfo("Schedule Activated", "Schedule has been sent to Arduino.")
        except Exception as e:
            print("[ERROR] Failed to send schedule:", e)
            messagebox.showerror("Error", "Failed to send schedule to Arduino.")
    else:
        print("[WARN] No valid times to send.")
        messagebox.showwarning("Invalid Times", "No valid feeding times found.")



# --- Read Serial Output from Arduino ---
def read_from_arduino():
    while True:
        if arduino.in_waiting:
            try:
                line = arduino.readline().decode(errors='ignore').strip()
                if line:
                    print("[ARDUINO]:", line)
            except Exception as e:
                print("[ERROR Reading Arduino]:", e)


threading.Thread(target=read_from_arduino, daemon=True).start()




def reset_schedule():
    confirm = messagebox.askyesno("Reset Schedule", "Are you sure you want to reset the feeding schedule?")
    if not confirm:
        return


    try:
        arduino.write(b'RESETSCH\n')
        print("[INFO] Sent 'RESETSCH' to Arduino")
        schedule_label.config(text="")
        messagebox.showinfo("Schedule Reset", "The feeding schedule has been reset.")
    except Exception as e:
        print("[ERROR] Failed to send reset command:", e)
        messagebox.showerror("Error", "Failed to reset schedule. Make sure Arduino is connected.")
















# --- Manual Feed Button Logic ---
def activate_manual_feed():
    confirm = messagebox.askyesno("Confirm Dispensing", "Are you sure you want to dispense dog food?")
    if not confirm:
        return


    def run():
        # Disable the button temporarily
        page3_button.config(state="disabled", disabledforeground="white")


        # Send the manual feed command
        arduino.write(b'D')
        print("[MANUAL] Sent 'D' to Arduino")


        time.sleep(5)  # Wait for servo action


        messagebox.showinfo("Manual Feed", "Your pet’s food has been dispensed.")


        # Re-enable the button
        root.after(300, lambda: page3_button.config(text="Dispense", state="normal"))


    threading.Thread(target=run, daemon=True).start()











# --- Setup Functions ---

def check_terms_accepted():
    """Checks if the terms and conditions have been accepted."""
    terms_file = "pkl/terms_accepted.pkl"
    if os.path.exists(terms_file):
        with open(terms_file, "rb") as f:
            return pickle.load(f)
    return False

def run_terms_acceptance():
    """Runs the terms.py script."""
    terms_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "terms.py")
    result = subprocess.run([sys.executable, terms_path])
    return result.returncode == 0

def run_pin_verification():
    """Runs the access_pin.py script."""
    access_pin_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "accesspin.py")
    result = subprocess.run([sys.executable, access_pin_path])
    return result.returncode == 0

# --- Check Terms and PIN ---

if __name__ == "__main__":
    if not check_terms_accepted():
        if not run_terms_acceptance():
            sys.exit()  # Exit if terms are not accepted

    if not run_pin_verification():
        sys.exit()  # Exit if PIN verification fails







    # --- Main App Starts Here ---

    root = tk.Tk()
    root.geometry('1000x600')
    root.title("PawFeeder: Automatic Dog Food Dispenser")
    root.resizable(True, True)

    # Set window icon
    img = PhotoImage(file='icons/pawfeeder.png')
    root.iconphoto(False, img)

    # Center the window
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    width, height = 1000, 600
    root.geometry(f"{width}x{height}+{(screen_width - width) // 2}+{(screen_height - height) // 2}")

    # --- Styling ---
    BACKGROUND_COLOR = "#134B70"
    BUTTON_COLOR = "#508C9B"
    WHITE = "#F0F4F8"
    BUTTON_FONT = ("Arial", 12, "bold")
    HEADER_FONT = ("Arial", 20, "bold")
    SMALL_FONT = ("Arial", 12)
    TABLE_FONT = ("Arial", 10)

    # --- Functions ---

    def start_feeding():
        main_page_frame.pack_forget()
        options_frame.pack(side=tk.LEFT, fill="y")
        options_frame.pack_propagate(False)

    def switch_to_page1():
        page3_frame.pack_forget()
        page1_frame.pack(fill="both", expand=True)

    def switch_to_page2():
        page1_frame.pack_forget()
        page3_frame.pack_forget()
        # Placeholder for page2_frame if needed

    def switch_to_page3():
        page1_frame.pack_forget()
        page3_frame.pack(fill="both", expand=True)

    def switch_to_main():
        page1_frame.pack_forget()
        page3_frame.pack_forget()
        options_frame.pack_forget()
        main_page_frame.pack(fill="both", expand=True)

    def update_time():
        current_time = time.strftime("%I:%M:%S %p")
        current_date = time.strftime("%A, %B %d, %Y")
        page1_time_label.config(text=current_time)
        page1_date_label.config(text=current_date)
        page3_time_label.config(text=current_time)
        page3_date_label.config(text=current_date)
        root.after(1000, update_time)

    # --- Layout Frames ---

    main_frame = tk.Frame(root)
    main_frame.pack(side=tk.RIGHT, fill="both", expand=True)

    # Main Page Frame
    main_page_frame = tk.Frame(main_frame, bg="#F0F4F8")
    main_page_frame.pack(fill="both", expand=True)

    # Main Logo
    main_logo_frame = tk.Frame(main_page_frame, bg="#F0F4F8")
    main_logo_frame.place(relx=0.5, rely=0.4, anchor="center")

    main_logo_icon = PhotoImage(file="icons/pawfeeder.png").subsample(2)
    main_logo_label = tk.Label(main_logo_frame, image=main_logo_icon, bg="#F0F4F8")
    main_logo_label.pack(pady=20)

    # Start Button
    start_button = tk.Button(
        main_page_frame, text="Start Feeding",font=BUTTON_FONT, bg="#134B70", fg="white",
        padx=15, pady=5, relief="flat", activebackground=BUTTON_COLOR, activeforeground="white",
        cursor="hand2", command=start_feeding
    )
    start_button.place(relx=0.5, rely=0.7, anchor="center")

    # Options Sidebar
    options_frame = tk.Frame(root, bg=BACKGROUND_COLOR, width=200, height=500)
    options_frame.pack_propagate(False)

    # Sidebar Logo
    logo_frame = tk.Frame(options_frame, bg=BACKGROUND_COLOR)
    logo_frame.pack(padx=10, pady=10, side=tk.TOP, anchor="w")

    logo_icon = PhotoImage(file="icons/pawfeeder.png").subsample(3)
    logo_label = tk.Label(logo_frame, image=logo_icon, bg=BACKGROUND_COLOR)
    logo_label.pack(pady=20)

    # Sidebar Buttons
    button_frame = tk.Frame(options_frame, bg=BACKGROUND_COLOR)
    button_frame.pack(side=tk.TOP, fill="both", expand=True)

    auto_feed_button = tk.Button(
        button_frame, text="AUTOMATIC FEED", font=BUTTON_FONT, bg=BACKGROUND_COLOR,
        fg=WHITE, relief="flat", activebackground=BUTTON_COLOR, padx=15, pady=15, command=switch_to_page1
    )
    auto_feed_button.pack(pady=5, fill="x")

    manual_feed_button = tk.Button(
        button_frame, text="MANUAL FEED", font=BUTTON_FONT, bg=BACKGROUND_COLOR,
        fg=WHITE, relief="flat", activebackground=BUTTON_COLOR, padx=15, pady=15, command=switch_to_page3
    )
    manual_feed_button.pack(pady=5, fill="x")

    exit_feed_button = tk.Button(
        button_frame, text="Exit", font=BUTTON_FONT, bg=BACKGROUND_COLOR,
        fg=WHITE, relief="flat", activebackground=BUTTON_COLOR, padx=15, pady=15, command=switch_to_main
    )
    exit_feed_button.pack(side="bottom", fill="x")

    # --- Page 1 (Automatic Feed) ---

    page1_frame = tk.Frame(main_frame, bg="#F0F4F8")
    page1_frame.pack_propagate(False)

    page1_label = tk.Label(page1_frame, text="Automatic Feed Setup", font=HEADER_FONT, fg="#2A3B5A", bg="#F0F4F8")
    page1_label.place(x=30, y=90)

    page1_label1 = tk.Label(page1_frame, text="Choose schedule", font=SMALL_FONT, fg="#2A3B5A", bg="#F0F4F8")
    page1_label1.place(x=30, y=125)

    page1_time_label = tk.Label(page1_frame, font=("Arial", 20, "bold"),  fg="#2A3B5A", bg="#F0F4F8")
    page1_time_label.place(x=30, y=20)

    page1_date_label = tk.Label(page1_frame, font=("Arial", 12), fg="#2A3B5A", bg="#F0F4F8")
    page1_date_label.place(x=30, y=50)

    schedule_set = tk.Label(page1_frame, text="Schedule Set:", font=("Arial", 10, "bold", "italic"),  fg="#2A3B5A", bg="#F0F4F8")
    schedule_set.place(x=30, y=460)

    schedule_label = tk.Label(page1_frame, text="", font=("Arial", 10, "bold", "italic"),  fg="#2A3B5A", bg="#F0F4F8")
    schedule_label.place(x=125, y=460)

    # Table Style
    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
    style.configure("Treeview", font=("Arial", 9), background="white", foreground="black", rowheight=30)
    style.map("Treeview", background=[("selected", BUTTON_COLOR)])

    # Table Widget
    columns = ("Dog Type", "Age/Size", "Meal Frequency", "Portion per Meal", "Time of Feeding")
    table = ttk.Treeview(page1_frame, columns=columns, show="headings", height=8)
    table.place(x=32, y=180)

    for col in columns:
        table.heading(col, text=col)

    table.column("Dog Type", width=100, anchor="center")
    table.column("Age/Size", width=130, anchor="center")
    table.column("Meal Frequency", width=130, anchor="center")
    table.column("Portion per Meal", width=135, anchor="center")
    table.column("Time of Feeding", width=235, anchor="center")

    # Sample Data
    rows = [
        ("Adult Dog", "Small (up to 20 lbs)", "2 times/day", "1/2-1 cup", "7:00 AM, 6:00 PM"),
        ("Adult Dog", "Medium (21-50 lbs)", "2 times/day", "1-2 cups", "7:00 AM, 6:00 PM"),
        ("Adult Dog", "Large (51-90 lbs)", "2 times/day", "2-3 cups", "7:00 AM, 6:00 PM"),
        ("Adult Dog", "Giant (91+ lbs)", "2 times/day", "3-4 cups", "7:00 AM, 6:00 PM"),
        ("Puppy", "Up to 4 months", "3-4 times/day", "1/4-1 cup", "7:00 AM, 12:00 PM, 5:00 PM, 6:00 PM"),
        ("Puppy", "4 to 6 months", "3 times/day", "1/2-1 cup", "7:00 AM, 12:00 PM, 5:00 PM"),
        ("Puppy", "6 months and older", "2 times/day", "1-2 cups", "9:28 PM, 9:30 PM"),
    ]
    for row in rows:
        table.insert("", "end", values=row)
    
    table.bind("<<TreeviewSelect>>", confirm_schedule)

    # Reset Schedule Button
    page1_reset_button = tk.Button(
        page1_frame,
        text="Reset Schedule",
        font=("Arial", 10, "bold"),
        fg="WHITE",
        bg="#508C9B",
        padx=15,
        pady=5,
        relief="flat",
        activebackground="#2E8C9B",
        command=reset_schedule 
    )
    page1_reset_button.place(relx=0.5, y=540, anchor="center")

    # --- Page 3 (Manual Feed) ---

    page3_frame = tk.Frame(main_frame, bg="#F0F4F8")
    page3_frame.pack_propagate(False)

    page3_label = tk.Label(page3_frame, text="Manual Feed Setup", font=HEADER_FONT, bg="#F0F4F8",  fg="#2A3B5A")
    page3_label.place(x=30, y=90)

    page3_label1 = tk.Label(page3_frame, text="Click button to dispense dog foods", font=SMALL_FONT, fg="#2A3B5A", bg="#F0F4F8")
    page3_label1.place(x=30, y=125)

    page3_time_label = tk.Label(page3_frame, font=("Arial", 20, "bold"), fg="#2A3B5A", bg="#F0F4F8")
    page3_time_label.place(x=30, y=20)

    page3_date_label = tk.Label(page3_frame, font=("Arial", 12), bg="#F0F4F8", fg="#2A3B5A")
    page3_date_label.place(x=30, y=50)

    # Dispense Button
    page3_button = tk.Button(
        page3_frame,
        text="Dispense",
        font=("Arial", 10, "bold"),
        bg="#508C9B",
        fg="white",
        disabledforeground="white",
        padx=15,
        pady=5,
        relief="flat",
        activebackground="white",
        command=activate_manual_feed
    )
    page3_button.place(relx=0.5, y=450, anchor="center")

    # --- Start Time Update ---
    update_time()

    # --- Main Loop ---
    root.mainloop()
