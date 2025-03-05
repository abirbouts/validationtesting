import pandas as pd
import matplotlib.pyplot as plt

# Load the SoC data
data = {
    "Time": [
        "12/31/2031 12:00", "12/31/2031 13:00", "12/31/2031 14:00", "12/31/2031 15:00",
        "12/31/2031 16:00", "12/31/2031 17:00", "12/31/2031 18:00", "12/31/2031 19:00",
        "12/31/2031 20:00", "12/31/2031 21:00", "12/31/2031 22:00", "12/31/2031 23:00",
        "1/1/2032 00:00", "1/1/2032 01:00", "1/1/2032 02:00", "1/1/2032 03:00",
        "1/1/2032 04:00", "1/1/2032 05:00", "1/1/2032 06:00", "1/1/2032 07:00",
        "1/1/2032 08:00", "1/1/2032 09:00", "1/1/2032 10:00", "1/1/2032 11:00",
        "1/1/2032 12:00"
    ],
    "SoC Model": [76.3, 86.65, 94.38, 98.41, 98.41, 93.57, 84.99, 73.06, 60.27, 47.13,
                  36.15, 30.12, 20, 20, 20, 20, 20, 20, 20, 20, 25.12, 32.18, 44.31, 53.09, 67.06],
    "SoC Benchmark": [76.3, 86.65, 94.38, 98.41, 98.41, 93.57, 84.99, 73.06, 60.27, 47.13,
                      36.15, 30.12, 43.6, 43.6, 43.6, 43.6, 43.6, 43.6, 43.6, 43.6,
                      48.72, 55.78, 67.91, 76.69, 90.66]
}

# Convert to DataFrame
df = pd.DataFrame(data)

# Convert Time column to datetime
df["Time"] = pd.to_datetime(df["Time"])

# Use FiveThirtyEight style
plt.style.use('fivethirtyeight')
textwidthfraction = 0.7
fontsize = 12 / textwidthfraction
fontsize2 = 10 / textwidthfraction
plt.rcParams.update({
    "text.usetex": True,      
    "font.family": "serif",
    "font.size": fontsize,
    "axes.titlesize": fontsize,
    "axes.labelsize": fontsize,
    "legend.fontsize": fontsize,
    "xtick.labelsize": fontsize2,
    "ytick.labelsize": fontsize2
})

# Create the figure
fig, ax = plt.subplots(figsize=(12, 6))

# Plot Model and Benchmark SoC
ax.plot(df["Time"], df["SoC Model"], label="Model SoC", color='#E57373', linestyle="-")
ax.plot(df["Time"], df["SoC Benchmark"], label="Benchmark SoC", color='#64B5F6', linestyle="-")

# Set labels and title
ax.set_xlabel("Time")
ax.set_ylabel(r"SoC [\%]")
#ax.set_title("SoC Comparison")

# Set y-axis limits from 0 to 100
ax.set_ylim(0, 100)

# Format x-axis ticks
ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%m-%d-%y %H:%M"))

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Display legend
ax.legend(loc="upper right")

# Show grid
ax.grid(True)

# Adjust layout
plt.tight_layout()

# Show the plot
plt.savefig(f"microgridspyusecase\\SoCValidationPlot.png", bbox_inches='tight', facecolor="white", edgecolor="white")

