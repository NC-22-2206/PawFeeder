import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
import time
import threading
import serial
from datetime import datetime

# --- Serial Setup ---
try:
    arduino = serial.Serial('COM3', 9600, timeout=1)
    time.sleep(2)  # Allow Arduino to reset
except serial.SerialException:
    print("[ERROR] Cannot connect to Arduino on COM3")
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




# --- Custom Feed Button Logic ---
def activate_custom_feed():
    confirm = messagebox.askyesno("Confirm Dispensing", "Are you sure you want to dispense dog food?")
    if not confirm:
        return

    def run():
        # Disable the button temporarily
        custom_feed_button.config(state="disabled", disabledforeground="white")

        # Send the manual feed command
        arduino.write(b'D')
        print("[MANUAL] Sent 'D' to Arduino")

        time.sleep(5)  # Wait for servo action

        messagebox.showinfo("Manual Feed", "Your pet's food has been dispensed.")

        # Re-enable the button
        root.after(300, lambda: custom_feed_button.config(text="Dispense", state="normal"))

    threading.Thread(target=run, daemon=True).start()


# Function to validate custom time entry
def validate_time_entry(index):
    # Get the values from the time entry fields
    hour = custom_hour_vars[index].get()
    minute = custom_minute_vars[index].get()
    ampm = custom_ampm_vars[index].get()
    
    # Check if any of the time fields are empty
    if not hour or not minute or not ampm:
        # If time is not complete, show an error message
        messagebox.showwarning("Time Selection Required", "Please set a time first!")
        # Reset the checkbox state
        custom_time_active[index].set(False)
        return False
    
    return True


# Function to handle checkbox state changes
def on_checkbox_toggle(index):
    if custom_time_active[index].get():  # If checkbox is checked
        if not validate_time_entry(index):
            # The validation failed, checkbox will be unchecked by validate_time_entry
            pass
        else:
            # Checkbox is checked and time is valid
            # You can add additional logic here if needed
            pass

def confirm_custom_schedule():
    active_times = []

    # Collect active times
    for i in range(5):
        if custom_time_active[i].get():
            hour = custom_hour_vars[i].get()
            minute = custom_minute_vars[i].get()
            ampm = custom_ampm_vars[i].get()

            # Validate that time is set
            if not hour or not minute or not ampm:
                messagebox.showwarning("Invalid Time", f"Please set a complete time for Time {i+1}!")
                return

            active_times.append(f"{hour}:{minute} {ampm}")

    if not active_times:
        messagebox.showwarning("No Times Selected", "Please select at least one feeding time!")
        return

    # Ask for confirmation
    response = messagebox.askyesno(
        "Confirm Custom Schedule",
        f"Time of Feeding:\n{', '.join(active_times)}\n\nDo you want to activate this custom schedule?"
    )
    if not response:
        return

    # Convert to 24-hour format
    formatted_times = []
    for t in active_times:
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
            schedule_text = "Scheduled times: " + ", ".join(active_times)
            custom_schedule_label.config(text=schedule_text, fg="#008000")
            messagebox.showinfo("Schedule Activated", "Custom schedule has been sent to Arduino.")
        except Exception as e:
            print("[ERROR] Failed to send schedule:", e)
            messagebox.showerror("Error", "Failed to send custom schedule to Arduino.")
    else:
        print("[WARN] No valid times to send.")
        messagebox.showwarning("Invalid Times", "No valid feeding times found.")

def reset_custom_schedule():
    has_schedule = False

    # Check if any time slot has been set
    for i in range(5):
        if (custom_time_active[i].get() or
            custom_hour_vars[i].get() or
            custom_minute_vars[i].get() or
            custom_ampm_vars[i].get()):
            has_schedule = True
            break

    # Reset all time selections
    for i in range(5):
        custom_time_active[i].set(False)
        custom_hour_vars[i].set("")
        custom_minute_vars[i].set("")
        custom_ampm_vars[i].set("")

    # Reset the schedule display
    custom_schedule_label.config(text="No times scheduled yet", fg="#777777")

    if has_schedule:
        messagebox.showinfo("Schedule Reset", "Your custom feeding schedule has been reset!")
    else:
        messagebox.showinfo("No Schedule", "You have no custom feeding schedule set recently.")


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

        messagebox.showinfo("Manual Feed", "Your pet's food has been dispensed.")

        # Re-enable the button
        root.after(300, lambda: page3_button.config(text="Dispense", state="normal"))

    threading.Thread(target=run, daemon=True).start()


