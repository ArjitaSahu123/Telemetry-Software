import random
import threading
import time
import matplotlib.pyplot as plt
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from matplotlib.animation import FuncAnimation
from sys import exit
from tkintermapview import TkinterMapView
import importlib
import os
import subprocess
import webbrowser
import serial

# Global values and functions
T_time = 0

# Global Control Flags
RUNNING_VALUES = False
RUNNING_DASHBOARD = False

graph_frames = [] # for Graphs
axes = []
canvas_list = []
ani_list = []

flight_name = ""
baud_rate = 0
com = ""

Values_Dictionaries = {"Team_ID":"", "TimeStamp":"", "Packet_Count":"", "Altitude":"", "Pressure":"", "Temperature":"",
                       "Voltage":"", "GNSS_Time":"", "GNSS_Latitude":"", "GNSS_Longitude":"",
                       "GNSS_Altitude":"", "GNSS_Sats":"", "Accelerometer_data":"", "Gyro_Spin_Rate":"", "FS_State":"",
                       "Humidity":"", "Magnetic_Field":"", "CO":""}

def destroy_frame(app, fn, br, cm):
    global flight_name, baud_rate, com
    flight_name = fn
    baud_rate = br
    com = cm
    app.destroy()

# Starter app
starter_app = ctk.CTk()

def CenterWindowToDisplay(Screen: ctk, width: int, height: int, scale_factor: float = 1.0):
    """Centers the window to the main display/monitor"""
    screen_width = Screen.winfo_screenwidth()
    screen_height = Screen.winfo_screenheight()
    x = int(((screen_width/2) - (width/2)) * scale_factor)
    y = int(((screen_height/2) - (height/1.5)) * scale_factor)
    return f"{width}x{height}+{x}+{y}"

# starter_app.geometry("400x250")
starter_app.geometry(CenterWindowToDisplay(starter_app, 400, 240, starter_app._get_window_scaling()))
starter_app.overrideredirect(True)

flight_label = ctk.CTkLabel(starter_app, text="Flight Details", font=("Times new roman", 30))
flight_label.place(relx=0.3, rely=0.1)

flight_input = ctk.CTkEntry(starter_app, placeholder_text="Flight Name", width=300)
flight_input.place(relx=0.14, rely=0.3)

flight_rate = ctk.CTkOptionMenu(starter_app,values=["Baud Rate", "3200", "9600"], width=300)
flight_rate.place(relx=0.14, rely=0.45)

flight_com = ctk.CTkEntry(starter_app, placeholder_text="COM<Number>", width=300)
flight_com.place(relx=0.14, rely=0.6)

start_button = ctk.CTkButton(starter_app, text="Start", command=lambda: destroy_frame(starter_app, flight_input.get(), flight_rate.get(), flight_com.get()))
start_button.place(relx=0.14, rely=0.75)

cancel_button = ctk.CTkButton(starter_app, text="Cancel", command=exit)
cancel_button.place(relx=0.54, rely=0.75)

starter_app.mainloop()

# Clear frames
def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()



# Stop background threads when switching views
def stop_background_threads():
    global RUNNING_VALUES, RUNNING_DASHBOARD
    RUNNING_VALUES = False
    RUNNING_DASHBOARD = False

# Tkinter data values
APP = ctk.CTk()

width  = APP.winfo_screenwidth()
height = APP.winfo_screenheight()

APP.after(1, APP.wm_state, 'zoomed')
APP.title("Team Sudarshan Ground Control")

APP.iconbitmap(r"Testing Software\sudarshan.ico")


# Set the background color for the entire window
APP.configure(fg_color="#111010")

# Title Frame at the top
titleFrame = ctk.CTkFrame(APP, fg_color='#000000', height=80)
titleFrame.pack(side="top", fill="x")

# Option Frame on the left
optionFrame = ctk.CTkFrame(APP, fg_color='#000000', width=300)
optionFrame.pack(side="left", fill="y")

# Window Frame takes the remaining space
windowFrame = ctk.CTkFrame(APP, fg_color='#111010')
windowFrame.pack(side="left", fill="both", expand=True)

# topics in top frame
# Flight status
statusFixedLabel = ctk.CTkLabel(titleFrame, text='Status', font=("Font Awesome 5 Brands", 30))
statusFixedLabel.grid(row=0, column=1, padx='20', pady='25')

statusVariableLabel = ctk.CTkLabel(titleFrame, text='Preparing', font=("Font Awesome 5 Brands", 30))
statusVariableLabel.configure(text_color="#ABFFA9")
statusVariableLabel.grid(row=0, column=2)

# Flight Name
nameFixedLabel = ctk.CTkLabel(titleFrame, text='Flight Name', font=("Font Awesome 5 Brands", 30))
nameFixedLabel.grid(row=0, column=3, padx=(370, 20))

nameVariableLabel = ctk.CTkLabel(titleFrame, text=flight_name, font=("Font Awesome 5 Brands", 30))
nameVariableLabel.configure(text_color="Yellow")
nameVariableLabel.grid(row=0, column=4)

# Time
def live_Time():
    t = time.strftime('%H:%M:%S')
    timeLabel.configure(text = t)
    timeLabel.after(1000, live_Time)

timeLabel = ctk.CTkLabel(titleFrame, text='20:20:20', font=("Font Awesome 5 Brands", 30))
live_Time()
timeLabel.grid(row=0, column=5, padx=(500,20))

'''-------------------------------------Getting Values ---------------------------------------------------------'''
# String Parsing and filling
def stringParse(string):
    global Values_Dictionaries
    string = string.decode('utf-8')
    parsed_data = list(string[:].strip().split(','))
    j = 0
    for i in Values_Dictionaries:
        Values_Dictionaries[i] = parsed_data[j]
        j+=1


