import csv
from pathlib import Path
from collections import defaultdict

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
    region_name = entry_dict.get('region_name', '').lower()
    return REGION_ORDER.get(region_name, 99)

def escape_lua_string(s):
    """Escapes strings to safely insert them into Lua format."""
    return str(s).replace('"', '\\"').replace('\n', '\\n').replace('\r', '')

def build_pokemon_locations_lua(csv_path: Path):
    """
    Reads the pokemon_locations.csv file and generates a nested Lua table.
    """
    if not csv_path.exists():
        print(f"Warning: '{csv_path.name}' not found at {csv_path}.")
        return "-- pokemon_locations file not found\n\n"
        
    grouped_data = defaultdict(list)
    
    with csv_path.open(mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Safely get the pokemon_id to use as the primary key
            poke_id = str(row.get('pokemon_id') or '').strip()
            if not poke_id:
                continue
                
            # Extract and safely escape all details
            entry = {
                'type': escape_lua_string(str(row.get('type') or '').strip()),
                'region_id': escape_lua_string(str(row.get('region_id') or '').strip()),
                'region_name': escape_lua_string(str(row.get('region_name') or '').strip()),
                'location': escape_lua_string(str(row.get('location') or '').strip()),
                'min_level': escape_lua_string(str(row.get('min_level') or '').strip()),
                'max_level': escape_lua_string(str(row.get('max_level') or '').strip()),
                'rarity': escape_lua_string(str(row.get('rarity') or '').strip())
            }
            
            grouped_data[poke_id].append(entry)
            
    lua_str = "p.pokemon_locations = {\n"
    
    # Sort the dictionary keys (pokemon_id) numerically
    sorted_ids = sorted(grouped_data.keys(), key=lambda x: int(x) if x.isdigit() else float('inf'))
    
    for poke_id in sorted_ids:
        entries = grouped_data[poke_id]
        
        # Sort locations by Region chronological order, then alphabetically by location name
        entries.sort(key=lambda x: (get_region_weight(x), x['location']))
        
        lua_str += f'    ["{escape_lua_string(poke_id)}"] = {{\n'
        for e in entries:
            lua_str += f'        {{ type = "{e["type"]}", region_id = "{e["region_id"]}", region_name = "{e["region_name"]}", location = "{e["location"]}", min_level = "{e["min_level"]}", max_level = "{e["max_level"]}", rarity = "{e["rarity"]}" }},\n'
        lua_str += '    },\n'
            
    lua_str += "}\n\n"
    
    return lua_str

def generate_pokemon_locations_database(data_dir: Path, output_dir: Path):
    final_lua = "local p = {}\n\n"
    
    # Process the pokemon_locations CSV
    csv_path = data_dir / 'pokemon_locations.csv'
    final_lua += build_pokemon_locations_lua(csv_path)
    
    final_lua += "return p\n"
    
    # Output to a new file specifically for Pokémon Locations
    output_path = output_dir / 'Module:PokemonLocations.lua'
    with output_path.open('w', encoding='utf-8') as f:
        f.write(final_lua)
    print(f"Pokémon Locations Database generated! Check '{output_path}'.")

if __name__ == "__main__":
    # 1. Resolve the directory where this script is located (lua_table_scripts)
    SCRIPT_DIR = Path(__file__).resolve().parent
    
    # 2. Move one level up to the parent directory
    PARENT_DIR = SCRIPT_DIR.parent
    
    # 3. Define the data and output directories based on the parent structure
    DATA_DIR = PARENT_DIR / 'pokemon_information' 
    OUTPUT_DIR = PARENT_DIR / 'lua_table_outputs'
    
    # 4. Create the output folder if it doesn't already exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 5. Pass the Path objects into the generation functions
    generate_pokemon_locations_database(DATA_DIR, OUTPUT_DIR)