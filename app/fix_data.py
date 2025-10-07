# fix_data.py
import numpy as np
import os

ENCODINGS_FILE = "faces_data.npy"

if os.path.exists(ENCODINGS_FILE):
    try:
        # Load the corrupted data (using pickle allows loading the broken structure)
        corrupted_encodings = np.load(ENCODINGS_FILE, allow_pickle=True)

        repaired_encodings = []

        print(f"Loaded {len(corrupted_encodings)} items. Checking structure...")

        # Iterate through the data and repair corrupted elements
        for i, item in enumerate(corrupted_encodings):
            # The expected type is a NumPy array (np.ndarray)
            if isinstance(item, np.ndarray):
                repaired_encodings.append(item)

            # If it's a list (which should be an array), convert it. 
            # This catches the string-saved format, though less likely now.
            elif isinstance(item, list):
                repaired_encodings.append(np.array(item, dtype='float32'))

            # If it's a single float, skip it and flag it as corruption
            elif isinstance(item, (float, np.float64, np.float32)):
                print(f"❌ WARNING: Found corrupted single float element at index {i}. Skipping element.")

            else:
                # Catch any other unexpected type
                print(f"⚠️ UNEXPECTED TYPE at index {i}: {type(item)}. Skipping element.")


        # Overwrite the corrupted file with the cleaned, repaired data
        print(f"\nRepair complete. Repaired {len(repaired_encodings)} out of {len(corrupted_encodings)} entries.")
        if len(repaired_encodings) > 0:
            np.save(ENCODINGS_FILE, np.array(repaired_encodings, dtype=object))
            print("✅ Successfully saved the repaired data to disk.")
        else:
             print("❗ REPAIR FAILED: No valid encodings were found. Please proceed with deletion.")

    except Exception as e:
        print(f"CRITICAL FAILURE during data loading/inspection: {e}")
        print("Please delete the .npy file manually.")

else:
    print("Data file not found. Nothing to repair.")