# def gettingValues():
#     global RUNNING_VALUES, RUNNING_DASHBOARD
#     try:
#         # ser = serial.Serial('COM3', 9600, timeout=1)
#         while True:
#             # data = ser.readline()
#             data = b'Team_ID,7:5:20,6,8.96,1002.56,23.10,0.00,7:5:20,0.00,0.00,0.00,1,1:2:3,4:5:6,1,0.00,7:8:9,7.44\r\n'
#             if data:
#                 stringParse(data)  # Assuming this function exists
#
#                 # Safe UI updates
#                 if APP.winfo_exists() and RUNNING_VALUES:
#                     APP.after(0, update_labels_safely)
#                 if APP.winfo_exists() and RUNNING_DASHBOARD:
#                     APP.after(0)
#             time.sleep(1)
#     except serial.SerialException as e:
#         print(f"Serial connection error: {e}")

def gettingValues():
    global RUNNING_VALUES, RUNNING_DASHBOARD
    while RUNNING_VALUES or RUNNING_DASHBOARD:
        # Simulate random data
        Values_Dictionaries['Accelerometer_data'] = f"{random.randint(-10, 10)}:{random.randint(-10, 10)}:{random.randint(-10, 10)}"
        Values_Dictionaries['Gyro_Spin_Rate'] = f"{random.randint(-5, 5)}:{random.randint(-5, 5)}:{random.randint(-5, 5)}"
        Values_Dictionaries['Magnetic_Field'] = f"{random.randint(-5, 5)}:{random.randint(-5, 5)}:{random.randint(-5, 5)}"
        Values_Dictionaries['Altitude'] = f"{random.uniform(0, 100):.2f}"
        Values_Dictionaries['Temperature'] = f"{random.uniform(15, 35):.2f}"
        Values_Dictionaries['GNSS_Time'] = time.strftime('%H:%M:%S')
        Values_Dictionaries['TimeStamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
        Values_Dictionaries['GNSS_Altitude'] = f"{random.uniform(0, 100):.2f}"
        Values_Dictionaries['GNSS_Sats'] = f"{random.randint(15, 35)}"
        Values_Dictionaries['GNSS_Latitude'] = f"{random.uniform(-90, 90):.5f}"
        Values_Dictionaries['GNSS_Longitude'] = f"{random.uniform(-180, 180):.5f}"
        Values_Dictionaries['Pressure'] = f"{random.uniform(900, 1100):.2f}"
        Values_Dictionaries['Humidity'] = f"{random.randint(30, 70)}"
        Values_Dictionaries['CO'] = f"{random.randint(15, 35)}"

        # Update the GUI safely
        if APP.winfo_exists() and RUNNING_VALUES:
            APP.after(0, update_labels_safely)
        if APP.winfo_exists() and RUNNING_DASHBOARD:
            APP.after(0, lambda: update_graph(axes))

        time.sleep(1)

'''-------------------------------------DashBoard-------------------------------------------------------------'''

real_time_data = {
    "velocity": [],
    "pressure": [],
    "temperature": [],
    "accelerometer": [],
    "time": []  # Common time axis
}

def dashboard():
    """Main dashboard function to initialize graphs"""
    stop_background_threads()
    global RUNNING_DASHBOARD, dashboard_thread
    RUNNING_DASHBOARD = True
    clear_frame(windowFrame)
    
    dashboardButton.configure(fg_color="#111010")
    valuesButton.configure(fg_color="#000000")
    trajectoryButton.configure(fg_color='#000000')
    
    global axes, canvas_list
    axes, canvas_list = [], []
    
    graph_frames = [ctk.CTkFrame(windowFrame, fg_color='#222222', corner_radius=15) for _ in range(4)]
    
    graph_frames[0].grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
    graph_frames[1].grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
    graph_frames[2].grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
    graph_frames[3].grid(row=1, column=1, padx=10, pady=10, sticky='nsew')

    windowFrame.grid_rowconfigure(0, weight=1)
    windowFrame.grid_rowconfigure(1, weight=1)
    windowFrame.grid_columnconfigure(0, weight=1)
    windowFrame.grid_columnconfigure(1, weight=1)

    plot_empty_graph(graph_frames[0], 'Velocity', 'Velocity (m/s)')
    plot_empty_graph(graph_frames[1], 'Pressure', 'Pressure (Pa)')
    plot_empty_graph(graph_frames[2], 'Temperature', 'Temperature (°C)')
    plot_empty_graph(graph_frames[3], 'Accelerometer', 'Acceleration (m/s²)')
    
    if ani_list:
        for i, (ax, canvas) in enumerate(zip(axes, canvas_list)):
            ylabel = ["Velocity", "Pressure", "Temperature", "Accelerometer"][i]
            ani = plot_live_data(ax, canvas, ylabel)
            ani_list.append(ani)


def update_graph(axes):
    print("Updating graph...")  # Debugging print statement
    if len(real_time_data["time"]) == 0:
        real_time_data["time"].append(time.time())
    else:
        real_time_data["time"].append(real_time_data["time"][-1] + 0.3)

    for key in ["velocity", "pressure", "temperature", "accelerometer"]:
        new_value = random.randint(0, 100)  # Replace with actual sensor values
        real_time_data[key].append(new_value)
        print(f"{key.capitalize()} updated: {new_value}")  # Print updated values

    for ax, key in zip(axes, ["velocity", "pressure", "temperature", "accelerometer"]):
        ax.clear()
        ax.plot(real_time_data["time"], real_time_data[key], label=key.capitalize(), color='blue', linewidth=2)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel(key.capitalize())
        ax.grid(True)
        ax.legend()


def animate(i, axes, canvas):
    print("Animating...")  # Debugging print
    update_graph(axes)
    canvas.draw()



def display_dashboard(frame):
    clear_frame(frame)
    
    figure, axes = plt.subplots(2, 2, figsize=(10, 6))
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, wspace=0.2, hspace=0.2)
    
    canvas = FigureCanvasTkAgg(figure, frame)
    canvas.get_tk_widget().pack(fill='both', expand=True)
    
    global ani
    ani = FuncAnimation(figure, animate, fargs=(axes, canvas), interval=300, save_count=100)


