# 🖥️ Card Validation Desktop App

A Python-based desktop GUI application designed for the card manufacturing industry. It scans cards in real-time using a QR scanner via the COM port, verifies their sequence from a preloaded `.cpd` file, and provides immediate feedback. Logs are auto-generated for audit and validation purposes.

---

## 📁 Folder Structure

```bash
card-sequence-validator/
│
├── gui/                    # All GUI-related files
│   ├── main.py             # Entry point for launching the GUI app
│   ├── widgets.py          # Custom reusable widgets (e.g., input fields, log table)
│   └── layout.png          # Preview image of the intended GUI layout
│
├── logic/                  # Core processing and backend logic
│   ├── parser.py           # Converts .cpd to .txt for line-based matching
│   ├── matcher.py          # Matches scanned QR code data against expected list
│   ├── logger.py           # Handles log file writing and error tracking
│   └── serial_reader.py    # Reads input from the serial (COM) port used by QR scanner
│
├── data/                   # Files related to input, output, and logs
│   ├── input.cpd           # Sample input file with expected card sequence
│   ├── input.txt           # Auto-generated text file used for fast comparison
│   └── input.csv           # **Log file** recording scan results (OK/Not OK, timestamp, scanned data)
│
├── assets/                 # Icons, branding, and static visual assets
│   └── logo.png            # Company or app logo shown in the GUI
│
├── README.md               # Complete project documentation and setup guide
├── requirements.txt        # All required Python libraries for the app
└── .gitignore              # Files and folders ignored by Git

---

## 🧰 Tech Stack

| Technology     | Purpose                            |
|----------------|-------------------------------------|
| Python         | Core programming language           |
| Tkinter        | GUI framework                       |
| pyserial       | Reading data from the COM port      |
| pandas         | Handling tabular data and logs      |
| csv / os       | File handling and system I/O        |

---

## 🚀 Features

- Upload `.cpd` files → automatically convert to `.txt` for validation
- Real-time QR code scan input via COM port
- Display current scan and expected value
- Visual feedback: ✅ OK / ❌ NOT OK
- Option to select line number to resume reading
- Log generation in `.csv` format named after `.cpd`
- Preview `.txt` file content within GUI
- Mismatch handling with auto-resume search feature
- Desktop executable ready (via `pyinstaller`)

---

## 📦 Setup Instructions

```bash
git clone https://github.com/AyushRaj1329/Python-GUI.git
cd Python-GUI
pip install -r requirements.txt
python src/main.py
```

To build into an executable:

```bash
pyinstaller --onefile src/main.py
```

---

## 📌 Future Enhancements

- Download button for logs
- Error reports by date
- Export in multiple formats (CSV, XLSX)
- Multi-user authentication

---

## 📄 License

This project is licensed under the MIT License.

---

> 💡 *Built for quality assurance and sequence validation in card manufacturing.*