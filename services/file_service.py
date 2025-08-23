import csv

def parse_cpd_cards(file_path):
    """
    Parses a CPD (Card Profile Data) file to extract card details (NUMCARD and ICCID)
    and returns them as pairs of (current_card, next_card).

    Args:
        file_path (str): Path to the input CPD file.

    Returns:
        list: A list of tuples, where each tuple contains (current_card, next_card).
              - current_card: (NUMCARD, ICCID) of the current row
              - next_card: (NUMCARD, ICCID) of the next row, or None if it's the last
    """
    
    card_data = []       # Stores extracted card details as (NUMCARD, ICCID)
    start_reading = False  # Flag to identify when to start reading data rows

    # Open the CPD file for reading
    with open(file_path, mode='r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()  # Remove extra spaces/newlines from each line

            # Detect the header row that starts the card section
            if line.startswith("NUMCARD;MAXCARD;DATAFILE;ICCID;IMSI"):
                start_reading = True   # Start reading after the header
                header = line.split(";")  # Split header into column names
                numcard_idx = header.index("NUMCARD")  # Find column index for NUMCARD
                iccid_idx = header.index("ICCID")      # Find column index for ICCID
                continue  # Skip to the next line (don't treat header as data)

            # Once inside card section, extract relevant values from each row
            if start_reading and line:
                parts = line.split(";")       # Split row by semicolon
                numcard = parts[numcard_idx]  # Extract NUMCARD value
                iccid = parts[iccid_idx]      # Extract ICCID value
                card_data.append((numcard, iccid))  # Store the pair

    # Build pairs of (current_card, next_card) for easier comparison/validation
    paired_cards = []
    for i in range(len(card_data)):
        current = card_data[i]  # Current card details
        next_card = card_data[i + 1] if i + 1 < len(card_data) else None  # Next card (or None if last)
        paired_cards.append((current, next_card))

    return paired_cards


def parse_txt_file(file_path):
    """
    Parses a simple text file where each line contains an ICCID.

    Args:
        file_path (str): Path to the input text file.

    Returns:
        list: A list of tuples, where each tuple contains (current_card, next_card).
              - current_card: (None, ICCID) of the current row
              - next_card: (None, ICCID) of the next row, or None if it's the last
    """
    
    iccid_data = []  # Stores extracted ICCIDs

    # Open the text file for reading
    with open(file_path, mode='r', encoding='utf-8') as f:
        for line in f:
            iccid = line.strip()  # Remove extra spaces/newlines
            if iccid:  # Ensure the line is not empty
                iccid_data.append((None, iccid))  # Store with None for NUMCARD

    # Build pairs of (current_card, next_card)
    paired_cards = []
    for i in range(len(iccid_data)):
        current = iccid_data[i]
        next_card = iccid_data[i + 1] if i + 1 < len(iccid_data) else None
        paired_cards.append((current, next_card))

    return paired_cards


def parse_csv_file(file_path):
    """
    Parses a CSV file to extract card details (NUMCARD and ICCID).

    Args:
        file_path (str): Path to the input CSV file.

    Returns:
        list: A list of tuples, where each tuple contains (current_card, next_card).
              - current_card: (NUMCARD, ICCID) of the current row
              - next_card: (NUMCARD, ICCID) of the next row, or None if it's the last
    """
    
    card_data = []  # Stores extracted card details

    # Open the CSV file for reading
    with open(file_path, mode='r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        header = next(reader)  # Read the header row
        
        # Find column indices for NUMCARD and ICCID
        try:
            numcard_idx = header.index("NUMCARD")
            iccid_idx = header.index("ICCID")
        except ValueError:
            raise ValueError("CSV file must contain 'NUMCARD' and 'ICCID' columns.")

        # Extract data from each row
        for row in reader:
            numcard = row[numcard_idx]
            iccid = row[iccid_idx]
            card_data.append((numcard, iccid))

    # Build pairs of (current_card, next_card)
    paired_cards = []
    for i in range(len(card_data)):
        current = card_data[i]
        next_card = card_data[i + 1] if i + 1 < len(card_data) else None
        paired_cards.append((current, next_card))

    return paired_cards