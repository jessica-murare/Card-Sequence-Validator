from PyQt6.QtWidgets import QInputDialog

class CardValidator:
    def __init__(self, main_window):
        self.main_window = main_window

    def handle_com_data(self, scanned_code):
        self.main_window.scanner_input.setText(scanned_code)
        timestamp = self.main_window.get_timestamp()

        if self.main_window.first_scan_received:
            self.main_window.first_scan_received = False

        expected_numcard = "N/A"
        expected_iccid_for_display = "N/A"
        status = "N/A"

        if self.main_window.expected_cards and self.main_window.current_card_index < len(self.main_window.expected_cards):
            expected_numcard = self.main_window.expected_cards[self.main_window.current_card_index][0]
            expected_iccid_for_display = self.main_window.expected_cards[self.main_window.current_card_index][1]
            status = "OK" if scanned_code == expected_iccid_for_display else "NOT OK"
        elif self.main_window.expected_cards and self.main_window.current_card_index >= len(self.main_window.expected_cards):
            expected_iccid_for_display = "End of sequence"
            status = "N/A"

        self.main_window.add_log_entry(timestamp, scanned_code, expected_iccid_for_display, status, self.main_window.log_table.rowCount() + 1)
        self.main_window.status_bar.showMessage(f"Scanned: {scanned_code} - {status}")

        if status == "NOT OK":
            similar_cards = []
            for i in range(self.main_window.current_card_index + 1, len(self.main_window.expected_cards)):
                expected_card_value = self.main_window.expected_cards[i][1]
                if scanned_code in expected_card_value or expected_card_value in scanned_code:
                    similar_cards.append((self.main_window.expected_cards[i][0], expected_card_value, i))

            if similar_cards:
                # Automatically select the first similar card
                chosen_numcard, chosen_iccid, chosen_index = similar_cards[0]

                for i in range(self.main_window.current_card_index, chosen_index):
                    skipped_num, skipped_iccid = self.main_window.expected_cards[i]
                    self.main_window.add_log_entry(timestamp, "MISSING", skipped_iccid, "SKIPPED", self.main_window.log_table.rowCount() + 1)

                self.main_window.current_card_index = chosen_index
                expected_numcard = self.main_window.expected_cards[self.main_window.current_card_index][0]
                expected_iccid_for_display = self.main_window.expected_cards[self.main_window.current_card_index][1]
                status = "OK"

                self.main_window.add_log_entry(timestamp, scanned_code, expected_iccid_for_display, status, self.main_window.log_table.rowCount() + 1)
                self.main_window.status_bar.showMessage(f"Scanned: {scanned_code} - {status} (Jumped)")
            else:
                self.main_window.stop_reading()

        self.main_window.update_card_display()

        self.main_window.current_card_index += 1
