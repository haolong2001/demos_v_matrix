# %%
import pandas as pd
import numpy as np

# --- Configuration ---
FILE_MEDCLAIM = "medclaim_ckd.csv"
FILE_POP_START = "new_standard_ckd_1990_2050_start.csv"
FILE_POP_END = "new_standard_ckd_1990_2050_end.csv"

# --- 1. Load and Process Medclaim Data (Numerator) ---
def load_and_process_medclaim(filepath):
    print(f"Loading medclaim data from {filepath}...")
    df = pd.read_csv(filepath)
    
    # Rename the unnamed column to 'Stage'
    df.rename(columns={df.columns[0]: 'Stage'}, inplace=True)
    
    # Set Stage as index
    df.set_index('Stage', inplace=True)
    
    # Transpose so Year is the index
    df_t = df.T
    df_t.index.name = 'Year'
    df_t.index = df_t.index.astype(int) # Convert years to integers
    
    # Clean column names (strip whitespace just in case)
    df_t.columns = df_t.columns.str.strip()
    
    # --- Grouping Logic for Numerator ---
    # 1. Combine "other(1 or 2)" and "stage 2" -> "Stage_1_2"
    # Note: Using .get() with default 0 to avoid errors if exact string match fails
    col_other = [c for c in df_t.columns if "other" in c.lower()][0] # Find "other(1 or 2)"
    col_stg2  = [c for c in df_t.columns if "stage 2" in c.lower()][0]
    
    df_t['Hosp_Stage_1_2'] = df_t[col_other] + df_t[col_stg2]
    
    # 2. Stage 3 (Already aggregated in medclaim usually, but checking)
    # The file has "stage 3", which we assume covers both 3a and 3b
    col_stg3 = [c for c in df_t.columns if "stage 3" in c.lower()][0]
    df_t['Hosp_Stage_3'] = df_t[col_stg3]
    
    # 3. Stage 4
    col_stg4 = [c for c in df_t.columns if "stage 4" in c.lower()][0]
    df_t['Hosp_Stage_4'] = df_t[col_stg4]
    
    # 4. Stage 5
    col_stg5 = [c for c in df_t.columns if "stage 5" in c.lower()][0]
    df_t['Hosp_Stage_5'] = df_t[col_stg5]
    
    return df_t[['Hosp_Stage_1_2', 'Hosp_Stage_3', 'Hosp_Stage_4', 'Hosp_Stage_5']]

# --- 2. Load and Process Population Data (Denominator) ---
def load_and_process_population(filepath):
    print(f"Loading population data from {filepath}...")
    # Assuming the file index is Year (from previous step)
    df = pd.read_csv(filepath, index_col=0)
    
    # --- Grouping Logic for Denominator ---
    # 1. Stage 1+2 = K1 + K2
    df['Pop_Stage_1_2'] = (df['K1'] + df['K2']) * 20
    
    # 2. Stage 3 = K3a + K3b
    df['Pop_Stage_3'] = (df['K3a'] + df['K3b']) * 20
    
    # 3. Stage 4 = K4
    df['Pop_Stage_4'] = df['K4'] * 20
    
    # 4. Stage 5 = K5
    df['Pop_Stage_5'] = df['K5'] * 20
    
    return df[['Pop_Stage_1_2', 'Pop_Stage_3', 'Pop_Stage_4', 'Pop_Stage_5']]

# --- 3. Calculate Rates ---
def calculate_rates(df_hosp, df_pop, suffix=""):
    # Merge on Year (Index)
    # We use inner join to only calculate for years where we have BOTH medclaim and population data
    merged = pd.merge(df_hosp, df_pop, left_index=True, right_index=True, how='inner')
    
    rates = pd.DataFrame(index=merged.index)
    
    # Calculate Rate: Hosp / Pop
    # Note: Result is a ratio (e.g., 0.05). Multiply by 100 for percentage if desired.
    rates[f'Rate_Stage_1_2_{suffix}'] = merged['Hosp_Stage_1_2'] / merged['Pop_Stage_1_2']
    rates[f'Rate_Stage_3_{suffix}']   = merged['Hosp_Stage_3']   / merged['Pop_Stage_3']
    rates[f'Rate_Stage_4_{suffix}']   = merged['Hosp_Stage_4']   / merged['Pop_Stage_4']
    rates[f'Rate_Stage_5_{suffix}']   = merged['Hosp_Stage_5']   / merged['Pop_Stage_5']
    
    return rates

