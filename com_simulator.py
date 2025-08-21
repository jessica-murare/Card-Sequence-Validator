import serial
import time
import argparse

# Configure the virtual COM port that the simulator will write to
# This should be one end of your virtual COM port pair (e.g., 'COM3' or '/dev/pts/X')
# IMPORTANT: CHANGE THIS VALUE to one of the virtual ports you created in Step 2.
# For Windows, it might be 'COM3'. For Linux, it might be '/dev/pts/0'.
SERIAL_PORT = 'COM1'  # <--- CHANGE THIS VALUE
BAUDRATE = 115200

def send_data_from_file(file_path, delay):
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
        print(f"Simulator connected to {SERIAL_PORT}. Sending data from {file_path}...")
        with open(file_path, 'r') as f:
            for line in f:
                data_to_send = line.strip()
                if data_to_send:
                    ser.write(f"{data_to_send}\r\n".encode()) # Send data with a newline
                    print(f"Sent: {data_to_send}")
                    time.sleep(delay)
    except serial.SerialException as e:
        print(f"Serial port error: {e}")
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Simulator disconnected.")

def send_data_interactive():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
        print(f"Simulator connected to {SERIAL_PORT}. Sending data interactively...")
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
    parser = argparse.ArgumentParser(description="COM Port Simulator for sending data.")
    parser.add_argument("-f", "--file", help="Path to a file containing data to send (one value per line).")
    parser.add_argument("-d", "--delay", type=float, default=0.01, help="Delay in seconds between sending each data point (default: 0.01).")
    args = parser.parse_args()

    if args.file:
        send_data_from_file(args.file, args.delay)
    else:
        send_data_interactive()