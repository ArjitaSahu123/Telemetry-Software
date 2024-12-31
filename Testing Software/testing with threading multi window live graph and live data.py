import customtkinter as ctk
from tkinter import Label
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import random
import time
import serial  # For communicating with Arduino

# Configure Arduino port
# arduino = serial.Serial('COM3', 9600)  # Replace with your Arduino's COM port

# Global variables to store graph data
x_data = []
y_data = []

# Global counter variable
counter = 0


# Function to clear the content of a frame
def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


# Function to start a counter (Task 1)
def start_counter(label_counter):
    global counter
    while True:
        counter += 1
        label_counter.configure(text=f"Counter: {counter}")
        time.sleep(1)


# Function to send a request to Arduino (Task 2)
def send_request_to_arduino():
    # Send the start command to Arduino once
    # arduino.write(b'START\n')  # Uncomment this when using with Arduino
    print("Request sent to Arduino to start sending data.")


# Function to collect data from Arduino (Task 3)
def collect_data_from_arduino(label_id, label_lat, label_lon):
    while True:
        # Simulate receiving data from Arduino
        # Replace this with actual Arduino data parsing
        data_packet = {
            "id": random.randint(1000, 9999),
            "latitude": random.uniform(-90, 90),
            "longitude": random.uniform(-180, 180)
        }
        # Update the labels with the received data
        label_id.configure(text=f"ID: {data_packet['id']}")
        label_lat.configure(text=f"Latitude: {data_packet['latitude']:.6f}")
        label_lon.configure(text=f"Longitude: {data_packet['longitude']:.6f}")
        time.sleep(1)


# Function to update the graph (Task 4 - real-time graph)
def update_graph(canvas, ax):
    x_data.append(time.time())
    y_data.append(random.randint(0, 100))
    ax.clear()
    ax.plot(x_data, y_data)
    canvas.draw()
    canvas.get_tk_widget().after(1000, update_graph, canvas, ax)


# Function to display the dashboard with real-time graphs and Arduino data
def display_dashboard(frame):
    clear_frame(frame)  # Clear previous content

    # Create labels for Arduino data
    label_id = ctk.CTkLabel(frame, text="ID: 0")
    label_id.pack(pady=10)

    label_lat = ctk.CTkLabel(frame, text="Latitude: 0.000000")
    label_lat.pack(pady=10)

    label_lon = ctk.CTkLabel(frame, text="Longitude: 0.000000")
    label_lon.pack(pady=10)

    # Create a graph using Matplotlib
    figure = plt.Figure(figsize=(5, 4), dpi=100)
    ax = figure.add_subplot(111)
    canvas = FigureCanvasTkAgg(figure, frame)
    canvas.get_tk_widget().pack(pady=20)

    # Start real-time graph updates (maintaining previous state)
    update_graph(canvas, ax)

    # Start collecting data from Arduino (Task 3)
    arduino_thread = threading.Thread(target=collect_data_from_arduino, args=(label_id, label_lat, label_lon))
    arduino_thread.daemon = True
    arduino_thread.start()


# Function to start both tasks simultaneously (Task 1 and Task 2)
def start_tasks(label_counter):
    # Disable button after it's pressed
    start_button.configure(state="disabled")

    # Start Task 1 (Counter) in a new thread
    counter_thread = threading.Thread(target=start_counter, args=(label_counter,))
    counter_thread.daemon = True
    counter_thread.start()

    # Start Task 2 (Send request to Arduino)
    send_request_to_arduino()


# Main window setup
root = ctk.CTk()
root.geometry("800x600")
root.title("Simultaneous Tasks with Real-time Graphs and Arduino Data")

# Create a frame that will hold the dynamic content (graphs/values)
dynamic_frame = ctk.CTkFrame(root, width=600, height=400)
dynamic_frame.pack(pady=20)

# Create a label for counter
label_counter = ctk.CTkLabel(root, text="Counter: 0")
label_counter.pack(pady=10)

# Button to start the tasks
start_button = ctk.CTkButton(root, text="Start", command=lambda: start_tasks(label_counter))
start_button.pack(pady=20)

# Button to switch to the Dashboard view
dashboard_button = ctk.CTkButton(root, text="Dashboard", command=lambda: display_dashboard(dynamic_frame))
dashboard_button.pack(pady=20)

root.mainloop()


