import os
import pandas as pd
import torch
from chronos import BaseChronosPipeline
import matplotlib.pyplot as plt

# Load the Chronos model
pipeline = BaseChronosPipeline.from_pretrained(
    "amazon/chronos-t5-small",
    device_map="cpu",
    torch_dtype=torch.bfloat16,
)

# Set the absolute path for data directory
data_directory = r"\Users\edena\BNO_Data_Logging\chronos-forecasting\chronos-forecasting\data_directory"

# Ensure the directory exists
if not os.path.exists(data_directory):
    raise FileNotFoundError(f"Error: The directory {data_directory} does not exist. Please check the path.")

# Function to process each CSV file and generate graphs for body parts
def process_csv(file_path, participant_name):
    # Extract body part from the file name
    body_part = "unknown"

    # Determine body part based on the file name
    if "leftarm" in participant_name.lower():
        body_part = "left arm"
    elif "rightarm" in participant_name.lower():
        body_part = "right arm"
    elif "chest" in participant_name.lower():
        body_part = "chest"
    elif "waist" in participant_name.lower():
        body_part = "waist"

    df = pd.read_csv(file_path)

    # Ensure required columns exist
    required_columns = ["Accel_X", "Accel_Y", "Accel_Z"]
    if not all(col in df.columns for col in required_columns):
        print(f"Skipping {file_path}: Required columns missing.")
        return

    # Convert columns to numeric and drop NaNs
    for col in required_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=required_columns)

    # Use the correct data for the identified body part
    context_data = df["Accel_X"].values  # Replace with actual data for the body part if available

    # Perform forecasting
    quantiles, mean = pipeline.predict_quantiles(
        context=torch.tensor(context_data, dtype=torch.float32),
        prediction_length=12,
        quantile_levels=[0.1, 0.5, 0.9],
    )

    # Extract forecast values
    forecast_index = range(len(df), len(df) + 12)
    low, median, high = quantiles[0, :, 0], quantiles[0, :, 1], quantiles[0, :, 2]

    # Plot results
    plt.figure(figsize=(8, 4))
    plt.plot(context_data, color="royalblue", label=f"Historical Data ({body_part})")
    plt.plot(forecast_index, median, color="tomato", label="Median Forecast")
    plt.fill_between(forecast_index, low, high, color="tomato", alpha=0.3, label="80% Prediction Interval")
    plt.xlabel("Time (samples)")  # Label for X-axis
    plt.ylabel("Acceleration (m/s²)")  # Label for Y-axis
    plt.legend()
    plt.grid()
    plt.title(f"IMU Forecasting for {participant_name} - {body_part}")
    plt.show()

# Main Execution: Loop through all CSV files in the directory
for file in os.listdir(data_directory):
    if file.endswith(".csv"):  # Ensure it's a CSV file
        file_path = os.path.join(data_directory, file)
        participant_name = os.path.splitext(file)[0]  # Use file name as participant name
        print(f"Processing file: {file}")
        process_csv(file_path, participant_name)