# Create the root window
root = tk.Tk()
root.geometry('1000x600')
root.title("PawFeeder: Automatic Dog Food Dispenser")
root.pack_propagate(False)
root.resizable(True, True)

img = PhotoImage(file='icons/pawfeeder.png')
root.iconphoto(False, img)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
width, height = 1000, 600
root.geometry(f"{width}x{height}+{(screen_width - width) // 2}+{(screen_height - height) // 2}")


# Main Style
BACKGROUND_COLOR = "#134B70"
BUTTON_COLOR = "#508C9B"
WHITE = "#ffffff"
TEXT_COLOR = "white"
BUTTON_FONT = ("Arial", 12, "bold")
HEADER_FONT = ("Arial", 20, "bold")
SMALL_FONT = ("Arial", 12)
TABLE_FONT = ("Arial", 10)


# Functions
def start_feeding():
    main_page_frame.pack_forget()
    options_frame.pack(side=tk.LEFT, fill="y", anchor="n")
    options_frame.pack_propagate(False)


# Switch to page 1 (Automatic Feed)
def switch_to_page1():
    page3_frame.pack_forget()
    page2_frame.pack_forget()
    page1_frame.pack(fill="both", expand=True)


# Switch to page 2 (Custom Feed)
def switch_to_page2():
    page1_frame.pack_forget()
    page3_frame.pack_forget()
    page2_frame.pack(fill="both", expand=True)


# Switch to page 3 (Manual Feed)
def switch_to_page3():
    page1_frame.pack_forget()
    page2_frame.pack_forget()
    page3_frame.pack(fill="both", expand=True)


# Switch to back to main page
def switch_to_main():
    page1_frame.pack_forget()
    page2_frame.pack_forget()
    page3_frame.pack_forget()
    options_frame.pack_forget()
    main_page_frame.pack(fill="both", expand=True)


# Update time and date every second
def update_time():
    current_time = time.strftime("%I:%M:%S %p")
    current_date = time.strftime("%A, %B %d, %Y")

    page1_time_label.config(text=current_time)
    page2_time_label.config(text=current_time)
    page3_time_label.config(text=current_time)
    page1_date_label.config(text=current_date)
    page2_date_label.config(text=current_date)
    page3_date_label.config(text=current_date)

    root.after(1000, update_time)


# Main frame for the content area
main_frame = tk.Frame(root)
main_frame.pack(side=tk.RIGHT, fill="both", expand=True)


# Main Page Frame (Welcome page)
main_page_frame = tk.Frame(main_frame, bg=BACKGROUND_COLOR)
main_page_frame.pack(fill="both", expand=True)

# Logo frame
main_logo_frame = tk.Frame(main_page_frame, bg=BACKGROUND_COLOR)
main_logo_frame.pack(pady=10)
main_logo_frame.place(relx=0.5, rely=0.4, anchor="center")

# Logo image
main_logo_icon = tk.PhotoImage(file="icons/pawfeeder.png")
main_logo_icon = main_logo_icon.subsample(2)

main_logo_label = tk.Label(main_logo_frame, image=main_logo_icon, bg=BACKGROUND_COLOR)
main_logo_label.pack(pady=20)

# Start Feeding Button
start_button = tk.Button(main_page_frame,
                        text="Start Feeding",
                        font=("Arial", 12, "bold"),
                        bg="#508C9B",
                        fg="white",
                        padx=15,
                        pady=5,
                        relief="flat",
                        activebackground="#508C9B",
                        activeforeground="white",
                        cursor="hand2",
                        command=start_feeding)
start_button.place(relx=0.5, rely=0.7, anchor="center")

# Side bar frame
options_frame = tk.Frame(root, bg=BACKGROUND_COLOR, width=200, height=500)
options_frame.pack_propagate(False)

