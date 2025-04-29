import os
import pandas as pd
import torch
from chronos import BaseChronosPipeline
import matplotlib.pyplot as plt

# Force CPU usage
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# Load pre-trained Chronos model
pipeline = BaseChronosPipeline.from_pretrained(
    "amazon/chronos-t5-small",
    device_map="cpu",  # Ensure the model runs on CPU
    torch_dtype=torch.bfloat16,
)

# Load sample time series dataset
df = pd.read_csv(
    "https://raw.githubusercontent.com/AileenNielsen/TimeSeriesAnalysisWithPython/master/data/AirPassengers.csv"
)

# Forecasting using Chronos model
quantiles, mean = pipeline.predict_quantiles(
    context=torch.tensor(df["#Passengers"], dtype=torch.float32, device="cpu"),  # Explicitly set device to CPU
    prediction_length=12,
    quantile_levels=[0.1, 0.5, 0.9],
)

# Visualization
forecast_index = range(len(df), len(df) + 12)
low, median, high = quantiles[0, :, 0], quantiles[0, :, 1], quantiles[0, :, 2]

plt.figure(figsize=(8, 4))
plt.plot(df["#Passengers"], color="royalblue", label="Historical Data")
plt.plot(forecast_index, median, color="tomato", label="Median Forecast")
plt.fill_between(forecast_index, low, high, color="tomato", alpha=0.3, label="80% Prediction Interval")
plt.legend()
plt.grid()
plt.show()
