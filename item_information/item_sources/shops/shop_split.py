import csv
import os
from collections import defaultdict

def create_shop_directories(input_filename):
    # Dictionary to hold the rows, grouped by region and then by location
    shop_data = defaultdict(lambda: defaultdict(list))
    
    # 1. Read the main CSV file
    try:
        with open(input_filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames # Save original headers
            
            for row in reader:
                # Safely get the values, defaulting to an empty string if missing
                region_raw = row.get('Region')
                location_raw = row.get('Location')
                
                # Skip completely empty rows or rows missing crucial columns
                if not region_raw or not location_raw:
                    continue
                    
                region = region_raw.strip()
                location = location_raw.strip()
                
                # Skip if the row was just whitespace
                if not region or not location:
                    continue
                    
                shop_data[region][location].append(row)
                
    except FileNotFoundError:
        print(f"Error: Could not find '{input_filename}'.")
        return

    # 2. Create folders and write the individual CSVs
    for region, locations in shop_data.items():
        # Format the folder name (e.g., "Kanto" -> "kanto")
        folder_name = region.lower().replace(" ", "_")
        
        # Only try to make the directory if folder_name is valid
        if folder_name:
            os.makedirs(folder_name, exist_ok=True)
            
            for location, rows in locations.items():
                # Format the file name (e.g., "Viridian City" -> "viridian_city.csv")
                file_name = f"{location.lower().replace(' ', '_')}.csv"
                file_path = os.path.join(folder_name, file_name)
                
                with open(file_path, mode='w', newline='', encoding='utf-8') as out_file:
                    writer = csv.DictWriter(out_file, fieldnames=headers)
                    writer.writeheader()
                    writer.writerows(rows)
                
                print(f"Created: {file_path} ({len(rows)} items)")

if __name__ == "__main__":
    # Ensure this matches the name of your original CSV file
    input_csv = 'shop_data.csv' 
    
    print(f"Organizing '{input_csv}' into regional shop folders...\n")
    create_shop_directories(input_csv)
    print("\nProcess complete!")