# Logo frame
logo_frame = tk.Frame(options_frame, bg=BACKGROUND_COLOR)
logo_frame.pack(padx=10, pady=10, side=tk.TOP, anchor="w")

# Logo image
logo_icon = PhotoImage(file="icons/pawfeeder.png")
logo_icon = logo_icon.subsample(3)
logo_label = tk.Label(logo_frame, image=logo_icon, bg=BACKGROUND_COLOR)
logo_label.pack(pady=20)

# Button frame
button_frame = tk.Frame(options_frame, bg=BACKGROUND_COLOR)
button_frame.pack(side=tk.TOP, fill="both", expand=True)

# Automatic Feed Button
auto_feed_button = tk.Button(
    button_frame,
    text="AUTOMATIC FEED",
    bg=BACKGROUND_COLOR,
    fg=WHITE,
    font=BUTTON_FONT,
    relief="flat",
    bd=0,
    padx=15,
    pady=15,
    activebackground=BUTTON_COLOR,
    command=switch_to_page1
)
auto_feed_button.pack(pady=5, fill="x")

# Custom Feed Button
custom_feed_button = tk.Button(
    button_frame,
    text="CUSTOM FEED",
    bg=BACKGROUND_COLOR,
    fg=WHITE,
    font=BUTTON_FONT,
    relief="flat",
    bd=0,
    padx=15,
    pady=15,
    activebackground=BUTTON_COLOR,
    command=switch_to_page2
)
custom_feed_button.pack(pady=5, fill="x")

# Manual Feed Button
manual_feed_button = tk.Button(
    button_frame,
    text="MANUAL FEED",
    bg=BACKGROUND_COLOR,
    fg=WHITE,
    font=BUTTON_FONT,
    relief="flat",
    bd=0,
    padx=15,
    pady=15,
    activebackground=BUTTON_COLOR,
    command=switch_to_page3
)
manual_feed_button.pack(pady=5, fill="x")

# Exit Feed Button
exit_feed_button = tk.Button(
    button_frame,
    text="Exit",
    bg=BACKGROUND_COLOR,
    fg=WHITE,
    font=BUTTON_FONT,
    relief="flat",
    bd=0,
    padx=15,
    pady=15,
    activebackground=BUTTON_COLOR,
    command=switch_to_main
)
exit_feed_button.pack(side="bottom", fill="x")

# Page 1 Frame (Automatic Feed)
page1_frame = tk.Frame(main_frame, bg="white")
page1_frame.pack_propagate(False)
page1_label = tk.Label(page1_frame, text="Automatic Feed Setup", font=("Helvetica", 20), bg="white")
page1_label.place(x=30, y=90)

page1_label1 = tk.Label(page1_frame, text="Choose schedule", font=("Helvetica", 14), bg="white")
page1_label1.place(x=30, y=125)

page1_time_label = tk.Label(page1_frame, font=("Arial", 20, "bold"), fg="black", anchor="nw", bg="white")
page1_time_label.place(x=30, y=20)

page1_date_label = tk.Label(page1_frame, font=("Arial", 12), fg="black", anchor="nw", bg="white")
page1_date_label.place(x=30, y=50)

# --- Schedule Feedback ---
schedule_set = tk.Label(page1_frame, text=" Schedule Set:", font=("Arial", 10, "bold", "italic"), bg="white", fg="green")
schedule_set.place(x=30, y=460)


schedule_label = tk.Label(page1_frame, text="", font=("Arial", 10, "bold", "italic"), bg="white", fg="green")
schedule_label.place(x=125, y=460)


# --- Table Style ---
style = ttk.Style()
style.configure("Treeview.Heading",
                font=("Helvetica", 10, "bold"),
                background="#2A3A59",
                foreground="black",
                padding=10)

style.configure("Treeview",
                font=("Arial", 9),
                background="white",
                foreground="black",
                fieldbackground="white",
                rowheight=30)

style.map("Treeview",
          background=[("selected", "#508C9B"),
                      ("!selected", "white")])

# --- Table Widget ---
columns = ("Dog Type", "Age/Size", "Meal Frequency", "Portion per Meal", "Time of Feeding")
table = ttk.Treeview(page1_frame, columns=columns, show="headings", height=8)
table.pack(pady=30, padx=20, fill="both")
table.place(x=32, y=180)

