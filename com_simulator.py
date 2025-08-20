import serial
import time

# Configure the virtual COM port that the simulator will write to
# This should be one end of your virtual COM port pair (e.g., 'COM3' or '/dev/pts/X')
# IMPORTANT: CHANGE THIS VALUE to one of the virtual ports you created in Step 2.
# For Windows, it might be 'COM3'. For Linux, it might be '/dev/pts/0'.
SERIAL_PORT = 'COM1'  # <--- CHANGE THIS VALUE
BAUDRATE = 115200

def send_data():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
        print(f"Simulator connected to {SERIAL_PORT}. Sending data...")
        while True:
            data_to_send = input("Enter data to send (or 'exit' to quit): ")
            if data_to_send.lower() == 'exit':
                break
            ser.write(f"{data_to_send}\r\n".encode()) # Send data with a newline
            print(f"Sent: {data_to_send}")
            time.sleep(0.1) # Small delay to prevent overwhelming the receiver
    except serial.SerialException as e:
        print(f"Serial port error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Simulator disconnected.")

if __name__ == "__main__":
    send_data()
