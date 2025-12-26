#%%
from Age_BMI_loading import (
    age_dict,
    bmi_samples_dict,
)
from Age_BMI_loading import (
    age_matrix_vec_2050,
)
import os
import numpy as np
from impute_ckd import *

from prevalence_3d import *
#%%
age_matrix_vec = age_matrix_vec_2050
#%% load bmi matrix
bmi_matrix_ls = []
for i in range(8):
    bmi_matrix = np.load(f'../future_data_1990_2050/bmi_matrix/bmi_matrix_{i}.npy')
    print(f"Loaded: bmi_matrix_{i}.npy with shape {bmi_matrix.shape}")
    bmi_matrix_ls.append(bmi_matrix)

# #%% Save the modified bmi matrices back to disk for reproducibility (overwrite original files)
# for i, bmi_matrix in enumerate(bmi_matrix_ls):
#     np.save(f'../future_data_1990_2050/bmi_matrix/bmi_matrix_{i}.npy', bmi_matrix)
#     print(f"Saved modified: bmi_matrix_{i}.npy with shape {bmi_matrix.shape}")


#%% load albu matrix
albu_mat_storage = []
for i in range(8):
    albu_mat = np.load(f'../future_data_1990_2050/albu_matrix_forecast/albu_mat_group_{i}.npy')
    print(f"Loaded: albu_mat_{i}.npy with shape {albu_mat.shape}")
    albu_mat_storage.append(albu_mat)

#%% load diabetes matrix
diabetes_mat_storage = []
for i in range(8):
    diabetes_mat = np.load(f'../future_data_1990_2050/diabetes_matrix/diabetes_mat_{i}.npy')
    print(f"Loaded: diabetes_mat_{i}.npy with shape {diabetes_mat.shape}")
    diabetes_mat_storage.append(diabetes_mat)

#%% load hypertension matrix
hypertension_mat_storage = []
for i in range(8):
    hypertension_mat = np.load(f'../future_data_1990_2050/hyper_matrix/hypertension_mat_{i}.npy')
    print(f"Loaded: hypertension_mat_{i}.npy with shape {hypertension_mat.shape}")
    hypertension_mat_storage.append(hypertension_mat)

#%% check if albu matrix is correct: 0,1,2
if np.max(albu_mat_storage[0]) != 2:
    for i in range(len(albu_mat_storage)):
        albu_mat_storage[i] = albu_mat_storage[i] * 2

# %% diabetes values are 0.0.5,1
if np.max(diabetes_mat[0]) == 1:
    print("correct")
#%%
# Check unique values for diabetes_mat_storage[0] and hypertension_mat_storage[0]
print("Unique values in diabetes_mat_storage[0]:", np.unique(diabetes_mat_storage[0]))
print("Unique values in hypertension_mat_storage[0]:", np.unique(hypertension_mat_storage[0]))

# %%
for idx in range(8):
    eth = map_eth_str(idx)
    beta0, beta1, beta2, beta3, beta4, sigma = coefficients[eth]
    print(f"eth={idx} ({eth}): beta0={beta0}, beta1={beta1}, beta2={beta2}, beta3={beta3}, beta4={beta4}, sigma={sigma}")

#%% begin 
import numpy as np

eGFR_matrix_ls = []  # List to store eGFR matrices

for idx in range(8):
  # Iterate over the five cases (k=0 to 4)
    case_matrices = []  # Store matrices for this case
    for i, k in enumerate([0,4]):  # k from 0 to 4 range(5)
        # Extract age matrix for this index
        matrix = age_matrix_vec[idx]  # Contains age values
        bmi_values = bmi_matrix_ls[idx]  # Corresponding BMI values

        albu_value = albu_mat_storage[idx][k, :, :] 
        diabetes_value = diabetes_mat_storage[idx]
        hypertension_value = hypertension_mat_storage[idx]
        
        
        # Get ethnicity and gender
        eth = map_eth_str(idx)  # 'chn', 'ind', or 'mal'
        gender2 = idx % 2  # 0 for Male, 1 for Female

        # Extract coefficients for the ethnicity
        beta0, beta1, beta2, beta3, beta4, sigma = coefficients[eth]
        
        # Generate noise
        row_noise = np.random.normal(loc=0, scale=sigma, size=(matrix.shape[0], matrix.shape[1]))

        # 2. Reshape to (10, 103903, 1)
        # This allows it to broadcast across the 61 time points
        row_noise = row_noise[:, :, np.newaxis]
        
        # Compute coefficients based on conditions
        diabetes_coefficient = np.where(diabetes_value == 0.5, 0.5, np.where(diabetes_value == 1, 1., 0))
        albu_coefficient = np.where(albu_value == 1, 0.1, np.where(albu_value == 2, 0.5, 0))
        hypertension_coefficient = 0.1


        # 1. Initialize eGFR_matrix with -1.0
        eGFR_matrix = np.full_like(matrix, -1.0, dtype=float)

        # 2. Create a boolean mask for valid parts (where matrix is not -1)
        valid_mask = (matrix != -1)

        # 3. Compute eGFR (using np.where to apply logic only on valid_mask)
        # This prevents having to "fix" the -1s later

        eGFR_matrix = np.where(
            valid_mask,
            (
                beta0 +
                beta1 * matrix * 0.5 +  # Age contribution
                beta2 * gender2 +  # Gender contribution
                beta3 * matrix * gender2 * 0.5 +  # Age * Gender interaction
                beta4 * np.log(bmi_values) +  # BMI contribution
                beta1 * matrix * hypertension_coefficient * hypertension_value + 
                beta1 * matrix * diabetes_coefficient * diabetes_value + 
                beta1 * matrix * albu_coefficient * albu_value + 

                row_noise  # Random noise
            ),
            -1.0  # Fallback value (though already initialized, this ensures assignment)
        )

        
        case_matrices.append(eGFR_matrix)
    case_matrices = np.array(case_matrices)
    
    eGFR_matrix_ls.append(case_matrices)

# Convert list to a NumPy array for better structure


# Display the resulting eGFR matrix
print("eGFR Matrix:")
print(eGFR_matrix_ls[0][0,:,:])


# %%
# eGFR_matrix_ls = []
# for idx in range(8):
#     case_matrices = []
#     for k in [0,4]:#range(5):
#         matrix = age_matrix_vec[idx]  # Age matrix
#         bmi_values = bmi_matrix_ls[idx]
#         albu_value = albu_mat_storage[idx][k, :, :] 
#         diabetes_value = diabetes_mat_storage[idx]
#         hypertension_value = hypertension_mat_storage[idx]
        
#         eth = map_eth_str(idx)
#         gender2 = idx % 2
#         beta0, beta1, beta2, beta3, beta4, sigma = coefficients[eth]
        
#         # Generate noise consistent across time for the individual simulation
#         row_noise = np.random.normal(loc=0, scale=sigma, size=(matrix.shape[0], matrix.shape[1]))
#         row_noise = row_noise[:, :, np.newaxis]
        
#         # Define coefficients
#         diab_coeff = np.where(diabetes_value == 0.5, 0.5, np.where(diabetes_value == 1, 1., 0))
#         albu_coeff = np.where(albu_value == 1, 0.1, np.where(albu_value == 2, 0.5, 0))
#         hyp_coeff = 0.1

#         # Initialize the result matrix
#         n_sim, n_people, n_years = matrix.shape
#         eGFR_final = np.full_like(matrix, -1.0, dtype=float)

