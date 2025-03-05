import pandas as pd
import matplotlib.pyplot as plt

# Define the data
data = {
    "Output Power (kW)": [45, 90, 135, 180, 225, 270, 315, 360, 405],
    "Benchmark Efficiency (%)": [15.74, 23.15, 26.39, 30.10, 30.56, 31.48, 31.48, 32.41, 31.94]
}

# Convert data into a DataFrame
df = pd.DataFrame(data)

# Define a static efficiency model (constant 30%)
df["Model Efficiency (%)"] = 30.0

# Use FiveThirtyEight style
plt.style.use('fivethirtyeight')
textwidthfraction = 0.45
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

# Create figure
fig, ax = plt.subplots(figsize=(10, 6))

# Plot benchmark efficiency (dynamic) with red solid line and circular markers
ax.plot(df["Output Power (kW)"], df["Benchmark Efficiency (%)"], label="Benchmark Efficiency", color='#64B5F6', linestyle="-")

# Plot model efficiency (static 30%) with blue solid line and circular markers
ax.plot(df["Output Power (kW)"], df["Model Efficiency (%)"], label="Model Efficiency", color='#E57373', linestyle="-")

# Labels and title
ax.set_xlabel("Output Power (kW)")
ax.set_ylabel(r"Efficiency [\%]")
#ax.set_title("Generator Efficiency: Model vs. Benchmark")

# Add legend
ax.legend()

# Show grid
ax.grid(True)

# Show the plot
plt.savefig(f"microgridspyusecase\\GeneratorEfficiencyPlot.png", bbox_inches='tight', facecolor="white", edgecolor="white")


