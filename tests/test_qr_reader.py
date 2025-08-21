import tkinter as tk
from tkinter import ttk
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logic.com_selector import list_com_ports
from logic.com_reader import ComPortReader

class ComPortApp:
    def __init__(self, root):
        self.root = root
        self.root.title("COM Port QR Reader")

        # Dropdown for COM ports
        self.port_label = ttk.Label(root, text="Select COM Port:")
        self.port_label.pack(pady=5)
        self.port_dropdown = ttk.Combobox(root, values=list_com_ports())
        self.port_dropdown.pack(pady=5)
        
        # Refresh button for COM ports
        self.refresh_button = ttk.Button(root, text="Refresh Ports", command=self.refresh_ports)
        self.refresh_button.pack(pady=5)

        # Button to start/stop reading
        self.start_button = ttk.Button(root, text="Start Reading", command=self.start_reading)
        self.start_button.pack(pady=5)
        
        # Button to stop reading
        self.stop_button = ttk.Button(root, text="Stop Reading", command=self.stop_reading, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        # Status label for error messages
        self.status_label = ttk.Label(root, text="Status: Ready")
        self.status_label.pack(pady=5)
        
        # Visual indicator for reading status
        self.status_indicator = tk.Canvas(root, width=20, height=20)
        self.status_indicator.pack(pady=5)
        self.status_indicator.create_oval(5, 5, 15, 15, fill="gray", tags="indicator")

        # Field for COM port data
        self.output_label = ttk.Label(root, text="COM Port Data:")
        self.output_label.pack(pady=5)
        self.output_field = tk.Text(root, height=15, width=80)
        self.output_field.pack(pady=5)

        self.reader = None

    def start_reading(self):
        selected_port = self.port_dropdown.get()
        if not selected_port:
            self.output_field.insert(tk.END, "Please select a COM port first.\n")
            return

        # Clear old text
        self.output_field.delete(1.0, tk.END)
        
        # Update status
        self.status_label.config(text="Status: Reading...")
        self.status_indicator.itemconfig("indicator", fill="green")

        # Start reader
        self.reader = ComPortReader(port=selected_port, baudrate=115200, callback=self.show_output, error_callback=self.show_error)
        self.reader.start_reading()
        
        # Update button states
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.port_dropdown.config(state=tk.DISABLED)

    def stop_reading(self):
        if self.reader:
            self.reader.stop_reading()
            self.reader = None
            
        # Update status
        self.status_label.config(text="Status: Stopped")
        self.status_indicator.itemconfig("indicator", fill="gray")
        
        # Update button states
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.port_dropdown.config(state=tk.NORMAL)

    def show_error(self, error_message):
        # Display error in status label
        self.status_label.config(text=f"Error: {error_message}")
        # Change visual indicator to red
        self.status_indicator.itemconfig("indicator", fill="red")
        # Also add error to output field
        self.output_field.insert(tk.END, f"Error: {error_message}\n")
        self.output_field.see(tk.END)
        
    def refresh_ports(self):
        # Refresh the list of available COM ports
        from logic.com_selector import list_com_ports
        self.port_dropdown.config(values=list_com_ports())
        self.status_label.config(text="Status: COM ports refreshed")

    def show_output(self, data):
        self.output_field.insert(tk.END, f"{data}\n")
        self.output_field.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ComPortApp(root)
    root.mainloop()