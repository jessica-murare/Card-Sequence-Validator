import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QFileDialog,
    QComboBox, QTextEdit, QFrame, QHeaderView, QMessageBox, QStatusBar, QDialog, QListWidget, QDialogButtonBox, QInputDialog
)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QColor, QPixmap
import constants
import csv
from logic.com_reader import ComPortReader
from logic.com_selector import list_com_ports
from logic.file_parser import parse_file
from services.card_validator import CardValidator
from gui.ui.preview_window import PreviewWindow
from gui.ui.select_start_card_dialog import SelectStartCardDialog


class Worker(QObject):
    data_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

class ModernCardValidator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = Worker()
        self.card_validator = CardValidator(self)
        self.log_data = []
        self.selected_file_path = ""
        self.expected_cards = []
        self.current_card_index = 0
        self.first_scan_received = True
        self.init_ui()
        self.setup_timer()
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
            self.status_bar.showMessage(constants.MSG_NO_COM_PORTS)
        else:
            self.start_btn.setEnabled(True)
            self.status_bar.showMessage(constants.MSG_COM_PORTS_REFRESHED)

    def start_reading(self):
        selected_port = self.com_port_combo.currentText()
        if not selected_port:
            self.status_bar.showMessage(constants.MSG_SELECT_COM_PORT)
            return

        self.com_port_reader = ComPortReader(
            port=selected_port,
            callback=self.worker.data_received.emit,
            error_callback=self.worker.error_occurred.emit
        )
        self.com_port_reader.start_reading()
        self.status_bar.showMessage(constants.MSG_LISTENING_ON_PORT.format(port=selected_port))
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.com_port_combo.setEnabled(False)
        self.findChild(QPushButton, "refreshBtn").setEnabled(False)

    def stop_reading(self):
        if self.com_port_reader:
            self.com_port_reader.stop_reading()
            self.com_port_reader = None
        self.status_bar.showMessage(constants.MSG_STOPPED_LISTENING)
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.com_port_combo.setEnabled(True)
        self.findChild(QPushButton, "refreshBtn").setEnabled(True)

    def handle_com_data(self, scanned_code):
        self.card_validator.handle_com_data(scanned_code)

    def get_timestamp(self):
        return datetime.now().strftime("%H:%M:%S.%f")[:-3]

    def update_card_display(self):
        if self.expected_cards:
            if self.current_card_index < len(self.expected_cards):
                self.current_card_input.setText(self.expected_cards[self.current_card_index][1])
            else:
                self.current_card_input.setText("End of sequence")
            
            if self.current_card_index + 1 < len(self.expected_cards):
                self.next_expected_card_input.setText(self.expected_cards[self.current_card_index + 1][1])
            else:
                self.next_expected_card_input.setText("End of sequence")
        else:
            self.current_card_input.setText("N/A")
            self.next_expected_card_input.setText("N/A")

    def handle_com_error(self, error):
        self.status_bar.showMessage(error)

    def init_ui(self):
        self.setWindowTitle(constants.APP_TITLE)
        self.setMinimumSize(900, 650)

        self.setStyleSheet("""
             /* General Window and Background */
             QMainWindow {
                background-color: #FFFFFF; /* General Backgrounds */
                color: #354563; /* Headers/Main UI Text */
             }
 
             /* Labels */
             QLabel {
                color: #354563; /* Headers/Main UI Text */
                 font-weight: bold;
                 padding: 2px;
             }
 
             /* LineEdits and ComboBoxes (Input/Display Fields) */
             QLineEdit, QComboBox {
                 padding: 10px;
                border: 1px solid #A0B0C0; /* Slightly darker than #BAC7D2 */
                 border-radius: 5px;
                background-color: #BAC7D2; /* Panels/Card Backgrounds */
                color: #354563; /* Headers/Main UI Text */
                selection-background-color: #7AB8F3; /* Lighter shade for selection */
                selection-color: #FFFFFF; /* General Backgrounds */
             }
             QLineEdit:focus, QComboBox:focus {
                border-color: #4896DD; /* Primary Buttons & Active Controls */
                background-color: #BAC7D2; /* Panels/Card Backgrounds */
             }
             QLineEdit::placeholder {
                 color: #99AABF; /* Lighter shade for placeholder */
             }
 
             /* Buttons */
             QPushButton {
                 padding: 10px 20px;
                 border-radius: 5px;
                 font-weight: bold;
                color: #FFFFFF; /* General Backgrounds */
                background-color: #4896DD; /* Primary Buttons & Active Controls */
                 border: none;
             }
             QPushButton:hover {
                background-color: #7DD2F3; /* Hover Effects/Sliders */
             }
             QPushButton:pressed {
                background-color: #7AB8F3; /* Lighter shade for pressed state */
             }
             QPushButton:disabled {
                background-color: #D0D8E0; /* Lighter shade of Panels/Card Backgrounds */
                color: #354563; /* Headers/Main UI Text */
                border: 1px solid #BAC7D2; /* Panels/Card Backgrounds */
             }
 
             /* Table Widget */
             QTableWidget {
                background-color: #BAC7D2; /* Panels/Card Backgrounds */
                color: #354563; /* Headers/Main UI Text */
                border: 1px solid #FFFFFF; /* General Backgrounds */
                 border-radius: 5px;
                gridline-color: #FFFFFF; /* General Backgrounds */
                selection-background-color: #4896DD; /* Primary Buttons & Active Controls */
                selection-color: #FFFFFF; /* General Backgrounds */
                alternate-background-color: #FFFFFF; /* General Backgrounds */
             }
             QHeaderView::section {
                background-color: #FFFFFF; /* General Backgrounds */
                 padding: 10px;
                 font-weight: bold;
                color: #354563; /* Headers/Main UI Text */
                border: 1px solid #BAC7D2; /* Panels/Card Backgrounds */
                border-bottom: 2px solid #4896DD; /* Primary Buttons & Active Controls */
             }
 
             /* Header Frame */
             QFrame#headerFrame {
                background-color: #BAC7D2; /* Panels/Card Backgrounds */
                border: 1px solid #FFFFFF; /* General Backgrounds */
                 border-radius: 5px;
                 padding: 10px;
             }
 
             /* Specific Labels */
             QLabel#titleLabel {
                 font-size: 26px;
                 font-weight: bold;
                color: #000000; /* Changed to black for visibility */
             }
             QLabel#clockLabel {
                 font-size: 14px;
                color: #000000; /* Changed to black for visibility */
                border: 1px solid #BAC7D2; /* Panels/Card Backgrounds */
                 border-radius: 4px;
                 padding: 6px;
                background-color: #BAC7D2; /* Panels/Card Backgrounds */
             }
 
             /* Status Bar */
             QStatusBar {
                background-color: #BAC7D2; /* Panels/Card Backgrounds */
                color: #354563; /* Headers/Main UI Text */
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
        self.status_bar.showMessage(constants.MSG_APP_READY)

    def create_header(self, layout):
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        h_layout = QHBoxLayout(header_frame)
        h_layout.setContentsMargins(15, 5, 15, 5)

        logo_label = QLabel()
        logo_path = constants.LOGO_PATH
        logo_pixmap = QPixmap(logo_path)
        logo_label.setFixedSize(142, 100)
        logo_label.setScaledContents(True)
        logo_label.setPixmap(logo_pixmap)
        h_layout.addWidget(logo_label)

        title_label = QLabel(constants.APP_TITLE)
        title_label.setObjectName("titleLabel")
        h_layout.addWidget(title_label)
        h_layout.addStretch()

        self.clock_label = QLabel()
        self.clock_label.setObjectName("clockLabel")
        h_layout.addWidget(self.clock_label)

        layout.addWidget(header_frame)

    def create_input_sections(self, layout):
        com_port_layout = QHBoxLayout()
        com_port_layout.addWidget(QLabel("Select COM Port:"))
        self.com_port_combo = QComboBox()
        com_port_layout.addWidget(self.com_port_combo)
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("refreshBtn")
        refresh_btn.clicked.connect(self.refresh_com_ports)
        com_port_layout.addWidget(refresh_btn)
        layout.addLayout(com_port_layout)

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
        self.scanner_input.setPlaceholderText(constants.MSG_WAITING_FOR_SCAN)
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
        self.log_table.setHorizontalHeaderLabels(constants.LOG_TABLE_HEADERS)
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
        layout.addWidget(self.log_table, 1)

    def create_file_operations(self, layout):
        file_layout = QHBoxLayout()
        select_btn = QPushButton(constants.BTN_SELECT_FILE)
        select_btn.setObjectName("fileBtn")
        select_btn.clicked.connect(self.select_file)
        preview_btn = QPushButton(constants.BTN_PREVIEW_FILE)
        preview_btn.setObjectName("fileBtn")
        preview_btn.clicked.connect(self.preview_file)
        download_btn = QPushButton(constants.BTN_DOWNLOAD_LOGS)
        download_btn.setObjectName("fileBtn")
        download_btn.clicked.connect(self.download_logs)
        clear_upload_btn = QPushButton(constants.BTN_CLEAR_UPLOAD)
        clear_upload_btn.setObjectName("clearUploadBtn")
        clear_upload_btn.clicked.connect(self.clear_loaded_file)
        
        self.set_start_card_btn = QPushButton(constants.BTN_SET_START_CARD)
        self.set_start_card_btn.setObjectName("setStartCardBtn")
        self.set_start_card_btn.clicked.connect(self.select_start_card)
        self.set_start_card_btn.setEnabled(False)

        clear_log_btn = QPushButton(constants.BTN_CLEAR_LOG)
        clear_log_btn.setObjectName("clearLogBtn")
        clear_log_btn.clicked.connect(self.clear_log_table)
        
        file_layout.addWidget(select_btn)
        file_layout.addWidget(preview_btn)
        file_layout.addWidget(download_btn)
        file_layout.addWidget(clear_upload_btn)
        file_layout.addWidget(self.set_start_card_btn)
        file_layout.addWidget(clear_log_btn)
        layout.addLayout(file_layout)

    def create_bottom_section(self, layout):
        pass

    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.update_clock()

    def update_clock(self):
        now = datetime.now().strftime("%Y-%m-%d | %H:%M:%S.%f")[:-3]
        self.clock_label.setText(now)

    def add_log_entry(self, timestamp, scanned_code, expected_code, status, index):
        row_pos = self.log_table.rowCount()
        self.log_table.insertRow(row_pos)
        
        index_item = QTableWidgetItem(str(index))
        timestamp_item = QTableWidgetItem(timestamp)
        scanned_code_item = QTableWidgetItem(scanned_code)
        expected_code_item = QTableWidgetItem(expected_code)
        status_item = QTableWidgetItem(status)

        index_item.setFlags(index_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        timestamp_item.setFlags(timestamp_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        scanned_code_item.setFlags(scanned_code_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        expected_code_item.setFlags(expected_code_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

        self.log_table.setItem(row_pos, 0, index_item)
        self.log_table.setItem(row_pos, 1, timestamp_item)
        self.log_table.setItem(row_pos, 2, scanned_code_item)
        self.log_table.setItem(row_pos, 3, expected_code_item)

        status_item.setFont(QFont("Arial", weight=QFont.Weight.Bold))
        if status == "OK":
            status_item.setForeground(QColor("#2ecc71"))
        else:
            status_item.setForeground(QColor("#e74c3c"))
        self.log_table.setItem(row_pos, 4, status_item)

        self.log_data.append({
            "index": index, "timestamp": timestamp, "scanned_code": scanned_code, "expected_code": expected_code, "status": status
        })

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, constants.TITLE_SELECT_FILE, "", constants.FILE_FILTER)
        if file_path:
            self.selected_file_path = file_path
            self.status_bar.showMessage(constants.MSG_FILE_SELECTED.format(file=os.path.basename(file_path)), 3000)
            self.load_expected_cards()
            self.findChild(QPushButton, "fileBtn").setEnabled(False)

    def preview_file(self):
        if not self.selected_file_path:
            QMessageBox.warning(self, "Warning", constants.MSG_NO_FILE_SELECTED)
            return
        
        preview_dialog = PreviewWindow(self.expected_cards, self)
        preview_dialog.exec()

    def load_expected_cards(self):
        if not self.selected_file_path:
            self.expected_cards = []
            return
        try:
            parsed_data = parse_file(self.selected_file_path)
            self.expected_cards = [card_tuple for card_tuple, _ in parsed_data]
            
            self.current_card_index = 0
            self.first_scan_received = True
            self.status_bar.showMessage(constants.MSG_LOADED_CARDS.format(count=len(self.expected_cards)), 3000)
            self.set_start_card_btn.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Error", constants.MSG_ERROR_LOADING_CARDS.format(error=str(e)))
            self.expected_cards = []

    def download_logs(self):
        if not self.log_data:
            QMessageBox.information(self, "Info", constants.MSG_NO_LOG_DATA)
            return
        file_path, _ = QFileDialog.getSaveFileName(self, constants.TITLE_SAVE_LOGS, f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", constants.CSV_FILE_FILTER)
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=['index', 'timestamp', 'scanned_code', 'expected_code', 'status'])
                    writer.writeheader()
                    writer.writerows(self.log_data)
                QMessageBox.information(self, "Success", constants.MSG_LOGS_SAVED.format(path=file_path))
                self.status_bar.showMessage("Logs downloaded successfully", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", constants.MSG_ERROR_SAVING_FILE.format(error=str(e)))

    def clear_loaded_file(self):
        self.selected_file_path = ""
        self.expected_cards = []
        self.current_card_index = 0
        self.first_scan_received = True
        self.scanner_input.clear()
        self.current_card_input.clear()
        self.next_expected_card_input.clear()
        self.findChild(QPushButton, "fileBtn").setEnabled(True)
        self.set_start_card_btn.setEnabled(False)
        self.status_bar.showMessage(constants.MSG_CLEARED_LOADED_FILE, 3000)

    def clear_log_table(self):
        reply = QMessageBox.question(self, "Clear Log", constants.MSG_CONFIRM_CLEAR_LOG, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.log_table.setRowCount(0)
            self.log_data = []
            self.status_bar.showMessage(constants.MSG_LOG_TABLE_CLEARED, 3000)

    def select_start_card(self):
        if not self.expected_cards:
            QMessageBox.warning(self, "Warning", constants.MSG_NO_FILE_SELECTED)
            return

        dialog = SelectStartCardDialog(self.expected_cards, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_index = dialog.get_selected_index()
            if selected_index != -1:
                self.current_card_index = selected_index
                self.update_card_display()
                QMessageBox.information(self, "Success", constants.MSG_START_PROCESSING_FROM.format(numcard=self.expected_cards[selected_index][0]))
            else:
                QMessageBox.warning(self, "Warning", constants.MSG_NO_CARD_SELECTED)

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = ModernCardValidator()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()