for col in columns:
    table.heading(col, text=col)

table.column("Dog Type", width=100, anchor="center")
table.column("Age/Size", width=130, anchor="center")
table.column("Meal Frequency", width=130, anchor="center")
table.column("Portion per Meal", width=135, anchor="center")
table.column("Time of Feeding", width=235, anchor="center")

# --- Sample Schedule Data ---
rows = [
    ("Adult Dog", "Small (up to 20 lbs)", "2 times/day", "1/2-1 cup", "7:00 AM, 6:00 PM"),
    ("Adult Dog", "Medium (21-50 lbs)", "2 times/day", "1-2 cups", "7:00 AM, 6:00 PM"),
    ("Adult Dog", "Large (51-90 lbs)", "2 times/day", "2-3 cups", "7:00 AM, 6:00 PM"),
    ("Adult Dog", "Giant (91+ lbs)", "2 times/day", "3-4 cups", "7:00 AM, 6:00 PM"),
    ("Puppy", "Up to 4 months", "3-4 times/day", "1/4-1 cup", "7:00 AM, 12:00 PM, 5:00 PM, 6:00 PM"),
    ("Puppy", "4 to 6 months", "3 times/day", "1/2-1 cup", "7:00 AM, 12:00 PM, 5:00 PM"),
    ("Puppy", "6 months and older", "2 times/day", "1-2 cups", "10:00 AM, 10:01 AM"),
]

for row in rows:
    table.insert("", "end", values=row)

table.bind("<<TreeviewSelect>>", confirm_schedule)

page1_reset_button = tk.Button(
    page1_frame,
    text="Reset Schedule",
    font=("Arial", 10, "bold"),
    bg="#f44336", 
    fg="white",
    relief="flat", 
    activebackground="#d32f2f",
    padx=15,
    pady=5,
    command=reset_schedule
)
page1_reset_button.place(relx=0.5, y=540, anchor="center")





# Page 2 Frame (Custom Feed) - MODIFIED FOR 5 TIMES
page2_frame = tk.Frame(main_frame, bg="white")
page2_frame.pack_propagate(False)

# Header for Custom Feed
page2_label = tk.Label(page2_frame, text="Custom Feed Setup", font=("Helvetica", 20), bg="white")
page2_label.pack(pady=20)
page2_label.place(x=30, y=90)

# Instructions
page2_label1 = tk.Label(page2_frame, text="Set up to 5 custom feeding times", font=("Helvetica", 14), bg="white")
page2_label1.place(x=30, y=125)

# Time and Date Labels
page2_time_label = tk.Label(page2_frame, font=("Arial", 20, "bold"), fg="black", anchor="nw", bg="white")
page2_time_label.place(x=30, y=20)

page2_date_label = tk.Label(page2_frame, font=("Arial", 12), fg="black", anchor="nw", bg="white")
page2_date_label.place(x=30, y=50)

# Create a centered main content frame
content_width = 340  # Adjust as needed
main_content = tk.Frame(page2_frame, bg="white", width=content_width)
main_content.place(relx=0.5, y=170, anchor="n")

# Time selection variables and widgets - create lists for up to 5 times
custom_hour_vars = []
custom_minute_vars = []
custom_ampm_vars = []
custom_time_active = []
time_frames = []

# Hours and minutes lists
hours_12h = [f"{i}" for i in range(1, 13)]
minutes = [f"{i:02d}" for i in range(60)]

# Create a container for all time entries with a light background for visual separation
time_entries_container = tk.Frame(main_content, bg="white", padx=20, pady=10, bd=1, relief="flat")
time_entries_container.pack(fill="x", padx=20, pady=(0, 20))

