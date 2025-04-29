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

# data directory path
data_directory = r"C:\Users\edena\chronos-forecasting\chronos-forecasting\Rowing_Data"

# Ensure the directory exists
if not os.path.exists(data_directory):
    raise FileNotFoundError(f"Error: The directory {data_directory} does not exist. Please check the path.")

# Function to process each participant's data
def process_participant(participant_path, participant_name):
    for file in os.listdir(participant_path):
        if file.endswith(".csv"):  # Ensure it's a CSV file
            file_path = os.path.join(participant_path, file)
            df = pd.read_csv(file_path)

            # Ensure Accel_X exists
            if "Accel_X" not in df.columns:
                print(f"Skipping {file}: 'Accel_X' column missing.")
                continue

            # Convert Accel_X to numeric and drop NaNs
            df["Accel_X"] = pd.to_numeric(df["Accel_X"], errors="coerce")
            df = df.dropna(subset=["Accel_X"])

            # Perform forecasting
            quantiles, mean = pipeline.predict_quantiles(
                context=torch.tensor(df["Accel_X"].values, dtype=torch.float32),
                prediction_length=12,
                quantile_levels=[0.1, 0.5, 0.9],
            )

            # Extract forecast values
            forecast_index = range(len(df), len(df) + 12)
            low, median, high = quantiles[0, :, 0], quantiles[0, :, 1], quantiles[0, :, 2]

            # Plot results
            plt.figure(figsize=(8, 4))
            plt.plot(df["Accel_X"], color="royalblue", label="Historical Accel_X Data")
            plt.plot(forecast_index, median, color="tomato", label="Median Forecast")
            plt.fill_between(forecast_index, low, high, color="tomato", alpha=0.3, label="80% Prediction Interval")
            plt.legend()
            plt.grid()
            plt.title(f"IMU Forecasting for {participant_name} ({file})")
            plt.show()

# Main Execution: Loop through all participant folders
for participant in os.listdir(data_directory):
    participant_path = os.path.join(data_directory, participant)
    if os.path.isdir(participant_path):  # Ensure it's a directory
        print(f"Processing data for {participant}...")
        process_participant(participant_path, participant)
