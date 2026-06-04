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
# %% 
# for i in range(8):
#     np.save(f'../future_data_1990_2050/ckd_matrix/stage_mat_{i}.npy', stage_matrix_ls[i])
# # %%

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



# %% albu values are 0,1,2
if np.max(albu_mat_storage[0]) == 2:
    print("correct")

# %% diabetes values are 0.0.5,1
if np.max(diabetes_mat[0]) == 1:
    print("correct")

# %%
age_matrix_vec[0].shape

# %% 

#%%
# Check unique values for diabetes_mat_storage[0] and hypertension_mat_storage[0]
print("Unique values in diabetes_mat_storage[0]:", np.unique(diabetes_mat_storage[0]))
print("Unique values in hypertension_mat_storage[0]:", np.unique(hypertension_mat_storage[0]))

# %%
for idx in range(8):
    eth = map_eth_str(idx)
    beta0, beta1, beta2, beta3, beta4, sigma = coefficients[eth]
    print(f"eth={idx} ({eth}): beta0={beta0}, beta1={beta1}, beta2={beta2}, beta3={beta3}, beta4={beta4}, sigma={sigma}")

# %% adherence matrix
import numpy as np

# Sigmoid parameters derived from the fit
L, k, x0, b = 27.55, 0.32, 45.19, 57.52
ethnicity_factors = [58.7/60.4, 66.0/60.4, 64.9/60.4] # [Chinese, Malay, Indian]

# Create a 2D matrix (83 ages x 3 ethnicities)
# To make it 3D as requested, we could add a dimension for [Good Rate, Poor Rate]
# matrix[age_idx][eth_idx][0] = Good Rate
# matrix[age_idx][eth_idx][1] = Poor Rate
adherence_matrix = np.zeros((83, 3, 2))

for age in range(18, 101):
    age_idx = age - 18
    base_poor = L / (1 + np.exp(k * (age - x0))) + b
    
    for eth_idx, factor in enumerate(ethnicity_factors):
        poor_rate = base_poor * factor
        good_rate = 100 - poor_rate
        
        adherence_matrix[age_idx, eth_idx, 0] = round(good_rate, 2)
        adherence_matrix[age_idx, eth_idx, 1] = round(poor_rate, 2)

# %% 
# Accessing the value
age = 45
eth_map = {'Chinese': 0, 'Malay': 1, 'Indian': 2}
val = adherence_matrix[age - 18, eth_map['Indian'], 0]

print(f"Good Control Rate for a {age} year old Indian: {val}%")


# %% 

eGFR_matrix_ls = []

# --- 1. PRE-CALCULATE GLOBAL RANDOMNESS (Crucial for Speed) ---
# We generate all random rolls for the entire simulation upfront.
# Assuming n_years is the length of your time dimension.


# Roll for detection: 8 ethnicities, 2 albuminuria cases (0 and 4)

eGFR_matrix_ls = []

