import tkinter as tk
import sqlite3
import time

# Database setup
conn = sqlite3.connect('sensor_data.db')
cursor = conn.cursor()

# Create the database table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS sensor_data (
                    timestamp REAL PRIMARY KEY,
                    velocity_x REAL,
                    velocity_y REAL,
                    velocity_z REAL,
                    acceleration_x REAL,
                    acceleration_y REAL,
                    acceleration_z REAL,
                    longitude REAL,
                    latitude REAL,
                    humidity REAL,
                    altitude REAL,
                    pressure REAL,
                    temperature REAL,
                    magnetic_field_x REAL,
                    magnetic_field_y REAL,
                    magnetic_field_z REAL,
                    co REAL,
                    h2 REAL
                )''')

# Function to update the UI with data from the database
def update_ui():
    cursor.execute("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 1")
    data = cursor.fetchone()
    if data:
        # Update the UI elements with data from the database
        velocity_x_label.config(text=f"X {data[1]}")
        velocity_y_label.config(text=f"Y {data[2]}")
        velocity_z_label.config(text=f"Z {data[3]}")
        acceleration_x_label.config(text=f"X {data[4]}")
        acceleration_y_label.config(text=f"Y {data[5]}")
        acceleration_z_label.config(text=f"Z {data[6]}")
        longitude_label.config(text=f"Longitude {data[7]}")
        latitude_label.config(text=f"Latitude {data[8]}")
        humidity_label.config(text=f"Humidity {data[9]}")
        altitude_label.config(text=f"Altitude {data[10]} Ft")
        pressure_label.config(text=f"Pressure {data[11]} psi")
        temperature_label.config(text=f"Temperature {data[12]} F")
        magnetic_field_x_label.config(text=f"X {data[13]}")
        magnetic_field_y_label.config(text=f"Y {data[14]}")
        magnetic_field_z_label.config(text=f"Z {data[15]}")
        co_label.config(text=f"CO {data[16]} psi")
        h2_label.config(text=f"H2 {data[17]} F")
    root.after(1000, update_ui)  # Update every second

# Create the main window
root = tk.Tk()
root.title("Sensor Data")
root.geometry("800x600")

# Create frames for the UI elements
velocity_frame = tk.Frame(root)
velocity_frame.pack(pady=10)
acceleration_frame = tk.Frame(root)
acceleration_frame.pack(pady=10)
location_frame = tk.Frame(root)
location_frame.pack(pady=10)
environment_frame = tk.Frame(root)
environment_frame.pack(pady=10)
magnetic_field_frame = tk.Frame(root)
magnetic_field_frame.pack(pady=10)
gases_frame = tk.Frame(root)
gases_frame.pack(pady=10)
log_frame = tk.Frame(root)
log_frame.pack(pady=10)

# Create labels for velocity
velocity_label = tk.Label(velocity_frame, text="Velocity", font=("Arial", 16))
velocity_label.pack(pady=5)
velocity_x_label = tk.Label(velocity_frame, text="X 0", font=("Arial", 14))
velocity_x_label.pack(side=tk.LEFT, padx=10)
velocity_y_label = tk.Label(velocity_frame, text="Y 0", font=("Arial", 14))
velocity_y_label.pack(side=tk.LEFT, padx=10)
velocity_z_label = tk.Label(velocity_frame, text="Z 0", font=("Arial", 14))
velocity_z_label.pack(side=tk.LEFT, padx=10)

# Create labels for acceleration
acceleration_label = tk.Label(acceleration_frame, text="Acceleration", font=("Arial", 16))
acceleration_label.pack(pady=5)
acceleration_x_label = tk.Label(acceleration_frame, text="X 0", font=("Arial", 14))
acceleration_x_label.pack(side=tk.LEFT, padx=10)
acceleration_y_label = tk.Label(acceleration_frame, text="Y 0", font=("Arial", 14))
acceleration_y_label.pack(side=tk.LEFT, padx=10)
acceleration_z_label = tk.Label(acceleration_frame, text="Z 0", font=("Arial", 14))
acceleration_z_label.pack(side=tk.LEFT, padx=10)

# Create labels for longitude and latitude
longitude_label = tk.Label(location_frame, text="Longitude 0", font=("Arial", 14))
longitude_label.pack(side=tk.LEFT, padx=10)
latitude_label = tk.Label(location_frame, text="Latitude 0", font=("Arial", 14))
latitude_label.pack(side=tk.LEFT, padx=10)

# Create labels for humidity, altitude, pressure, and temperature
humidity_label = tk.Label(environment_frame, text="Humidity 0", font=("Arial", 14))
humidity_label.pack(side=tk.LEFT, padx=10)
altitude_label = tk.Label(environment_frame, text="Altitude 0 Ft", font=("Arial", 14))
altitude_label.pack(side=tk.LEFT, padx=10)
pressure_label = tk.Label(environment_frame, text="Pressure 0 psi", font=("Arial", 14))
pressure_label.pack(side=tk.LEFT, padx=10)
temperature_label = tk.Label(environment_frame, text="Temperature 0 F", font=("Arial", 14))
temperature_label.pack(side=tk.LEFT, padx=10)

# Create labels for magnetic field
magnetic_field_label = tk.Label(magnetic_field_frame, text="Magnetic Field", font=("Arial", 16))
magnetic_field_label.pack(pady=5)
magnetic_field_x_label = tk.Label(magnetic_field_frame, text="X 0", font=("Arial", 14))
magnetic_field_x_label.pack(side=tk.LEFT, padx=10)
magnetic_field_y_label = tk.Label(magnetic_field_frame, text="Y 0", font=("Arial", 14))
magnetic_field_y_label.pack(side=tk.LEFT, padx=10)
magnetic_field_z_label = tk.Label(magnetic_field_frame, text="Z 0", font=("Arial", 14))
magnetic_field_z_label.pack(side=tk.LEFT, padx=10)

# Create labels for CO and H2
co_label = tk.Label(gases_frame, text="CO 0 psi", font=("Arial", 14))
co_label.pack(side=tk.LEFT, padx=10)
h2_label = tk.Label(gases_frame, text="H2 0 F", font=("Arial", 14))
h2_label.pack(side=tk.LEFT, padx=10)

# Create labels for the log
log_label = tk.Label(log_frame, text="Log", font=("Arial", 16))
log_label.pack(pady=5)
log_text = tk.StringVar()
log_text.set("17:02:30-> Data packet\n17:02:31-> Data packet\n17:02:32-> Data packet")
log_label = tk.Label(log_frame, textvariable=log_text, font=("Arial", 12))
log_label.pack(pady=5)

# Start updating the UI
update_ui()

# Run the main loop
root.mainloop()

# Close the database connection
conn.close()