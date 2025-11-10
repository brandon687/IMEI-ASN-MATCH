import pandas as pd
import re
from io import BytesIO

def extract_imeis_from_file(file_data, filename):
    """
    Extract IMEIs from uploaded file (Excel, CSV, or TXT)

    IMEIs are 15-digit numbers starting with 35
    Looks for columns: SERIAL, IMEI, Serial No, serialnumber, etc.

    Returns: tuple (list of IMEIs, total count, error message if any)
    """
    try:
        imeis = []

        # Determine file type
        file_ext = filename.lower().split('.')[-1]

        if file_ext in ['xlsx', 'xls']:
            # Read Excel file
            df = pd.read_excel(BytesIO(file_data))
        elif file_ext == 'csv':
            # Read CSV file
            df = pd.read_csv(BytesIO(file_data))
        elif file_ext == 'txt':
            # Read text file - assume one IMEI per line or comma/tab separated
            content = file_data.decode('utf-8', errors='ignore')
            # Try to find all 15-digit numbers starting with 35
            imeis = re.findall(r'\b35\d{13}\b', content)
            return list(set(imeis)), len(imeis), None
        else:
            return [], 0, f"Unsupported file type: {file_ext}"

        # Look for IMEI/Serial columns (case insensitive)
        possible_column_names = [
            'imei', 'serial', 'serial no', 'serial number', 'serialnumber',
            'serial_no', 'serial_number', 'imei number', 'imei_number',
            'device serial', 'device_serial', 'sn'
        ]

        # Find matching columns
        imei_columns = []
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if any(name in col_lower for name in possible_column_names):
                imei_columns.append(col)

        # Extract IMEIs from found columns
        for col in imei_columns:
            for value in df[col].dropna():
                # Convert to string and clean
                value_str = str(value).strip()

                # Extract 15-digit numbers starting with 35
                found_imeis = re.findall(r'\b35\d{13}\b', value_str)
                imeis.extend(found_imeis)

        # If no columns found, search entire dataframe
        if not imei_columns:
            for col in df.columns:
                for value in df[col].dropna():
                    value_str = str(value).strip()
                    found_imeis = re.findall(r'\b35\d{13}\b', value_str)
                    imeis.extend(found_imeis)

        # Remove duplicates while preserving order
        unique_imeis = []
        seen = set()
        for imei in imeis:
            if imei not in seen:
                unique_imeis.append(imei)
                seen.add(imei)

        return unique_imeis, len(unique_imeis), None

    except Exception as e:
        return [], 0, f"Error extracting IMEIs: {str(e)}"


def validate_imei(imei):
    """
    Validate IMEI format:
    - Must be 15 digits
    - Must start with 35
    """
    if not imei:
        return False

    # Remove any whitespace
    imei = str(imei).strip()

    # Check if 15 digits
    if len(imei) != 15:
        return False

    # Check if starts with 35
    if not imei.startswith('35'):
        return False

    # Check if all digits
    if not imei.isdigit():
        return False

    return True


def format_imeis_for_display(imeis):
    """
    Format IMEIs for easy copying
    One IMEI per line
    """
    return '\n'.join(imeis)