#
# ''' Try 2 '''
#
# import customtkinter as ctk
# from tkinter import Label
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import threading
# import random
# import time
#
# # import serial  # Uncomment when using Arduino
#
# # Initialize the global variables
# tasks_started = False
# counter = 0
# x_data = []
# y_data = []
#
#
# # arduino = serial.Serial('COM3', 9600)  # Uncomment for actual Arduino
#
# # Function to clear the frame before switching views
# def clear_frame(frame):
#     for widget in frame.winfo_children():
#         widget.destroy()
#
#
# # Task 1: Counter function
# def start_counter(label_counter):
#     global counter
#     while tasks_started:
#         counter += 1
#         label_counter.configure(text=f"Counter: {counter}")
#         time.sleep(1)
#
#
# # Task 2: Send command to Arduino (send once)
# def send_request_to_arduino():
#     # arduino.write(b'START\n')  # Uncomment when using Arduino
#     print("Request sent to Arduino to start sending data.")
#
#
# # Task 3: Receive data from Arduino and update labels
# def collect_data_from_arduino(label_id, label_lat, label_lon):
#     while tasks_started:
#         # Simulated Arduino data; replace with actual serial data when using Arduino
#         data_packet = {
#             "id": random.randint(1000, 9999),
#             "latitude": random.uniform(-90, 90),
#             "longitude": random.uniform(-180, 180)
#         }
#         # Update labels with received data
#         label_id.configure(text=f"ID: {data_packet['id']}")
#         label_lat.configure(text=f"Latitude: {data_packet['latitude']:.6f}")
#         label_lon.configure(text=f"Longitude: {data_packet['longitude']:.6f}")
#         time.sleep(1)
#
#
# # Task 4: Real-time graph updates
# def update_graph(canvas, ax):
#     if tasks_started:
#         x_data.append(time.time())
#         y_data.append(random.randint(0, 100))  # Simulated data, replace with actual
#         ax.clear()
#         ax.plot(x_data, y_data, label="Real-time Data")
#         ax.legend()
#         canvas.draw()
#         canvas.get_tk_widget().after(1000, update_graph, canvas, ax)
#
#
# # Function to display the dashboard with graphs
# def display_dashboard(frame):
#     clear_frame(frame)
#     # Create a graph using Matplotlib
#     figure = plt.Figure(figsize=(5, 4), dpi=100)
#     ax = figure.add_subplot(111)
#     canvas = FigureCanvasTkAgg(figure, frame)
#     canvas.get_tk_widget().pack(pady=20)
#     # Start real-time graph updates
#     update_graph(canvas, ax)
#
#
# # Function to display real-time values
# def display_values(frame):
#     clear_frame(frame)
#     # Create labels for Arduino data
#     label_id = ctk.CTkLabel(frame, text="ID: 0")
#     label_id.pack(pady=10)
#     label_lat = ctk.CTkLabel(frame, text="Latitude: 0.000000")
#     label_lat.pack(pady=10)
#     label_lon = ctk.CTkLabel(frame, text="Longitude: 0.000000")
#     label_lon.pack(pady=10)
#
#
#
#
# # Function to start all tasks when "Start" button is clicked
# def start_tasks(label_counter):
#     global tasks_started
#     tasks_started = True
#     start_button.configure(state="disabled")  # Disable start button
#
#     # Start Task 1: Counter
#     counter_thread = threading.Thread(target=start_counter, args=(label_counter,), daemon = True)
#     counter_thread.start()
#
#     # Start Task 2: Send request to Arduino (only once)
#     send_request_to_arduino()
#
#     # Start collecting data from Arduino
#     arduino_thread = threading.Thread(target=collect_data_from_arduino, daemon=True)
#     arduino_thread.daemon = True
#     arduino_thread.start()
#
#
# # Main window setup
# root = ctk.CTk()
# root.geometry("800x600")
# root.title("Simultaneous Tasks with Real-time Graphs and Arduino Data")
#
# # Create a frame for dynamic content (graph/values)
# dynamic_frame = ctk.CTkFrame(root, width=600, height=400)
# dynamic_frame.pack(pady=20)
#
# # Create a label for the counter
# label_counter = ctk.CTkLabel(root, text="Counter: 0")
# label_counter.pack(pady=10)
#
# # Start button to initiate all tasks
# start_button = ctk.CTkButton(root, text="Start", command=lambda: start_tasks(label_counter))
# start_button.pack(pady=20)
#
# # Button to switch to the Dashboard (graphs)
# dashboard_button = ctk.CTkButton(root, text="Dashboard", command=lambda: display_dashboard(dynamic_frame))
# dashboard_button.pack(pady=20)
#
# # Button to switch to the Values view (real-time data)
# values_button = ctk.CTkButton(root, text="Values", command=lambda: display_values(dynamic_frame))
# values_button.pack(pady=20)
#
# root.mainloop()
#

