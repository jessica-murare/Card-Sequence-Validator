from logic.parser import parse_cpd_cards

def test_parser():
    file_path = "data/sample.CPD"   # relative path from project root
    paired_cards = parse_cpd_cards(file_path)

    for current, next_card in paired_cards:
        print(f"Current: {current}")
        if next_card:
            print(f"Next: {next_card}")
        else:
            print("Next: None")
        print("-" * 50)  # separator for clarity

if __name__ == "__main__":
    test_parser()
