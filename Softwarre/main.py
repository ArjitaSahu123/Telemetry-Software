import random
import threading
import time
import matplotlib.pyplot as plt
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from matplotlib.animation import FuncAnimation
from sys import exit
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
APP.iconbitmap("sudarshan.ico")

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

'''-------------------------------------DashBoard-------------------------------------------------------------'''

def dashboard():
    '''Function to bring dashboard in window frame'''

    stop_background_threads()  # Stop threads before switching
    global RUNNING_DASHBOARD, dashboard_thread
    RUNNING_DASHBOARD = True
    clear_frame(windowFrame)  # Assuming this function exists
    # dashboard_thread = threading.Thread(target=updatingGraphs, daemon=True)
    # dashboard_thread.start()
    #
    dashboardButton.configure(fg_color="#111010")
    valuesButton.configure(fg_color="#000000")
    gyroButton.configure(fg_color="#000000")
    trajectoryButton.configure(fg_color='#000000')

    global axes, canvas_list
    axes, canvas_list = [], []

    # Reinitialize graph_frames as it is emptied earlier
    graph_frames = []

    # Destroy any existing graph frames to avoid TclError when switching views
    for frame in graph_frames:
        frame.destroy()

    # Creating empty frames for graphs
    for i in range(4):
        frame = ctk.CTkFrame(windowFrame, fg_color='#222222', corner_radius=15)
        graph_frames.append(frame)

    # Layout for the frames (2x2 grid)
    graph_frames[0].grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
    graph_frames[1].grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
    graph_frames[2].grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
    graph_frames[3].grid(row=1, column=1, padx=10, pady=10, sticky='nsew')

    windowFrame.grid_rowconfigure(0, weight=1)
    windowFrame.grid_rowconfigure(1, weight=1)
    windowFrame.grid_columnconfigure(0, weight=1)
    windowFrame.grid_columnconfigure(1, weight=1)

    # Plot empty graphs (no data yet)
    plot_empty_graph(graph_frames[0], 'Acceleration', 'Acceleration (m/s²)')
    plot_empty_graph(graph_frames[1], 'Speed', 'Speed (km/h)')
    plot_empty_graph(graph_frames[2], 'Altitude', 'Altitude (m)')
    plot_empty_graph(graph_frames[3], 'Temperature', 'Temperature (°C)')

    # Restart live plotting if it's already launched
    if ani_list:  # Check if the launch has already started
        for i, (ax, canvas) in enumerate(zip(axes, canvas_list)):
            ylabel = 'Acceleration' if i == 0 else 'Speed' if i == 1 else 'Altitude' if i == 2 else 'Temperature'
            ani = plot_live_data(ax, canvas, ylabel)
            ani_list.append(ani)  # Keep reference to animations

def plot_empty_graph(frame, title, ylabel):
    '''Plot empty graph with just axes, no data'''
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.set_title(title, fontsize=14, color='white')
    ax.set_ylabel(ylabel, fontsize=12, color='white')
    ax.set_xlabel("Time (s)", fontsize=12, color='white')
    ax.set_facecolor('#000000')
    fig.patch.set_facecolor('#000000')
    ax.grid(True, color='gray', linestyle='--', linewidth=0.5)
    ax.tick_params(axis='both', colors='white')

    # Create a canvas for the empty plot
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)

    # Store for future use in launch (as placeholder for plotting data)
    axes.append(ax)
    canvas_list.append(canvas)

def plot_live_data(ax, canvas, ylabel):
    '''Plot live data on the graph after launch using animation'''
    x = np.arange(10)
    y = np.zeros_like(x)  # Initial empty data

    line, = ax.plot(x, y, linestyle='-', color='cyan', linewidth=2)
    fig = ax.get_figure()

    def update(frame):
        new_ydata = np.random.random(10) * (10 if ylabel == 'Acceleration' else 50)
        line.set_ydata(new_ydata)
        ax.relim()
        ax.autoscale_view()
        canvas.draw()

    ani = FuncAnimation(fig, update, interval=1000)
    return ani


'''---------------------------------------------------VALUES---------------------------------------------------------'''

# Frames to keep Application Stable
accelerationFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=590, height=130)
accelerationData = ctk.CTkLabel(accelerationFrame, text=("X : 0 \t Y : 0 \t Z : 0"),font=("Font Awesome 5 Brands", 30), text_color="white")

velocityFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=590, height=130)
velocityData = ctk.CTkLabel(velocityFrame, text=("X : 0 \t Y : 0 \t Z : 0"), font=("Font Awesome 5 Brands", 30), text_color="white")

llFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=1190, height=60)
longitudeData = ctk.CTkLabel(llFrame, text="000.00000", font=("Font Awesome 5 Brands", 30), text_color="white")
latitudeData = ctk.CTkLabel(llFrame, text="000.00000", font=("Font Awesome 5 Brands", 30), text_color="white")

humidityFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=285, height=130)
humidityFrameData = ctk.CTkLabel(humidityFrame, text=("0"), font=("Font Awesome 5 Brands", 30), text_color="white")

altitudeFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=285, height=130)
altitudeFrameData = ctk.CTkLabel(altitudeFrame, text=("0  ft"), font=("Font Awesome 5 Brands", 30), text_color="white")

pressureFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=285, height=130)
pressureFrameData = ctk.CTkLabel(pressureFrame, text=("0  psi"), font=("Font Awesome 5 Brands", 30), text_color="white")

tempratureFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=285, height=130)
tempratureFrameData = ctk.CTkLabel(tempratureFrame, text=("0  F"), font=("Font Awesome 5 Brands", 30),text_color="white")

mfFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=590, height=130)
mfFrameData = ctk.CTkLabel(mfFrame, text=("X : 0 \t Y : 0 \t Z : 0"), font=("Font Awesome 5 Brands", 30),text_color="white")

coFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=285, height=130)
coFrameData = ctk.CTkLabel(coFrame, text=("0  psi"), font=("Font Awesome 5 Brands", 30), text_color="white")

h2Frame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=285, height=130)
h2FrameData = ctk.CTkLabel(h2Frame, text=("0  F"), font=("Font Awesome 5 Brands", 30), text_color="white")

logFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=1190, height=160)
logFrameData = ctk.CTkLabel(logFrame, text="No logs yet...", font=("Font Awesome 5 Brands", 20), text_color="white",anchor="nw", justify="left")


# String Parsing and filling
def stringParse(string):
    global Values_Dictionaries
    string = string.decode('utf-8')
    parsed_data = list(string[:].strip().split(','))
    j = 0
    for i in Values_Dictionaries:
        Values_Dictionaries[i] = parsed_data[j]
        j+=1


# Thread-safe function to update labels
def update_labels_safely():
    try:
        print("start")
        Accelerometer_data = list(Values_Dictionaries["Accelerometer_data"].split(":"))
        accelerationData.configure(text=f"X : {Accelerometer_data[0]} \t Y : {Accelerometer_data[1]} \t Z : {Accelerometer_data[2]}")
        # velocity_data = list(Values_Dictionaries["Velocity_data"].split(":"))

        longitudeData.configure(text=f"{Values_Dictionaries['GNSS_Longitude']}")
        latitudeData.configure(text=f"{Values_Dictionaries['GNSS_Latitude']}")
        humidityFrameData.configure(text=f"{Values_Dictionaries['Humidity']}")
        altitudeFrameData.configure(text=f"{Values_Dictionaries['Altitude']}")
        pressureFrameData.configure(text=f"{Values_Dictionaries['Pressure']}")
        tempratureFrameData.configure(text=f"{Values_Dictionaries['Temperature']}")
        Magnetic_Field = list(Values_Dictionaries['Magnetic_Field'].split(':'))
        mfFrameData.configure(text=f"X : {Magnetic_Field[0]} \t Y : {Magnetic_Field[1]} \t Z : {Magnetic_Field[2]}")
        coFrameData.configure(text=f"{Values_Dictionaries['CO']}")
        h2FrameData.configure(text=f"{0}  F")
        print("end")

    except ctk.TclError:
        print("Frame no longer exists. Skipping update.")


# Receiving values from Serial
# data = b'Team_ID,7:5:20,6,8.96,1002.56,23.10,0.00,7:5:20,0.00,0.00,0.00,1,1:2:3,4:5:6,1,0.00,7:8:9,7.44\r\n'
def gettingValues():
    global RUNNING_VALUES
    try:
        # ser = serial.Serial('COM3', 9600, timeout=1)
        while RUNNING_VALUES:
            # data = ser.readline()
            data = b'Team_ID,7:5:20,6,8.96,1002.56,23.10,0.00,7:5:20,0.00,0.00,0.00,1,1:2:3,4:5:6,1,0.00,7:8:9,7.44\r\n'
            if data:
                stringParse(data)  # Assuming this function exists

                # Safe UI updates
                if APP.winfo_exists():
                    APP.after(0, update_labels_safely)
            time.sleep(1)
    except serial.SerialException as e:
        print(f"Serial connection error: {e}")


