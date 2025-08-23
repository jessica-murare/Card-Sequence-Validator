from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
)

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