#
# ''' Try 3 '''
#
# import customtkinter as ctk
# from tkinter import Label
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import threading
# import random
# import time
# import serial  # For serial communication with Arduino
#
# # Initialize global variables
# tasks_started = False
# data_collected = []
#
# # Configure serial port (adjust port and baudrate as needed)
# SERIAL_PORT = 'COM3'  # Replace with your Arduino's port
# BAUDRATE = 9600  # Replace with your Arduino's baudrate
#
#
# # Function to clear the frame
# def clear_frame(frame):
#     for widget in frame.winfo_children():
#         widget.destroy()
#
#
# # Function to start a counter (Task 1)
# def start_counter(label_counter):
#     global counter
#     counter = 0
#     while tasks_started:
#         counter += 1
#         label_counter.configure(text=f"Counter: {counter}")
#         time.sleep(1)
#
#
# # Function to send a request to Arduino (Task 2)
# def send_request_to_arduino():
#     # This function can send an initial message to Arduino if needed
#     # arduino.write(b'START\n')  # Uncomment when using Arduino
#     print("Request sent to Arduino to start sending data.")
#
#
# # Function to collect data from Arduino (Task 3)
# def collect_data_from_arduino():
#     global data_collected
#     try:
#         # Open serial connection to Arduino
#         with serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1) as arduino:
#             while tasks_started:
#                 if arduino.in_waiting > 0:
#                     # Read data from Arduino
#                     line = arduino.readline().decode('utf-8').strip()
#                     if line:
#                         # Assuming the data is in the format: "id,latitude,longitude"
#                         data_fields = line.split(',')
#                         if len(data_fields) == 3:
#                             data_packet = {
#                                 "id": int(data_fields[0]),
#                                 "latitude": float(data_fields[1]),
#                                 "longitude": float(data_fields[2])
#                             }
#                             data_collected.append(data_packet)
#                             print(f"Data collected: {data_packet}")
#                 time.sleep(1)  # Adjust based on your needs
#     except Exception as e:
#         print(f"Error in serial communication: {e}")
#
#
# # Function to update the graph with collected data
# def update_graph(canvas, ax):
#     if tasks_started and data_collected:
#         x_data = [i for i in range(len(data_collected))]
#         y_data = [random.randint(0, 100) for _ in range(len(data_collected))]  # Simulated y_data; replace as needed
#         ax.clear()
#         ax.plot(x_data, y_data, label="Real-time Data")
#         ax.legend()
#         canvas.draw()
#         canvas.get_tk_widget().after(1000, update_graph, canvas, ax)
#
#
# # Function to display the Dashboard (graphs)
# def display_dashboard(frame):
#     clear_frame(frame)
#     figure = plt.Figure(figsize=(5, 4), dpi=100)
#     ax = figure.add_subplot(111)
#     canvas = FigureCanvasTkAgg(figure, frame)
#     canvas.get_tk_widget().pack(pady=20)
#     # Start updating the graph
#     update_graph(canvas, ax)
#
#
# # Function to display real-time values
# def display_values(frame):
#     clear_frame(frame)
#     label_id = ctk.CTkLabel(frame, text="ID: 0")
#     label_id.pack(pady=10)
#     label_lat = ctk.CTkLabel(frame, text="Latitude: 0.000000")
#     label_lat.pack(pady=10)
#     label_lon = ctk.CTkLabel(frame, text="Longitude: 0.000000")
#     label_lon.pack(pady=10)
#
#     # Update labels with the latest data
#     def update_labels():
#         if data_collected:
#             latest_data = data_collected[-1]
#             label_id.configure(text=f"ID: {latest_data['id']}")
#             label_lat.configure(text=f"Latitude: {latest_data['latitude']:.6f}")
#             label_lon.configure(text=f"Longitude: {latest_data['longitude']:.6f}")
#         frame.after(1000, update_labels)  # Update every second
#
#     update_labels()
#
#
# # Function to start all tasks when "Start" button is clicked
# def start_tasks(label_counter):
#     global tasks_started
#     tasks_started = True
#     start_button.configure(state="disabled")  # Disable the start button
#
#     # Start Task 1: Counter
#     counter_thread = threading.Thread(target=start_counter, args=(label_counter,))
#     counter_thread.daemon = True
#     counter_thread.start()
#
#     # Start Task 2: Send request to Arduino (only once)
#     send_request_to_arduino()
#
#     # Start Task 3: Collect data from Arduino
#     data_collection_thread = threading.Thread(target=collect_data_from_arduino)
#     data_collection_thread.daemon = True
#     data_collection_thread.start()
#
#
# # Main window setup
# root = ctk.CTk()
# root.geometry("800x600")
# root.title("Simultaneous Tasks with Real-time Graphs and Arduino Data")
#
# # Create a frame for dynamic content (graph/values)
# dynamic_frame = ctk.CTkFrame(root, width=600, height=400)
# dynamic_frame.pack(pady=20)
#
# # Create a label for the counter
# label_counter = ctk.CTkLabel(root, text="Counter: 0")
# label_counter.pack(pady=10)
#
# # Start button to initiate all tasks
# start_button = ctk.CTkButton(root, text="Start", command=lambda: start_tasks(label_counter))
# start_button.pack(pady=20)
#
# # Button to switch to the Dashboard (graphs)
# dashboard_button = ctk.CTkButton(root, text="Dashboard", command=lambda: display_dashboard(dynamic_frame))
# dashboard_button.pack(pady=20)
#
# # Button to switch to the Values view (real-time data)
# values_button = ctk.CTkButton(root, text="Values", command=lambda: display_values(dynamic_frame))
# values_button.pack(pady=20)
#
# root.mainloop()
