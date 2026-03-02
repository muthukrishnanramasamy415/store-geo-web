import pandas as pd

# ======================================================
# Configuration
# ======================================================
INPUT_FILE = "stores.xlsx"
ZIP_DB_FILE = r"C:\Users\test\Downloads\simplemaps_uszips_basicv1.94\uszips.csv"
OUTPUT_FILE = "stores_with_coordinates.xlsx"

# ======================================================
# Load Store Data
# ======================================================
print("Loading store file...")
stores = pd.read_excel(INPUT_FILE, dtype={"Zip Code": str})

# Clean ZIP format (remove '-' if present)
stores["Zip Code"] = stores["Zip Code"].str.replace("-", "").str.strip()

# ======================================================
# Load ZIP Database
# ======================================================
print("Loading ZIP database...")
zip_db = pd.read_csv(ZIP_DB_FILE, dtype={"zip": str})

# Keep only required columns
zip_db = zip_db[["zip", "lat", "lng"]]
zip_db.columns = ["Zip Code", "Latitude", "Longitude"]

zip_db["Zip Code"] = zip_db["Zip Code"].str.strip()

# ======================================================
# Merge Data (Offline Lookup)
# ======================================================
print("Matching ZIP codes with coordinates...")
result = stores.merge(zip_db, on="Zip Code", how="left")

# ======================================================
# Validation Summary
# ======================================================
total = len(result)
matched = result["Latitude"].notna().sum()
missing = total - matched

print(f"Total Stores   : {total}")
print(f"Matched        : {matched}")
print(f"Missing ZIP    : {missing}")

# ======================================================
# Save Output
# ======================================================
result.to_excel(OUTPUT_FILE, index=False)

print("\nCompleted successfully!")

print("Output file:", OUTPUT_FILE)