def plot_empty_graph(frame, title, ylabel):
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.set_title(title, fontsize=14, color='white')
    ax.set_ylabel(f"Unit of {ylabel}", fontsize=12, color='white')
    ax.set_xlabel("Value", fontsize=12, color='white')
    
    ax.set_facecolor('#000000')
    fig.patch.set_facecolor('#000000')
    ax.grid(True, color='gray', linestyle='--', linewidth=0.5, alpha=0.6)
    ax.tick_params(axis='both', colors='white')

    canvas = FigureCanvasTkAgg(fig, master=frame) 
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)
    
    axes.append(ax)
    canvas_list.append(canvas)


def plot_live_data(ax, canvas, ylabel):
    """Dynamically update live graphs"""
    x = time.time()
    y = float(Values_Dictionaries.get(ylabel.lower(), 0))

    line, = ax.plot([x], [y], linestyle='-', color='cyan', linewidth=2)
    fig = ax.get_figure()

    def update(frame):
        new_x = time.time()
        new_y = float(Values_Dictionaries.get(ylabel.lower(), 0))
        line.set_xdata([new_x])
        line.set_ydata([new_y])
        ax.relim()
        ax.autoscale_view()
        canvas.draw()

    ani = FuncAnimation(fig, update, interval=1000, save_count=100, cache_frame_data=False)

    return ani

#
# def plot_live_data(ax, canvas, ylabel):
#     print(Values_Dictionaries)
#     x_data = np.arange(0, 10, 1)  # Time steps
#     y_data = np.zeros(10)  # Initialize with zero data
#
#     line, = ax.plot(x_data, y_data, linestyle='-', color='cyan', linewidth=2)
#
#     def update(frame):
#         # Shift data left and append new value from Values_Dictionaries
#         y_data[:-1] = y_data[1:]
#         y_data[-1] = get_live_value(ylabel)  # Get new value from dictionary
#
#         line.set_ydata(y_data)
#         ax.relim()
#         ax.autoscale_view()
#         canvas.draw()
#
#     ani = FuncAnimation(ax.figure, update, interval=1000)  # Update every second
#     return ani
#
#
# def get_live_value(ylabel):
#     """Fetch live data from Values_Dictionaries based on the data type"""
#     if ylabel == 'Accelerometer_data':
#         # Taking the Z-axis value as an example
#         return float(Values_Dictionaries['Accelerometer_data'].split(':')[2])
#     elif ylabel == 'Gyro_Spin_Rate':
#         return float(Values_Dictionaries['Gyro_Spin_Rate'].split(':')[2])
#     elif ylabel == 'Altitude':
#         return float(Values_Dictionaries['Altitude'])
#     elif ylabel == 'Temperature':
#         return float(Values_Dictionaries['Temperature'])
#     return 0


'''---------------------------------------------------VALUES---------------------------------------------------------'''

# Frames to keep Application Stable
accelerationFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=320, height=100)
# accelerationData = ctk.CTkLabel(accelerationFrame, text=("X : 0 \t Y : 0 \t Z : 0"),font=("Font Awesome 5 Brands", 20), text_color="white")
accelerationDataX = ctk.CTkLabel(accelerationFrame, text=("X : 0"),font=("Font Awesome 5 Brands", 20), text_color="red")
accelerationDataY = ctk.CTkLabel(accelerationFrame, text=("Y : 0"),font=("Font Awesome 5 Brands", 20), text_color="green")
accelerationDataZ = ctk.CTkLabel(accelerationFrame, text=("Z : 0"),font=("Font Awesome 5 Brands", 20), text_color="blue")

gnssTimeFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=200, height=100)
gnssTimeFrameData = ctk.CTkLabel(gnssTimeFrame, text=("00:00:00"), font=("Font Awesome 5 Brands", 20), text_color="white")

gnssSatsFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=200, height=100)
gnssSatsFrameData = ctk.CTkLabel(gnssTimeFrame, text=("0"), font=("Font Awesome 5 Brands", 20), text_color="white")

gnssAltitudeFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=200, height=100)
gnssAltitudeFrameData = ctk.CTkLabel(gnssTimeFrame, text=("0   m"), font=("Font Awesome 5 Brands", 20), text_color="white")

gyroRateFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=590, height=130)
# gyroRateData = ctk.CTkLabel(gyroRateFrame, text=("X : 0 \t Y : 0 \t Z : 0"), font=("Font Awesome 5 Brands", 30), text_color="white")
gyroRateDataX = ctk.CTkLabel(gyroRateFrame, text=("X : 0"), font=("Font Awesome 5 Brands", 20), text_color="red")
gyroRateDataY = ctk.CTkLabel(gyroRateFrame, text=("Y : 0"), font=("Font Awesome 5 Brands", 20), text_color="green")
gyroRateDataZ = ctk.CTkLabel(gyroRateFrame, text=("Z : 0"), font=("Font Awesome 5 Brands", 20), text_color="blue")

voltageFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=200, height=100)
voltageFrameData = ctk.CTkLabel(gnssTimeFrame, text=("00:00:00"), font=("Font Awesome 5 Brands", 20), text_color="white")

packetFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=200, height=100)
packetFrameData = ctk.CTkLabel(gnssTimeFrame, text=("0"), font=("Font Awesome 5 Brands", 20), text_color="white")

fsStateFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=200, height=100)
fsStateFrameData = ctk.CTkLabel(gnssTimeFrame, text=("0   m"), font=("Font Awesome 5 Brands", 20), text_color="white")

mfFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=590, height=100)
# mfFrameData = ctk.CTkLabel(mfFrame, text=("X : 0 \t Y : 0 \t Z : 0"), font=("Font Awesome 5 Brands", 30),text_color="white")
mfFrameDataX = ctk.CTkLabel(mfFrame, text=("X : 0"), font=("Font Awesome 5 Brands", 30),text_color="red")
mfFrameDataY = ctk.CTkLabel(mfFrame, text=("Y : 0"), font=("Font Awesome 5 Brands", 30),text_color="green")
mfFrameDataZ = ctk.CTkLabel(mfFrame, text=("Z : 0"), font=("Font Awesome 5 Brands", 30),text_color="blue")

altitudeFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=285, height=100)
altitudeFrameData = ctk.CTkLabel(altitudeFrame, text=("0  ft"), font=("Font Awesome 5 Brands", 30), text_color="white")

pressureFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=285, height=100)
pressureFrameData = ctk.CTkLabel(pressureFrame, text=("0  psi"), font=("Font Awesome 5 Brands", 30), text_color="white")

tempratureFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=285, height=100)
tempratureFrameData = ctk.CTkLabel(tempratureFrame, text=("0  F"), font=("Font Awesome 5 Brands", 30),text_color="white")

llFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=590, height=100)
longitudeData = ctk.CTkLabel(llFrame, text="000.00000", font=("Font Awesome 5 Brands", 30), text_color="white")
latitudeData = ctk.CTkLabel(llFrame, text="000.00000", font=("Font Awesome 5 Brands", 30), text_color="white")

humidityFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=285, height=100)
humidityFrameData = ctk.CTkLabel(humidityFrame, text=("0"), font=("Font Awesome 5 Brands", 30), text_color="white")

coFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=285, height=100)
coFrameData = ctk.CTkLabel(coFrame, text=("0  psi"), font=("Font Awesome 5 Brands", 30), text_color="white")

logFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=590, height=240)
logFrameData = ctk.CTkLabel(logFrame, text="No logs yet...", font=("Font Awesome 5 Brands", 20), text_color="white",anchor="nw", justify="left")

trajectoryFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=570, height=240)


# Thread-safe function to update labels
def update_labels_safely():
    try:
        print("start")
        Accelerometer_data = list(Values_Dictionaries["Accelerometer_data"].split(":"))
        accelerationDataX.configure(text=f"X : {Accelerometer_data[0]}")
        accelerationDataY.configure(text=f"Y : {Accelerometer_data[1]}")
        accelerationDataZ.configure(text=f"Z : {Accelerometer_data[2]}")

        gyroRate_data = list(Values_Dictionaries["Gyro_Spin_Rate"].split(":"))
        gyroRateDataX.configure(text=f"X : {gyroRate_data[0]}")
        gyroRateDataY.configure(text=f"Y : {gyroRate_data[1]}")
        gyroRateDataZ.configure(text=f"Z : {gyroRate_data[2]}")

        Magnetic_Field = list(Values_Dictionaries['Magnetic_Field'].split(':'))
        mfFrameDataX.configure(text=f"X : {Magnetic_Field[0]}")
        mfFrameDataY.configure(text=f"Y : {Magnetic_Field[1]}")
        mfFrameDataZ.configure(text=f"Z : {Magnetic_Field[2]}")

        gnssTimeFrameData.configure(text=f"{Values_Dictionaries['GNSS_Time']}")
        gnssSatsFrameData.configure(text=f"{Values_Dictionaries['GNSS_Sats']}")
        gnssAltitudeFrameData.configure(text=f"{Values_Dictionaries['GNSS_Altitude']}\tm")
        longitudeData.configure(text=f"{Values_Dictionaries['GNSS_Longitude']}")
        latitudeData.configure(text=f"{Values_Dictionaries['GNSS_Latitude']}")
        humidityFrameData.configure(text=f"{Values_Dictionaries['Humidity']}")
        altitudeFrameData.configure(text=f"{Values_Dictionaries['Altitude']}\tm")
        pressureFrameData.configure(text=f"{Values_Dictionaries['Pressure']}\tP")
        tempratureFrameData.configure(text=f"{Values_Dictionaries['Temperature']}\tC")
        coFrameData.configure(text=f"{Values_Dictionaries['CO']}\tpsi")
        voltageFrameData.configure(text=f"{0}\tv")
        print("end")

    except Exception as e:
        print(f"An error occurred: {e}")

