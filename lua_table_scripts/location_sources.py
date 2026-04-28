import csv
from pathlib import Path

# Define the sorting priority for regions
REGION_ORDER = {
    "kanto": 1,
    "johto": 2,
    "hoenn": 3,
    "sinnoh": 4,
    "unova": 5,
    "sevii islands": 6,
    "all regions": 7
}

def get_region_weight(entry_dict):
    """Helper function to sort entries by region order."""
    region_name = entry_dict.get('region', '').lower()
    return REGION_ORDER.get(region_name, 99)

def escape_lua_string(s):
    """Escapes strings to safely insert them into Lua format."""
    return s.replace('"', '\\"').replace('\n', '\\n').replace('\r', '')

def build_locations_lua(data_dir: Path):
    """
    Reads all region location CSVs and generates a Lua table structure.
    """
    if not data_dir.exists():
        print(f"Warning: Directory '{data_dir}' not found.")
        return "-- locations directory not found\n\n"
        
    grouped_data = {}
    
    # Process all CSVs in the location_information directory
    for csv_path in data_dir.glob('*.csv'):
        with csv_path.open(mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Safely handle missing values and strip whitespace
                location = str(row.get('Location') or '').strip()
                region = str(row.get('Region') or '').strip()
                
                if not location:
                    continue
                    
                if location not in grouped_data:
                    grouped_data[location] = []
                    
                # Append as a dictionary for sorting
                grouped_data[location].append({
                    'region': escape_lua_string(region)
                })
            
    # Format the final Lua string
    lua_str = "p.locations = {\n"
    
    # Sort the dictionary keys (Locations) alphabetically for a cleaner Lua file
    for location in sorted(grouped_data.keys()):
        entries = grouped_data[location]
        
        # Sort the entries for each location chronologically by region
        entries.sort(key=get_region_weight)
        
        formatted_entries = []
        for entry_dict in entries:
            formatted_entries.append(f'        {{ region = "{entry_dict["region"]}" }}')
            
        lua_str += f'    ["{escape_lua_string(location)}"] = {{\n'
        lua_str += ",\n".join(formatted_entries) + '\n'
        lua_str += '    },\n'
        
    lua_str += "}\n\n"
    
    return lua_str

def generate_location_database(data_dir: Path, output_dir: Path):
    final_lua = "local p = {}\n\n"
    
    # Process the location files
    final_lua += build_locations_lua(data_dir)
    
    final_lua += "return p\n"
    
    # Output to a new file specifically for locations
    output_path = output_dir / 'Module:LocationData.lua'
    with output_path.open('w', encoding='utf-8') as f:
        f.write(final_lua)
    print(f"Location Database generated! Check '{output_path}'.")

if __name__ == "__main__":
    # 1. Resolve the directory where this script is located (lua_table_scripts)
    SCRIPT_DIR = Path(__file__).resolve().parent
    
    # 2. Move one level up to the parent directory
    PARENT_DIR = SCRIPT_DIR.parent
    
    # 3. Define the data and output directories based on the parent structure
    DATA_DIR = PARENT_DIR / 'location_information'
    OUTPUT_DIR = PARENT_DIR / 'lua_table_outputs'
    
    # 4. Create the output folder if it doesn't already exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 5. Pass the Path objects into the generation functions
    generate_location_database(DATA_DIR, OUTPUT_DIR)