#         # alive mask
#         valid_mask = (bmi_values > 0)
#         safe_bmi = np.where(valid_mask, bmi_values, 1.0)

#         # To track who has already crossed the <60 threshold for macro cases
#         # shape: (n_sim, n_people)
#         has_crossed_60 = np.zeros((n_sim, n_people), dtype=bool)

#         for t in range(n_years):
#             # 1. Standard calculation for current year
#             base_egfr = (
#                 beta0 +
#                 beta1 * matrix[:, :, t] * 0.5 +
#                 beta2 * gender2 +
#                 beta3 * matrix[:, :, t] * gender2 * 0.5 +
#                 beta4 * np.log(safe_bmi) +
#                 row_noise[:, :, 0]
#             )

#             comorbidity_impact = (
#                 beta1 * matrix[:, :, t] * hyp_coeff * hypertension_value[:, :, t] + 
#                 beta1 * matrix[:, :, t] * diab_coeff[:, :, t] * diabetes_value[:, :, t] + 
#                 beta1 * matrix[:, :, t] * albu_coeff[:, :, t] * albu_value[:, :, t]
#             )

#             # 2. Apply 1.2x Multiplier for non-macro cases (albu < 2) if eGFR < 60
#             multiplier_mask = (albu_value[:, :, t] < 2) & (base_egfr < 60)
#             # Add an extra 20% of the comorbidity impact
#             final_impact = np.where(multiplier_mask, comorbidity_impact * 1.2, comorbidity_impact)
            
#             current_calc_egfr = np.where(valid_mask, base_egfr + final_impact, -1.0)
            
#             # 3. Macroalbuminuria Static Decrease Logic (Abandon formula after first <60)
#             is_macro = (albu_value[:, :, t] == 2)
            
#             # Identify who just crossed or has already crossed 60 with Macro
#             newly_crossed = is_macro & (current_calc_egfr < 60) & (~has_crossed_60)
#             has_crossed_60 = has_crossed_60 | newly_crossed

#             # Determine fixed decrease rate based on status
#             is_dm = (diabetes_value[:, :, t] > 0)
#             is_htn = (hypertension_value[:, :, t] == 1) & (diabetes_value[:, :, t] == 0)
            
#             dec_rate = np.where(is_dm, 5.2, np.where(is_htn, 3.9, 4.2))

#             if t == 0:
#                 eGFR_final[:, :, t] = np.where(matrix[:, :, t] != -1, current_calc_egfr, -1.0)
#             else:
#                 # If they already crossed, take previous year and subtract fixed rate
#                 # Otherwise, use the standard calculated value
#                 eGFR_final[:, :, t] = np.where(
#                     has_crossed_60 & (matrix[:, :, t] != -1),
#                     eGFR_final[:, :, t-1] - dec_rate,
#                     np.where(matrix[:, :, t] != -1, current_calc_egfr, -1.0)
#                 )

#         case_matrices.append(eGFR_final)
#     eGFR_matrix_ls.append(np.array(case_matrices))

eGFR_matrix_ls = []

for idx in range(8):
    case_matrices = []
    
    # --- PRE-CALCULATE CONSTANTS OUTSIDE THE INNER LOOP ---
    eth = map_eth_str(idx)
    gender2 = idx % 2
    beta0, beta1, beta2, beta3, beta4, sigma = coefficients[eth]
    
    for k in [0, 4]:
        matrix = age_matrix_vec[idx]
        bmi_values = bmi_matrix_ls[idx]
        albu_value = albu_mat_storage[idx][k, :, :] 
        diabetes_value = diabetes_mat_storage[idx]
        hypertension_value = hypertension_mat_storage[idx]

        n_sim, n_people, n_years = matrix.shape

        # ---------------------------------------------------------
        # STEP 1: Fully Vectorized "Standard" Calculation (No Loop)
        # ---------------------------------------------------------
        
        # 1. Generate Noise (Broadcastable to Time)
        row_noise = np.random.normal(loc=0, scale=sigma, size=(n_sim, n_people, 1))
        
        # 2. Global Masks & Coefficients
        valid_mask = (bmi_values > 0)  # Shape: (n_sim, n_people, n_years)
        safe_bmi = np.where(valid_mask, bmi_values, 1.0)
        
        diab_coeff = np.where(diabetes_value == 0.5, 0.5, np.where(diabetes_value == 1, 1., 0))
        albu_coeff = np.where(albu_value == 1, 0.1, np.where(albu_value == 2, 0.5, 0))
        hyp_coeff = 0.1

        # 3. Calculate Base eGFR (All years at once)
        base_egfr = (
            beta0 +
            beta1 * matrix * 0.5 +
            beta2 * gender2 +
            beta3 * matrix * gender2 * 0.5 +
            beta4 * np.log(safe_bmi) +
            row_noise 
        )

        # 4. Comorbidity Impact
        comorbidity_impact = (
            beta1 * matrix * hyp_coeff * hypertension_value + 
            beta1 * matrix * diab_coeff * diabetes_value + 
            beta1 * matrix * albu_coeff * albu_value
        )

        # 5. Multiplier Logic
        multiplier_mask = (albu_value < 2) & (base_egfr < 60)
        final_impact = np.where(multiplier_mask, comorbidity_impact * 1.2, comorbidity_impact)

        # 6. Create the "Standard Trajectory" Matrix
        # This contains the values assuming NO macro-drop logic applied yet
        eGFR_final = np.where(valid_mask, base_egfr + final_impact, -1.0)

        # ---------------------------------------------------------
        # STEP 2: Sequential Logic for "Macro Drop" (Must Loop)
        # ---------------------------------------------------------
        
        # Track who has crossed the line
        # has_crossed_60 = np.zeros((n_sim, n_people), dtype=bool)
        is_dm = (diabetes_value > 0)
        is_htn = (hypertension_value == 1) & (diabetes_value == 0)
        
        # New constants: DM=5.2, HTN=4.2, Others=3.9
        dec_rate = np.where(is_dm, 5.2, np.where(is_htn, 4.2, 3.9))

        for t in range(n_years):
            # Define "Macro" status for this year
            is_macro = (albu_value[:, :, t] == 2)
            
            if t == 0:
                # SPECIAL CASE: t=0
                # Check based on the current standard calculation
                standard_val = eGFR_final[:, :, t]
                under_60 = (standard_val < 60) & is_macro
                
                # If under 60 & Macro: Apply immediate penalty
                # If valid but not under 60: Keep standard
                # If invalid: Keep -1
                
                # We reuse the logic: If Override -> Standard - Rate
                eGFR_final[:, :, t] = np.where(
                    under_60 & valid_mask[:, :, t], 
                    standard_val - dec_rate[:, :, t], 
                    standard_val
                )
                
            else:
                # STANDARD LOOP: t > 0
                # Logic: Check PREVIOUS year's final value
                prev_val = eGFR_final[:, :, t-1]
                prev_alive = (prev_val != -1)
                
                # Condition: Did we finish last year < 60 (and have Macro)?
                under_60 = (prev_val < 60) & is_macro
                
                # The Mask: Under 60 (prev) AND Alive (prev) AND Alive (now)
                override_mask = under_60 & prev_alive & valid_mask[:, :, t]
                
                # Apply the Override
                # If Mask is True:  Previous Value - Decrease Rate
                # If Mask is False: Use the Standard Calculation (already in eGFR_final)
                eGFR_final[:, :, t] = np.where(
                    override_mask,
                    prev_val - dec_rate[:, :, t],
                    eGFR_final[:, :, t] 
                )

        case_matrices.append(eGFR_final)
    eGFR_matrix_ls.append(np.array(case_matrices))