def values():
    '''
    Function to bring values in window frame
    '''

    stop_background_threads()  # Stop threads before switching
    global RUNNING_VALUES, values_filling_thread
    RUNNING_VALUES = True
    clear_frame(windowFrame)  # Assuming this function exists
    values_filling_thread = threading.Thread(target=gettingValues, daemon=True)
    values_filling_thread.start()

    # Initialize Values section UI here
    dashboardButton.configure(fg_color="#000000")
    valuesButton.configure(fg_color="#111010")
    gyroButton.configure(fg_color="#000000")
    trajectoryButton.configure(fg_color='#000000')

    # Acceleration Frame and Data
    global accelerationFrame, accelerationData
    accelerationFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=590, height=130)
    accelerationFrame.grid(row=0, columnspan=2, padx=(10, 5), pady=(10, 5))

    accelerationFixedLabel = ctk.CTkLabel(accelerationFrame, text="Acceleration", font=("Font Awesome 5 Brands", 30),text_color="white")
    accelerationFixedLabel.place(relx=0.5, rely=0.3, anchor="center")
    accelerationcanvas = ctk.CTkCanvas(accelerationFrame, height=1, width=595, bg="white")
    accelerationcanvas.place(relx=0.5, rely=0.5, anchor="center")
    accelerationData = ctk.CTkLabel(accelerationFrame, text=("X : 0 \t Y : 0 \t Z : 0"),font=("Font Awesome 5 Brands", 30), text_color="white")  # Data value of Acceleration
    accelerationData.place(relx=0.5, rely=0.7, anchor="center")

    # Velocity Frame and Data
    global velocityFrame, velocityData
    velocityFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=590, height=130)
    velocityFrame.grid(row=0, column=2, columnspan=2, padx=(5, 10), pady=(10, 5))

    velocityFixedLabel = ctk.CTkLabel(velocityFrame, text="Velocity", font=("Font Awesome 5 Brands", 30), text_color="white")
    velocityFixedLabel.place(relx=0.5, rely=0.3, anchor="center")
    velocitycanvas = ctk.CTkCanvas(velocityFrame, height=1, width=595, bg="white")
    velocitycanvas.place(relx=0.5, rely=0.5, anchor="center")
    velocityData = ctk.CTkLabel(velocityFrame, text=("X : 0 \t Y : 0 \t Z : 0"), font=("Font Awesome 5 Brands", 30), text_color="white")
    velocityData.place(relx=0.5, rely=0.7, anchor="center")

    global llFrame, longitudeData, latitudeData
    llFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=1190, height=60)
    llFrame.grid(row=1, columnspan=4, padx=(10, 5), pady=(10, 5))

    longitudeLabel = ctk.CTkLabel(llFrame, text="Longitude :", font=("Font Awesome 5 Brands", 30), text_color="white")
    longitudeLabel.place(relx=0.04, rely=0.25)
    longitudeData = ctk.CTkLabel(llFrame, text="000.00000", font=("Font Awesome 5 Brands", 30), text_color="white")
    longitudeData.place(relx=0.18, rely=0.25)
    latitudeLabel = ctk.CTkLabel(llFrame, text="Latitude :", font=("Font Awesome 5 Brands", 30), text_color="white")
    latitudeLabel.place(relx=0.55, rely=0.25)
    latitudeData = ctk.CTkLabel(llFrame, text="000.00000", font=("Font Awesome 5 Brands", 30), text_color="white")
    latitudeData.place(relx=0.67, rely=0.25)

    global humidityFrame, humidityFrameData
    humidityFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=285, height=130)
    humidityFrame.grid(row=2, column=0, padx=(5, 5), pady=(10, 5))

    humidityFrameFixedLabel = ctk.CTkLabel(humidityFrame, text="Humidity", font=("Font Awesome 5 Brands", 30), text_color="white")
    humidityFrameFixedLabel.place(relx=0.5, rely=0.3, anchor="center")
    humidityFramecanvas = ctk.CTkCanvas(humidityFrame, height=1, width=285, bg="white")
    humidityFramecanvas.place(relx=0.5, rely=0.5, anchor="center")
    humidityFrameData = ctk.CTkLabel(humidityFrame, text=("0"), font=("Font Awesome 5 Brands", 30), text_color="white")
    humidityFrameData.place(relx=0.5, rely=0.7, anchor="center")

    global altitudeFrame, altitudeFrameData
    altitudeFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=285, height=130)
    altitudeFrame.grid(row=2, column=1, padx=(5, 5), pady=(10, 5))

    altitudeFrameFixedLabel = ctk.CTkLabel(altitudeFrame, text="Altitude", font=("Font Awesome 5 Brands", 30), text_color="white")
    altitudeFrameFixedLabel.place(relx=0.5, rely=0.3, anchor="center")
    altitudeFramecanvas = ctk.CTkCanvas(altitudeFrame, height=1, width=285, bg="white")
    altitudeFramecanvas.place(relx=0.5, rely=0.5, anchor="center")
    altitudeFrameData = ctk.CTkLabel(altitudeFrame, text=("0  ft"), font=("Font Awesome 5 Brands", 30), text_color="white")
    altitudeFrameData.place(relx=0.5, rely=0.7, anchor="center")

    global pressureFrame, pressureFrameData
    pressureFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=285, height=130)
    pressureFrame.grid(row=2, column=2, padx=(5, 10), pady=(10, 5))

    pressureFrameFixedLabel = ctk.CTkLabel(pressureFrame, text="Pressure", font=("Font Awesome 5 Brands", 30),text_color="white")
    pressureFrameFixedLabel.place(relx=0.5, rely=0.3, anchor="center")
    pressureFramecanvas = ctk.CTkCanvas(pressureFrame, height=1, width=285, bg="white")
    pressureFramecanvas.place(relx=0.5, rely=0.5, anchor="center")
    pressureFrameData = ctk.CTkLabel(pressureFrame, text=("0  psi"), font=("Font Awesome 5 Brands", 30), text_color="white")
    pressureFrameData.place(relx=0.5, rely=0.7, anchor="center")

    global temperatureFrame, tempratureFrameData
    tempratureFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=285, height=130)
    tempratureFrame.grid(row=2, column=3, padx=(5, 10), pady=(10, 5))

    tempratureFrameFixedLabel = ctk.CTkLabel(tempratureFrame, text="Temperature", font=("Font Awesome 5 Brands", 30), text_color="white")
    tempratureFrameFixedLabel.place(relx=0.5, rely=0.3, anchor="center")
    tempratureFramecanvas = ctk.CTkCanvas(tempratureFrame, height=1, width=285, bg="white")
    tempratureFramecanvas.place(relx=0.5, rely=0.5, anchor="center")
    tempratureFrameData = ctk.CTkLabel(tempratureFrame, text=("0  F"), font=("Font Awesome 5 Brands", 30), text_color="white")
    tempratureFrameData.place(relx=0.5, rely=0.7, anchor="center")

    global mfFrame, mfFrameData
    mfFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=590, height=130)
    mfFrame.grid(row=3, columnspan=2, padx=(10, 5), pady=(10, 5))

    mfFrameFixedLabel = ctk.CTkLabel(mfFrame, text="Magnetic Field", font=("Font Awesome 5 Brands", 30),text_color="white")
    mfFrameFixedLabel.place(relx=0.5, rely=0.3, anchor="center")
    mfFramecanvas = ctk.CTkCanvas(mfFrame, height=1, width=590, bg="white")
    mfFramecanvas.place(relx=0.5, rely=0.5, anchor="center")
    mfFrameData = ctk.CTkLabel(mfFrame, text=("X : 0 \t Y : 0 \t Z : 0"), font=("Font Awesome 5 Brands", 30),text_color="white")
    mfFrameData.place(relx=0.5, rely=0.7, anchor="center")

    global coFrame, coFrameData
    coFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=285, height=130)
    coFrame.grid(row=3, column=2, padx=(5, 10), pady=(10, 5))

    coFrameFixedLabel = ctk.CTkLabel(coFrame, text="CO", font=("Font Awesome 5 Brands", 30), text_color="white")
    coFrameFixedLabel.place(relx=0.5, rely=0.3, anchor="center")
    coFramecanvas = ctk.CTkCanvas(coFrame, height=1, width=285, bg="white")
    coFramecanvas.place(relx=0.5, rely=0.5, anchor="center")
    coFrameData = ctk.CTkLabel(coFrame, text=("0  psi"), font=("Font Awesome 5 Brands", 30), text_color="white")
    coFrameData.place(relx=0.5, rely=0.7, anchor="center")

    global h2Frame, h2FrameData
    h2Frame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=285, height=130)
    h2Frame.grid(row=3, column=3, padx=(5, 10), pady=(10, 5))

    h2FrameFixedLabel = ctk.CTkLabel(h2Frame, text="H2", font=("Font Awesome 5 Brands", 30), text_color="white")
    h2FrameFixedLabel.place(relx=0.5, rely=0.3, anchor="center")
    h2Framecanvas = ctk.CTkCanvas(h2Frame, height=1, width=285, bg="white")
    h2Framecanvas.place(relx=0.5, rely=0.5, anchor="center")
    h2FrameData = ctk.CTkLabel(h2Frame, text=("0  F"), font=("Font Awesome 5 Brands", 30), text_color="white")
    h2FrameData.place(relx=0.5, rely=0.7, anchor="center")

    global logFrame, logFrameData
    logFrame = ctk.CTkFrame(windowFrame, fg_color="#000000", width=1190, height=160)
    logFrame.grid(row=4, columnspan=4, padx=(10, 5), pady=(10, 5))

    # Title for the Log Frame (Log Packet) on the extreme left
    logFrameFixedLabel = ctk.CTkLabel(logFrame, text="Log", font=("Font Awesome 5 Brands", 30), text_color="white",anchor="w", justify="left")
    logFrameFixedLabel.place(relx=0.1, rely=0.2, anchor="center")  # anchor and padding adjusted
    # Removed the Canvas for a horizontal line
    logFrameCanvas = ctk.CTkCanvas(logFrame, height=1, width=1290, bg="black")
    logFrameCanvas.place(relx=0.5, rely=0.33, anchor="center")
    # Multi-line log display (using a label to show the log data)
    logFrameData = ctk.CTkLabel(logFrame, text="No logs yet...", font=("Font Awesome 5 Brands", 20), text_color="white",anchor="nw", justify="left")
    logFrameData.place(relx=0.5, rely=0.7, anchor="center")

