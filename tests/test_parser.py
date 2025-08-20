import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logic.parser import parse_cpd_cards
def test_parser():
    file_path = "data/sample.CPD"   # relative path from project root
    paired_cards = parse_cpd_cards("C:/Users/khushi yadav/OneDrive/Documents/Pyhton projects/card_sequence_validator/Card-Sequence-Validator/data/sample.CPD")

    for current, next_card in paired_cards:
        print(f"Current: {current}")
        if next_card:
            print(f"Next: {next_card}")
        else:
            print("Next: None")
        print("-" * 50)  # separator for clarity

if __name__ == "__main__":
    test_parser()