def values():
    '''
    Function to bring values in window frame
    '''

    stop_background_threads()  # Stop threads before switching
    global RUNNING_VALUES, values_filling_thread
    RUNNING_VALUES = True
    clear_frame(windowFrame)  # Assuming this function exists


    # Initialize Values section UI here
    dashboardButton.configure(fg_color="#000000")
    valuesButton.configure(fg_color="#111010")
    trajectoryButton.configure(fg_color='#000000')

    # Acceleration Frame and Data
    global accelerationFrame, accelerationDataX, accelerationDataY, accelerationDataZ
    accelerationFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=370, height=100)
    accelerationFrame.grid(row=0, column=0, padx=(10, 2), pady=(10, 5))

    accelerationFixedLabel = ctk.CTkLabel(accelerationFrame, text="Acceleration", font=("Font Awesome 5 Brands", 25),text_color="white")
    accelerationFixedLabel.place(relx=0.5, rely=0.3, anchor="center")
    accelerationcanvas = ctk.CTkCanvas(accelerationFrame, height=0.1, width=370, bg="white")
    accelerationcanvas.place(relx=0.5, rely=0.5, anchor="center")
    # accelerationData = ctk.CTkLabel(accelerationFrame, text=("X : 0 \t Y : 0 \t Z : 0"),font=("Font Awesome 5 Brands", 20), text_color="white")
    accelerationDataX = ctk.CTkLabel(accelerationFrame, text=("X : 0"),font=("Font Awesome 5 Brands", 20), text_color="red")
    accelerationDataY = ctk.CTkLabel(accelerationFrame, text=("Y : 0"),font=("Font Awesome 5 Brands", 20), text_color="green")
    accelerationDataZ = ctk.CTkLabel(accelerationFrame, text=("Z : 0"),font=("Font Awesome 5 Brands", 20), text_color="blue")
    # accelerationData.place(relx=0.5, rely=0.7, anchor="center")
    accelerationDataX.place(relx=0.2, rely=0.7, anchor="w")
    accelerationDataY.place(relx=0.5, rely=0.7, anchor="center")
    accelerationDataZ.place(relx=0.8, rely=0.7, anchor="e")

    # GNSS time frame
    global gnssTimeFrame, gnssTimeFrameData
    gnssTimeFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=270, height=100)
    gnssTimeFrame.grid(row=0, column=1, padx=(5, 2), pady=(10, 5))

    gnssTimeFrameFixedLabel = ctk.CTkLabel(gnssTimeFrame, text="Gnss Time", font=("Font Awesome 5 Brands", 25), text_color="white")
    gnssTimeFrameFixedLabel.place(relx=0.5, rely=0.3, anchor="center")
    gnssTimeFramecanvas = ctk.CTkCanvas(gnssTimeFrame, height=0.1, width=270, bg="white")
    gnssTimeFramecanvas.place(relx=0.5, rely=0.5, anchor="center")
    gnssTimeFrameData = ctk.CTkLabel(gnssTimeFrame, text=("00:00:00"), font=("Font Awesome 5 Brands", 20), text_color="white")
    gnssTimeFrameData.place(relx=0.5, rely=0.7, anchor="center")

    # GNSS Sats frame
    global gnssSatsFrame, gnssSatsFrameData
    gnssSatsFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=270, height=100)
    gnssSatsFrame.grid(row=0, column=2, padx=(5, 2), pady=(10, 5))

    gnssSatsFrameFixedLabel = ctk.CTkLabel(gnssSatsFrame, text="Gnss Sats", font=("Font Awesome 5 Brands", 25), text_color="white")
    gnssSatsFrameFixedLabel.place(relx=0.5, rely=0.3, anchor="center")
    gnssSatsFramecanvas = ctk.CTkCanvas(gnssSatsFrame, height=0.1, width=270, bg="white")
    gnssSatsFramecanvas.place(relx=0.5, rely=0.5, anchor="center")
    gnssSatsFrameData = ctk.CTkLabel(gnssSatsFrame, text=("0"), font=("Font Awesome 5 Brands", 20), text_color="white")
    gnssSatsFrameData.place(relx=0.5, rely=0.7, anchor="center")

    # GNSS Altitude frame
    global gnssAltitudeFrame, gnssAltitudeFrameData
    gnssAltitudeFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=270, height=100)
    gnssAltitudeFrame.grid(row=0, column=3, padx=(5, 5), pady=(10, 5))

    gnssAltitudeFrameFixedLabel = ctk.CTkLabel(gnssAltitudeFrame, text="Gnss Altitude",
                                               font=("Font Awesome 5 Brands", 25), text_color="white")
    gnssAltitudeFrameFixedLabel.place(relx=0.5, rely=0.3, anchor="center")
    gnssAltitudeFramecanvas = ctk.CTkCanvas(gnssAltitudeFrame, height=0.1, width=270, bg="white")
    gnssAltitudeFramecanvas.place(relx=0.5, rely=0.5, anchor="center")
    gnssAltitudeFrameData = ctk.CTkLabel(gnssAltitudeFrame, text=("0"), font=("Font Awesome 5 Brands", 20),
                                         text_color="white")
    gnssAltitudeFrameData.place(relx=0.5, rely=0.7, anchor="center")

    # gyroRate Frame and Data
    global gyroRateFrame, gyroRateDataX, gyroRateDataY, gyroRateDataZ
    gyroRateFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=370, height=100)
    gyroRateFrame.grid(row=1, column=0, padx=(10, 2), pady=(5, 5))

    gyroRateFixedLabel = ctk.CTkLabel(gyroRateFrame, text="Gyro-Rate", font=("Font Awesome 5 Brands", 25), text_color="white")
    gyroRateFixedLabel.place(relx=0.5, rely=0.3, anchor="center")
    gyroRatecanvas = ctk.CTkCanvas(gyroRateFrame, height=0.1, width=370, bg="white")
    gyroRatecanvas.place(relx=0.5, rely=0.5, anchor="center")
    # gyroRateData = ctk.CTkLabel(gyroRateFrame, text=("X : 0 \t Y : 0 \t Z : 0"), font=("Font Awesome 5 Brands", 20), text_color="white")
    gyroRateDataX = ctk.CTkLabel(gyroRateFrame, text=("X : 0"), font=("Font Awesome 5 Brands", 20), text_color="red")
    gyroRateDataY = ctk.CTkLabel(gyroRateFrame, text=("Y : 0"), font=("Font Awesome 5 Brands", 20), text_color="green")
    gyroRateDataZ = ctk.CTkLabel(gyroRateFrame, text=("Z : 0"), font=("Font Awesome 5 Brands", 20), text_color="blue")
    # gyroRateData.place(relx=0.5, rely=0.7, anchor="center")
    gyroRateDataX.place(relx=0.2, rely=0.7, anchor="w")
    gyroRateDataY.place(relx=0.5, rely=0.7, anchor="center")
    gyroRateDataZ.place(relx=0.8, rely=0.7, anchor="e")

    # Voltage frame
    global voltageFrame, voltageFrameData
    voltageFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=270, height=100)
    voltageFrame.grid(row=1, column=1, padx=(5, 2), pady=(5, 5))

    voltageFrameFixedLabel = ctk.CTkLabel(voltageFrame, text="Voltage", font=("Font Awesome 5 Brands", 25), text_color="white")
    voltageFrameFixedLabel.place(relx=0.5, rely=0.3, anchor="center")
    voltageFramecanvas = ctk.CTkCanvas(voltageFrame, height=0.1, width=270, bg="white")
    voltageFramecanvas.place(relx=0.5, rely=0.5, anchor="center")
    voltageFrameData = ctk.CTkLabel(voltageFrame, text=("0    v"), font=("Font Awesome 5 Brands", 20), text_color="white")
    voltageFrameData.place(relx=0.5, rely=0.7, anchor="center")

    # Packet Count frame
    global packetFrame, packetFrameData
    packetFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=270, height=100)
    packetFrame.grid(row=1, column=2, padx=(5, 2), pady=(5, 5))

    packetFrameFixedLabel = ctk.CTkLabel(packetFrame, text="Packet Count", font=("Font Awesome 5 Brands", 25),
                                           text_color="white")
    packetFrameFixedLabel.place(relx=0.5, rely=0.3, anchor="center")
    packetFramecanvas = ctk.CTkCanvas(packetFrame, height=0.1, width=270, bg="white")
    packetFramecanvas.place(relx=0.5, rely=0.5, anchor="center")
    packetFrameData = ctk.CTkLabel(packetFrame, text=("0"), font=("Font Awesome 5 Brands", 20), text_color="white")
    packetFrameData.place(relx=0.5, rely=0.7, anchor="center")

    # Flight Software State frame
    global fsStateFrame, fsStateFrameData
    fsStateFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=270, height=100)
    fsStateFrame.grid(row=1, column=3, padx=(5, 5), pady=(5, 5))

    fsStateFrameFixedLabel = ctk.CTkLabel(fsStateFrame, text="FS State",
                                               font=("Font Awesome 5 Brands", 25), text_color="white")
    fsStateFrameFixedLabel.place(relx=0.5, rely=0.3, anchor="center")
    fsStateFramecanvas = ctk.CTkCanvas(fsStateFrame, height=0.1, width=270, bg="white")
    fsStateFramecanvas.place(relx=0.5, rely=0.5, anchor="center")
    fsStateFrameData = ctk.CTkLabel(fsStateFrame, text=("0"), font=("Font Awesome 5 Brands", 20),
                                         text_color="white")
    fsStateFrameData.place(relx=0.5, rely=0.7, anchor="center")

    # Magnetic field frame
    global mfFrame, mfFrameDataX, mfFrameDataY, mfFrameDataZ
    mfFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=370, height=100)
    mfFrame.grid(row=2, column=0, padx=(10, 2), pady=(5, 5))

    mfFrameFixedLabel = ctk.CTkLabel(mfFrame, text="Magnetic Field", font=("Font Awesome 5 Brands", 25),text_color="white")
    mfFrameFixedLabel.place(relx=0.5, rely=0.3, anchor="center")
    mfFramecanvas = ctk.CTkCanvas(mfFrame, height=0.1, width=370, bg="white")
    mfFramecanvas.place(relx=0.5, rely=0.5, anchor="center")
    # mfFrameData = ctk.CTkLabel(mfFrame, text=("X : 0 \t Y : 0 \t Z : 0"), font=("Font Awesome 5 Brands", 20),text_color="white")
    mfFrameDataX = ctk.CTkLabel(mfFrame, text=("X : 0"), font=("Font Awesome 5 Brands", 20),text_color="red")
    mfFrameDataY = ctk.CTkLabel(mfFrame, text=("Y : 0"), font=("Font Awesome 5 Brands", 20),text_color="green")
    mfFrameDataZ = ctk.CTkLabel(mfFrame, text=("Z : 0"), font=("Font Awesome 5 Brands", 20),text_color="blue")
    # mfFrameData.place(relx=0.5, rely=0.7, anchor="center")
    mfFrameDataX.place(relx=0.2, rely=0.7, anchor="w")
    mfFrameDataY.place(relx=0.5, rely=0.7, anchor="center")
    mfFrameDataZ.place(relx=0.8, rely=0.7, anchor="e")

    # Altitude frame
    global altitudeFrame, altitudeFrameData
    altitudeFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=270, height=100)
    altitudeFrame.grid(row=2, column=1, padx=(5, 2), pady=(5, 5))

    altitudeFrameFixedLabel = ctk.CTkLabel(altitudeFrame, text="Altitude", font=("Font Awesome 5 Brands", 25), text_color="white")
    altitudeFrameFixedLabel.place(relx=0.5, rely=0.3, anchor="center")
    altitudeFramecanvas = ctk.CTkCanvas(altitudeFrame, height=0.1, width=270, bg="white")
    altitudeFramecanvas.place(relx=0.5, rely=0.5, anchor="center")
    altitudeFrameData = ctk.CTkLabel(altitudeFrame, text=("0  m"), font=("Font Awesome 5 Brands", 20), text_color="white")
    altitudeFrameData.place(relx=0.5, rely=0.7, anchor="center")

    # Pressure frame
    global pressureFrame, pressureFrameData
    pressureFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=270, height=100)
    pressureFrame.grid(row=2, column=2, padx=(5, 2), pady=(5, 5))

    pressureFrameFixedLabel = ctk.CTkLabel(pressureFrame, text="Pressure", font=("Font Awesome 5 Brands", 25),text_color="white")
    pressureFrameFixedLabel.place(relx=0.5, rely=0.3, anchor="center")
    pressureFramecanvas = ctk.CTkCanvas(pressureFrame, height=0.1, width=270, bg="white")
    pressureFramecanvas.place(relx=0.5, rely=0.5, anchor="center")
    pressureFrameData = ctk.CTkLabel(pressureFrame, text=("0  P"), font=("Font Awesome 5 Brands", 20), text_color="white")
    pressureFrameData.place(relx=0.5, rely=0.7, anchor="center")

    # Temperature Frame
    global temperatureFrame, tempratureFrameData
    tempratureFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=270, height=100)
    tempratureFrame.grid(row=2, column=3, padx=(5, 2), pady=(5, 5))

    tempratureFrameFixedLabel = ctk.CTkLabel(tempratureFrame, text="Temperature", font=("Font Awesome 5 Brands", 25), text_color="white")
    tempratureFrameFixedLabel.place(relx=0.5, rely=0.3, anchor="center")
    tempratureFramecanvas = ctk.CTkCanvas(tempratureFrame, height=0.1, width=270, bg="white")
    tempratureFramecanvas.place(relx=0.5, rely=0.5, anchor="center")
    tempratureFrameData = ctk.CTkLabel(tempratureFrame, text=("0  C"), font=("Font Awesome 5 Brands", 20), text_color="white")
    tempratureFrameData.place(relx=0.5, rely=0.7, anchor="center")

    # Longitude Latutude frame
    global llFrame, longitudeData, latitudeData
    llFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=650, height=100)
    llFrame.grid(row=3, columnspan=2, column=0, padx=(10, 2), pady=(5, 5))

    longitudeLabel = ctk.CTkLabel(llFrame, text="Longitude :", font=("Font Awesome 5 Brands", 25), text_color="white")
    longitudeLabel.place(relx=0.08, rely=0.23)
    longitudeData = ctk.CTkLabel(llFrame, text="000.00000", font=("Font Awesome 5 Brands", 25), text_color="white")
    longitudeData.place(relx=0.3, rely=0.23)
    latitudeLabel = ctk.CTkLabel(llFrame, text="Latitude :", font=("Font Awesome 5 Brands", 25), text_color="white")
    latitudeLabel.place(relx=0.08, rely=0.52)
    latitudeData = ctk.CTkLabel(llFrame, text="000.00000", font=("Font Awesome 5 Brands", 25), text_color="white")
    latitudeData.place(relx=0.3, rely=0.52)

    global humidityFrame, humidityFrameData
    humidityFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=270, height=100)
    humidityFrame.grid(row=3, column=2, padx=(5, 2), pady=(5, 5))

    humidityFrameFixedLabel = ctk.CTkLabel(humidityFrame, text="Humidity", font=("Font Awesome 5 Brands", 25), text_color="white")
    humidityFrameFixedLabel.place(relx=0.5, rely=0.3, anchor="center")
    humidityFramecanvas = ctk.CTkCanvas(humidityFrame, height=0.1, width=270, bg="white")
    humidityFramecanvas.place(relx=0.5, rely=0.5, anchor="center")
    humidityFrameData = ctk.CTkLabel(humidityFrame, text=("0"), font=("Font Awesome 5 Brands", 20), text_color="white")
    humidityFrameData.place(relx=0.5, rely=0.7, anchor="center")

    global coFrame, coFrameData
    coFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=270, height=100)
    coFrame.grid(row=3, column=3, padx=(5, 2), pady=(5, 5))

    coFrameFixedLabel = ctk.CTkLabel(coFrame, text="CO", font=("Font Awesome 5 Brands", 25), text_color="white")
    coFrameFixedLabel.place(relx=0.5, rely=0.3, anchor="center")
    coFramecanvas = ctk.CTkCanvas(coFrame, height=0.1, width=270, bg="white")
    coFramecanvas.place(relx=0.5, rely=0.5, anchor="center")
    coFrameData = ctk.CTkLabel(coFrame, text=("0  psi"), font=("Font Awesome 5 Brands", 20), text_color="white")
    coFrameData.place(relx=0.5, rely=0.7, anchor="center")

    global logFrame, logFrameData
    logFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=650, height=240)
    logFrame.grid(row=4, columnspan=2, padx=(10, 2), pady=(5, 10))

    # Title for the Log Frame (Log Packet) on the extreme left
    logFrameFixedLabel = ctk.CTkLabel(logFrame, text="Log", font=("Font Awesome 5 Brands", 25), text_color="white",anchor="w", justify="left")
    logFrameFixedLabel.place(relx=0.1, rely=0.12, anchor="center")  # anchor and padding adjusted
    # Removed the Canvas for a horizontal line
    logFrameCanvas = ctk.CTkCanvas(logFrame, height=0.1, width=750, bg="white")
    logFrameCanvas.place(relx=0.5, rely=0.22, anchor="center")
    # Multi-line log display (using a label to show the log data)
    logFrameData = ctk.CTkLabel(logFrame, text="No logs yet...", font=("Font Awesome 5 Brands", 20), text_color="white",anchor="nw", justify="left")
    logFrameData.place(relx=0.5, rely=0.7, anchor="center")

    global trajectoryFrame
    trajectoryFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=550, height=240)
    trajectoryFrame.grid(row=4, columnspan=2,column=2, padx=(5, 2), pady=(5, 10))

