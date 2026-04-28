import csv
from pathlib import Path

# Define the sorting priority for regions
REGION_ORDER = {
    "kanto": 1,
    "johto": 2,
    "hoenn": 3,
    "sinnoh": 4,
    "unova": 5,
    "all regions": 6
}

def get_region_weight(entry_dict):
    """Helper function to sort entries by region order."""
    # Look for 'region' key, make it lowercase to match REGION_ORDER
    region_name = entry_dict.get('region', '').lower()
    # If the region isn't in the dict (or doesn't exist), give it a weight of 99 so it goes to the bottom
    return REGION_ORDER.get(region_name, 99)

def escape_lua_string(s):
    """Escapes strings to safely insert them into Lua format."""
    return s.replace('"', '\\"').replace('\n', '\\n').replace('\r', '')

def build_lua_category_from_csv(csv_path: Path, category_name: str, item_col_idx: int, prop_map: dict):
    """
    Reads a single CSV file and generates a Lua table structure.
    """
    if not csv_path.exists():
        print(f"Warning: '{csv_path.name}' not found at {csv_path}. Skipping {category_name}.")
        return f"-- {category_name} file not found\n\n"
        
    grouped_data = {}
    
    with csv_path.open(mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        # Skip header
        next(reader, None) 
        
        for row in reader:
            if not row or len(row) <= item_col_idx:
                continue
                
            item_name = row[item_col_idx].strip()
            if not item_name:
                continue
                
            if item_name not in grouped_data:
                grouped_data[item_name] = []
                
            entry_dict = {}
            for prop_key, col_idx in prop_map.items():
                cell_value = str(row[col_idx]).strip() if col_idx < len(row) else ""
                entry_dict[prop_key] = escape_lua_string(cell_value)
                
            # Store the dict instead of the string so we can sort it later
            grouped_data[item_name].append(entry_dict)
            
    # Format the final Lua string for this category
    lua_str = f"p.{category_name} = {{\n"
    for item, entries in grouped_data.items():
        # Sort the entries. If they have a 'region', they sort chronologically. Otherwise, they stay in order.
        entries.sort(key=get_region_weight)
        
        formatted_entries = []
        for entry_dict in entries:
            # Reconstruct the string in the exact order specified by prop_map
            parts = [f'{k} = "{entry_dict[k]}"' for k in prop_map.keys()]
            formatted_entries.append("        { " + ", ".join(parts) + " }")
            
        lua_str += f'    ["{item}"] = {{\n'
        lua_str += ",\n".join(formatted_entries) + '\n'
        lua_str += '    },\n'
    lua_str += "}\n\n"
    
    return lua_str

def build_shops_lua(shops_base_dir: Path):
    """
    Specifically processes the nested shops directories (e.g., shops/kanto/viridian_city.csv)
    """
    if not shops_base_dir.exists():
        print(f"Warning: Shops directory '{shops_base_dir}' not found.")
        return "-- shops directory not found\n\n"

    grouped_data = {}
    
    # Walk through the region folders
    for region_path in shops_base_dir.iterdir():
        if region_path.is_dir():
            # Read every city/shop CSV in that region using glob
            for csv_path in region_path.glob('*.csv'):
                with csv_path.open(mode='r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Use `or ''` to convert any None values safely to an empty string
                        item_name = str(row.get('Item') or '').strip()
                        if not item_name:
                            continue
                            
                        if item_name not in grouped_data:
                            grouped_data[item_name] = []
                            
                        # Extract and escape the data safely
                        region = escape_lua_string(str(row.get('Region') or ''))
                        location = escape_lua_string(str(row.get('Location') or ''))
                        price = escape_lua_string(str(row.get('Price') or ''))
                        
                        # Append as a dictionary for sorting
                        grouped_data[item_name].append({
                            'region': region,
                            'location': location,
                            'price': price
                        })
                            
    lua_str = "p.shops = {\n"
    for item, entries in grouped_data.items():
        # Sort the shop entries chronologically by region
        entries.sort(key=get_region_weight)
        
        formatted_entries = []
        for entry_dict in entries:
            entry_str = f'region = "{entry_dict["region"]}", location = "{entry_dict["location"]}", price = "{entry_dict["price"]}"'
            formatted_entries.append("        { " + entry_str + " }")
            
        lua_str += f'    ["{item}"] = {{\n'
        lua_str += ",\n".join(formatted_entries) + '\n'
        lua_str += '    },\n'
    lua_str += "}\n\n"
    
    return lua_str

def generate_item_database(data_dir: Path, output_dir: Path):
    final_lua = "local p = {}\n\n"
    
    # Process the Items List CSV
    csv_path = data_dir / 'item_list.csv'
    final_lua += build_lua_category_from_csv(csv_path, 'itemslist', 0, {
        'category': 1,
        'main_category': 2,
        'description': 3,
        'buy_pokeyen': 4,
        'buy_bp': 5,
        'buy_coin': 6,
        'buy_rp': 7,
        'sell_pokeyen': 8
    })
    
    final_lua += "return p\n"
    
    output_path = output_dir / 'Module:ItemDescriptions.lua'
    with output_path.open('w', encoding='utf-8') as f:
        f.write(final_lua)
    print(f"Item Database generated! Check '{output_path}'.")

def generate_item_sources(data_dir: Path, output_dir: Path):
    final_lua = "local p = {}\n\n"

    # 1. Process Shops (from nested folders)
    shops_dir = data_dir / 'shops'
    final_lua += build_shops_lua(shops_dir)

    # 2. Process Held Items
    csv_path = data_dir / 'held_items.csv'
    final_lua += build_lua_category_from_csv(csv_path, 'helditems', 1, {
        'pokemon': 0
    })

    # 3. Process Overworld Pickup
    csv_path = data_dir / 'pickup.csv'
    final_lua += build_lua_category_from_csv(csv_path, 'pickup', 2, {
        'region': 1, 'location': 0
    })

    # 4. Process Environmental
    csv_path = data_dir / 'environmental.csv'
    final_lua += build_lua_category_from_csv(csv_path, 'environmental', 2, {
        'region': 0, 'location': 1, 'method': 3
    })

    # 5. Process Crafting
    csv_path = data_dir / 'crafting.csv'
    final_lua += build_lua_category_from_csv(csv_path, 'crafting', 0, {
        'powder': 1, 'ingredients': 2
    })

    # 6. Process Overworld Items
    csv_path = data_dir / 'overworld_items.csv'
    final_lua += build_lua_category_from_csv(csv_path, 'overworlditems', 3, {
        'region': 0, 'location': 1, 'area': 2, 'amount': 4, 'type': 5, 'details': 6
    })

    final_lua += "return p\n"

    # Write to file
    output_path = output_dir / 'Module:ItemData.lua'
    with output_path.open('w', encoding='utf-8') as f:
        f.write(final_lua)
    print(f"Lua code generated successfully! Check '{output_path}'.")

if __name__ == "__main__":
    # 1. Resolve the directory where this script is located (lua_table_scripts)
    SCRIPT_DIR = Path(__file__).resolve().parent
    
    # 2. Move one level up to the parent directory
    PARENT_DIR = SCRIPT_DIR.parent
    
    # 3. Define the data and output directories based on the parent structure
    OUTPUT_DIR = PARENT_DIR / 'lua_table_outputs'
    
    # 4. Create the output folder if it doesn't already exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 5. Pass the Path objects into the generation functions
    generate_item_database(PARENT_DIR / 'item_information', OUTPUT_DIR)
    generate_item_sources(PARENT_DIR / 'item_information' / 'item_sources', OUTPUT_DIR)