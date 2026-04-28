import csv
from pathlib import Path
from collections import defaultdict

def escape_lua_string(s):
    """Escapes strings to safely insert them into Lua format."""
    return str(s).replace('"', '\\"').replace('\n', '\\n').replace('\r', '')

def get_level_sort_key(level_str):
    """Helper function to safely sort learn levels numerically."""
    try:
        return int(level_str)
    except ValueError:
        # If it's not a number (e.g., a string or empty), push it to the end
        return 999

def build_pokemon_moves_lua(csv_path: Path):
    """
    Reads the pokemon_moves.csv file and generates a nested Lua table.
    """
    if not csv_path.exists():
        print(f"Warning: '{csv_path.name}' not found at {csv_path}.")
        return "-- pokemon_moves file not found\n\n"
        
    grouped_data = defaultdict(list)
    
    with csv_path.open(mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Safely get the pokemon_id to use as the primary key
            poke_id = str(row.get('pokemon_id') or '').strip()
            if not poke_id:
                continue
                
            # Extract and escape the move details
            entry = {
                'move_id': escape_lua_string(str(row.get('move_id') or '').strip()),
                'move_name': escape_lua_string(str(row.get('move_name') or '').strip()),
                'learn_method': escape_lua_string(str(row.get('learn_method') or '').strip()),
                'learn_level': escape_lua_string(str(row.get('learn_level') or '').strip())
            }
            
            grouped_data[poke_id].append(entry)
            
    lua_str = "p.pokemon_moves = {\n"
    
    # Sort the dictionary keys (pokemon_id) numerically
    sorted_ids = sorted(grouped_data.keys(), key=lambda x: int(x) if x.isdigit() else float('inf'))
    
    for poke_id in sorted_ids:
        entries = grouped_data[poke_id]
        
        # Sort moves by learn_method alphabetically, then by learn_level numerically
        entries.sort(key=lambda x: (x['learn_method'], get_level_sort_key(x['learn_level'])))
        
        lua_str += f'    ["{escape_lua_string(poke_id)}"] = {{\n'
        for e in entries:
            lua_str += f'        {{ move_id = "{e["move_id"]}", move_name = "{e["move_name"]}", learn_method = "{e["learn_method"]}", learn_level = "{e["learn_level"]}" }},\n'
        lua_str += '    },\n'
            
    lua_str += "}\n\n"
    
    return lua_str

def generate_moves_database(data_dir: Path, output_dir: Path):
    final_lua = "local p = {}\n\n"
    
    # Process the pokemon_moves CSV
    csv_path = data_dir / 'pokemon_moves.csv'
    final_lua += build_pokemon_moves_lua(csv_path)
    
    final_lua += "return p\n"
    
    # Output to a new file specifically for Pokémon Moves
    output_path = output_dir / 'Module:PokemonMoves.lua'
    with output_path.open('w', encoding='utf-8') as f:
        f.write(final_lua)
    print(f"Pokémon Moves Database generated! Check '{output_path}'.")

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
    generate_moves_database(DATA_DIR, OUTPUT_DIR)