# %%
# eGFR_matrix_ls_new = eGFR_matrix_ls
#%% define stages
stages = {
    1: lambda x: x >= 90,
    2: lambda x: (x >= 60) & (x < 90),
    3.1: lambda x: (x >= 45) & (x < 60),
    3.2: lambda x: (x >= 30) & (x < 45),
    4 : lambda x: (x >= 15) & (x < 30),
    5 : lambda x: (x >= 0) & (x < 15),
    -1 :lambda x: x == -1
}

# For each matrix, create a corresponding stage matrix (same shape) where each element gets the stage value.
stage_matrix_ls = []
for i in range(8):
    matrix = eGFR_matrix_ls[i]
    # Initialize an output matrix with NaNs
    stage_matrix = np.full(matrix.shape, np.nan)
    # For every stage, update the positions where the condition is True
    for stage, condition in stages.items():
        mask = condition(matrix)
        stage_matrix[mask] = stage
    stage_matrix_ls.append(stage_matrix)

# %%

# %%

target_year = 2025
print(f"Generating CKD Prevalence Table for Year: {target_year}")

df_result = build_table_for_year(target_year)
print(df_result)
    

# %%

import pandas as pd
import numpy as np

# --- 1. Define Constants & Labels ---
# Define Stage keys and labels
STAGE_KEYS = [1, 2, 3.1, 3.2, 4, 5]
STAGE_LABELS = [
    "Stage 1 (eGFR >= 90)",
    "Stage 2 (60-89)",
    "Stage 3a (45-59)",
    "Stage 3b (30-44)",
    "Stage 4 (15-29)",
    "Stage 5 (<15)"
]

# Define ACR categories (0=Normal, 1=Micro, 2=Macro)
# Adjust these based on your specific albu_mat values if they differ.
ACR_CATEGORIES = [0, 1, 2]
ACR_LABELS = ["Normal", "Microalbuminuria", "Macroalbuminuria"]


# # --- 2. Define the Table Builder Function ---
# def build_table_for_year(year: int, max_age: int = 74) -> pd.DataFrame:
#     """
#     Constructs a prevalence table for a specific year using the 
#     pre-calculated stage_matrix_ls, albu_mat_storage, and age_matrix_vec.
#     """
    
#     # 1. Determine time index
#     year0 = 1990
#     # Check shape from the first matrix in the list
#     # shape is (5, n_people, n_years)
#     n_years = stage_matrix_ls[0].shape[-1]
#     year_index = year - year0
    
#     if year_index < 0 or year_index >= n_years:
#         raise ValueError(f"Year {year} is out of range [{year0}, {year0 + n_years - 1}]")

#     # We assume 'n_simu' is the number of people (rows) to normalize the count
#     # In your loops, n_people is matrix.shape[0]
#     # We sum counts across all 8 ethnic/gender groups and then divide by total population?
#     # Or is n_simu just 1 if we are summing counts? 
#     # Usually, if these are "counts", we just sum them up. 
#     # If the user code meant "average over Monte Carlo runs", that's different.
#     # Based on previous context, we likely just want the raw counts first.
    
#     df_counts = pd.DataFrame(0.0, index=STAGE_KEYS, columns=ACR_CATEGORIES)
#     df_counts_upper = pd.DataFrame(0.0, index=STAGE_KEYS, columns=ACR_CATEGORIES)

#     total_pop_count = 0

#     for idx in range(8):
#         # --- Extract Data for the specific Year ---
        
#         # 1. Stages: Shape (5, n_people, n_years)
#         # Base (Case 0) and Upper (Case 4)
#         stage_base = stage_matrix_ls[idx][0, :, year_index]
#         stage_upper = stage_matrix_ls[idx][-1, :, year_index]
        
#         # 2. Albuminuria: Shape (5, n_people, n_years)
#         acr_base = albu_mat_storage[idx][0, :, year_index]
#         acr_upper = albu_mat_storage[idx][-1, :, year_index]
        
#         # 3. Age: Shape (n_people, n_years) 
#         # Note: Age is consistent across the 5 simulation cases
#         age_slice = age_matrix_vec[idx][:, year_index]
        
#         # --- Filter Mask (Age 18 to max_age) ---
#         age_mask = (age_slice >= 18) & (age_slice <= max_age)
        
#         # Count valid population for this group
#         total_pop_count += np.sum(age_mask)

#         # --- Helper to accumulate counts ---
#         def accumulate(stage_arr, acr_arr, target_df):
#             # Apply age mask
#             valid_stages = stage_arr[age_mask]
#             valid_acr = acr_arr[age_mask]
            
#             for stage_val in STAGE_KEYS:
#                 # Find people with this stage
#                 # Use isclose for float comparison safety
#                 stage_matches = np.isclose(valid_stages, stage_val)
                
#                 if not np.any(stage_matches):
#                     continue
                
#                 for acr_val in ACR_CATEGORIES:
#                     # Count intersection of Stage + ACR category
#                     count = np.sum(stage_matches & (valid_acr == acr_val))
#                     target_df.loc[stage_val, acr_val] += count

#         accumulate(stage_base, acr_base, df_counts)
#         accumulate(stage_upper, acr_upper, df_counts_upper)

#     # --- Calculation of Percentages ---
#     # The totals in df_counts are sum of people. 
#     # If your simulation is a "representative sample" scaled to population, these are raw counts.
#     # If it is just a cohort, these are cohort counts.
    
#     grand_total_base = df_counts.values.sum()
#     grand_total_upper = df_counts_upper.values.sum()

#     df_perc = (df_counts / grand_total_base) * 100
#     df_perc_upper = (df_counts_upper / grand_total_upper) * 100

#     # --- Formatting the DataFrame ---
#     # Rename Indices/Columns
#     df_counts.index = STAGE_LABELS
#     df_counts_upper.index = STAGE_LABELS
#     df_perc.index = STAGE_LABELS
#     df_perc_upper.index = STAGE_LABELS
    
#     df_counts.columns = ACR_LABELS
#     df_counts_upper.columns = ACR_LABELS
#     df_perc.columns = ACR_LABELS
#     df_perc_upper.columns = ACR_LABELS

#     # Combine Count and Percentage into string: "Count (Perc%)"
#     # Format: "Base (%), Upper (%)"
    
#     df_final = pd.DataFrame(index=STAGE_LABELS, columns=ACR_LABELS)
    
#     for r in STAGE_LABELS:
#         for c in ACR_LABELS:
#             val_base = df_counts.loc[r, c]
#             pct_base = df_perc.loc[r, c]
#             val_upper = df_counts_upper.loc[r, c]
#             pct_upper = df_perc_upper.loc[r, c]
            
#             df_final.loc[r, c] = (
#                 f"{val_base:.0f} ({pct_base:.2f}%), {val_upper:.0f} ({pct_upper:.2f}%)"
#             )

#     # --- Calculate Row/Column Totals ---
#     row_totals_base = df_counts.sum(axis=1)
#     row_totals_upper = df_counts_upper.sum(axis=1)
#     row_perc_base = df_perc.sum(axis=1)
#     row_perc_upper = df_perc_upper.sum(axis=1)

#     df_final["Total"] = [
#         f"{row_totals_base[i]:.0f} ({row_perc_base[i]:.2f}%), {row_totals_upper[i]:.0f} ({row_perc_upper[i]:.2f}%)"
#         for i in range(len(STAGE_LABELS))
#     ]

