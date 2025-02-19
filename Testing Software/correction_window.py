import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import random
import time

# Global variables to store graph data
real_time_data = {
    "velocity": [],
    "pressure": [],
    "temperature": [],
    "accelerometer": [],
    "time": []  # Common time axis
}

def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

# Function to update the graph and print data to terminal
def update_graph(axes):
    if len(real_time_data["time"]) == 0:
        real_time_data["time"].append(time.time())
    else:
        real_time_data["time"].append(real_time_data["time"][-1] + 0.3)  # Update the interval to every 0.3 seconds
    
    for key in ["velocity", "pressure", "temperature", "accelerometer"]:
        real_time_data[key].append(random.randint(0, 100))
    
    data_keys = list(real_time_data.keys())[:-1]  # Convert dict_keys to list and slice
    
    for ax, key in zip(axes.flatten(), data_keys):
        ax.clear()
        ax.plot(real_time_data["time"], real_time_data[key], label=key.capitalize(), color='blue', linewidth=2)  # Set the line width to 2 for bold lines
        
        # Ensure x and y-axis labels are plotted
        ax.set_xlabel("Time")
        ax.set_ylabel(key.capitalize())
        
        # Increase the line width of the vertical scaling (y-axis)
        ax.tick_params(axis='y', width=2)  # Set the tick width for y-axis
        ax.grid(True, which='both', axis='y', linewidth=2)  # Set the grid line width for y-axis

        ax.legend()
        ax.grid()
        
        # Print the data to the terminal
        print(f"{key.capitalize()}: {real_time_data[key]}")

def animate(i, axes, canvas):
    update_graph(axes)
    canvas.draw()

# Function to create and display multiple graphs within the provided frame
def display_dashboard(frame):
    clear_frame(frame)
    
    # Create a 2x2 grid of subplots (4 graphs) with slight padding between graphs
    figure, axes = plt.subplots(2, 2, figsize=(10, 6))
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, wspace=0.2, hspace=0.2)  # Add slight padding around the graphs
    
    canvas = FigureCanvasTkAgg(figure, frame)
    canvas.get_tk_widget().pack(fill='both', expand=True)

    # Use matplotlib's animation function to update graphs in real-time
    global ani
    ani = FuncAnimation(figure, animate, fargs=(axes, canvas), interval=300, save_count=100)  # Interval set to 300 ms (0.3 seconds)

# Main window setup
APP = ctk.CTk()
APP.geometry("900x700")
APP.title("Dynamic Real-time Graphs")

# Title Frame
titleFrame = ctk.CTkFrame(APP, fg_color='#000000', height=80)
titleFrame.pack(side="top", fill="x")

# Option Frame on the left
optionFrame = ctk.CTkFrame(APP, fg_color='#000000', width=300)
optionFrame.pack(side="left", fill="y")

# Window Frame takes the remaining space
windowFrame = ctk.CTkFrame(APP, fg_color='#111010')
windowFrame.pack(side="left", fill="both", expand=True)

# Display the dashboard in the windowFrame
display_dashboard(windowFrame)

APP.mainloop()
