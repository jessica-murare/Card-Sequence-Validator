import os
from services.file_service import parse_cpd_cards, parse_txt_file, parse_csv_file

def parse_file(file_path):
    """
    Parses a file based on its extension.

    Args:
        file_path (str): Path to the input file.

    Returns:
        list: A list of tuples, where each tuple contains (current_card, next_card).
    """
    _, file_extension = os.path.splitext(file_path)

    if file_extension.lower() == '.cpd':
        return parse_cpd_cards(file_path)
    elif file_extension.lower() == '.txt':
        return parse_txt_file(file_path)
    elif file_extension.lower() == '.csv':
        return parse_csv_file(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")
