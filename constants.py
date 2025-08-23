"""
This module contains constants used throughout the application.
"""

# UI Constants
APP_TITLE = "Card Sequence Validator"
BTN_SELECT_FILE = "Select .cpd/txt File"
BTN_PREVIEW_FILE = "Preview File"
BTN_DOWNLOAD_LOGS = "Download Logs"
BTN_CLEAR_UPLOAD = "Clear Upload"
BTN_SET_START_CARD = "Set Start Card"
BTN_CLEAR_LOG = "Clear Log"
TITLE_SELECT_FILE = "Select File"
FILE_FILTER = "CPD Files (*.cpd);;Text Files (*.txt);;All Files (*)"
TITLE_SAVE_LOGS = "Save Logs"
CSV_FILE_FILTER = "CSV Files (*.csv)"
LOG_TABLE_HEADERS = ["Index", "Timestamp", "Scanned Code", "Expected Code", "Status"]
MSG_WAITING_FOR_SCAN = "Waiting for scan..."


# File Paths
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

ASSETS_DIR = "assets"
LOGO_FILE = "logo.png"
LOGO_PATH = resource_path(os.path.join(ASSETS_DIR, LOGO_FILE))

# Messages
MSG_NO_COM_PORTS = "No COM ports found."
MSG_COM_PORTS_REFRESHED = "COM ports refreshed."
MSG_SELECT_COM_PORT = "Please select a COM port first."
MSG_LISTENING_ON_PORT = "Listening on {port}"
MSG_STOPPED_LISTENING = "Stopped listening."
MSG_APP_READY = "Application ready."
MSG_FILE_SELECTED = "Selected: {file}"
MSG_NO_FILE_SELECTED = "Please select a file first!"
MSG_LOADED_CARDS = "Loaded {count} expected cards."
MSG_CLEARED_LOADED_FILE = "Loaded file cleared."
MSG_LOG_TABLE_CLEARED = "Log table cleared."
MSG_NO_LOG_DATA = "No log data to download!"
MSG_LOGS_SAVED = "Logs saved to {path}"
MSG_ERROR_SAVING_FILE = "Error saving file: {error}"
MSG_ERROR_LOADING_CARDS = "Error loading expected cards: {error}"
MSG_CONFIRM_CLEAR_LOG = "Are you sure you want to clear the log table? This action cannot be undone."
MSG_NO_CARD_SELECTED = "No card selected."
MSG_START_PROCESSING_FROM = "Starting processing from NUMCARD: {numcard}"