'''-----------------------------------------------------------------------------------------------------------------'''
def gyro():
    '''Function to bring gyro section as separate window'''
    dashboardButton.configure(fg_color="#000000")
    valuesButton.configure(fg_color="#000000")
    gyroButton.configure(fg_color="#111010")
    trajectoryButton.configure(fg_color='#000000')

'''----------------------------------------------------------------------------------------------------------------'''
def trajectory():
    '''Function to bring gyro section as separate window'''
    dashboardButton.configure(fg_color="#000000")
    valuesButton.configure(fg_color="#000000")
    gyroButton.configure(fg_color="#000000")
    trajectoryButton.configure(fg_color='#111010')

    # Function to execute index.py and open output.html
    def execute_and_open():
        # Run index.py to generate output.html
        subprocess.run(["python", "index.py"])

        # Get the path of output.html
        output_file_path = os.path.join(os.getcwd(), "output.html")

        # Open output.html in the default web browser
        webbrowser.open(f"file://{output_file_path}")

    execute_and_open()

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
    global counter_thred

    statusVariableLabel.configure(text='Launching', text_color="#ABFFA9")
    launchButton.configure(state=ctk.DISABLED, text_color="Green")

    # Thread started for counter
    counter_thred.start()


    # Set up live plotting
    for i, (ax, canvas) in enumerate(zip(axes, canvas_list)):
        ylabel = 'Acceleration' if i == 0 else 'Speed' if i == 1 else 'Altitude' if i == 2 else 'Temperature'
        ani = plot_live_data(ax, canvas, ylabel)
        ani_list.append(ani)  # Keep reference to animations
        canvas.draw()


