# 🌟 Contributing to the PokeMMO Wiki Database

Welcome! Thank you for helping keep the PokeMMO Wiki up to date. 

This repository holds the raw data (like item prices, Pokémon stats, and locations) that powers the wiki. Instead of manually typing out complicated code on the wiki itself, we manage everything in simple spreadsheet files (.csv). Python scripts then magically turn these spreadsheets into the code (Lua) that the wiki uses.

If you've never used Git or contributed to a GitHub project before, don't worry! This guide will walk you through the process step-by-step.

## 🛠️ What You Need to Start
1. **[GitHub Desktop](https://desktop.github.com/):** A visual app that makes downloading and sharing files much easier than using the command line.
2. **[Python](https://www.python.org/downloads/):** You will need this installed to run the scripts that generate the wiki code. *(Make sure to check the box that says "Add Python to PATH" when installing!)*
3. **A Code Editor or Spreadsheet App:** You can use VS Code (recommended, with the "Edit csv" extension), Notepad++, Excel, or Google Sheets to edit the CSV files.

---

## 📖 Step-by-Step Guide
### Step 1: Get the Files (Fork & Clone)
Before you can make changes, you need your own copy of the project.
1. Scroll to the top right of this GitHub page and click the **Fork** button. This creates a copy of the project under your own account.
2. Open **GitHub Desktop**.
3. Go to **File > Clone repository**.
4. Look under the "GitHub.com" tab, find your forked copy of the database, and click **Clone**. The files are now on your computer!


### Step 2: Make Your Edits
Open the folder on your computer. You will see several directories, such as `item_information`, `pokemon_information`, and `location_information`.
1. Find the `.csv` file you want to update (for example, `pokemon_information/pokemon_base.csv`).
2. Open it in your editor and make your changes. 
   * *Tip: Ensure you keep the exact same column headers!*
3. Save the file.

### Step 3: Generate the Lua Tables
Now that you've updated the raw data, you need to generate the code for the wiki.
1. Open your computer's terminal (Command Prompt on Windows, Terminal on Mac).
2. Execute the Python script for the category you updated:
   ```bash
   python pokemon_sources.py
   ```
3. The script will automatically create or update the corresponding .lua file inside the lua_table_outputs/ folder.

### Step 4: Update the Wiki
1. Open the newly generated `.lua` file (e.g., `Module:PokemonData.lua`) in a text editor.
2. Copy all the text inside.
3. Head over to the corresponding Module page on the PokeMMO Wiki.
4. Click **Edit**, delete the old code, paste your new code, and save the page. You've officially updated the wiki!

### Step 5: Share Your Changes (Commit & Pull Request)
Finally, let's submit your changes back here so everyone else can benefit from your work.
1. Open **GitHub Desktop**. It will automatically detect the files you changed.
2. In the bottom left corner, type a short summary of what you did (e.g., *"Updated Bulbasaur's base stats"*).
3. Click the blue **Commit to main** button.
4. Click **Push origin** at the top of the screen to send your changes to the cloud.
5. Go back to your forked repository on the GitHub website. You'll see a prompt to **Compare & pull request**. Click it, add a quick note about what you fixed, and submit! 

A project maintainer will review your changes and merge them into the main database.

---

### 📂 Directory Overview
If you are wondering where everything is, here is a quick map:
* `*_information/` - This is where the CSV spreadsheets live. **(Edit these!)**
* `lua_table_scripts/` - The Python scripts that read the CSVs. 
* `lua_table_outputs/` - The generated Lua files. **(Copy from here to the wiki!)**

Thank you for contributing! If you run into any errors or need help, feel free to open an Issue on GitHub.
