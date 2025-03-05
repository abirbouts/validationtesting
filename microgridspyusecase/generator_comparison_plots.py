import pandas as pd
import matplotlib.pyplot as plt
import calendar

# Load CSV file (Update the file path accordingly)
file_path = "microgridspyusecase\\generator_validation_fuel_cost_comparison.csv" 
df = pd.read_csv(file_path, parse_dates=['Time'])

# Set the time column as index
df.set_index('Time', inplace=True)

# Resample to hourly data if needed
df = df.resample('h').mean()

df['Benchmark Discounted Fuel Cost generator Total [$]'] = 100 * df['Benchmark Discounted Fuel Cost generator Total [$]']
df.fillna(0, inplace=True)

# Use FiveThirtyEight style for better aesthetics
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

# --- Plot Time-Series Comparison ---
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['Model Discounted Fuel Cost generator Total [$]'], label='Model Fuel Cost', color='#E57373')
plt.plot(df.index, df['Benchmark Discounted Fuel Cost generator Total [$]'], label='Benchmark Fuel Cost', color='#64B5F6')
plt.xlabel('Time')
plt.ylabel(r'Discounted Fuel Cost [\$]')
plt.title('Model vs Benchmark: Discounted Fuel Cost Over Time')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("microgridspyusecase\\fuel_cost_timeseries.png")  # Save the plot

# --- Daily Pattern Comparison ---
df['Hour'] = df.index.hour
hourly_stats_model = df.groupby('Hour')['Model Discounted Fuel Cost generator Total [$]'].agg(['mean', 'min', 'max'])
hourly_stats_benchmark = df.groupby('Hour')['Benchmark Discounted Fuel Cost generator Total [$]'].agg(['mean', 'min', 'max'])

fig, ax = plt.subplots(figsize=(12, 6))
hours = hourly_stats_model.index
ax.plot(hours, hourly_stats_model['mean'], label='Model Output', color='#E57373')
ax.plot(hours, hourly_stats_benchmark['mean'], label='Benchmark Output', color='#64B5F6')
ax.fill_between(hours, hourly_stats_model['min'], hourly_stats_model['max'], color='#E57373', alpha=0.3, label='Model Output Range')
ax.fill_between(hours, hourly_stats_benchmark['min'], hourly_stats_benchmark['max'], color='#64B5F6', alpha=0.3, label='Benchmark Output Range')
ax.set_xlabel('Hour of the Day')
ax.set_ylabel(r'Discounted Fuel Cost [\$]')
#ax.set_title('Daily Pattern: Model vs Benchmark Fuel Costs')
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
ax.grid(True)
plt.tight_layout()
plt.savefig("microgridspyusecase\\fuel_cost_daily_pattern.png", facecolor="white", edgecolor="white")  # Save the plot

# --- Monthly Pattern Comparison ---
df['Month'] = df.index.month


# --- First 10 Days Pattern Comparison ---
days = sorted(df.index.normalize().unique())[:10]

for day in days:
    daily_data = df[df.index.normalize() == day]
    if not daily_data.empty:
        hourly_stats_model = daily_data.groupby(daily_data.index.hour)['Model Discounted Fuel Cost generator Total [$]'].agg(['mean', 'min', 'max'])
        hourly_stats_benchmark = daily_data.groupby(daily_data.index.hour)['Benchmark Discounted Fuel Cost generator Total [$]'].agg(['mean', 'min', 'max'])

        fig, ax = plt.subplots(figsize=(12, 6))
        hours = hourly_stats_model.index
        ax.plot(hours, hourly_stats_model['mean'], label='Model Output', color='#E57373')
        ax.plot(hours, hourly_stats_benchmark['mean'], label='Benchmark Output', color='#64B5F6')
        ax.set_xlabel('Hour of the Day')
        ax.set_ylabel(r'Discounted Fuel Cost [\$]')
        #ax.set_title(f'Day {day.date()} Fuel Cost Pattern: Model vs Benchmark')
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax.grid(True)
        plt.tight_layout()
        
        plt.savefig(f"microgridspyusecase\\fuel_cost_day_{day.date()}.png", facecolor="white", edgecolor="white")  # Save the plot

print("All plots saved successfully!")