# %% --- Main Execution ---

# 1. Get Numerator (Hospitalization Counts)
df_hosp = load_and_process_medclaim(FILE_MEDCLAIM)
print("\nProcessed Hospitalization Data (First 5 rows):")
print(df_hosp.head())

# 2. Get Denominator (Population Counts) - Start Scenario
try:
    df_pop_start = load_and_process_population(FILE_POP_START)
    rates_start = calculate_rates(df_hosp, df_pop_start, suffix="Start")
    print("\n=== Hospitalization Rates (Using START Population) ===")
    
    rates_start = rates_start.clip(upper=1.0)
    rates_start = rates_start.round(2)
    print(rates_start)
    rates_start.to_csv("hospitalization_rates_start.csv")

    ###########
    ###########
    df_pop_end = load_and_process_population(FILE_POP_END)
    rates_end = calculate_rates(df_hosp, df_pop_end, suffix="End")
    rates_end = rates_end.clip(upper=1.0)
    rates_end = rates_end.round(2)
    print("\n=== Hospitalization Rates (Using END Population) ===")
    print(rates_end)
    rates_end.to_csv("hospitalization_rates_end.csv")
except FileNotFoundError:
    print(f"\nCould not find {FILE_POP_END}. Skipping...")
# %%
import pandas as pd

# 1. Load the data (if not already in variables)
rates_start = pd.read_csv("hospitalization_rates_start.csv", index_col=0)
rates_end = pd.read_csv("hospitalization_rates_end.csv", index_col=0)

# 2. Create the Combined DataFrame
df_combined = pd.DataFrame(index=rates_start.index)

# Iterate through columns in the Start dataframe
for col_start in rates_start.columns:
    if "_Start" in col_start:
        # Determine the base name and the matching End column
        base_name = col_start.replace("_Start", "")
        col_end = col_start.replace("_Start", "_End")
        
        if col_end in rates_end.columns:
            # 3. Combine values into string format "(End, Start)"
            # formatting to 4 decimal places for clarity
            df_combined[base_name] = [
                f"({e:.4f}, {s:.4f})" 
                for s, e in zip(rates_start[col_start], rates_end[col_end])
            ]

# 4. Display and Save
print("Combined Hospitalization Rates (End, Start):")
print(df_combined.head())

# Optional: Save to CSV
df_combined.to_csv("hospitalization_rates_combined_tuple.csv")
# %%
# 2. Define the mapping between corresponding columns
# We want to match Stage 1-2 with Stage 1-2, etc.
df_end = pd.read_csv('hospitalization_rates_end.csv', index_col=0)
df_start = pd.read_csv('hospitalization_rates_start.csv', index_col=0)

stages = {
    'Rate_Stage_1_2': ('Rate_Stage_1_2_End', 'Rate_Stage_1_2_Start'),
    'Rate_Stage_3': ('Rate_Stage_3_End', 'Rate_Stage_3_Start'),
    'Rate_Stage_4': ('Rate_Stage_4_End', 'Rate_Stage_4_Start'),
    'Rate_Stage_5': ('Rate_Stage_5_End', 'Rate_Stage_5_Start')
}

# 3. Create a dictionary to hold the combined tuple data
combined_data = {}

for new_col_name, (end_col, start_col) in stages.items():
    # Use zip to create tuples of (end_value, start_value) for every row
    combined_data[new_col_name] = [
        (e, s) for e, s in zip(df_end[end_col], df_start[start_col])
    ]

# 4. Convert the dictionary back into a DataFrame
df_combined = pd.DataFrame(combined_data, index=df_end.index)

# 5. Save the result to a new CSV file
df_combined.to_csv('combined_hospitalization_rates.csv')

# Display the result
print(df_combined.head())
# %%