# Buttons

dashboardButton = ctk.CTkButton(optionFrame, width=290, height=80, text='Dashboard', font=("Font Awesome 5 Brands", 30), fg_color='#000', hover_color='#111010', corner_radius=20, command=dashboard)
dashboardButton.grid(row=0, column=1, padx=10, pady=(25, 5))

valuesButton = ctk.CTkButton(optionFrame, width=290, height=80, text='Values', font=("Font Awesome 5 Brands", 30), fg_color='#000', hover_color='#111010', corner_radius=20, command=values)
valuesButton.grid(row=1, column=1, padx=10, pady=(5, 5))

gyroButton = ctk.CTkButton(optionFrame, width=290, height=80, text='Gyro Visuals', font=("Font Awesome 5 Brands", 30), fg_color='#000', hover_color='#111010', corner_radius=20, command=gyro)
gyroButton.grid(row=2, column=1, padx=10, pady=(5, 5))

trajectoryButton = ctk.CTkButton(optionFrame, width=290, height=80, text='Trajectory', font=("Font Awesome 5 Brands", 30), fg_color='#000', hover_color='#111010', corner_radius=20, command=trajectory)
trajectoryButton.grid(row=3, column=1, padx=10, pady=(5, 5))

launchButton = ctk.CTkButton(optionFrame, width=290, height=80, text='Launch', text_color='red', font=("Font Awesome 5 Brands", 30), fg_color='#000', hover_color='#111010', corner_radius=20, command=launch)
launchButton.grid(row=4, column=1, padx=10, pady=(5, 5))

tLable = ctk.CTkLabel(optionFrame, text='T 0', font=("Font Awesome 5 Brands", 50))
tLable.grid(row=5, column=1, padx=10, pady=(150, 5))



APP.mainloop()