#     col_totals_base = df_counts.sum(axis=0)
#     col_totals_upper = df_counts_upper.sum(axis=0)
#     col_perc_base = df_perc.sum(axis=0)
#     col_perc_upper = df_perc_upper.sum(axis=0)

#     total_row = []
#     for i in range(len(ACR_LABELS)):
#         c = ACR_LABELS[i]
#         total_row.append(
#             f"{col_totals_base[c]:.0f} ({col_perc_base[c]:.2f}%), {col_totals_upper[c]:.0f} ({col_perc_upper[c]:.2f}%)"
#         )
    
#     # Grand Total
#     grand_str = f"{grand_total_base:.0f} (100.00%), {grand_total_upper:.0f} (100.00%)"
#     total_row.append(grand_str)

#     df_final.loc["Total"] = total_row

#     return df_final
# %%
import pandas as pd
import numpy as np

def build_table_for_year(year: int, max_age: int = 74) -> pd.DataFrame:
    """
    Constructs a prevalence table for a specific year using the 
    pre-calculated stage_matrix_ls, albu_mat_storage, and age_matrix_vec.
    
    Returns the AVERAGE count across simulations (n_sim).
    """
    
    # 0. Constants and Setup
    year0 = 1990
    # Assuming the structure is (Case, People, Sim, Time) based on your snippet
    # stage_matrix_ls[0] shape: (5, n_people, n_sim, n_years)
    n_years = stage_matrix_ls[0].shape[-1]
    n_sim = stage_matrix_ls[0].shape[2] # Extract number of simulations
    
    year_index = year - year0
    
    if year_index < 0 or year_index >= n_years:
        raise ValueError(f"Year {year} is out of range [{year0}, {year0 + n_years - 1}]")

    # Define Categories
    # CKD Stages: 1, 2, 3, 4, 5
    # ACR Categories: 1 (A1), 2 (A2), 3 (A3)
    STAGE_KEYS = [1.0, 2.0, 3.0, 4.0, 5.0] 
    ACR_CATEGORIES = [1.0, 2.0, 3.0]
    
    STAGE_LABELS = ["G1", "G2", "G3", "G4", "G5"]
    ACR_LABELS = ["A1", "A2", "A3"]

    # Initialize accumulation DataFrames (Summing across all Sims first)
    df_sum_base = pd.DataFrame(0.0, index=STAGE_KEYS, columns=ACR_CATEGORIES)
    df_sum_upper = pd.DataFrame(0.0, index=STAGE_KEYS, columns=ACR_CATEGORIES)

    # 1. Loop through demographics groups
    for idx in range(8):
        # --- Extract Data for the specific Year ---
        # Dimensions: [Case, People, Sim, Time] -> Slice Time -> [Case, People, Sim]
        
        # Base (Case 0) and Upper (Case 4)
        # Slicing: [Case Index, :, :, Year Index]
        stage_base = stage_matrix_ls[idx][0, :, :, year_index]
        stage_upper = stage_matrix_ls[idx][-1, :, :, year_index]
        
        acr_base = albu_mat_storage[idx][0, :, :, year_index]
        acr_upper = albu_mat_storage[idx][-1, :, :, year_index]
        
        # Age: [People, Sim, Time] (Based on your updated dimension logic)
        age_slice = age_matrix_vec[idx][:, :, year_index]
        
        # --- Filter Mask (Age 18 to max_age) ---
        # This mask is shape (n_people, n_sim)
        valid_mask = (age_slice >= 18) & (age_slice <= max_age)
        
        # Helper to accumulate counts into the global dataframe
        def accumulate_counts(stage_mat, acr_mat, target_df, mask):
            # Flatten arrays based on the mask to speed up counting
            # We are summing occurrences across ALL simulations here
            valid_stages = stage_mat[mask]
            valid_acrs = acr_mat[mask]
            
            for s_val in STAGE_KEYS:
                # Boolean array for current stage
                is_stage = np.isclose(valid_stages, s_val)
                if not np.any(is_stage):
                    continue
                
                for a_val in ACR_CATEGORIES:
                    # Count intersection where Stage == S and ACR == A
                    # We sum the Trues
                    count = np.sum(is_stage & (valid_acrs == a_val))
                    target_df.loc[s_val, a_val] += count

        accumulate_counts(stage_base, acr_base, df_sum_base, valid_mask)
        accumulate_counts(stage_upper, acr_upper, df_sum_upper, valid_mask)

    # 2. Calculate Averages and Percentages
    # We summed across (8 groups * n_sim simulations).
    # To get the "Average Population Count", we divide by n_sim.
    
    df_avg_base = df_sum_base / n_sim
    df_avg_upper = df_sum_upper / n_sim
    
    grand_total_base = df_avg_base.values.sum()
    grand_total_upper = df_avg_upper.values.sum()
    
    # Avoid division by zero if empty
    if grand_total_base == 0: grand_total_base = 1e-9
    if grand_total_upper == 0: grand_total_upper = 1e-9

    df_perc_base = (df_avg_base / grand_total_base) * 100
    df_perc_upper = (df_avg_upper / grand_total_upper) * 100

    # 3. Format Output Table
    # Structure: "Base_Count (Base_%) , Upper_Count (Upper_%)"
    df_final = pd.DataFrame(index=STAGE_LABELS, columns=ACR_LABELS)

    # Fill Main Body
    for i, r_key in enumerate(STAGE_KEYS):
        for j, c_key in enumerate(ACR_CATEGORIES):
            r_lbl = STAGE_LABELS[i]
            c_lbl = ACR_LABELS[j]
            
            val_b = df_avg_base.loc[r_key, c_key]
            pct_b = df_perc_base.loc[r_key, c_key]
            val_u = df_avg_upper.loc[r_key, c_key]
            pct_u = df_perc_upper.loc[r_key, c_key]
            
            df_final.loc[r_lbl, c_lbl] = (
                f"{val_b:.0f} ({pct_b:.1f}%), {val_u:.0f} ({pct_u:.1f}%)"
            )

    # 4. Calculate Totals (Rows and Cols)
    
    # Row Totals
    row_sum_b = df_avg_base.sum(axis=1)
    row_sum_u = df_avg_upper.sum(axis=1)
    row_pct_b = (row_sum_b / grand_total_base) * 100
    row_pct_u = (row_sum_u / grand_total_upper) * 100

    df_final["Total"] = [
        f"{row_sum_b.iloc[i]:.0f} ({row_pct_b.iloc[i]:.1f}%), {row_sum_u.iloc[i]:.0f} ({row_pct_u.iloc[i]:.1f}%)"
        for i in range(len(STAGE_LABELS))
    ]

    # Column Totals
    col_sum_b = df_avg_base.sum(axis=0)
    col_sum_u = df_avg_upper.sum(axis=0)
    col_pct_b = (col_sum_b / grand_total_base) * 100
    col_pct_u = (col_sum_u / grand_total_upper) * 100

    total_row_strs = []
    for j, c_key in enumerate(ACR_CATEGORIES):
        total_row_strs.append(
            f"{col_sum_b[c_key]:.0f} ({col_pct_b[c_key]:.1f}%), {col_sum_u[c_key]:.0f} ({col_pct_u[c_key]:.1f}%)"
        )
    
    # Grand Total Cell
    grand_str = f"{grand_total_base:.0f} (100.0%), {grand_total_upper:.0f} (100.0%)"
    total_row_strs.append(grand_str)

    df_final.loc["Total"] = total_row_strs

    return df_final

