import os
import csv
from pathlib import Path

# --- CONFIGURATION ---
# Root directory based on your project structure
BASE_DIR = Path(__file__).resolve().parent.parent 
OUTPUT_FILE = "audit_list.csv"

def generate_csv():
    # Directories to scan based on your screenshot
    folders_to_scan = [
        'item_information',
        'location_information',
        'pokemon_information'
    ]
    
    data = []
    
    # 1. Scan root for any CSVs first
    for f in BASE_DIR.glob("*.csv"):
        data.append(["Root", f.name, "FALSE", "FALSE", ""])

    # 2. Scan the subfolders
    for subfolder in folders_to_scan:
        folder_path = BASE_DIR / subfolder
        if folder_path.exists():
            for root, dirs, files in os.walk(folder_path):
                # Get the folder path relative to the project root
                relative_root = Path(root).relative_to(BASE_DIR)
                for file in files:
                    if file.endswith(".csv"):
                        # Structure: Folder, Filename, Status, Updated, Notes
                        data.append([str(relative_root), file, "FALSE", "FALSE", ""])

    # 3. Write to the CSV file
    header = ["Folder", "File Name", "Audit Complete", "Wiki Updated", "Notes"]
    
    with open(OUTPUT_FILE, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)

    print(f"Successfully generated {OUTPUT_FILE}")
    print(f"Total files found: {len(data)}")

if __name__ == "__main__":
    generate_csv()