'''----------------------------------------------------------------------------------------------------------------'''

# Lists to store past trajectory and timestamps
trajectory_data = []
timestamps_data = []

def get_trajectory_data():
    
    try:
        
        timestamp = Values_Dictionaries["TimeStamp"]
        lat = Values_Dictionaries["GNSS_Latitude"]
        lon = Values_Dictionaries["GNSS_Longitude"]
        print(f"timestamp: {timestamp}, lat: {lat}, lon: {lon}")
        if not timestamp or not lat or not lon:
            print("Warning: Missing lat, lon, or timestamp. Returning empty list.")
            return [], []
        
        return [(float(lat), float(lon))], [timestamp]
    except Exception as e:
        print(f"Error fetching data: {e}")
        return [], []
    
def trajectory():
    """
    Function to display the trajectory of the satellite on the map.
    """
    global trajectory_data, timestamps_data
    
    dashboardButton.configure(fg_color="#000000")
    valuesButton.configure(fg_color="#000000")
    trajectoryButton.configure(fg_color='#111010')

    global trajectoryFrame
    # Create a TkinterMapView widget.
    map_widget = TkinterMapView(trajectoryFrame, width=700, height=320, corner_radius=0)
    map_widget.pack(fill="both", expand=True)

    # Set an initial zoom level.
    map_widget.set_zoom(16) 

    # Set the initial map position.
    trajectory, timestamps = get_trajectory_data()
    if trajectory:
        init_lat, init_lon = trajectory[-1]
    else:
        # Default to coordinates for Delhi
        init_lat = 28.7041
        init_lon = 77.1025

    map_widget.set_position(init_lat, init_lon)

    markers = []

    def update_map():
        global trajectory_data, timestamps_data
        print("update_map called!!!!")
        new_trajectory, new_timestamps = get_trajectory_data()
        if new_trajectory and new_timestamps and len(new_trajectory) == len(new_timestamps):
            # Append new data to the past data lists
            trajectory_data.extend(new_trajectory)
            timestamps_data.extend(new_timestamps)

            # Center the map on the most recent position
            lat, lon = trajectory_data[-1]
            map_widget.set_position(lat, lon)
            marker = map_widget.set_marker(lat, lon)
            
            # Remove previous markers.
            for marker in markers:
                marker.delete()
            markers.clear()

            # Draw a polyline connecting the trajectory points if there are at least two points
            if len(trajectory_data) > 1:
                map_widget.set_path(trajectory_data)
            else:
                print("Not enough data points to draw a path.")
        else:
            print("No valid trajectory and timestamp data to update the map.")

        # Schedule the next update
        APP.after(1000, update_map)

    # Start the first update after a short delay.
    APP.after(1000, update_map)


    # # Function to execute index.py and open output.html
    # def execute_and_open():
    #     # Run index.py to generate output.html
    #     subprocess.run(["python", "index.py"])

    #     # Get the path of output.html
    #     output_file_path = os.path.join(os.getcwd(), "output.html")

    #     # Open output.html in the default web browser
    #     webbrowser.open(f"file://{output_file_path}")

    # execute_and_open()