# %%
# --- 3. Execute and Print ---
target_year = 2025
print(f"Generating CKD Prevalence Table for Year: {target_year}")
try:
    df_result = build_table_for_year(target_year)
    print(df_result)
    
    # Optional: Save to CSV
    # df_result.to_csv(f"ckd_prevalence_{target_year}.csv")
    
except Exception as e:
    print(f"Error generating table: {e}")


# %% information check 

egfr_data_sample = eGFR_matrix_ls[2][0][0]
stage_data_sample = stage_matrix_ls[2][0][0]

# Find rows (individuals) where there is any stage 4 present
rows_with_stage_4 = np.any(stage_data_sample == 5, axis=1)
indices_with_stage_4 = np.where(rows_with_stage_4)[0]

# Print corresponding egfr rows
for idx in indices_with_stage_4:
    print(f"Individual {idx} eGFR trajectory: {egfr_data_sample[idx]}")

# For Individual 20158, check BMI, albuminuria, hypertension, and diabetes status
# %%
def extract_infor(group_idx, case_idx, sim_idx, ind_idx):
    """
    Extracts input variables for a specific individual.
    
    Parameters:
    - group_idx: Index for the demographic group (0-7)
    - case_idx: Index for the case (k, 0-4)
    - sim_idx: Index for the simulation/batch (0-9)
    - ind_idx: Index for the individual row (e.g., 20158)
    """
    print(f"--- Extracting info for Group {group_idx}, Case {case_idx}, Sim {sim_idx}, Individual {ind_idx} ---")
    
    # 1. Extract Age
    # Assumption: age_matrix_vec[group_idx] is shape (Simulations, Individuals) or (Sim, Ind, Time)
    raw_age = age_matrix_vec[group_idx]
    if raw_age.ndim == 3:
        ind_age = raw_age[sim_idx, ind_idx, :]
    else:
        ind_age = raw_age[sim_idx, ind_idx]
    
    # 2. Extract BMI
    # Assumption: bmi_matrix_ls[group_idx] matches age structure
    raw_bmi = bmi_matrix_ls[group_idx]
    if raw_bmi.ndim == 3:
        ind_bmi = raw_bmi[sim_idx, ind_idx, :]
    else:
        ind_bmi = raw_bmi[sim_idx, ind_idx]
        
    # 3. Extract Albuminuria
    # Note: Loop used albu_mat_storage[idx][k, :, :] 
    # This implies albu_mat_storage[idx] is (Cases, Sim, Ind, Time) or (Cases, Ind, Time)
    raw_albu = albu_mat_storage[group_idx]
    # We need to handle if 'Sim' dimension exists in storage or if it broadcasts
    try:
        # Try accessing with Case and Sim
        ind_albu = raw_albu[case_idx, sim_idx, ind_idx, :] 
    except:
        # Fallback: Maybe structure is (Cases, Ind, Time) and it broadcasts over Sim
        ind_albu = raw_albu[case_idx, ind_idx, :]

    # 4. Extract Diabetes
    # Note: Loop used diabetes_mat_storage[idx]
    raw_diab = diabetes_mat_storage[group_idx]
    try:
        if raw_diab.ndim == 4: # (Cases, Sim, Ind, Time)
            ind_diab = raw_diab[case_idx, sim_idx, ind_idx, :]
        elif raw_diab.ndim == 3: # (Sim, Ind, Time) or (Cases, Ind, Time)
            # Hard to distinguish, but based on loop `diabetes_value` didn't use `k`, 
            # so likely (Sim, Ind, Time) or (Ind, Time)
            ind_diab = raw_diab[sim_idx, ind_idx, :]
        else:
            ind_diab = raw_diab[ind_idx, :]
    except:
         ind_diab = "Error extracting Diabetes (Check shape)"

    # 5. Extract Hypertension
    # Note: Loop used hypertension_mat_storage[idx]
    raw_hyper = hypertension_mat_storage[group_idx]
    try:
        if raw_hyper.ndim == 4:
            ind_hyper = raw_hyper[case_idx, sim_idx, ind_idx, :]
        elif raw_hyper.ndim == 3:
            ind_hyper = raw_hyper[sim_idx, ind_idx, :]
        else:
            ind_hyper = raw_hyper[ind_idx, :]
    except:
        ind_hyper = "Error extracting Hypertension (Check shape)"

    # Print Results
    print(f"Age (Sample): {ind_age}")
    print(f"BMI (Sample): {ind_bmi}")
    print(f"Albuminuria Trajectory: \n{ind_albu}")
    print(f"Diabetes Trajectory: \n{ind_diab}")
    print(f"Hypertension Trajectory: \n{ind_hyper}")
    
    return {
        "age": ind_age,
        "bmi": ind_bmi,
        "albu": ind_albu,
        "diabetes": ind_diab,
        "hypertension": ind_hyper
    }

# --- Execute for the problematic individual ---
# Based on your snippet: eGFR_matrix_ls[2][0][0] and index 20158
problem_data = extract_infor(group_idx=2, case_idx=0, sim_idx=0, ind_idx=20158)

# %%
problem_data = extract_infor(group_idx=2, case_idx=0, sim_idx=0, ind_idx=20790)
# %%
def extract_egfr_value(group_idx, case_idx, sim_idx, ind_idx):
    """
    Extracts the calculated eGFR trajectory for a specific individual.
    
    Parameters:
    - group_idx: Index for the eGFR_matrix_ls list (0-7)
    - case_idx: Index for the case/matrix (0-4)
    - sim_idx: Index for the simulation (0 corresponding to matrix dimension 0)
    - ind_idx: Index for the individual row (e.g., 20158)
    """
    try:
        # Access the specific matrix from the list
        # eGFR_matrix_ls[group] is shape (Cases, Simulations, Individuals, Time)
        target_matrix = eGFR_matrix_ls[group_idx]
        
        # Extract the specific trajectory
        # resulting shape should be (Time_Points,)
        egfr_trajectory = target_matrix[case_idx, sim_idx, ind_idx, :]
        
        print(f"--- eGFR Extraction: Group {group_idx}, Case {case_idx}, Sim {sim_idx}, Ind {ind_idx} ---")
        print(f"Shape: {egfr_trajectory.shape}")
        print(f"Trajectory values:\n{egfr_trajectory}")
        
        # Check for invalid values explicitly
        if np.any(egfr_trajectory == -1):
            print("\nWARNING: Contains -1 values (Masking/Initialization issue).")
            
        return egfr_trajectory

    except IndexError as e:
        print(f"Error: Index out of bounds. Check your inputs. ({e})")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

# --- Usage Example ---
# Extracting for the problematic individual you found
egfr_values = extract_egfr_value(group_idx=2, case_idx=0, sim_idx=0, ind_idx=20158)
# %%

import numpy as np

# Turn the provided numbers into a numpy array
egfr_arr = np.array([
    64.56977771, 63.8758092, 63.50339034, 63.29595582, 63.05910981, 62.89675571, 
    62.4411778, 62.08648585, 52.11531732, 51.68268633, 51.15274369, 50.45092559, 
    50.05540778, 49.27942426, 48.82464223, 47.86406969, 47.73334571
])

# Calculate the per-step changes for the first 5 and last 5 terms
first5_stepdiff = np.diff(egfr_arr[:5])
last5_stepdiff = np.diff(egfr_arr[-5:])

