import pandas as pd
from datetime import datetime, timedelta

def combine_excel_sheets_to_csv(excel_file):
    # Read the Excel file
    xls = pd.ExcelFile(excel_file)
    
    # Initialize an empty DataFrame to hold the combined data
    combined_df = pd.DataFrame()
    
    # Loop through each sheet in the Excel file
    count = 0
    for sheet_name in xls.sheet_names:
        if sheet_name.startswith("Year"):
            # Read the sheet into a DataFrame
            df = pd.read_excel(xls, sheet_name=sheet_name)
            # Append the DataFrame to the combined DataFrame
            combined_df = pd.concat([combined_df, df], ignore_index=True)
            count += 1
    
    # Write the combined DataFrame to a CSV file
    return combined_df

def add_total_battery_energy(data):
    data['Total Battery Energy (kWh)'] = data['Battery Outflow (kWh)'] - data['Battery Inflow (kWh)']
    return data

def add_time_column_to_csv(data, start_time, output_file):
    # Generate a list of hourly timestamps for the given year
    time_stamps = []
    current_time = start_time
    while len(time_stamps) < len(data):
        if not (current_time.month == 2 and current_time.day == 29):
            time_stamps.append(current_time)
        current_time += timedelta(hours=1)

    # Add the new 'Time' column
    if len(data) != len(time_stamps):
        print(f"The Excel file has {len(data)} rows, but a full year's hourly data has {len(time_stamps)} rows.")
        return

    data['Time'] = time_stamps

    # Save the updated CSV
    try:
        data.to_csv(output_file, index=False)
        print(f"Updated CSV saved as '{output_file}'")
    except Exception as e:
        print("Error saving the updated CSV file:", e)

scenarios = ["basecaseerrorsolar"]

scenario = scenarios[0]
print(scenario)

excel_file = f"microgridspyusecase\\{scenario}\\results\\Energy Balance - Scenario 1.xlsx"
start_time = datetime(2022, 1, 1, 0, 0, 0)
output_file = f"microgridspyusecase\\{scenario}\\results\\Energy Balance with time.csv"
combined_df = combine_excel_sheets_to_csv(excel_file)
try:
    combined_df = add_total_battery_energy(combined_df)
except:
    print("No battery data found")
add_time_column_to_csv(combined_df, start_time, output_file)