'''-----------------------------------------------------------------------------------------------------------------'''
# Counter time
def count():
    '''Function To start timer and goes till end'''
    global T_time

    tLable.configure(text=f'T {T_time}')

    tLable.after(1000, count)
    if T_time > 0:
        statusVariableLabel.configure(text='Launched', text_color="#52F44F")
    T_time += 1


# Thread declaration
counter_thred = threading.Thread(target=count, daemon=True)
values_filling_thread = threading.Thread(target=gettingValues, daemon=True)

def launch():
    '''To Launch the rocket and start the time button'''
    global counter_thred, values_filling_thread

    # Check if Dashboard or Values has been clicked
    if not (RUNNING_VALUES or RUNNING_DASHBOARD):
        # Default to Dashboard if neither has been initialized
        dashboard()  # or values() if you want to default to the Values view

    statusVariableLabel.configure(text='Launching', text_color="#ABFFA9")
    launchButton.configure(state=ctk.DISABLED, text='Unlink', text_color="Green")

    # Thread started for counter
    counter_thred.start()
    values_filling_thread.start()

    # Set up live plotting
    for i, (ax, canvas) in enumerate(zip(axes, canvas_list)):
        ylabel = 'Accelerometer_data' if i == 0 else 'Gyro_Spin_Rate' if i == 1 else 'Altitude' if i == 2 else 'Temperature'
        ani = plot_live_data(ax, canvas, ylabel)
        ani_list.append(ani)  # Keep reference to animations
        canvas.draw()