print("Array:", egfr_arr)
print("Difference (first 5 terms):", first5_stepdiff)
print("Difference (last 5 terms):", last5_stepdiff)
# %%



os.makedirs(f'../future_data_1990_2050/ckd_matrix/', exist_ok=True)
for i in range(8):
    np.save(f'../future_data_1990_2050/ckd_matrix/stage_mat_{i}.npy', stage_matrix_ls[i])
# %% analysis 

#%% Analysis: Average annual decrease by CKD stage

# Initialize dictionary to store sum of declines and count of observations for each stage
# Stages: 1, 2, 3.1 (3a), 3.2 (3b), 4, 5
stage_stats = {k: {'sum': 0.0, 'count': 0} for k in [1, 2, 3.1, 3.2, 4, 5]}

print("Calculating annual eGFR decline statistics...")

for group_idx in range(1):
    # Load data for the current group
    # Shape is (5, Individuals, Years)
    egfr_data = eGFR_matrix_ls[group_idx][[0, 4], 0, :,:]
    stage_data = stage_matrix_ls[group_idx][[0, 4], 0, :,:]
    
    # Ensure there is a time dimension to calculate difference
    if egfr_data.shape[-1] < 2:
        continue

    # 1. Calculate Annual Decline: eGFR(t) - eGFR(t+1)
    # Positive value indicates worsening kidney function
    # Negative value indicates improvement
    decline_matrix = egfr_data[:, :, :-1] - egfr_data[:, :, 1:]
    
    # 2. Identify Stage at start of the year (time t)
    current_stage_matrix = stage_data[:, :, :-1]
    
    # 3. Create Validity Mask
    # We must exclude data points where eGFR is -1 (missing/dead) in either current or next year
    # We assume -1 was used for invalid entries based on previous code blocks
    mask_valid = (egfr_data[:, :, :-1] != -1) & (egfr_data[:, :, 1:] != -1)
    
    # 4. Aggregate stats per stage
    for stage_val in stage_stats.keys():
        # Create mask: Where (Stage == stage_val) AND (Data is valid)
        # Using np.isclose in case of floating point minor differences, though direct equality usually works for assigned keys
        mask_stage = np.isclose(current_stage_matrix, stage_val) & mask_valid
        
        # Extract the decline values matching this stage
        valid_declines = decline_matrix[mask_stage]
        
        # Update accumulators
        if valid_declines.size > 0:
            stage_stats[stage_val]['sum'] += np.sum(valid_declines)
            stage_stats[stage_val]['count'] += valid_declines.size

# %% Report Results
print("\n=== Average Annual eGFR Decrease by Stage ===")
print("(Positive values = decline, Negative values = improvement)")
print(f"{'Stage':<10} | {'Avg Annual Decline (ml/min/1.73m^2)':<35} | {'N (Observations)'}")
print("-" * 65)

for stage_val in [1, 2, 3.1, 3.2, 4, 5]:
    stats = stage_stats[stage_val]
    if stats['count'] > 0:
        avg_decline = stats['sum'] / stats['count']
        print(f"{str(stage_val):<10} | {avg_decline:<35.4f} | {stats['count']}")
    else:
        print(f"{str(stage_val):<10} | {'No Data':<35} | 0")


# %% 
import pandas as pd
import numpy as np

# 1. Configuration
conditions = ['Healthy', 'Diabetes', 'Hypertension']
stages_list = [1, 2, 3.1, 3.2, 4, 5]

# Initialize storage: results[condition][stage] = [sum_decline, count]
# We use a nested dict for easy accumulation
stats_accumulator = {
    cond: {stage: {'sum': 0.0, 'count': 0} for stage in stages_list} 
    for cond in conditions
}

print("Starting aggregation across all cohorts...")

# 2. Iterate through cohorts (0-7)
for group_idx in range(8):
    # We focus on the baseline case (Case 0) and the first simulation (Sim 0)
    # You can wrap this in another loop if you want to average across simulations
    k_idx = 0 
    s_idx = 0 
    
    egfr_data = eGFR_matrix_ls[group_idx][k_idx, s_idx, :, :]
    stage_data = stage_matrix_ls[group_idx][k_idx, s_idx, :, :]
    
    # Extract condition matrices for this cohort
    # Handling potential dimension differences in your storage
    diab_mat = diabetes_mat_storage[group_idx]
    if diab_mat.ndim == 3: diab_mat = diab_mat[s_idx, :, :]
    
    hyper_mat = hypertension_mat_storage[group_idx]
    if hyper_mat.ndim == 3: hyper_mat = hyper_mat[s_idx, :, :]

    # Calculate Annual Decline: eGFR(t) - eGFR(t+1)
    # Positive = Decline (e.g., 90 -> 88 = 2.0 decline)
    decline_matrix = egfr_data[:, :-1] - egfr_data[:, 1:]
    
    # Align masks to the 't' index (the start of the year interval)
    mask_valid = (egfr_data[:, :-1] != -1) & (egfr_data[:, 1:] != -1)
    curr_stages = stage_data[:, :-1]
    curr_diab = diab_mat[:, :-1]
    curr_hyper = hyper_mat[:, :-1]

    for stage_val in stages_list:
        # Base mask: correct stage and valid data
        mask_base = np.isclose(curr_stages, stage_val) & mask_valid
        
        # Define condition masks
        # Healthy: No diabetes AND no hypertension
        mask_healthy = mask_base & (curr_diab == 0) & (curr_hyper == 0)
        # Diabetes: Any positive diabetes value
        mask_diabetes = mask_base & (curr_diab > 0)
        # Hypertension: Hypertension value present
        mask_hypertension = mask_base & (curr_hyper == 1)

        # Accumulate
        for cond_name, final_mask in zip(conditions, [mask_healthy, mask_diabetes, mask_hypertension]):
            valid_declines = decline_matrix[final_mask]
            if valid_declines.size > 0:
                stats_accumulator[cond_name][stage_val]['sum'] += np.sum(valid_declines)
                stats_accumulator[cond_name][stage_val]['count'] += valid_declines.size

# 3. Create the Final DataFrame
table_data = []
for cond in conditions:
    row = {'Status': cond}
    for stage in stages_list:
        total_sum = stats_accumulator[cond][stage]['sum']
        total_count = stats_accumulator[cond][stage]['count']
        # Calculate mean, handle division by zero
        mean_decline = total_sum / total_count if total_count > 0 else np.nan
        row[f'Stage {stage}'] = round(mean_decline, 3)
    table_data.append(row)

df_decline_summary = pd.DataFrame(table_data).set_index('Status')

print("\nAverage Annual eGFR Decrease (mL/min/1.73m² per year):")
print(df_decline_summary)

# %%
len(eGFR_matrix_ls)
# Only keep the last 8 elements of eGFR_matrix_ls
if len(eGFR_matrix_ls) > 8:
    eGFR_matrix_ls = eGFR_matrix_ls[-8:]

# %%
# RuntimeWarning: invalid value encountered in log
#   beta4 * np.log(bmi_values[:, :, t]) +
# %% 
### print out the drop
import pandas as pd
import numpy as np

# 1. Configuration for the categories
conditions = ['Neither', 'HTN', 'DM']
macro_albu_status = ['No macroalbuminuria', 'Macroalbuminuria']
egfr_thresholds = ['>=60', '<60']

# Initialize nested dictionary for accumulation
# Structure: results[DM/HTN][Macro][eGFR_Cat] = [sum_decline, count]
stats = {c: {m: {e: {'sum': 0.0, 'count': 0} for e in egfr_thresholds} for m in macro_albu_status} for c in conditions}

