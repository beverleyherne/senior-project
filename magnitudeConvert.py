import pandas as pd
import numpy as np
import os

# Load the uploaded CSV file
file_path = r"C:\Users\edena\chronos-forecasting\chronos-forecasting\data_directory4\slowFastTestCardboard_20250423_075637.csv"
df = pd.read_csv(file_path)

#Inspect column names
print("CSV columns:", df.columns.tolist())

# Update required columns
required_columns = ["Accel_X", "Accel_Y", "Accel_Z", "Timestamp"]
if all(col in df.columns for col in required_columns):
    # Convert to numeric and drop invalid rows
    for col in ["Accel_X", "Accel_Y", "Accel_Z"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["Accel_X", "Accel_Y", "Accel_Z", "Timestamp"])
    
    # Compute acceleration magnitude
    df["Accel_Magnitude"] = np.sqrt(df["Accel_X"]**2 + df["Accel_Y"]**2 + df["Accel_Z"]**2)
    
    # Select only the timestamp and computed magnitude
    result_df = df[["Timestamp", "Accel_Magnitude"]]
    
    # Output path
    output_path = r"C:\Users\edena\chronos-forecasting\chronos-forecasting\data_directory4\slowFastTestCardboard_20250423_075637_Data_with_magnitude.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if os.path.exists(output_path):
        print(f"Warning: {output_path} already exists and will be overwritten.")

    result_df.to_csv(output_path, index=False)

    if os.path.exists(output_path):
        print(f"File successfully saved to: {output_path}")
    else:
        print("Error: File was not saved.")
else:
    missing = [col for col in required_columns if col not in df.columns]
    print(f"Missing columns in the input file: {missing}")
