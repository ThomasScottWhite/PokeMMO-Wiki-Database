import csv
from pathlib import Path
from collections import defaultdict

# --- CONFIGURATION ---
MAX_FILE_SIZE_BYTES = 1.8 * 1024 * 1024  # 1.8 MB (Extra safety margin)
# ---------------------

def escape_lua_string(s):
    return str(s).replace('"', '\\"').replace('\n', '\\n').replace('\r', '')

def get_level_sort_key(level_str):
    try:
        return int(level_str)
    except ValueError:
        return 999

def get_grouped_moves(csv_path: Path):
    if not csv_path.exists():
        return {}, []
    
    grouped_data = defaultdict(list)
    with csv_path.open(mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            poke_id = str(row.get('pokemon_id') or '').strip()
            if not poke_id: continue
            
            grouped_data[poke_id].append({
                'move_id': escape_lua_string(str(row.get('move_id') or '').strip()),
                'move_name': escape_lua_string(str(row.get('move_name') or '').strip()),
                'learn_method': escape_lua_string(str(row.get('learn_method') or '').strip()),
                'learn_level': escape_lua_string(str(row.get('learn_level') or '').strip())
            })
            
    sorted_ids = sorted(grouped_data.keys(), key=lambda x: int(x) if x.isdigit() else float('inf'))
    return grouped_data, sorted_ids

def generate_moves_database(data_dir: Path, output_dir: Path):
    csv_path = data_dir / 'pokemon_moves.csv'
    grouped_data, sorted_ids = get_grouped_moves(csv_path)

    if not sorted_ids:
        print("No data found to process.")
        return

    file_count = 1
    current_chunk_ids = []
    master_index = {} # Maps poke_id -> file_count
    
    header_footer_size = len("local p = {}\n\np.pokemon_moves = {\n}\n\nreturn p")
    current_bytes = header_footer_size

    for poke_id in sorted_ids:
        # Build string for this specific Pokémon
        entries = grouped_data[poke_id]
        entries.sort(key=lambda x: (x['learn_method'], get_level_sort_key(x['learn_level'])))
        
        entry_str = f'    ["{escape_lua_string(poke_id)}"] = {{\n'
        for e in entries:
            entry_str += f'        {{ move_id = "{e["move_id"]}", move_name = "{e["move_name"]}", learn_method = "{e["learn_method"]}", learn_level = "{e["learn_level"]}" }},\n'
        entry_str += '    },\n'
        
        entry_bytes = len(entry_str.encode('utf-8'))

        # Check if we need to start a new file
        if current_bytes + entry_bytes > MAX_FILE_SIZE_BYTES and current_chunk_ids:
            save_chunk_file(output_dir, file_count, current_chunk_ids, grouped_data)
            file_count += 1
            current_chunk_ids = []
            current_bytes = header_footer_size
        
        current_chunk_ids.append(poke_id)
        master_index[poke_id] = file_count
        current_bytes += entry_bytes

    # Save the last chunk
    if current_chunk_ids:
        save_chunk_file(output_dir, file_count, current_chunk_ids, grouped_data)

    # Generate the Master Loader file
    generate_master_loader(output_dir, master_index)

def save_chunk_file(output_dir, index, ids, data):
    file_name = f'Module:PokemonMoves_{index}.lua'
    output_path = output_dir / file_name
    
    content = "local p = {}\n\np.pokemon_moves = {\n"
    for poke_id in ids:
        entries = data[poke_id]
        content += f'    ["{escape_lua_string(poke_id)}"] = {{\n'
        for e in entries:
            content += f'        {{ move_id = "{e["move_id"]}", move_name = "{e["move_name"]}", learn_method = "{e["learn_method"]}", learn_level = "{e["learn_level"]}" }},\n'
        content += '    },\n'
    content += "}\n\nreturn p"
    
    with output_path.open('w', encoding='utf-8') as f:
        f.write(content)
    print(f"Saved {file_name} ({len(content.encode('utf-8')) / 1024:.2f} KB)")

def generate_master_loader(output_dir: Path, master_index: dict):
    """Generates the central Module:PokemonMoves.lua file."""
    content = "local p = {}\n\n"
    content += "-- This index tells the module which sub-file to load for each Pokemon ID\n"
    content += "local index = {\n"
    
    # Sort index keys for a clean file
    sorted_master = sorted(master_index.keys(), key=lambda x: int(x) if x.isdigit() else float('inf'))
    for poke_id in sorted_master:
        content += f'    ["{poke_id}"] = {master_index[poke_id]},\n'
    
    content += "}\n\n"
    content += "function p.get_moves(pokemon_id)\n"
    content += "    local id_str = tostring(pokemon_id)\n"
    content += "    local file_num = index[id_str]\n"
    content += "    if not file_num then return nil end\n\n"
    content += "    -- mw.loadData is efficient; it only loads the file once per page request\n"
    content += "    local data = mw.loadData('Module:PokemonMoves_' .. file_num)\n"
    content += "    return data.pokemon_moves[id_str]\n"
    content += "end\n\n"
    content += "return p"
    
    output_path = output_dir / 'Module:PokemonMoves.lua'
    with output_path.open('w', encoding='utf-8') as f:
        f.write(content)
    print(f"\nSUCCESS: Master Loader generated as '{output_path.name}'.")

if __name__ == "__main__":
    SCRIPT_DIR = Path(__file__).resolve().parent
    DATA_DIR = SCRIPT_DIR.parent / 'pokemon_information'
    OUTPUT_DIR = SCRIPT_DIR.parent / 'lua_table_outputs'
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    generate_moves_database(DATA_DIR, OUTPUT_DIR)