print("Aggregating decline data by status and albuminuria...")
for group_idx in range(8):
    # Base simulation indices
    k_idx, s_idx = 0, 0 
    
    egfr_data = eGFR_matrix_ls[group_idx][k_idx, s_idx, :, :]
    
    # Load Age matrix (n_sim, n_people, n_year)
    # We slice to match (n_people, n_year) for the specific sim
    age_mat = age_matrix_vec[group_idx]
    if age_mat.ndim == 4: # (n_albu, n_sim, n_people, n_year)
        age_mat = age_mat[0, s_idx, :, :]
    elif age_mat.ndim == 3: # (n_sim, n_people, n_year)
        age_mat = age_mat[s_idx, :, :]

    # Load covariate matrices
    diab_mat = diabetes_mat_storage[group_idx]
    if diab_mat.ndim == 3: diab_mat = diab_mat[s_idx, :, :]
    
    hyper_mat = hypertension_mat_storage[group_idx]
    if hyper_mat.ndim == 3: hyper_mat = hyper_mat[s_idx, :, :]
    
    albu_mat = albu_mat_storage[group_idx]
    if albu_mat.ndim == 4:
        albu_mat = albu_mat[k_idx, s_idx, :, :]
    else:
        albu_mat = albu_mat[k_idx, :, :]

    # Calculate Annual Decline (Year T - Year T+1)
    decline_matrix = egfr_data[:, :-1] - egfr_data[:, 1:]
    
    # --- MASKS ALIGNED TO START OF INTERVAL (Year T) ---
    mask_valid = (egfr_data[:, :-1] != -1) & (egfr_data[:, 1:] != -1)
    
    # NEW: Age Mask (Must be > 18 at the start of the interval)
    mask_age = (age_mat[:, :-1] > 18)
    
    curr_egfr = egfr_data[:, :-1]
    curr_albu = albu_mat[:, :-1]

    # Health status logic (Look-ahead to catch transitions)
    diab_start, diab_end = diab_mat[:, :-1], diab_mat[:, 1:]
    hyper_start, hyper_end = hyper_mat[:, :-1], hyper_mat[:, 1:]

    for cond in conditions:
        if cond == 'DM':
            # Credited to DM if status is 1 at start OR end
            mask_status = (diab_start > 0) | (diab_end > 0)
        elif cond == 'HTN':
            # Credited to HTN if HTN at start/end AND no DM in either
            has_htn = (hyper_start == 1) | (hyper_end == 1)
            has_dm  = (diab_start > 0) | (diab_end > 0)
            mask_status = has_htn & ~has_dm
        elif cond == 'Neither':
            # Strictly NO disease at both start and end
            mask_status = (diab_start == 0) & (diab_end == 0) & \
                          (hyper_start == 0) & (hyper_end == 0)

        for macro in macro_albu_status:
            mask_macro = (curr_albu == 2) if macro == 'Macroalbuminuria' else (curr_albu < 2)
            
            for ethresh in egfr_thresholds:
                mask_egfr = (curr_egfr >= 60) if ethresh == '>=60' else (curr_egfr < 60)
                
                # Combine all masks including the new age filter
                final_mask = mask_valid & mask_age & mask_status & mask_macro & mask_egfr
                
                valid_declines = decline_matrix[final_mask]
                if valid_declines.size > 0:
                    stats[cond][macro][ethresh]['sum'] += np.sum(valid_declines)
                    stats[cond][macro][ethresh]['count'] += valid_declines.size

# 2. Format into a DataFrame
final_rows = []
for cond in conditions:
    for macro in macro_albu_status:
        for ethresh in egfr_thresholds:
            s = stats[cond][macro][ethresh]
            mean_val = s['sum'] / s['count'] if s['count'] > 0 else np.nan
            final_rows.append({
                'DM/HTN Status': cond,
                'Albuminuria': macro,
                'Estimated GFR': ethresh,
                'Annual GFR Decrease': round(mean_val, 2)
            })

df_final = pd.DataFrame(final_rows)
# Optional: multi-index to look exactly like the screenshot
df_styled = df_final.set_index(['DM/HTN Status', 'Albuminuria', 'Estimated GFR'])
print(df_styled)
# %%
print("Unique values in diab_mat:", np.unique(diab_mat))
# %%
# # Print all eGFR values where stage_data is 5 (for this group)
# stage_5_mask = np.isclose(stage_data, 5)
# egfr_at_stage_5 = egfr_data[stage_5_mask]

# print(f"All eGFR values where stage == 5 for group {group_idx}:")
# print(egfr_at_stage_5)



# %%


# %%
# Configuration for the search
g_idx = 2  # Looking at group 2
c_idx = 0  # Case 0
s_idx = 0  # Simulation 0

# Get the relevant matrices for this group/sim
egfr_sample = eGFR_matrix_ls[g_idx][c_idx, s_idx, :, :]
albu_sample = albu_mat_storage[g_idx][c_idx, s_idx, :, :] if albu_mat_storage[g_idx].ndim == 4 else albu_mat_storage[g_idx][c_idx, :, :]
diab_sample = diabetes_mat_storage[g_idx][s_idx, :, :] if diabetes_mat_storage[g_idx].ndim == 3 else diabetes_mat_storage[g_idx]

# Logic: Find individuals who:
# 1. Have NO macroalbuminuria (albu < 2) across the trajectory
# 2. Have at least one point where eGFR < 60 (to see the 1.2x multiplier effect)
# 3. Filter by Diabetes status

# Mask for no macroalbuminuria (ever) and has dropped below 60
mask_no_macro = np.all(albu_sample < 2, axis=1)
mask_under_60 = np.any((egfr_sample < 60) & (egfr_sample != -1), axis=1)

# Subgroup A: With Diabetes (diab > 0)
idx_with_diab = np.where(mask_no_macro & mask_under_60 & np.any(diab_sample > 0, axis=1))[0]

# Subgroup B: Without Diabetes (diab == 0)
idx_without_diab = np.where(mask_no_macro & mask_under_60 & np.all(diab_sample == 0, axis=1))[0]

print(f"Found {len(idx_with_diab)} individuals WITH diabetes (No Macro, eGFR < 60)")
print(f"Found {len(idx_without_diab)} individuals WITHOUT diabetes (No Macro, eGFR < 60)")

# Show the first 5 indices for each
print("Indices (With Diab):", idx_with_diab[:5])
print("Indices (No Diab):", idx_without_diab[:5])

# %%
# Pick the first index from the 'without diabetes' list
if len(idx_without_diab) > 0:
    target_idx = idx_without_diab[0]
    print(f"\n--- INSPECTING NON-DIABETES CASE (Index {target_idx}) ---")
    data_no_diab = extract_infor(group_idx=g_idx, case_idx=c_idx, sim_idx=s_idx, ind_idx=target_idx)
    # Print the eGFR trajectory for the target individual
    egfr_row = eGFR_matrix_ls[g_idx][c_idx, s_idx, target_idx, :]
    print(f"eGFR trajectory for group {g_idx}, case {c_idx}, sim {s_idx}, individual {target_idx}:\n{egfr_row}")
    #egfr_vals = extract_egfr_value(group_idx=g_idx, case_idx=c_idx, sim_idx=s_idx, ind_idx=target_idx)


# %%

