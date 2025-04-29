import serial
import time
import csv
import datetime

PORT = "COM3"  # Port where Arduino is connected 
BAUD_RATE = 115200

try:
    ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print(f"Connected to Arduino on {PORT}")
except serial.SerialException as e:
    print(f"Serial error: {e}")
    exit()

participant_id = input("Enter Participant ID (e.g., participant_1): ").strip()
ser.write(participant_id.encode() + b"\n")

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
file_name = f"{participant_id}_{timestamp}.csv"
print(f"Data will be saved to: {file_name}")

input("Press ENTER to begin calibration monitoring...")
ser.write(b"start\n")
print("Waiting for calibration (Sys/Gyro/Accel/Mag > 1)...")

while True:
    line = ser.readline().decode().strip()
    if line.startswith("CALIBRATION:"):
        calib = list(map(int, line.replace("CALIBRATION:", "").split(",")))
        sys, gyro, accel, mag = calib
        print(f"Calibration -> Sys:{sys} Gyro:{gyro} Accel:{accel} Mag:{mag}")
    elif line == "LOGGING_STARTED":
        print("Logging started!\n")
        break
    time.sleep(0.1)

with open(file_name, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([
        "Participant", "Date_Time", "Arduino_Timestamp_ms",
        "Accel_X", "Accel_Y", "Accel_Z",
        "Gyro_X", "Gyro_Y", "Gyro_Z",
        "Mag_X", "Mag_Y", "Mag_Z",
        "Euler_Heading", "Euler_Roll", "Euler_Pitch"
    ])

    try:
        while True:
            line = ser.readline().decode().strip()
            if line == "LOGGING_STOPPED":
                break
            if line:
                try:
                    values = [float(x) for x in line.split(",")]
                    if len(values) == 13:
                        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                        row = [participant_id, now] + values
                        writer.writerow(row)
                        print(row)
                except ValueError:
                    print(f"Bad data: {line}")
    except KeyboardInterrupt:
        print("\nStopping logging...")
        ser.write(b"stop\n")
        time.sleep(1)
    finally:
        ser.close()
        print(f"Data saved to: {file_name}")
