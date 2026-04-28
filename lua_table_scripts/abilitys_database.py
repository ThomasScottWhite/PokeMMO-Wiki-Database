import csv
from pathlib import Path
from collections import defaultdict

def escape_lua_string(s):
    """Escapes strings to safely insert them into Lua format."""
    return str(s).replace('"', '\\"').replace('\n', '\\n').replace('\r', '')

def build_pokemon_abilities_lua(csv_path: Path):
    """
    Reads the pokemon_abilities.csv file and generates a nested Lua table.
    """
    if not csv_path.exists():
        print(f"Warning: '{csv_path.name}' not found at {csv_path}.")
        return "-- pokemon_abilities file not found\n\n"
        
    grouped_data = defaultdict(list)
    
    with csv_path.open(mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Safely get the pokemon_id to use as the primary key
            poke_id = str(row.get('pokemon_id') or '').strip()
            if not poke_id:
                continue
                
            # Extract and escape the ability details
            ability_id = escape_lua_string(str(row.get('ability_id') or '').strip())
            ability_name = escape_lua_string(str(row.get('ability_name') or '').strip())
            
            # Format as an inner Lua table and append to the list for this Pokémon
            entry = f'{{ ability_id = "{ability_id}", ability_name = "{ability_name}" }}'
            grouped_data[poke_id].append(entry)
            
    lua_str = "p.pokemon_abilities = {\n"
    
    # Sort the dictionary keys (pokemon_id) numerically for a cleaner Lua file
    sorted_ids = sorted(grouped_data.keys(), key=lambda x: int(x) if x.isdigit() else float('inf'))
    
    for poke_id in sorted_ids:
        entries = grouped_data[poke_id]
        
        lua_str += f'    ["{escape_lua_string(poke_id)}"] = {{\n'
        for entry in entries:
            lua_str += f'        {entry},\n'
        lua_str += '    },\n'
            
    lua_str += "}\n\n"
    
    return lua_str

def generate_abilities_database(data_dir: Path, output_dir: Path):
    final_lua = "local p = {}\n\n"
    
    # Process the pokemon_abilities CSV
    csv_path = data_dir / 'pokemon_abilities.csv'
    final_lua += build_pokemon_abilities_lua(csv_path)
    
    final_lua += "return p\n"
    
    # Output to a new file specifically for Pokémon Abilities
    output_path = output_dir / 'Module:PokemonAbilities.lua'
    with output_path.open('w', encoding='utf-8') as f:
        f.write(final_lua)
    print(f"Pokémon Abilities Database generated! Check '{output_path}'.")

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
    generate_abilities_database(DATA_DIR, OUTPUT_DIR)