# Pick the first index from the 'with diabetes' list
if len(idx_with_diab) > 0:
    target_idx = idx_with_diab[1]
    print(f"\n--- INSPECTING DIABETES CASE (Index {target_idx}) ---")
    data_diab = extract_infor(group_idx=g_idx, case_idx=c_idx, sim_idx=s_idx, ind_idx=target_idx)
    egfr_row = eGFR_matrix_ls[g_idx][c_idx, s_idx, target_idx, :]
    print(f"eGFR trajectory for group {g_idx}, case {c_idx}, sim {s_idx}, individual {target_idx}:\n{egfr_row}")


# %%
BMI
39.8263665  39.80860073 40.26572449
 41.06484854 39.35150227 39.7219147  41.40646594 42.61219605 41.19678647
 41.70612735

73.38335314 73.10480884 64.91616887
 64.26557722 63.89839606 63.29460543 62.5444217  60.61810367 60.17328772
 59.51880224

0.5 0.5 1. 1.  1.  1.  1.  1.  1.  1

#%% Analysis: Extract Stage 4 Examples (Separately)

# stage_4_examples = []
# TARGET_STAGE = 4
# MAX_EXAMPLES = 50

# print(f"\nSearching for {MAX_EXAMPLES} examples of trajectories containing Stage {TARGET_STAGE}...")

# # --- PART 2: Extract Examples ---
# # We iterate through groups again specifically to find examples
# for group_idx in range(8):
#     if len(stage_4_examples) >= MAX_EXAMPLES:
#         break
    
#     # Use Case 0 data
#     egfr_data = eGFR_matrix_ls[group_idx][0]
#     stage_data = stage_matrix_ls[group_idx][0]
    
#     # Boolean mask of where stage is 4 (ignoring -1s implicitly as they won't match 4)
#     # We want individuals who HIT stage 4 at any point
#     is_target_stage = np.isclose(stage_data, TARGET_STAGE)
    
#     # Find indices of rows (individuals) that have at least one True in is_target_stage
#     rows_with_stage = np.any(is_target_stage, axis=1)
#     individual_indices = np.where(rows_with_stage)[0]
    
#     for idx in individual_indices:
#         if len(stage_4_examples) >= MAX_EXAMPLES:
#             break
            
#         # Extract the full eGFR trajectory
#         traj = egfr_data[idx, :]
        
#         # Filter out -1 padding for cleaner display
#         valid_traj = traj[traj != -1]
        
#         # Store as (Group, Index, Trajectory)
#         stage_4_examples.append((group_idx, idx, valid_traj))

# # --- Report Examples ---
# print(f"\n=== Inspection: {len(stage_4_examples)} Trajectories containing Stage 4 ===")
# print("Format: [Year 0, Year 1, ...]")
# print("-" * 65)

# if len(stage_4_examples) == 0:
#     print("No Stage 4 trajectories found.")
# else:
#     for i, (grp, idx, traj) in enumerate(stage_4_examples):
#         # Format numbers to 2 decimal places
#         traj_str = ", ".join([f"{x:.2f}" for x in traj])
#         print(f"#{i+1:02d} (Grp {grp}, ID {idx}): [{traj_str}]")
# # %%


# %% 
# %% 
### print out the drop
import pandas as pd
import numpy as np

# 1. Configuration for the categories
conditions = ['Neither', 'HTN', 'DM']
macro_albu_status = ['No macroalbuminuria', 'Macroalbuminuria']
egfr_thresholds = ['>=60', '<60']

# Initialize nested dictionary for accumulation
# Structure: results[DM/HTN][Macro][eGFR_Cat] = [sum_decline, count]
stats = {c: {m: {e: {'sum': 0.0, 'count': 0} for e in egfr_thresholds} for m in macro_albu_status} for c in conditions}

print("Aggregating decline data by status and albuminuria...")


for group_idx in range(8):
    # Base simulation indices
    k_idx, s_idx = 0, 0 
    
    egfr_data = eGFR_matrix_ls[group_idx][k_idx, s_idx, :, :]
    
    # Load covariate matrices
    diab_mat = diabetes_mat_storage[group_idx]
    if diab_mat.ndim == 3: diab_mat = diab_mat[s_idx, :, :]
    
    hyper_mat = hypertension_mat_storage[group_idx]
    if hyper_mat.ndim == 3: hyper_mat = hyper_mat[s_idx, :, :]
    
    albu_mat = albu_mat_storage[group_idx]
    # Handle albu_mat dimensions (Cases, Sim, Ind, Time) vs (Cases, Ind, Time)
    if albu_mat.ndim == 4:
        albu_mat = albu_mat[k_idx, s_idx, :, :]
    else:
        albu_mat = albu_mat[k_idx, :, :]

    # Calculate Annual Decline (Year T - Year T+1)
    decline_matrix = egfr_data[:, :-1] - egfr_data[:, 1:]
    
    # 1. Temporal Alignment for Masks
    mask_valid = (egfr_data[:, :-1] != -1) & (egfr_data[:, 1:] != -1)
    curr_egfr = egfr_data[:, :-1]
    curr_albu = albu_mat[:, :-1]

    # Look at both current (T) and future (T+1) status
    diab_start = diab_mat[:, :-1]
    diab_end   = diab_mat[:, 1:]
    hyper_start = hyper_mat[:, :-1]
    hyper_end   = hyper_mat[:, 1:]

    for cond in conditions:
        # 2. UPDATED Health Status Logic
        if cond == 'DM':
            # Credited to DM if status is 1 at start OR end of the year
            has_dm  = (diab_start == 1) | (diab_end == 1)
            mask_status = has_dm
            
        elif cond == 'HTN':
            # Credited to HTN if status is 1 at start OR end, AND no DM in either
            has_htn = (hyper_start == 1) | (hyper_end == 1)
            #has_dm  = (diab_start > 0) | (diab_end > 0)
            # & ~has_dm
            mask_status = has_htn 
            
        elif cond == 'Neither':
            # Strictly NO disease at the start AND NO disease at the end
            # This automatically excludes the transition year
            mask_status = (diab_start == 0) & (diab_end == 0) & \
                          (hyper_start == 0) & (hyper_end == 0)

        for macro in macro_albu_status:
            mask_macro = (curr_albu == 2) if macro == 'Macroalbuminuria' else (curr_albu < 2)
            
            for ethresh in egfr_thresholds:
                mask_egfr = (curr_egfr >= 60) if ethresh == '>=60' else (curr_egfr < 60)
                
                # Combine all masks
                final_mask = mask_valid & mask_status & mask_macro & mask_egfr
                
                valid_declines = decline_matrix[final_mask]
                if valid_declines.size > 0:
                    stats[cond][macro][ethresh]['sum'] += np.sum(valid_declines)
                    stats[cond][macro][ethresh]['count'] += valid_declines.size


# 2. Format into a DataFrame
final_rows = []
for cond in conditions:
    for macro in macro_albu_status:
        for ethresh in egfr_thresholds:
            s = stats[cond][macro][ethresh]
            mean_val = s['sum'] / s['count'] if s['count'] > 0 else np.nan
            final_rows.append({
                'DM/HTN Status': cond,
                'Albuminuria': macro,
                'Estimated GFR': ethresh,
                'Annual GFR Decrease': round(mean_val, 2)
            })

df_final = pd.DataFrame(final_rows)
# Optional: multi-index to look exactly like the screenshot
df_styled = df_final.set_index(['DM/HTN Status', 'Albuminuria', 'Estimated GFR'])
print(df_styled)
# %%