for idx in range(8):
    case_matrices = []
    
    # --- PRE-CALCULATE CONSTANTS ---
    eth = map_eth_str(idx)
    gender2 = idx % 2
    beta0, beta1, beta2, beta3, beta4, sigma = coefficients[eth]
    
    # BMI and Comorbidity matrices (Yearly/Static)
    bmi_values = bmi_matrix_ls[idx]
    diabetes_value = diabetes_mat_storage[idx]
    hypertension_value = hypertension_mat_storage[idx]
    
    # Comorbidity coefficients
    diab_coeff = np.where(diabetes_value == 0.5, 0.5, np.where(diabetes_value == 1, 1., 0))
    hyp_coeff = 0.1
    
    # Fixed drop rates for Macro-Drop
    is_dm = (diabetes_value > 0)
    is_htn = (hypertension_value == 1) & (diabetes_value == 0)
    macro_dec_rate = np.where(is_dm, 5.2, np.where(is_htn, 4.2, 3.9))

    # people's age matrix
    current_age_mat = age_matrix_vec[idx]
    n_sim, n_people, n_years = current_age_mat.shape 
    
    

    for k_idx, k in enumerate([0, 4]):
        matrix = age_matrix_vec[idx]
        albu_value = albu_mat_storage[idx][k, :, :] 
        
        # 1. Base Trajectory (Standard Age-based path)
        valid_mask = (bmi_values > 0)
        safe_bmi = np.where(valid_mask, bmi_values, 1.0)
        albu_coeff = np.where(albu_value == 1, 0.1, np.where(albu_value == 2, 0.5, 0))

        eGFR_final = np.full((n_sim, n_people, n_years), -1.0)
        is_detected = np.zeros((n_sim, n_people), dtype=bool)
        
        # 4. GENERATE random rolls for this specific population size
        rolls = np.random.rand(n_sim, n_people, n_years)
        
        # Row-specific noise
        row_noise = np.random.normal(loc=0, scale=sigma, size=(n_sim, n_people, 1))

        # Vectorized base calculation
        base_egfr = (
            beta0 +
            beta1 * matrix * 0.5 +
            beta2 * gender2 +
            beta3 * matrix * gender2 * 0.5 +
            beta4 * np.log(safe_bmi) +
            beta1 * matrix * hyp_coeff * hypertension_value + 
            beta1 * matrix * diab_coeff * diabetes_value + 
            beta1 * matrix * albu_coeff * albu_value +
            row_noise 
        )

        # 2. Setup for Iterative Years
        eGFR_final = np.full((n_sim, n_people, n_years), -1.0)

        # Year 0 Initial State
        comorbidity_impact = (
            beta1 * matrix[:, :, [0]] * hyp_coeff * hypertension_value[:, :, [0]] + 
            beta1 * matrix[:, :, [0]] * diab_coeff * diabetes_value[:, :, [0]] + 
            beta1 * matrix[:, :, [0]] * albu_coeff[:, :, [0]] * albu_value[:, :, [0]]
        )
        mult_mask = (albu_value[:, :, [0]] < 2) & (base_egfr[:, :, [0]] < 60)
        final_impact = np.where(mult_mask, comorbidity_impact * 0.2, 0)
        
        eGFR_final[:, :, 0] = np.where(valid_mask[:, :, 0], (base_egfr[:, :, 0] + final_impact[:, :, 0]), -1.0)

        # --- THE YEARLY LOOP (Detection and Decline) ---
        for t in range(n_years):
            curr_egfr = eGFR_final[:, :, t]
            curr_alive = valid_mask[:, :, t]
            
            # A. Hospital Detection Logic
            not_detected_yet = ~is_detected & curr_alive
            if np.any(not_detected_yet):
                p = np.zeros_like(curr_egfr)
                # Apply stage-based probabilities
                p[curr_egfr < 15] = 0.95                                     # Stage 5
                p[(curr_egfr >= 15) & (curr_egfr < 30)] = 0.32                # Stage 4
                p[(curr_egfr >= 30) & (curr_egfr < 60)] = 0.07                # Stage 3
                p[(curr_egfr >= 60) & (albu_value[:, :, t] >= 1)] = 0.05      # Stage 1-2
                
                # Update status: once True, stays True
                is_detected |= (rolls[:, :, t] < p)

            # B. Calculate Decline for Next Year
            if t < n_years - 1:
                # 1. Identify populations
                is_alive_now = (eGFR_final[:, :, t] != -1.0)
                is_alive_next = valid_mask[:, :, t+1]
                new_entrants = is_alive_next & ~is_alive_now
                
                # 2. Determine Natural Decline (Standard logic)
                is_macro_next = (albu_value[:, :, t+1] == 2)
                under_60_now = (curr_egfr < 60)
                natural_decline = np.where(
                    (is_macro_next & under_60_now),
                    macro_dec_rate[:, :, t+1],
                    (base_egfr[:, :, t] - base_egfr[:, :, t+1])
                )

                # --- NEW ADHERENCE LOGIC ---
                # 1. Get column index for ethnicity (0: Chinese, 1: Malay, 2: Indian)
                # use malay to have others
                eth_col = idx // 2
                if eth_col == 3:
                    eth_col = 2
                # 2. Extract current ages and map to matrix rows (18-100 -> 0-82)
                # We clip to ensure we don't go out of bounds if age > 100
                age_at_t = current_age_mat[:, :, t].astype(int)
                age_indices = np.clip(age_at_t - 18, 0, 82)
                
                # 3. Pull adherence rates for these specific ages and ethnicity
                # adherence_matrix shape is (83, 3)
                current_adherence_probs = adherence_matrix[age_indices, eth_col,0] / 100.0
                
                # 4. Determine if the patient follows doctor's instructions this year
                # Note: We use a separate roll or a specific slice of your rolls matrix
                followed_instructions = (rolls[:, :, t] < current_adherence_probs)
                
                # 5. Apply Hospital Benefit ONLY if Detected AND Followed Instructions
                has_benefit = is_detected & followed_instructions
                actual_decline = np.where(has_benefit, natural_decline * 0.6, natural_decline)
                
                # --- End of Adherence Logic ---

                # 4. Final Update Logic
                next_val = np.where(
                    new_entrants, 
                    base_egfr[:, :, t+1], 
                    curr_egfr - actual_decline
                )
                
                eGFR_final[:, :, t+1] = np.where(is_alive_next, next_val, -1.0)

        case_matrices.append(eGFR_final)
    
    eGFR_matrix_ls.append(np.array(case_matrices))
# %%
# for name, arr in [
#     ("matrix", matrix), ("bmi", safe_bmi), 
#     ("diabetes", diabetes_value), ("hypertension", hypertension_value),
#     ("albu", albu_value), ("noise", row_noise)
# ]:
#     print(f"{name} shape: {arr.shape}")
# %%

for i in range(8):
    np.save(f'../future_data_1990_2050/ckd_matrix/eGFR_hospital_adherence_{i}.npy', eGFR_matrix_ls[i])

# %%

