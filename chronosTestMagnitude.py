import os
import pandas as pd
import torch
from chronos import ChronosPipeline
import matplotlib.pyplot as plt

# Force CPU usage
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# Load Chronos model
pipeline = ChronosPipeline.from_pretrained(
    "amazon/chronos-t5-small",
    device_map="cpu",
    torch_dtype=torch.bfloat16,
)

# Load your dataset
your_file = r"C:\Users\edena\chronos-forecasting\chronos-forecasting\data_directory4\slowFastTestCardboard_20250423_075637_Data_with_magnitude.csv"
df = pd.read_csv(your_file)

# Strip any extra spaces from column names
df.columns = df.columns.str.strip()

# Check that required columns exist
if "Accel_Magnitude" not in df.columns or "Timestamp" not in df.columns:
    raise ValueError("Missing 'Accel_Magnitude' or 'Timestamp' column in your file.")

# Convert Timestamp to datetime
df["Timestamp"] = pd.to_datetime(df["Timestamp"])


# Prepare input
context = torch.tensor(df["Accel_Magnitude"].values, dtype=torch.float32, device="cpu")

# Forecast
prediction_length = 50
quantiles, mean = pipeline.predict_quantiles(
    context=context,
    prediction_length=prediction_length,
    quantile_levels=[0.1, 0.5, 0.9],
)

# Generate forecast timestamps using regular interval
interval = df["Timestamp"].diff().median()
last_time = df["Timestamp"].iloc[-1]
future_times = pd.date_range(start=last_time + interval, periods=prediction_length, freq=interval)

# Extract quantile predictions
low, median, high = quantiles[0, :, 0], quantiles[0, :, 1], quantiles[0, :, 2]

# Plot with real time on X-axis
plt.figure(figsize=(12, 5))
plt.plot(df["Timestamp"], df["Accel_Magnitude"], label="Historical", color="royalblue")
plt.plot(future_times, median, label="Forecast (Median)", color="tomato")
plt.fill_between(future_times, low, high, color="tomato", alpha=0.3, label="80% Prediction Interval")
plt.title("Accel_Magnitude Cardboard Test")
plt.xlabel("Time")
plt.ylabel("Accel Magnitude")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
print(f"Each time step (interval): {interval}")
