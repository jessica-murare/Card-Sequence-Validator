import serial
import threading

class ComPortReader:
    def __init__(self, port, baudrate=115200, callback=None, error_callback=None):
        self.port = port
        self.baudrate = baudrate
        self.callback = callback
        self.error_callback = error_callback
        self.running = False
        self.thread = None

    def start_reading(self):
        self.running = True
        self.thread = threading.Thread(target=self.read_loop)
        self.thread.daemon = True
        self.thread.start()

    def stop_reading(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join()

    def read_loop(self):
        try:
            with serial.Serial(
                self.port,
                self.baudrate,
                bytesize=8,      # Data size = 8
                parity='N',      # Parity = none
                stopbits=1,      # Standard stop bits
                timeout=1,       # Timeout
                rtscts=False,    # Handshake = off
                dsrdtr=False     # Handshake = off
            ) as ser:
                while self.running:
                    if ser.in_waiting > 0:
                        raw_data = ser.readline()
                        # Show both raw bytes and decoded string for debugging
                        decoded_data = raw_data.decode(errors='ignore').strip()
                        if self.callback:
                            # Send the decoded data directly
                            self.callback(f"Data: {decoded_data}")
        except serial.SerialException as e:
            if self.error_callback:
                self.error_callback(f"Serial error: {e}")
            else:
                print(f"Error: {e}")
        except Exception as e:
            if self.error_callback:
                self.error_callback(f"Unexpected error: {e}")
            else:
                print(f"Unexpected error: {e}")