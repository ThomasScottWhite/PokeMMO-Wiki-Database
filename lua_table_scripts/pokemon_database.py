import csv
from pathlib import Path

def escape_lua_string(s):
    """Escapes strings to safely insert them into Lua format."""
    return str(s).replace('"', '\\"').replace('\n', '\\n').replace('\r', '')

def build_pokemon_base_lua(csv_path: Path):
    """
    Reads the pokemon_base.csv file and generates a flat Lua table structure.
    """
    if not csv_path.exists():
        print(f"Warning: '{csv_path.name}' not found at {csv_path}.")
        return "-- pokemon_base file not found\n\n"
        
    lua_str = "p.pokemon_base = {\n"
    
    with csv_path.open(mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Safely get the Pokémon name
            name = str(row.get('name') or '').strip()
            if not name:
                continue
                
            props = []
            for key, value in row.items():
                # Skip the name column since it's being used as the main table key
                if key == 'name':
                    continue
                    
                # Clean up the key and value
                safe_key = str(key or '').strip()
                safe_val = escape_lua_string(str(value or '').strip())
                
                # Format as key = "value"
                props.append(f'{safe_key} = "{safe_val}"')
                
            # Add the Pokémon entry to the string
            lua_str += f'    ["{escape_lua_string(name)}"] = {{ {", ".join(props)} }},\n'
            
    lua_str += "}\n\n"
    
    return lua_str

def generate_pokemon_database(data_dir: Path, output_dir: Path):
    final_lua = "local p = {}\n\n"
    
    # Process the pokemon_base CSV
    csv_path = data_dir / 'pokemon_base.csv'
    final_lua += build_pokemon_base_lua(csv_path)
    
    final_lua += "return p\n"
    
    # Output to a new file specifically for Pokémon
    output_path = output_dir / 'Module:PokemonData.lua'
    with output_path.open('w', encoding='utf-8') as f:
        f.write(final_lua)
    print(f"Pokémon Database generated! Check '{output_path}'.")

if __name__ == "__main__":
    # 1. Resolve the directory where this script is located (lua_table_scripts)
    SCRIPT_DIR = Path(__file__).resolve().parent
    
    # 2. Move one level up to the parent directory
    PARENT_DIR = SCRIPT_DIR.parent
    
    # 3. Define the data and output directories based on the parent structure
    # Assuming the folder is named 'pokemon_information' based on your previous structure
    DATA_DIR = PARENT_DIR / 'pokemon_information' 
    OUTPUT_DIR = PARENT_DIR / 'lua_table_outputs'
    
    # 4. Create the output folder if it doesn't already exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 5. Pass the Path objects into the generation functions
    generate_pokemon_database(DATA_DIR, OUTPUT_DIR)