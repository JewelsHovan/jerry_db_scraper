import json
import pandas as pd
from typing import Dict, Any
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def json_to_excel_with_sheets(input_file: str, output_filename: str = "output.xlsx") -> None:
    """
    Converts JSON concert data from a file to an Excel workbook with separate sheets for each year.
    
    Args:
        input_file (str): Path to the input JSON file
        output_filename (str): Path for the output Excel file
    
    Raises:
        FileNotFoundError: If the input file doesn't exist
        json.JSONDecodeError: If the JSON file is invalid
    """
    try:
        # Read JSON file
        input_path = Path(input_file)
        logging.info(f"Reading JSON data from {input_path}")
        
        with open(input_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        output_path = Path(output_filename)
        logging.info(f"Writing Excel file to {output_path}")

        with pd.ExcelWriter(output_path) as writer:
            for year, data in json_data.items():
                rows = []
                for item in data:
                    # Improved musician string formatting with error handling
                    musicians_str = ", ".join(
                        f"{m.get('name', 'Unknown')}" + 
                        (f" - {m.get('instrument')}" if m.get('instrument') else "")
                        for m in item.get('musicians', [])
                    )
                    
                    # More concise list-to-string conversions with safe defaults
                    row = {
                        "year": year,
                        "date": item.get("date", ""),
                        "url": item.get("url", ""),
                        "venue": item.get("venue", ""),
                        "band": item.get("band", ""),
                        "songs": item.get("songs", ""),
                        "category": item.get("category", ""),
                        "act_type": item.get("act_type", ""),
                        "show_id": item.get("show_id", ""),
                        "date_from_title": item.get("date_from_title", ""),
                        "date_is_placeholder": item.get("date_is_placeholder", ""),
                        "setlist": ", ".join(item.get('setlist', [])),
                        "musicians": musicians_str,
                        "notes": ", ".join(item.get('notes', []))
                    }
                    rows.append(row)

                if rows:  # Only create sheet if there's data
                    df = pd.DataFrame(rows)
                    logging.info(f"Creating sheet for year {year} with {len(rows)} entries")
                    df.to_excel(writer, sheet_name=str(year), index=False)

        logging.info("Excel file created successfully")

    except FileNotFoundError:
        logging.error(f"Input file not found: {input_file}")
        raise
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in input file: {input_file}")
        raise
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    # Example usage with the new file
    input_file = "event_data_detailed.json"
    output_file = "concert_data.xlsx"
    
    try:
        json_to_excel_with_sheets(input_file, output_file)
    except Exception as e:
        logging.error(f"Failed to convert JSON to Excel: {str(e)}")