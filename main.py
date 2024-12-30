import pandas as pd
import json
import os
import re

# Load data from ODS file
def load_ods_data(filepath):
    # Read the ODS file
    data = pd.read_excel(filepath, engine="odf")
    
    # Strip whitespace from column names
    data.columns = data.columns.str.strip()
    
    return data

# Load Dito numbers for lookup
def load_dito_numbers(filepath):
    data = pd.read_excel(filepath)
    # Strip whitespace from column names
    data.columns = data.columns.str.strip()
    return data.set_index("Code")

# Find the highest ID in each category in the existing JSON
def get_highest_ids(data):
    ids = {
        "main_id": 0,
        "german_id": 0,
        "danish_id": 0,
        "swedish_id": 0
    }
    for item in data:
        ids["main_id"] = max(ids["main_id"], item["id"])
        if item.get("german_car_part_types"):
            ids["german_id"] = max(ids["german_id"], item["german_car_part_types"][0]["id"])
        if item.get("danish_car_part_types"):
            ids["danish_id"] = max(ids["danish_id"], 
                                     max((t["id"] for t in item["danish_car_part_types"]), default=0))
        if item.get("swedish_car_part_types"):
            ids["swedish_id"] = max(ids["swedish_id"], item["swedish_car_part_types"][0]["id"])
    return ids

# Convert a name to a translation key
def generate_translation_key(name):
    # Remove special characters and convert to lowercase
    return re.sub(r'[^a-z0-9]', '_', name.lower())

# Convert each row of the DataFrame to the required JSON format
def convert_row_to_json(row, highest_ids, dito_lookup):
    highest_ids["main_id"] += 1
    highest_ids["german_id"] += 1
    highest_ids["swedish_id"] += 1

    dito_codes = str(row["Dito"]).split(",")
    danish_car_part_types = []
    for code in dito_codes:
        print(dito_codes)
        print(dito_lookup.index)
        print(dito_lookup)

        code = code.strip()


        try:
            code = int(code)  # Convert code to integer
        except ValueError:
            print(f"Invalid code: {code}")
            code = None


    if code in dito_lookup.index:
            print("found code")
            part_data = dito_lookup.loc[code]
            highest_ids["danish_id"] += 1
            danish_car_part_types.append({
                "id": highest_ids["danish_id"],
                "name": part_data["Name"],
                "code": code,
                "egluit_id": "1111"  # Hardcoded
            })

    return {
        "id": highest_ids["main_id"],
        "name": row["English Sparepart name"],
        "translation_key": generate_translation_key(row["English Sparepart name"]),
        "german_car_part_types": [
            {
                "id": highest_ids["german_id"],
                "name": row["German sparepart name"],
                "code": None,
                "autoteile_markt_category_id": row["Autoteile-Markt"]
            }
        ],
        "danish_car_part_types": danish_car_part_types,
        "swedish_car_part_types": [
            {
                "id": highest_ids["swedish_id"],
                "name": row["Svedish sparepart name"],
                "code": row["SBR"]
            }
        ]
    }

# Append new data to the JSON file
def append_to_json_file(filepath, new_data, dito_lookup):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    # Get highest IDs from existing data
    highest_ids = get_highest_ids(existing_data)
    
    # Convert ODS rows to JSON and append
    for _, row in new_data.iterrows():
        new_json_entry = convert_row_to_json(row, highest_ids, dito_lookup)
        existing_data.append(new_json_entry)

    # Write updated data back to file
    with open(filepath, "w", encoding="utf-8") as f:
       json.dump(existing_data, f, indent=4, ensure_ascii=False)

# Main function
def main(ods_filepath, dito_filepath, json_filepath):
    # Load ODS data
    ods_data = load_ods_data(ods_filepath)
    
    # Load Dito numbers
    dito_lookup = load_dito_numbers(dito_filepath)

    # Append new data to JSON file
    append_to_json_file(json_filepath, ods_data, dito_lookup)

# Example usage
ods_filepath = "./input.ods"
dito_filepath = "./dito-numbers.xlsx"
json_filepath = "./output.json"
main(ods_filepath, dito_filepath, json_filepath)
