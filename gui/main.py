import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QFileDialog,
    QComboBox, QTextEdit, QFrame, QHeaderView, QMessageBox, QStatusBar, QDialog
)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QColor
import csv
from logic.com_reader import ComPortReader
from logic.com_selector import list_com_ports
from logic.parser import parse_cpd_cards


class Worker(QObject):
    data_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

class PreviewWindow(QDialog):
    def __init__(self, expected_cards, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preview Expected Cards")
        self.setMinimumSize(400, 300)
        self.setStyleSheet(parent.styleSheet()) # Inherit stylesheet

        layout = QVBoxLayout(self)

        if not expected_cards:
            layout.addWidget(QLabel("No expected cards loaded."))
        else:
            table = QTableWidget(len(expected_cards), 2)
            table.setHorizontalHeaderLabels(["NUMCARD", "ICCID"])
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # Make table non-editable
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

            for row, (numcard, iccid) in enumerate(expected_cards):
                table.setItem(row, 0, QTableWidgetItem(numcard))
                table.setItem(row, 1, QTableWidgetItem(iccid))

            layout.addWidget(table)

class ModernCardValidator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = Worker()
        self.log_data = []
        self.selected_file_path = ""
        self.expected_cards = []
        self.current_card_index = 0
        self.first_scan_received = True
        self.init_ui()
        self.setup_timer()
        # self.load_sample_data() # Removed to prevent initial sample data
        self.com_port_reader = None
        self.refresh_com_ports()
        self.update_card_display()

        self.worker.data_received.connect(self.handle_com_data)
        self.worker.error_occurred.connect(self.handle_com_error)

    def refresh_com_ports(self):
        self.com_port_combo.clear()
        ports = list_com_ports()
        self.com_port_combo.addItems(ports)
        if not ports:
            self.start_btn.setEnabled(False)
            self.status_bar.showMessage("No COM ports found.")
        else:
            self.start_btn.setEnabled(True)
            self.status_bar.showMessage("COM ports refreshed.")

    def start_reading(self):
        selected_port = self.com_port_combo.currentText()
        if not selected_port:
            self.status_bar.showMessage("Please select a COM port first.")
            return

        self.com_port_reader = ComPortReader(
            port=selected_port,
            callback=self.worker.data_received.emit,
            error_callback=self.worker.error_occurred.emit
        )
        self.com_port_reader.start_reading()
        self.status_bar.showMessage(f"Listening on {selected_port}")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.com_port_combo.setEnabled(False)
        self.findChild(QPushButton, "refreshBtn").setEnabled(False)

    def stop_reading(self):
        if self.com_port_reader:
            self.com_port_reader.stop_reading()
            self.com_port_reader = None
        self.status_bar.showMessage("Stopped listening.")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.com_port_combo.setEnabled(True)
        self.findChild(QPushButton, "refreshBtn").setEnabled(True)

        # Clear display fields and reset parsing timeline
        self.clear_loaded_file()

    

    def handle_com_data(self, scanned_code):
        self.scanner_input.setText(scanned_code)
        timestamp = datetime.now().strftime("%H:%M:%S")

        if self.first_scan_received:
            self.first_scan_received = False
            # No update_card_display() here, it will be called at the end of this function
            # or when load_expected_cards is called.

        # Ensure we don't go out of bounds if expected_cards is empty or index is too high
        expected_numcard = "N/A"
        expected_iccid_for_display = "N/A"
        status = "N/A" # Default status if no expected cards

        if self.expected_cards and self.current_card_index < len(self.expected_cards):
            expected_numcard = self.expected_cards[self.current_card_index][0]
            expected_iccid_for_display = self.expected_cards[self.current_card_index][1]
            status = "OK" if scanned_code == expected_iccid_for_display else "NOT OK"
        elif self.expected_cards and self.current_card_index >= len(self.expected_cards):
            # Scans received after the expected sequence has ended
            expected_iccid_for_display = "End of sequence"
            status = "N/A" # Or "OVERFLOW" or similar

        # Log the current scan's details
        self.add_log_entry(timestamp, scanned_code, expected_iccid_for_display, status, self.log_table.rowCount() + 1)
        self.status_bar.showMessage(f"Scanned: {scanned_code} - {status}")

        # Update display for the *next* expected card
        self.update_card_display()

        # Now, advance the index for the *next* scan
        self.current_card_index += 1

    def update_card_display(self):
        if self.expected_cards:
            if self.current_card_index < len(self.expected_cards):
                # Display ICCID for current card
                self.current_card_input.setText(self.expected_cards[self.current_card_index][1])
            else:
                self.current_card_input.setText("End of sequence")
            
            if self.current_card_index + 1 < len(self.expected_cards):
                # Display ICCID for next expected card
                self.next_expected_card_input.setText(self.expected_cards[self.current_card_index + 1][1])
            else:
                self.next_expected_card_input.setText("End of sequence")
        else:
            self.current_card_input.setText("N/A")
            self.next_expected_card_input.setText("N/A")

    def handle_com_error(self, error):
        self.status_bar.showMessage(error)

    def init_ui(self):
        self.setWindowTitle("Card Sequence Validator")
        self.setMinimumSize(900, 650)

        self.setStyleSheet("""
            /* General Window and Background */
            QMainWindow {
                background-color: #1A2A3A; /* Deep Ocean: Background */
                color: #EAEAEA; /* Deep Ocean: Text */
            }

            /* Labels */
            QLabel {
                color: #EAEAEA; /* Deep Ocean: Text */
                font-weight: bold;
                padding: 2px;
            }

            /* LineEdits and ComboBoxes (Input/Display Fields) */
            QLineEdit, QComboBox {
                padding: 10px;
                border: 1px solid #2A3A4A; /* Deep Ocean: Panels/Surface */
                border-radius: 5px;
                background-color: #2A3A4A; /* Deep Ocean: Panels/Surface */
                color: #EAEAEA; /* Deep Ocean: Text */
                selection-background-color: #4A9A9A; /* Deep Ocean: Primary Accent */
                selection-color: #EAEAEA; /* Deep Ocean: Text */
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #4A9A9A; /* Deep Ocean: Primary Accent */
                background-color: #2A3A4A; /* Deep Ocean: Panels/Surface */
            }
            QLineEdit::placeholder {
                color: #99AABF; /* Lighter shade for placeholder */
            }

            /* PushButtons */
            QPushButton {
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                color: #EAEAEA; /* Deep Ocean: Text */
                background-color: #4A9A9A; /* Deep Ocean: Primary Accent */
                border: none;
            }
            QPushButton:hover {
                background-color: #5AAFAF; /* Lighter shade of Primary Accent */
            }
            QPushButton:pressed {
                background-color: #3A8A8A; /* Darker shade of Primary Accent */
            }
            QPushButton:disabled {
                background-color: #99AABF; /* Lighter shade for placeholder */
                color: #1A2A3A; /* Deep Ocean: Background */
                border: 1px solid #2A3A4A; /* Deep Ocean: Panels/Surface */
            }

            /* Table Widget */
            QTableWidget {
                background-color: #2A3A4A; /* Deep Ocean: Panels/Surface */
                color: #EAEAEA; /* Deep Ocean: Text */
                border: 1px solid #1A2A3A; /* Deep Ocean: Background */
                border-radius: 5px;
                gridline-color: #1A2A3A; /* Deep Ocean: Background */
                selection-background-color: #4A9A9A; /* Deep Ocean: Primary Accent */
                selection-color: #EAEAEA; /* Deep Ocean: Text */
                alternate-background-color: #1A2A3A; /* Deep Ocean: Background */
            }
            QHeaderView::section {
                background-color: #1A2A3A; /* Deep Ocean: Background */
                padding: 10px;
                font-weight: bold;
                color: #EAEAEA; /* Deep Ocean: Text */
                border: 1px solid #2A3A4A; /* Deep Ocean: Panels/Surface */
                border-bottom: 2px solid #4A9A9A; /* Deep Ocean: Primary Accent */
            }

            /* Header Frame */
            QFrame#headerFrame {
                background-color: #2A3A4A; /* Deep Ocean: Panels/Surface */
                border: 1px solid #1A2A3A; /* Deep Ocean: Background */
                border-radius: 5px;
                padding: 10px;
            }

            /* Title Label */
            QLabel#titleLabel {
                font-size: 26px;
                font-weight: bold;
                color: #4A9A9A; /* Deep Ocean: Primary Accent */
            }
            QLabel#clockLabel {
                font-size: 14px;
                color: #99AABF; /* Lighter shade for placeholder */
                border: 1px solid #2A3A4A; /* Deep Ocean: Panels/Surface */
                border-radius: 4px;
                padding: 6px;
                background-color: #2A3A4A; /* Deep Ocean: Panels/Surface */
            }

            /* Status Bar */
            QStatusBar {
                background-color: #2A3A4A; /* Deep Ocean: Panels/Surface */
                color: #EAEAEA; /* Deep Ocean: Text */
                padding: 5px;
            }
        """)


        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        self.create_header(main_layout)
        self.create_input_sections(main_layout)
        self.create_log_viewer(main_layout)
        self.create_file_operations(main_layout)
        self.create_bottom_section(main_layout)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Application ready")

    def create_header(self, layout):
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        h_layout = QHBoxLayout(header_frame)
        h_layout.setContentsMargins(15, 15, 15, 15)

        title_label = QLabel("Card Sequence Validator")
        title_label.setObjectName("titleLabel")
        h_layout.addWidget(title_label)
        h_layout.addStretch()

        self.clock_label = QLabel()
        self.clock_label.setObjectName("clockLabel")
        h_layout.addWidget(self.clock_label)

        layout.addWidget(header_frame)

    def create_input_sections(self, layout):
        # COM Port Selection
        com_port_layout = QHBoxLayout()
        com_port_layout.addWidget(QLabel("Select COM Port:"))
        self.com_port_combo = QComboBox()
        com_port_layout.addWidget(self.com_port_combo)
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("refreshBtn")
        refresh_btn.clicked.connect(self.refresh_com_ports)
        com_port_layout.addWidget(refresh_btn)
        layout.addLayout(com_port_layout)

        # Start/Stop Buttons
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.start_reading)
        button_layout.addWidget(self.start_btn)
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_reading)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        layout.addLayout(button_layout)

        scan_layout = QHBoxLayout()
        scan_layout.addWidget(QLabel("Scanner Input:"))
        self.scanner_input = QLineEdit()
        self.scanner_input.setPlaceholderText("Waiting for scan...")
        self.scanner_input.setReadOnly(True)
        scan_layout.addWidget(self.scanner_input)
        layout.addLayout(scan_layout)

        card_layout = QHBoxLayout()
        card_layout.addWidget(QLabel("Current Card:"))
        self.current_card_input = QLineEdit()
        self.current_card_input.setPlaceholderText("")
        self.current_card_input.setReadOnly(True)
        card_layout.addWidget(self.current_card_input)
        layout.addLayout(card_layout)

        next_card_layout = QHBoxLayout()
        next_card_layout.addWidget(QLabel("Next Expected Card:"))
        self.next_expected_card_input = QLineEdit()
        self.next_expected_card_input.setPlaceholderText("")
        self.next_expected_card_input.setReadOnly(True)
        next_card_layout.addWidget(self.next_expected_card_input)
        layout.addLayout(next_card_layout)

    def create_log_viewer(self, layout):
        layout.addWidget(QLabel("Log Viewer"))
        self.log_table = QTableWidget(0, 5)
        self.log_table.setHorizontalHeaderLabels(["Index", "Timestamp", "Scanned Code", "Expected Code", "Status"])
        header = self.log_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.log_table.setColumnWidth(0, 50)
        self.log_table.setColumnWidth(1, 100)
        self.log_table.setColumnWidth(4, 80)
        self.log_table.setAlternatingRowColors(True)
        layout.addWidget(self.log_table)

    def create_file_operations(self, layout):
        file_layout = QHBoxLayout()
        select_btn = QPushButton("Select .cpd/txt File")
        select_btn.setObjectName("fileBtn")
        select_btn.clicked.connect(self.select_file)
        preview_btn = QPushButton("Preview File")
        preview_btn.setObjectName("fileBtn")
        preview_btn.clicked.connect(self.preview_file)
        download_btn = QPushButton("Download Logs")
        download_btn.setObjectName("fileBtn")
        download_btn.clicked.connect(self.download_logs)
        clear_upload_btn = QPushButton("Clear Upload")
        clear_upload_btn.setObjectName("clearUploadBtn")
        clear_upload_btn.clicked.connect(self.clear_loaded_file)
        file_layout.addWidget(select_btn)
        file_layout.addWidget(preview_btn)
        file_layout.addWidget(download_btn)
        file_layout.addWidget(clear_upload_btn)
        layout.addLayout(file_layout)

    def create_bottom_section(self, layout):
        pass # Removed text_area and its layout

    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.update_clock()

    def update_clock(self):
        now = datetime.now().strftime("%Y-%m-%d | %H:%M:%S")
        self.clock_label.setText(now)

    def load_sample_data(self):
        self.add_log_entry("19:18:10", "ABCD123456", "N/A", "OK", 1)
        self.add_log_entry("19:18:30", "ABCD123457", "N/A", "NOT OK", 2)

    def add_log_entry(self, timestamp, scanned_code, expected_code, status, index):
        row_pos = self.log_table.rowCount()
        self.log_table.insertRow(row_pos)
        
        timestamp_item = QTableWidgetItem(timestamp)
        scanned_code_item = QTableWidgetItem(scanned_code)
        expected_code_item = QTableWidgetItem(expected_code)
        status_item = QTableWidgetItem(status)

        timestamp_item.setFlags(timestamp_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        scanned_code_item.setFlags(scanned_code_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        expected_code_item.setFlags(expected_code_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

        self.log_table.setItem(row_pos, 0, timestamp_item)
        self.log_table.setItem(row_pos, 1, scanned_code_item)
        self.log_table.setItem(row_pos, 2, expected_code_item)

        status_item.setFont(QFont("Arial", weight=QFont.Weight.Bold))
        if status == "OK":
            status_item.setForeground(QColor("#2ecc71")) # Green
        else:
            status_item.setForeground(QColor("#e74c3c")) # Red
        self.log_table.setItem(row_pos, 3, status_item)

        self.log_data.append({
            "index": index, "timestamp": timestamp, "scanned_code": scanned_code, "expected_code": expected_code, "status": status
        })

    

    

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "",
                                                   "CPD Files (*.cpd);;Text Files (*.txt);;All Files (*)")
        if file_path:
            self.selected_file_path = file_path
            self.status_bar.showMessage(f"Selected: {os.path.basename(file_path)}", 3000)
            self.load_expected_cards()
            self.findChild(QPushButton, "fileBtn").setEnabled(False)

    def preview_file(self):
        if not self.selected_file_path:
            QMessageBox.warning(self, "Warning", "Please select a file first!")
            return
        
        # Pass the expected_cards directly to the new preview window
        preview_dialog = PreviewWindow(self.expected_cards, self)
        preview_dialog.exec() # Show as modal dialog

    def load_expected_cards(self):
        if not self.selected_file_path:
            self.expected_cards = []
            return
        try:
            # Use the parser to get the paired cards
            parsed_data = parse_cpd_cards(self.selected_file_path)
            # self.expected_cards will now store (NUMCARD, ICCID) tuples
            self.expected_cards = [card_tuple for card_tuple, _ in parsed_data]
            
            self.current_card_index = 0
            self.first_scan_received = True
            self.status_bar.showMessage(f"Loaded {len(self.expected_cards)} expected cards.", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading expected cards: {str(e)}")
            self.expected_cards = []

    def download_logs(self):
        if not self.log_data:
            QMessageBox.information(self, "Info", "No log data to download!")
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Logs",
                                                   f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                                   "CSV Files (*.csv)")
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=['index', 'timestamp', 'scanned_code', 'expected_code', 'status'])
                    writer.writeheader()
                    writer.writerows(self.log_data)
                QMessageBox.information(self, "Success", f"Logs saved to {file_path}")
                self.status_bar.showMessage("Logs downloaded successfully", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving file: {str(e)}")

    def clear_loaded_file(self):
        self.selected_file_path = ""
        self.expected_cards = []
        self.current_card_index = 0
        self.first_scan_received = True
        self.scanner_input.clear()
        self.current_card_input.clear()
        self.next_expected_card_input.clear()
        # self.text_area.clear() # Removed as text_area is no longer present
        self.findChild(QPushButton, "fileBtn").setEnabled(True)
        self.status_bar.showMessage("Loaded file cleared.", 3000)

    


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = ModernCardValidator()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
