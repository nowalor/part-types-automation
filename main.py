import pandas as pd
import json
import os

# Load data from ODS file
def load_ods_data(filepath):
    # Read the ODS file
    data = pd.read_excel(filepath, engine="odf")
    
    # Strip whitespace from column names
    data.columns = data.columns.str.strip()
    
    return data

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
            ids["danish_id"] = max(ids["danish_id"], item["danish_car_part_types"][0]["id"])
        if item.get("swedish_car_part_types"):
            ids["swedish_id"] = max(ids["swedish_id"], item["swedish_car_part_types"][0]["id"])
    return ids

# Convert each row of the DataFrame to the required JSON format
def convert_row_to_json(row, highest_ids):
    highest_ids["main_id"] += 1
    highest_ids["german_id"] += 1
    highest_ids["danish_id"] += 1
    highest_ids["swedish_id"] += 1

    return {
        "id": highest_ids["main_id"],
        "name": row["English Sparepart name"],
        "german_car_part_types": [
            {
                "id": highest_ids["german_id"],
                "name": row["German sparepart name"],
                "code": None,
                "autoteile_markt_category_id": row["Autoteile-Markt"]
            }
        ],
        "danish_car_part_types": [
            {
                "id": highest_ids["danish_id"],
                "name": row["Danish sparepart name"],
                "code": "6666",  # Hardcoded
                "egluit_id": "1111"  # Hardcoded
            }
        ],
        "swedish_car_part_types": [
            {
                "id": highest_ids["swedish_id"],
                "name": row["Svedish sparepart name"],
                "code": row["SBR"]
            }
        ]
    }

# Append new data to the JSON file
def append_to_json_file(filepath, new_data):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    # Get highest IDs from existing data
    highest_ids = get_highest_ids(existing_data)
    
    # Convert ODS rows to JSON and append
    for _, row in new_data.iterrows():
        new_json_entry = convert_row_to_json(row, highest_ids)
        existing_data.append(new_json_entry)

    # Write updated data back to file
    with open(filepath, "w", encoding="utf-8") as f:
       json.dump(existing_data, f, indent=4, ensure_ascii=False)

# Main function
def main(ods_filepath, json_filepath):
    # Load ODS data
    ods_data = load_ods_data(ods_filepath)

        # Print column names for debugging
    print("Column names:", ods_data.columns)

    
    # Append new data to JSON file
    append_to_json_file(json_filepath, ods_data)

# Example usage
ods_filepath = "./input.ods"
json_filepath = "./output.json"
main(ods_filepath, json_filepath)