def unlink():
    '''To Stop Data from receiving means Delinking from Ground Control'''




# Buttons

dashboardButton = ctk.CTkButton(optionFrame, width=290, height=80, text='Dashboard', font=("Font Awesome 5 Brands", 30), fg_color='#000', hover_color='#111010', corner_radius=20, command=dashboard)
dashboardButton.grid(row=0, column=1, padx=10, pady=(25, 5))

valuesButton = ctk.CTkButton(optionFrame, width=290, height=80, text='Values', font=("Font Awesome 5 Brands", 30), fg_color='#000', hover_color='#111010', corner_radius=20, command=values)
valuesButton.grid(row=1, column=1, padx=10, pady=(5, 5))

trajectoryButton = ctk.CTkButton(optionFrame, width=290, height=80, text='Trajectory', font=("Font Awesome 5 Brands", 30), fg_color='#000', hover_color='#111010', corner_radius=20, command=trajectory)
trajectoryButton.grid(row=2, column=1, padx=10, pady=(5, 5))

launchButton = ctk.CTkButton(optionFrame, width=290, height=80, text='Link', text_color='red', font=("Font Awesome 5 Brands", 30), fg_color='#000', hover_color='#111010', corner_radius=20, command=launch)
launchButton.grid(row=3, column=1, padx=10, pady=(5, 5))

tLable = ctk.CTkLabel(optionFrame, text='T 0', font=("Font Awesome 5 Brands", 50))
tLable.grid(row=5, column=1, padx=10, pady=(150, 5))



APP.mainloop()