from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QDialogButtonBox
)

class SelectStartCardDialog(QDialog):
    def __init__(self, expected_cards, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Starting Card")
        self.setMinimumSize(300, 400)
        self.setStyleSheet(parent.styleSheet()) # Inherit stylesheet
        self.selected_index = -1

        layout = QVBoxLayout(self)

        label = QLabel("Select the NUMCARD to start processing from:")
        layout.addWidget(label)

        self.card_list_widget = QListWidget()
        for i, (numcard, iccid) in enumerate(expected_cards):
            self.card_list_widget.addItem(f"{numcard} (ICCID: {iccid})")
        layout.addWidget(self.card_list_widget)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.card_list_widget.itemClicked.connect(self._item_clicked)

    def _item_clicked(self, item):
        self.selected_index = self.card_list_widget.row(item)

    def get_selected_index(self):
        return self.selected_index