# Create frames for the 5 time entries
for i in range(5):
    # Create vars
    custom_hour_vars.append(tk.StringVar())
    custom_minute_vars.append(tk.StringVar())
    custom_ampm_vars.append(tk.StringVar())
    custom_time_active.append(tk.BooleanVar())
    
    # Position each time selection frame
    time_frame = tk.Frame(time_entries_container, bg="white")
    time_frame.pack(pady=5, fill="x")
    time_frames.append(time_frame)
    
    # Add a subtle separator between time entries (except for the first one)
    if i > 0:
        separator = tk.Frame(time_frame, height=1, bg="white")
        separator.pack(fill="x", pady=(0, 5))
    
    # Create a function that captures the current index
    def create_checkbox_command(idx):
        return lambda: on_checkbox_toggle(idx)
    
    # Checkbox to activate this time slot with better styling
    checkbox = tk.Checkbutton(time_frame, text=f"Time {i+1}:", variable=custom_time_active[i], 
                             bg="white", font=("Helvetica", 10, "bold"),
                             command=create_checkbox_command(i))
    checkbox.pack(side="left", padx=(0, 10))
    
    # Hour Selection
    tk.Label(time_frame, text="Hour:", bg="white").pack(side="left", padx=5)
    hour_menu = ttk.Combobox(time_frame, textvariable=custom_hour_vars[i], values=hours_12h, width=3)
    hour_menu.pack(side="left", padx=5)
    
    # Minute Selection
    tk.Label(time_frame, text="Minute:", bg="white").pack(side="left", padx=5)
    minute_menu = ttk.Combobox(time_frame, textvariable=custom_minute_vars[i], values=minutes, width=3)
    minute_menu.pack(side="left", padx=5)
    
    # AM/PM Selection
    tk.Label(time_frame, text="AM/PM:", bg="white").pack(side="left", padx=5)
    ampm_menu = ttk.Combobox(time_frame, textvariable=custom_ampm_vars[i], values=["AM", "PM"], width=3)
    ampm_menu.pack(side="left", padx=5)

# Current Schedule Display with improved design
schedule_frame = tk.LabelFrame(main_content, text="Current Custom Schedule", bg="white", bd=2, fg="#333333",
                              font=("Helvetica", 10, "bold"))
schedule_frame.pack(fill="x", padx=20, pady=(0, 20))

custom_schedule_label = tk.Label(schedule_frame, text="No times scheduled yet", font=("Arial", 12), bg="white", 
                                fg="#777777", wraplength=480)
custom_schedule_label.pack(pady=15, padx=10)

# Buttons for Custom Feed - centered
button_frame = tk.Frame(main_content, bg="white")
button_frame.pack(pady=15)

# Set Custom Schedule Button with improved design
set_schedule_button = tk.Button(
    button_frame, 
    text="Set Schedule", 
    font=("Arial", 10, "bold"), 
    bg="#4CAF50", 
    fg="white",
    relief="flat", 
    activebackground="#45a049",
    padx=15,
    pady=5,
    bd=0,
    cursor="hand2",
    command=confirm_custom_schedule
)
set_schedule_button.pack(side="left", padx=15)

# Reset Schedule Button with improved design
reset_schedule_button = tk.Button(
    button_frame, 
    text="Reset Schedule", 
    font=("Arial", 10, "bold"), 
    bg="#f44336", 
    fg="white",
    relief="flat", 
    activebackground="#d32f2f",
    padx=15,
    pady=5,
    bd=0,
    cursor="hand2",
    command=reset_custom_schedule
)
reset_schedule_button.pack(side="left", padx=15)





# Page 3 Frame (Manual Feed)
page3_frame = tk.Frame(main_frame, bg="white")
page3_frame.pack_propagate(False)
page3_label = tk.Label(page3_frame, text="Manual Feed Setup", font=("Helvetica", 20),  bg="white")
page3_label.pack(pady=20)
page3_label.place(x=30, y=90)


page3_label1 = tk.Label(page3_frame, text="Click button to dispense dog foods", font=("Helvetica", 14),  bg="white")
page3_label1.place(x=30, y=125)


# Time and Date Labels with different font sizes
page3_time_label = tk.Label(page3_frame, font=("Arial", 20, "bold"), fg="black", anchor="nw", bg="white")
page3_time_label.place(x=30, y=20)


page3_date_label = tk.Label(page3_frame, font=("Arial", 12), fg="black", anchor="nw", bg="white")
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


update_time()


root.mainloop()




