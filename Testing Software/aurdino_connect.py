import serial

flight_name = ""
baud_rate = 9600
com = "COM7"

Values_Dictionaries = {"Team_ID": "", "TimeStamp": "", "Packet_Count": "", "Altitude": "", "Pressure": "", "Temperature": "",
                       "Voltage": "", "GNSS_Time": "", "GNSS_Latitude": "", "GNSS_Longitude": "",
                       "GNSS_Altitude": "", "GNSS_Stats": "", "Accelerometer_data": "", "Gyro_Spin_Rate": "", "FS_State": "",
                       "Humidity": "", "Magnetic_Field": "", "CO": ""}

# ser = serial.Serial(com, baud_rate)

def stringParse(string):
    string = string.decode('utf-8')
    parsed_data = list(string[:].strip().split(','))
    j = 0
    for i in Values_Dictionaries:
        Values_Dictionaries[i] = parsed_data[j]
        j+=1


data = b'Team_ID,7:5:20,6,8.96,1002.56,23.10,0.00,7:5:20,0.00,0.00,0.00,1,1:2:3,4:5:6,1,0.00,7:8:9,7.44\r\n'

while True:

    # data = ser.readline()

    # print(data)

    stringParse(data)

    print(Values_Dictionaries)


# Team_ID,6:43:4,7,9.07,1002.37,21.30,Voltage,GNSS_Time,GNSS_Latitude,GNSS_Longitude,GNSS_Altitude,GNSS_Stats,Accelerometer_data,Gyro_Spin_Rate,FS_State,Humidity,Magnetic_Field,46.15\r\n'

# b'Team_ID,6:57:11,9,9.01,1002.51,27.00,Voltage,GNSS_Time,GNSS_Latitude,GNSS_Longitude,GNSS_Altitude,GNSS_Stats,Accelerometer_data,Gyro_Spin_Rate,FS_State,Humidity,Magnetic_Field,20.38\r\n'

# b'Team_ID,7:5:20,6,8.96,1002.56,23.10,0.00,7:5:20,0.00,0.00,0.00,1,1:2:3,4:5:6,1,0.00,7:8:9,7.44\r\n'