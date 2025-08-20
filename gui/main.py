import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QFileDialog,
    QComboBox, QTextEdit, QFrame, QHeaderView, QMessageBox, QStatusBar
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont, QColor
import csv


class ModernCardValidator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.log_data = []
        self.selected_file_path = ""
        self.init_ui()
        self.setup_timer()
        self.load_sample_data()

    def init_ui(self):
        self.setWindowTitle("Card Sequence Validator")
        self.setMinimumSize(900, 650)

        self.setStyleSheet("""
            QMainWindow { background-color: #121212; }

            QLabel {
                color: #f0f0f0;
                font-weight: bold;
            }

            QLineEdit, QComboBox {
                padding: 8px;
                border: 2px solid #333;
                border-radius: 6px;
                background-color: #1e1e1e;
                color: #ffffff;
                selection-background-color: #2979ff;
                selection-color: #ffffff;
            }
            QLineEdit:focus, QComboBox:focus { border-color: #2979ff; }
            QLineEdit::placeholder { color: #888888; }

            QPushButton {
                padding: 8px 15px;
                border-radius: 6px;
                font-weight: bold;
                color: #ffffff;
            }
            QPushButton:hover { opacity: 0.85; }
            QPushButton#scanBtn { background-color: #546e7a; }
            QPushButton#okBtn { background-color: #388e3c; }
            QPushButton#fileBtn { background-color: #0288d1; }

            QTableWidget {
                background-color: #1e1e1e;
                color: #f5f5f5;
                border: 1px solid #333;
                border-radius: 6px;
                gridline-color: #444;
                selection-background-color: #2979ff;
                selection-color: #ffffff;
                alternate-background-color: #2a2a2a;
            }
            QHeaderView::section {
                background-color: #2c2c2c;
                padding: 8px;
                font-weight: bold;
                color: #f0f0f0;
                border: none;
            }

            QTextEdit {
                border: 2px solid #333;
                border-radius: 6px;
                background-color: #1e1e1e;
                color: #f0f0f0;
                font-family: 'Courier New', monospace;
            }

            QFrame#headerFrame {
                background-color: #1f1f1f;
                border: 1px solid #333;
                border-radius: 6px;
            }

            QLabel#titleLabel {
                font-size: 24px;
                font-weight: bold;
                color: #bbdefb;
            }
            QLabel#clockLabel {
                font-size: 14px;
                color: #e0e0e0;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 6px;
                background-color: #1e1e1e;
            }

            QStatusBar {
                background-color: #1e1e1e;
                color: #f0f0f0;
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
        scan_layout = QHBoxLayout()
        scan_layout.addWidget(QLabel("Scanner Input:"))
        self.scanner_input = QLineEdit()
        self.scanner_input.setPlaceholderText("Enter scanner code...")
        scan_layout.addWidget(self.scanner_input)
        scan_btn = QPushButton("Scan")
        scan_btn.setObjectName("scanBtn")
        scan_btn.clicked.connect(self.handle_scan)
        scan_layout.addWidget(scan_btn)
        layout.addLayout(scan_layout)

        card_layout = QHBoxLayout()
        card_layout.addWidget(QLabel("Current Card:"))
        self.current_card_input = QLineEdit()
        self.current_card_input.setPlaceholderText("Enter current card code...")
        card_layout.addWidget(self.current_card_input)
        ok_btn = QPushButton("OK")
        ok_btn.setObjectName("okBtn")
        ok_btn.clicked.connect(self.handle_validation)
        card_layout.addWidget(ok_btn)
        layout.addLayout(card_layout)

        self.scanner_input.returnPressed.connect(self.handle_scan)
        self.current_card_input.returnPressed.connect(self.handle_validation)

    def create_log_viewer(self, layout):
        layout.addWidget(QLabel("Log Viewer"))
        self.log_table = QTableWidget(0, 4)
        self.log_table.setHorizontalHeaderLabels(["Timestamp", "Scanned Code", "Status", "Line"])
        header = self.log_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.log_table.setColumnWidth(0, 100)
        self.log_table.setColumnWidth(2, 80)
        self.log_table.setColumnWidth(3, 80)
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
        file_layout.addWidget(select_btn)
        file_layout.addWidget(preview_btn)
        file_layout.addWidget(download_btn)
        layout.addLayout(file_layout)

    def create_bottom_section(self, layout):
        line_layout = QHBoxLayout()
        line_layout.addWidget(QLabel("Select Line:"))
        self.line_combo = QComboBox()
        self.line_combo.addItems(["Line 1", "Line 2", "Line 3", "Line 4"])
        self.line_combo.currentTextChanged.connect(self.line_changed)
        line_layout.addWidget(self.line_combo)
        layout.addLayout(line_layout)

        self.text_area = QTextEdit()
        self.text_area.setPlaceholderText("File content will appear here...")
        self.text_area.setMaximumHeight(180)
        layout.addWidget(self.text_area)

    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.update_clock()

    def update_clock(self):
        now = datetime.now().strftime("%Y-%m-%d | %H:%M:%S")
        self.clock_label.setText(now)

    def load_sample_data(self):
        self.add_log_entry("19:18:10", "ABCD123456", "OK", "Line 1")
        self.add_log_entry("19:18:30", "ABCD123457", "NOT OK", "Line 2")

    def add_log_entry(self, timestamp, code, status, line):
        row_pos = self.log_table.rowCount()
        self.log_table.insertRow(row_pos)
        self.log_table.setItem(row_pos, 0, QTableWidgetItem(timestamp))
        self.log_table.setItem(row_pos, 1, QTableWidgetItem(code))

        status_item = QTableWidgetItem(status)
        status_item.setFont(QFont("Arial", weight=QFont.Weight.Bold))
        if status == "OK":
            status_item.setForeground(QColor(0, 128, 0))
        else:
            status_item.setForeground(QColor(200, 0, 0))
        self.log_table.setItem(row_pos, 2, status_item)

        self.log_table.setItem(row_pos, 3, QTableWidgetItem(line))
        self.log_data.append({
            "timestamp": timestamp, "code": code, "status": status, "line": line
        })

    def handle_scan(self):
        code = self.scanner_input.text().strip()
        if not code:
            self.status_bar.showMessage("Please enter a scanner code", 3000)
            return
        timestamp = datetime.now().strftime("%H:%M:%S")
        status = self.validate_code(code)
        line = self.line_combo.currentText()
        self.add_log_entry(timestamp, code, status, line)
        self.scanner_input.clear()
        self.status_bar.showMessage(f"Scanned: {code} - {status}", 3000)

    def handle_validation(self):
        code = self.current_card_input.text().strip()
        if not code:
            self.status_bar.showMessage("Please enter a current card code", 3000)
            return
        status = self.validate_code(code)
        if status == "OK":
            QMessageBox.information(self, "Validation", f"Card {code} is valid!")
        else:
            QMessageBox.warning(self, "Validation", f"Card {code} is not valid!")
        self.current_card_input.clear()

    def validate_code(self, code):
        return "OK" if len(code) >= 8 and code.isalnum() else "NOT OK"

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "",
                                                   "CPD Files (*.cpd);;Text Files (*.txt);;All Files (*)")
        if file_path:
            self.selected_file_path = file_path
            self.status_bar.showMessage(f"Selected: {os.path.basename(file_path)}", 3000)

    def preview_file(self):
        if not self.selected_file_path:
            QMessageBox.warning(self, "Warning", "Please select a file first!")
            return
        try:
            with open(self.selected_file_path, 'r', encoding='utf-8') as f:
                self.text_area.setPlainText(f.read())
            self.status_bar.showMessage("File loaded successfully", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error reading file: {str(e)}")

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
                    writer = csv.DictWriter(csvfile, fieldnames=['timestamp', 'code', 'status', 'line'])
                    writer.writeheader()
                    writer.writerows(self.log_data)
                QMessageBox.information(self, "Success", f"Logs saved to {file_path}")
                self.status_bar.showMessage("Logs downloaded successfully", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving file: {str(e)}")

    def line_changed(self, line_name):
        self.status_bar.showMessage(f"Selected: {line_name}", 2000)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = ModernCardValidator()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
