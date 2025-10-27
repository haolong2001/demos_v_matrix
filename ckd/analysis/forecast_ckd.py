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

#%% check if albu matrix is correct
if np.max(albu_mat_storage[0]) != 2:
    for i in range(len(albu_mat_storage)):
        albu_mat_storage[i] = albu_mat_storage[i] * 2

#%%
# Check unique values for diabetes_mat_storage[0] and hypertension_mat_storage[0]
print("Unique values in diabetes_mat_storage[0]:", np.unique(diabetes_mat_storage[0]))
print("Unique values in hypertension_mat_storage[0]:", np.unique(hypertension_mat_storage[0]))

#%% begin 
import numpy as np

eGFR_matrix_ls = []  # List to store eGFR matrices

for idx in range(8):
  # Iterate over the five cases (k=0 to 4)
    case_matrices = []  # Store matrices for this case
    for i, k in enumerate(range(5)):  # k from 0 to 4
        # Extract age matrix for this index
        matrix = age_matrix_vec[idx]  # Contains age values
        bmi_values = bmi_matrix_ls[idx]  # Corresponding BMI values
        albu_value = albu_mat_storage[idx][k, :, :] 
        diabetes_value = diabetes_mat_storage[idx]
        hypertension_value = hypertension_mat_storage[idx]
        
        eGFR_matrix = np.zeros_like(matrix, dtype=float)
        
        # Get ethnicity and gender
        eth = map_eth_str(idx)  # 'chn', 'ind', or 'mal'
        gender2 = idx % 2  # 0 for Male, 1 for Female

        # Extract coefficients for the ethnicity
        beta0, beta1, beta2, beta3, beta4, sigma = coefficients[eth]
        
        # Generate noise
        row_noise = np.random.normal(loc=0, scale=sigma, size=matrix.shape)
        
        # Compute coefficients based on conditions
        diabetes_coefficient = np.where(diabetes_value == 0.5, 0.5, np.where(diabetes_value == 1, 1., 0))
        albu_coefficient = np.where(albu_value == 1, 0.1, np.where(albu_value == 2, 0.5, 0))
        hypertension_coefficient = 0.1

        # Compute eGFR values
        eGFR_matrix = (
            beta0 +
            beta1 * matrix * 0.5 +  # Age contribution
            beta2 * gender2 +  # Gender contribution
            beta3 * matrix * gender2 * 0.5 +  # Age * Gender interaction
            beta4 * np.log(bmi_values) +  # BMI contribution
            beta1 * matrix * hypertension_coefficient * hypertension_value + 
            beta1 * matrix * diabetes_coefficient * diabetes_value + 
            beta1 * matrix * albu_coefficient * albu_value + 
            row_noise  # Random noise
        )
        
        # Replace invalid age values with -1 in eGFR matrix
        eGFR_matrix[matrix == -1] = -1
        
        case_matrices.append(eGFR_matrix)
    case_matrices = np.array(case_matrices)
    
    eGFR_matrix_ls.append(case_matrices)

# Convert list to a NumPy array for better structure


# Display the resulting eGFR matrix
print("eGFR Matrix:")
print(eGFR_matrix_ls[0][0,:,:])

#%% define stages
stages = {
    1: lambda x: x > 90,
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

#%% save stage matrix

# create directory
os.makedirs(f'../future_data_1990_2050/ckd_matrix/', exist_ok=True)
for i in range(8):
    np.save(f'../future_data_1990_2050/ckd_matrix/stage_mat_{i}.npy', stage_matrix_ls[i])
#%% load stage matrix
stage_matrix_ls = [0 for i in range(8)]
for i in range(8):
    stage_matrix_ls[i] = np.load(f'../future_data_1990_2050/ckd_matrix/stage_mat_{i}.npy')
    print(f"Loaded: stage_mat_{i}.npy with shape {stage_matrix_ls[i].shape}")
#%% get 2022 stage table; print out stage 1, 2, 3.1, 3.2, 4, 5


for i in range(8):
    print(f"Stage 1: {np.sum(stage_matrix_ls[i] == 1)}")
    print(f"Stage 2: {np.sum(stage_matrix_ls[i] == 2)}")
    print(f"Stage 3.1: {np.sum(stage_matrix_ls[i] == 3.1)}")
    print(f"Stage 3.2: {np.sum(stage_matrix_ls[i] == 3.2)}")
    print(f"Stage 4: {np.sum(stage_matrix_ls[i] == 4)}")
    print(f"Stage 5: {np.sum(stage_matrix_ls[i] == 5)}")




#%%

# Create general CKD matrix based on age, albumin (ACR), and stage matrices
general_ckd_mat_ls = []

for i in range(8):  # For each ethnicity group
    # Get the matrices for this ethnicity
    stage_matrix = stage_matrix_ls[i]
    acr_matrix = albu_mat_storage[i]
    age_matrix = age_matrix_vec[i]
    
    # Initialize CKD matrix with same shape as stage matrix
    ckd_matrix = np.zeros_like(stage_matrix, dtype=int)
    
    # Check if healthy (stage <= 2 AND ACR = 0)
    healthy_mask = (stage_matrix <= 2) & (acr_matrix == 0)
    ckd_matrix[healthy_mask] = 0
    
    # Otherwise unhealthy (CKD) - everything else that's not healthy
    unhealthy_mask = (~healthy_mask)
    ckd_matrix[unhealthy_mask] = 1
    
    general_ckd_mat_ls.append(ckd_matrix)
    print(f"Created CKD matrix for ethnicity {i} with shape {ckd_matrix.shape}")

print(f"Completed creation of general_ckd_mat_ls with {len(general_ckd_mat_ls)} ethnicity groups")





#%%

#%% 
print(age_matrix_vec[0].shape)
print(general_ckd_mat_ls[0].shape)

# 检查 general_ckd_mat_ls[0] 的唯一值
unique_vals = np.unique(general_ckd_mat_ls[0])
print(f"Unique values in general_ckd_mat_ls[0]: {unique_vals}")


#%% check prevalenceimport numpy as np
import pandas as pd

def simulate_ckd_prevalence(age_matrix_vec, ckd_mat_list, ckd_level=1):
    """
    Compute CKD prevalence across simulations, years, subgroups, and age groups.

    Parameters:
        age_matrix_vec (list): list of age matrices, each of shape (n_sims, n_persons, n_years)
        ckd_mat_list (list): list of CKD status matrices, each of shape (n_outer, n_sims, n_persons, n_years)
                             where n_outer is an extra dimension (e.g., 5), always one more than age_matrix_vec.
        ckd_level (int): Value representing CKD presence (default=1).

    Returns:
        pd.DataFrame: Prevalence results with columns:
                      year, sim, overall, male, female, chinese, malay, indian, (18,29), ...
    """
    import numpy as np
    import pandas as pd

    # Example:
    # age_matrix_vec[0].shape == (10, 103903, 61)
    # ckd_mat_list[0].shape == (5, 10, 103903, 61)

    age_groups = [(18, 29), (30, 39), (40, 49), (50, 59), (60, 69), (70, 79), (80, 200)]
    n_groups = len(age_matrix_vec)

    # Index sets (assumes fixed order of 8 groups)
    male_idx = [0, 2, 4, 6]
    female_idx = [1, 3, 5, 7]
    chinese_idx = [0, 1]
    malay_idx = [2, 3]
    indian_idx = [4, 5]

    n_albu, n_sims, _, n_years = ckd_mat_list[0].shape


    records = []
    # print("test")
    # n_albu = 5
    # n_sims = 10
    for albu in range(n_albu):
        for sim in range(n_sims):
            # Prepare storage for all years at once
            total_people = np.zeros((n_groups, n_years))
            total_ckd = np.zeros((n_groups, n_years))
            age_totals = np.zeros((n_groups, len(age_groups), n_years))
            age_ckd = np.zeros((n_groups, len(age_groups), n_years))

            for g in range(n_groups):
                ages = age_matrix_vec[g][sim, :, :]  # shape: (n_persons, n_years)
                ckd_status = ckd_mat_list[g][albu, sim, :, :]  # shape: (n_persons, n_years)

                mask_all = (ages >= 18) & (ages <= 200)  # shape: (n_persons, n_years)
                total_people[g, :] = np.sum(mask_all, axis=0)
                # print("total_people", total_people[g, :])
                ckd_mask = (ckd_status == ckd_level) & mask_all  # shape: (n_persons, n_years)
                total_ckd[g, :] = np.sum(ckd_mask, axis=0)
                # print("total_ckd", total_ckd[g, :])
                for a_idx, (lower, upper) in enumerate(age_groups):
                    mask = (ages >= lower) & (ages <= upper)
                    age_totals[g, a_idx, :] = np.sum(mask, axis=0)
                    age_ckd_mask = (ckd_status == ckd_level) & mask
                    age_ckd[g, a_idx, :] = np.sum(age_ckd_mask, axis=0)

            # Vectorized calculation for all years at once
            total_people_sum = total_people.sum(axis=0)
            total_ckd_sum = total_ckd.sum(axis=0)

            male_people = total_people[male_idx, :].sum(axis=0)
            male_ckd = total_ckd[male_idx, :].sum(axis=0)
            female_people = total_people[female_idx, :].sum(axis=0)
            female_ckd = total_ckd[female_idx, :].sum(axis=0)

            chinese_people = total_people[chinese_idx, :].sum(axis=0)
            chinese_ckd = total_ckd[chinese_idx, :].sum(axis=0)
            malay_people = total_people[malay_idx, :].sum(axis=0)
            malay_ckd = total_ckd[malay_idx, :].sum(axis=0)
            indian_people = total_people[indian_idx, :].sum(axis=0)
            indian_ckd = total_ckd[indian_idx, :].sum(axis=0)

            # Age-specific prevalence (shape: [len(age_groups), n_years])
            age_totals_sum = age_totals.sum(axis=0)
            age_ckd_sum = age_ckd.sum(axis=0)

            for year in range(n_years):
                record = {
                    "albu": albu,
                    "year": 1990 + year,
                    "sim": sim,
                    "overall": (total_ckd_sum[year] / total_people_sum[year]) if total_people_sum[year] > 0 else 0,
                    "male": (male_ckd[year] / male_people[year]) if male_people[year] > 0 else 0,
                    "female": (female_ckd[year] / female_people[year]) if female_people[year] > 0 else 0,
                    "chinese": (chinese_ckd[year] / chinese_people[year]) if chinese_people[year] > 0 else 0,
                    "malay": (malay_ckd[year] / malay_people[year]) if malay_people[year] > 0 else 0,
                    "indian": (indian_ckd[year] / indian_people[year]) if indian_people[year] > 0 else 0,
                }
                for a_idx, age_range in enumerate(age_groups):
                    den = age_totals_sum[a_idx, year]
                    num = age_ckd_sum[a_idx, year]

                    record[str(age_range)] = num / den if den > 0 else 0

                records.append(record)

    return pd.DataFrame(records)



#%% 
import numpy as np
import pandas as pd

def simulate_age_stratified_ckd_prevalence(age_matrix_vec, ckd_mat_list, ckd_level=1):
    """
    Compute age-specific CKD prevalence for (18–39), (40–54), (55–69), (70–74).

    Parameters:
        age_matrix_vec (list): list of age matrices, each of shape (n_sims, n_persons, n_years)
        ckd_mat_list (list): list of CKD status matrices, each of shape (n_outer, n_sims, n_persons, n_years)
        ckd_level (int): Value representing CKD presence (default=1)

    Returns:
        pd.DataFrame: columns = [albu, year, sim, (18,39), (40,54), (55,69), (70,74)]
    """

    age_groups = [(18, 39), (40, 54), (55, 69), (70, 74)]

    n_groups = len(age_matrix_vec)
    n_albu, n_sims, _, n_years = ckd_mat_list[0].shape

    records = []

    for albu in range(n_albu):
        for sim in range(n_sims):
            # containers for total counts
            age_totals = np.zeros((n_groups, len(age_groups), n_years))
            age_ckd = np.zeros((n_groups, len(age_groups), n_years))

            for g in range(n_groups):
                ages = age_matrix_vec[g][sim, :, :]              # (n_persons, n_years)
                ckd_status = ckd_mat_list[g][albu, sim, :, :]    # (n_persons, n_years)

                for a_idx, (lower, upper) in enumerate(age_groups):
                    mask = (ages >= lower) & (ages <= upper)
                    age_totals[g, a_idx, :] = np.sum(mask, axis=0)
                    age_ckd[g, a_idx, :] = np.sum((ckd_status == ckd_level) & mask, axis=0)

            # Sum across population subgroups
            age_totals_sum = age_totals.sum(axis=0)
            age_ckd_sum = age_ckd.sum(axis=0)

            for year in range(n_years):
                record = {
                    "albu": albu,
                    "year": 1990 + year,
                    "sim": sim
                }
                for a_idx, age_range in enumerate(age_groups):
                    den = age_totals_sum[a_idx, year]
                    num = age_ckd_sum[a_idx, year]
                    record[str(age_range)] = num / den if den > 0 else 0

                records.append(record)

    return pd.DataFrame(records)

#%% run it 

df_age_strat = simulate_age_stratified_ckd_prevalence(age_matrix_vec, general_ckd_mat_ls)

#%% 


#%% overall ckd prevalence with healthy/ diabetes/ hypertension

import pandas as pd
import numpy as np

def simulate_overall_ckd_prevalence(
    age_matrix_vec,
    ckd_mat_list,
    hypertension_mat_storage=None,
    diabetes_mat_storage=None,
    ckd_level=1,
    hypertension_only=False,
    diabetes_only=False
):
    """
    Compute overall CKD prevalence (optionally restricted to hypertensive or diabetic CKD)
    across simulations, years, and outer iterations.

    Parameters:
        age_matrix_vec (list): list of age matrices, each (n_sims, n_persons, n_years)
        ckd_mat_list (list): list of CKD status matrices, each (n_outer, n_sims, n_persons, n_years)
        hypertension_mat_storage (list): list of hypertension matrices, each (n_sims, n_persons, n_years)
        diabetes_mat_storage (list): list of diabetes matrices, each (n_sims, n_persons, n_years)
        ckd_level (int): Value representing CKD presence (default=1)
        hypertension_only (bool): If True, include only individuals with hypertension == 1
        diabetes_only (bool): If True, include only individuals with diabetes == 1

    Returns:
        pd.DataFrame: columns = [albu, year, sim, overall]
    """

    n_groups = len(age_matrix_vec)
    n_albu, n_sims, _, n_years = ckd_mat_list[0].shape

    records = []

    for albu in range(n_albu):
        for sim in range(n_sims):
            total_people = np.zeros((n_groups, n_years))
            total_ckd = np.zeros((n_groups, n_years))

            for g in range(n_groups):
                ages = age_matrix_vec[g][sim, :, :]                # (n_persons, n_years)
                ckd_status = ckd_mat_list[g][albu, sim, :, :]      # (n_persons, n_years)

                # Optional disease masks
                hyper_mask = hypertension_mat_storage[g][sim, :, :] == 1 if hypertension_mat_storage is not None else np.ones_like(ckd_status, dtype=bool)
                diab_mask = diabetes_mat_storage[g][sim, :, :] == 1 if diabetes_mat_storage is not None else np.ones_like(ckd_status, dtype=bool)

                # Apply conditions
                mask_all = (ages >= 18) & (ages <= 200)

                # Apply filters if needed
                if hypertension_only:
                    mask_all &= hyper_mask
                if diabetes_only:
                    mask_all &= diab_mask

                total_people[g, :] = np.sum(mask_all, axis=0)

                ckd_mask = (ckd_status == ckd_level) & mask_all
                total_ckd[g, :] = np.sum(ckd_mask, axis=0)

            total_people_sum = total_people.sum(axis=0)
            total_ckd_sum = total_ckd.sum(axis=0)

            for year in range(n_years):
                record = {
                    "albu": albu,
                    "year": 1990 + year,
                    "sim": sim,
                    "overall": (total_ckd_sum[year] / total_people_sum[year])
                    if total_people_sum[year] > 0 else 0
                }
                records.append(record)

    return pd.DataFrame(records)


# Overall CKD (age_matrix_vec, general_ckd_mat_ls)
df_all = simulate_overall_ckd_prevalence(age_matrix_vec, general_ckd_mat_ls)

# Hypertensive CKD only
df_hyper = simulate_overall_ckd_prevalence(age_matrix_vec, general_ckd_mat_ls,
                                   hypertension_mat_storage=hypertension_mat_storage,
                                   hypertension_only=True)

# Diabetic CKD only
df_diab = simulate_overall_ckd_prevalence(age_matrix_vec, general_ckd_mat_ls,
                                  diabetes_mat_storage=diabetes_mat_storage,
                                  diabetes_only=True)

#%% print the values
print("Overall CKD prevalence (all):")
print(df_all)

print("\nHypertensive CKD prevalence only:")
print(df_hyper)

print("\nDiabetic CKD prevalence only:")
print(df_diab)



#%% 
def summarize_ckd_with_indicator(df_hyper, df_diab, col='overall'):
    """
    Combine hypertensive and diabetic CKD results into one DataFrame
    with mean and 95% CI by year, and an indicator column.
    """
    def compute_summary(df, indicator):
        years = sorted(df['year'].unique())
        return pd.DataFrame({
            'year': years,
            'mean': [df.loc[df['year']==y, col].mean() for y in years],
            'lower': [df.loc[df['year']==y, col].quantile(0.025) for y in years],
            'upper': [df.loc[df['year']==y, col].quantile(0.975) for y in years],
            'indicator': indicator
        })

    df1 = compute_summary(df_hyper, 'hyper')
    df2 = compute_summary(df_diab, 'diab')

    return pd.concat([df1, df2], ignore_index=True)

df_summary = summarize_ckd_with_indicator(df_hyper, df_diab)

#%%
df_summary.to_csv('results_df/hyper_diab_ckd_prevalence_summary.csv', index=False)



#%%
df_summary[df_summary['year'].between(2017, 2024)]

#%%

# import numpy as np
# import pandas as pd

# def simulate_ckd_prevalence_vec(age_matrix_vec, ckd_mat_list, ckd_level=1, start_year=1990):
#     """
#     Vectorized CKD prevalence computation across simulations, years, subgroups, and age groups.

#     Parameters:
#         age_matrix_vec : list of np.ndarray
#             Each element shape (n_sims, n_persons, n_years)
#         ckd_mat_list : list of np.ndarray
#             Each element shape (n_albu, n_sims, n_persons, n_years)
#         ckd_level : int
#             Value representing CKD presence (default=1)
#         start_year : int
#             First year of the simulation (default=1990)

#     Returns:
#         pd.DataFrame
#     """
#     age_groups = [(18, 29), (30, 39), (40, 49), (50, 59), (60, 69), (70, 79), (80, 200)]
#     n_groups = len(age_matrix_vec)
    
#     # Index sets (assumes fixed order of 8 groups)
#     male_idx = [0, 2, 4, 6]
#     female_idx = [1, 3, 5, 7]
#     chinese_idx = [0, 1]
#     malay_idx = [2, 3]
#     indian_idx = [4, 5]
    
#     n_albu, n_sims, _, n_years = ckd_mat_list[0].shape
#     n_age_groups = len(age_groups)

#     # print("test")
#     # n_albu = 1
#     # n_sims = 1

#     # Preallocate arrays
#     overall = np.zeros((n_albu, n_sims, n_years))
#     male = np.zeros_like(overall)
#     female = np.zeros_like(overall)
#     chinese = np.zeros_like(overall)
#     malay = np.zeros_like(overall)
#     indian = np.zeros_like(overall)
#     age_specific = np.zeros((n_albu, n_sims, n_age_groups, n_years))

#     for g in range(n_groups):
#         ages = age_matrix_vec[g]                # (n_sims, n_persons, n_years)
#         ckd = ckd_mat_list[g]                   # (n_albu, n_sims, n_persons, n_years)
#         mask_all = (ages >= 18) & (ages <= 200) # boolean mask

#         # Total people and CKD counts
#         total_people = mask_all.sum(axis=1)             # (n_sims, n_years)
#         total_ckd = ((ckd == ckd_level) & mask_all[None, :, :]).sum(axis=2)  # (n_albu, n_sims, n_years)

#         # Add to overall
#         overall += total_ckd
#         if g in male_idx:
#             male += total_ckd
#         if g in female_idx:
#             female += total_ckd
#         if g in chinese_idx:
#             chinese += total_ckd
#         if g in malay_idx:
#             malay += total_ckd
#         if g in indian_idx:
#             indian += total_ckd

#         # Age-specific
#         for a_idx, (low, high) in enumerate(age_groups):
#             age_mask = (ages >= low) & (ages <= high)
#             age_total = age_mask.sum(axis=1)                         # (n_sims, n_years)
#             age_ckd_mask = ((ckd == ckd_level) & age_mask[None, :, :]).sum(axis=2)  # (n_albu, n_sims, n_years)
#             age_specific[:, :, a_idx, :] += age_ckd_mask / age_total[None, :, :]

#     # Flatten arrays to long-form DataFrame
#     albu_idx = np.arange(n_albu)[:, None, None].repeat(n_sims, axis=1).repeat(n_years, axis=2).flatten()
#     sim_idx = np.arange(n_sims)[None, :, None].repeat(n_albu, axis=0).repeat(n_years, axis=2).flatten()
#     year_idx = np.arange(n_years)[None, None, :].repeat(n_albu, axis=0).repeat(n_sims, axis=1).flatten()

#     data = {
#         "albu": albu_idx,
#         "sim": sim_idx,
#         "year": start_year + year_idx,
#         "overall": overall.flatten(),
#         "male": male.flatten(),
#         "female": female.flatten(),
#         "chinese": chinese.flatten(),
#         "malay": malay.flatten(),
#         "indian": indian.flatten()
#     }

#     # Age-specific columns
#     for a_idx, age_range in enumerate(age_groups):
#         data[str(age_range)] = age_specific[:, :, a_idx, :].flatten()

#     df = pd.DataFrame(data)
#     return df





#%% get ckd prevalence
ckd_prevalence = simulate_ckd_prevalence(age_matrix_vec, general_ckd_mat_ls)
ckd_prevalence

ckd_prevalence_2022 = ckd_prevalence[ckd_prevalence['year'] == 2022]
ckd_prevalence_2022


#%% save ckd prevalence
ckd_prevalence.to_csv('results_df/ckd_prevalence_forecast.csv', index=False)


#%% read prevalence


#%% save ckd prevalence 2018
# Select CKD prevalence data for year 2018
ckd_prevalence_2018 = ckd_prevalence[ckd_prevalence['year'] == 2018]

# Calculate mean and 95% confidence interval for overall prevalence
overall_vals = ckd_prevalence_2018['overall']
mean_overall = overall_vals.mean()
ci_lower = overall_vals.quantile(0.025)
ci_upper = overall_vals.quantile(0.975)

print(f"Mean overall CKD prevalence in 2018: {mean_overall:.4f}")
print(f"95% CI for overall CKD prevalence in 2018: [{ci_lower:.4f}, {ci_upper:.4f}]")

#%% 
import matplotlib.pyplot as plt
import numpy as np

# Ensure ckd_prevalence is loaded (already loaded above)
# We want years from 1990 to 2050
years = np.arange(1990, 2051)
age_group_cols = [col for col in ckd_prevalence.columns if col.startswith('(') and ',' in col and ')' in col]

def get_mean_ci(df, col):
    """Return mean, lower, upper arrays for a given column over years."""
    means = []
    lowers = []
    uppers = []
    for year in years:
        vals = df[df['year'] == year][col]
        means.append(vals.mean())
        lowers.append(vals.quantile(0.025))
        uppers.append(vals.quantile(0.975))
    return np.array(means), np.array(lowers), np.array(uppers)


# Publication-safe color palette (Okabe–Ito)
pub_colors = {
    'overall': '#1B4F72',  # navy blue
    'male': '#0072B2',     # blue
    'female': '#D55E00',   # orange
    'chinese': '#009E73',  # green
    'malay': '#E69F00',    # gold
    'indian': '#CC79A7'    # magenta
}

# Create figure
fig, axes = plt.subplots(1, 4, figsize=(24, 6), sharex=True)
plt.subplots_adjust(wspace=0.3)

# 1. Overall
mean, lower, upper = get_mean_ci(ckd_prevalence, 'overall')
axes[0].plot(years, mean, label='Overall', color=pub_colors['overall'], lw=2.5)
axes[0].fill_between(years, lower, upper, color=pub_colors['overall'], alpha=0.2)
axes[0].set_title('Overall CKD Prevalence')
axes[0].set_xlabel('Year')
axes[0].set_ylabel('Prevalence')
axes[0].set_ylim(0, None)
axes[0].legend(frameon=False)

# 2. Gender
for gender in ['male', 'female']:
    mean, lower, upper = get_mean_ci(ckd_prevalence, gender)
    axes[1].plot(years, mean, label=gender.capitalize(),
                 color=pub_colors[gender], lw=2.5)
    axes[1].fill_between(years, lower, upper,
                         color=pub_colors[gender], alpha=0.2)
axes[1].set_title('CKD Prevalence by Gender')
axes[1].set_xlabel('Year')
axes[1].set_ylim(0, None)
axes[1].legend(frameon=False)

# 3. Ethnicity
for eth in ['chinese', 'malay', 'indian']:
    mean, lower, upper = get_mean_ci(ckd_prevalence, eth)
    axes[2].plot(years, mean, label=eth.capitalize(),
                 color=pub_colors[eth], lw=2.5)
    axes[2].fill_between(years, lower, upper,
                         color=pub_colors[eth], alpha=0.2)
axes[2].set_title('CKD Prevalence by Ethnicity')
axes[2].set_xlabel('Year')
axes[2].set_ylim(0, None)
axes[2].legend(frameon=False)

# 4. Age groups
cmap = plt.get_cmap('viridis', len(age_group_cols))
for i, col in enumerate(age_group_cols):
    mean, lower, upper = get_mean_ci(ckd_prevalence, col)
    axes[3].plot(years, mean, label=col, lw=2, color=cmap(i))
    axes[3].fill_between(years, lower, upper, color=cmap(i), alpha=0.15)
axes[3].set_title('CKD Prevalence by Age Group')
axes[3].set_xlabel('Year')
axes[3].set_ylim(0, None)
axes[3].legend(title='Age Group', fontsize=9, frameon=False)

plt.suptitle('CKD Prevalence Trajectory (1990-2050) with 95% CI', fontsize=18)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()



#%% 


#%% find incidence rate

# Efficiently process all matrices in general_ckd_mat_ls so that for each 2D matrix,
# only the first occurrence of 1 in each row is kept, all subsequent 1s in that row are set to 0.

# Create a new list to store incidence matrices for each group
general_ckd_incidence_ls = []

for group in general_ckd_mat_ls:
    # group: shape (n_albu, n_sims, n_persons, n_years)
    group_incidence = np.zeros_like(group)
    n_albu, n_sims, n_persons, n_years = group.shape
    for albu in range(n_albu):
        for sim in range(n_sims):
            mat = group[albu, sim].copy()  # shape (n_persons, n_years)
            # For each person (row), find the first year (column) where CKD=1
            first_one_idx = (mat == 1).argmax(axis=1)
            has_one = (mat == 1).any(axis=1)
            # Zero out all 1s
            mat[:, :] = 0
            # Set only the first 1 in each row (if any)
            mat[np.arange(n_persons)[has_one], first_one_idx[has_one]] = 1
            group_incidence[albu, sim] = mat
    general_ckd_incidence_ls.append(group_incidence)

#%% read
import pandas as pd
ckd_incidence = pd.read_csv('results_df/ckd_incidence_forecast.csv')

#%%


# Calculate CKD incidence using the simulate_ckd_prevalence function
ckd_incidence = simulate_ckd_prevalence(age_matrix_vec, general_ckd_incidence_ls)


# Select CKD incidence data for the year 2018
ckd_incidence_2018 = ckd_incidence[ckd_incidence['year'] == 2018]

# Calculate mean and 95% confidence interval for overall incidence in 2018
incidence_overall_vals = ckd_incidence_2018['overall']
mean_incidence_overall = incidence_overall_vals.mean()
incidence_ci_lower = incidence_overall_vals.quantile(0.025)
incidence_ci_upper = incidence_overall_vals.quantile(0.975)

print(f"Mean overall CKD incidence in 2018: {mean_incidence_overall:.4f}")
print(f"95% CI for overall CKD incidence in 2018: [{incidence_ci_lower:.4f}, {incidence_ci_upper:.4f}]")

#%% save ckd incidence
ckd_incidence.to_csv('results_df/ckd_incidence_forecast.csv', index=False)


30#%%
# import pandas as pd
# # Initialize a comprehensive list to store all simulation results
# all_simulation_results = []

# # Iterate through all 6 ethnicity groups
# for i in range(6):  # Changed from 8 to 6 as per instruction
#     # Iterate through all 5*10=50 simulations
#     for sim_i in range(5):
#         for sim_j in range(10):
#             prevalence_yearly = []
            
#             # Iterate through each year (columns -61 to -1)
#             for year_col in range(-61, 0):
#                 # Extract age, diabetes, ACR, and stage matrices for this simulation
#                 ages = age_matrix_vec[i][sim_j, :, year_col]
#                 acr_values = albu_mat_storage[i][sim_i, sim_j, :, year_col]
#                 stages_col = stage_matrix_ls[i][sim_i, sim_j, :, year_col]

#                 # Apply age mask (18-74 years)
#                 age_mask = (ages >= 18) & (ages <= 74)

#                 # Filter variables based on the mask
#                 filtered_stages = stages_col[age_mask]
#                 filtered_acr = acr_values[age_mask]

#                 # Define healthy condition: stage 0 or 1 and ACR = 0
#                 healthy_mask = (filtered_stages <= 2) & (filtered_acr == 0)

#                 # Identify non-healthy (CKD) cases
#                 non_healthy_mask = ~healthy_mask

#                 # Count total people and CKD cases
#                 population_count = np.sum(age_mask)
#                 ckd_count = np.sum(non_healthy_mask)
                
#                 # Compute prevalence for this year
#                 ckd_prevalence = (ckd_count / population_count) * 100 if population_count > 0 else 0
#                 prevalence_yearly.append(ckd_prevalence)
            
#             # Store results for this simulation
#             simulation_id = sim_i * 10 + sim_j  # Unique simulation ID from 0 to 49
            
#             for year_idx, prevalence in enumerate(prevalence_yearly):
#                 year_value = -61 + year_idx  # Convert to actual year (-61 to -1)
#                 all_simulation_results.append({
#                     'ethnicity': i,
#                     'simulation': simulation_id,
#                     'year': year_value,
#                     'prevalence': prevalence
#                 })

# # Convert to DataFrame
# prevalence_df = pd.DataFrame(all_simulation_results)

# # Add ethnicity labels for clarity
# ethnicity_labels = {0: 'Chinese_Male', 1: 'Chinese_Female', 2: 'Malay_Male', 
#                    3: 'Malay_Female', 4: 'Indian_Male', 5: 'Indian_Female'}
# prevalence_df['ethnicity_label'] = prevalence_df['ethnicity'].map(ethnicity_labels)

# # Print summary statistics for 2022 (year -28)
# print("2022 CKD Prevalence (Ages 18-74) Summary:")
# year_2022_data = prevalence_df[prevalence_df['year'] == -28]
# for i in range(6):
#     eth_data = year_2022_data[year_2022_data['ethnicity'] == i]['prevalence']
#     print(f"{ethnicity_labels[i]}: Mean: {eth_data.mean():.2f}%, 95% CI: ({eth_data.quantile(0.025):.2f}% - {eth_data.quantile(0.975):.2f}%)")

# # Save the comprehensive dataframe
# results_folder = 'results_df'
# if not os.path.exists(results_folder):
#     os.makedirs(results_folder)

# prevalence_df.to_csv(os.path.join(results_folder, 'ckd_prevalence_forecast_comprehensive.csv'), index=False)


# # print(f"\nDataFrame shape: {prevalence_df.shape}")
# # print(f"Unique ethnicities: {prevalence_df['ethnicity'].nunique()}")
# # print(f"Unique simulations: {prevalence_df['simulation'].nunique()}")
# # print(f"Unique years: {prevalence_df['year'].nunique()}")


# # %%
# # Create panel plot with 1x3 layout
# import matplotlib.pyplot as plt

# fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# # Define pairs for plotting
# ethnicity_pairs = [(0, 1), (2, 3), (4, 5)]  # (Male, Female) pairs
# pair_labels = ['Chinese', 'Malay', 'Indian']

# for pair_idx, (male_eth, female_eth) in enumerate(ethnicity_pairs):
#     ax = axes[pair_idx]
    
#     # Get data for male and female of this ethnicity
#     male_data = prevalence_df[prevalence_df['ethnicity'] == male_eth]
#     female_data = prevalence_df[prevalence_df['ethnicity'] == female_eth]
    
#     # Calculate mean and confidence intervals across simulations for each year
#     male_summary = male_data.groupby('year')['prevalence'].agg(['mean', lambda x: x.quantile(0.025), lambda x: x.quantile(0.975)])
#     female_summary = female_data.groupby('year')['prevalence'].agg(['mean', lambda x: x.quantile(0.025), lambda x: x.quantile(0.975)])
    
#     # Convert years from relative to absolute (year -61 corresponds to 1990, year 0 corresponds to 2051)
#     years = male_summary.index + 2051
    
#     # Plot mean lines
#     ax.plot(years, male_summary['mean'], label=f'{pair_labels[pair_idx]} Male', color='blue', linewidth=2)
#     ax.plot(years, female_summary['mean'], label=f'{pair_labels[pair_idx]} Female', color='red', linewidth=2)
    
#     # Plot confidence intervals
#     ax.fill_between(years, male_summary['<lambda_0>'], male_summary['<lambda_1>'], 
#                     alpha=0.3, color='blue')
#     ax.fill_between(years, female_summary['<lambda_0>'], female_summary['<lambda_1>'], 
#                     alpha=0.3, color='red')
    
#     ax.set_xlabel('Year')
#     if pair_idx == 0:
#         ax.set_ylabel('CKD Prevalence (%)')
#     ax.legend()
#     ax.grid(False)
#     ax.set_xlim(1990, 2050)

# plt.tight_layout()
# plt.savefig(os.path.join(results_folder, 'ckd_prevalence_panel_plot.png'), dpi=300, bbox_inches='tight')
# plt.show()
# # %%

# %%

import pandas as pd

nphs_df = pd.read_csv('../../data/nphs.csv')
nphs_df
#%%
# Overwrite the 'year' column with 2019, 2022, 2024 directly (assume only 3 rows)
nphs_df = nphs_df.copy()
nphs_df['year'] = [2019, 2022, 2024]
nphs_df

#%%
nphs_df.to_csv('../../data/nphs.csv', index=False)

# %%
df_summary.columns
# %%

#%% save ckd incidence
ckd_incidence = pd.read_csv('results_df/ckd_incidence_forecast.csv')
ckd_incidence
# %%
import pandas as pd
import numpy as np

def compute_age_ci(df, age_cols):
    """
    Compute mean and 95% CI (2.5%, 97.5%) for each age group column per year.
    Returns a DataFrame with columns: year, (age_group)_mean, (age_group)_lower, (age_group)_upper
    """
    records = []
    years = sorted(df['year'].unique())

    for year in years:
        vals = df[df['year'] == year]
        record = {'year': year}
        for col in age_cols:
            record[f'{col}_mean'] = vals[col].mean()
            record[f'{col}_lower'] = vals[col].quantile(0.025)
            record[f'{col}_upper'] = vals[col].quantile(0.975)
        records.append(record)

    return pd.DataFrame(records)
def check_nphs_overlap(df_age_strat, nphs_df, year_col='year'):
    """
    Check if NPHS observed prevalence values fall within simulated 95% CI.
    Displays result as 'True [lower, upper], obs=value'.
    """
    # Convert tuple columns "(18, 39)" → "18-39"
    df = df_age_strat.copy()
    rename_map = {
        col: f"{col[1:-1].replace(',', '-').replace(' ', '')}"
        for col in df.columns if col.startswith('(')
    }
    df.rename(columns=rename_map, inplace=True)

    age_cols = ['18-39', '40-54', '55-69', '70-74']

    # Compute CI for simulated data
    ci_df = compute_age_ci(df, age_cols)

    # Prepare NPHS data (only relevant columns)
    nphs_sub = nphs_df[[year_col] + age_cols].copy()
    nphs_sub = nphs_sub.rename(columns={c: f"{c}_obs" for c in age_cols})
    
    # # Apply special year shift: 2021→2022, 2023→2024
    # nphs_sub[year_col] = nphs_sub[year_col].replace({2021: 2022, 2023: 2024})
    # Merge
    merged = pd.merge(ci_df, nphs_sub, on=year_col, how='inner')

    # Build results
    results = []
    for _, row in merged.iterrows():
        res = {'year': row[year_col]}
        for col in age_cols:
            obs = row[f'{col}_obs']
            lower = row[f'{col}_lower']
            upper = row[f'{col}_upper']
            inside = lower <= obs <= upper
            res[col] = f"{inside} [95% CI: {lower:.3f}-{upper:.3f}], obs={obs:.3f}"
        results.append(res)

    return pd.DataFrame(results)

#%% 
result = check_nphs_overlap(df_age_strat, nphs_df)
print(result)
# %%
nphs_df.columns
# %%
ckd_incidence
# %%
ckd_incidence.columns
# %%
def check_nphs_overlap_gender_race(ckd_incidence, nphs_df, year_col='year'):
    """
    Check if NPHS observed gender/race prevalence falls within simulated 95% CI.
    Handles column name mapping (chn→chinese, mal→malay, ind→indian).
    Applies year shift: NPHS 2021→2022, 2023→2024.
    Displays results as 'True [95% CI: lower-upper], obs=value'.
    """
    df = ckd_incidence.copy()

    # Simulation columns (from ckd_incidence)
    sim_cols = ['male', 'female', 'chinese', 'malay', 'indian']

    # Compute simulation CI
    ci_df = compute_age_ci(df, sim_cols)

    # Prepare NPHS data
    nphs_sub = nphs_df[[year_col, 'male', 'female', 'chn', 'mal', 'ind']].copy()
    nphs_sub = nphs_sub.rename(columns={
        'chn': 'chinese_obs',
        'mal': 'malay_obs',
        'ind': 'indian_obs',
        'male': 'male_obs',
        'female': 'female_obs'
    })

    # Apply year shift
    nphs_sub[year_col] = nphs_sub[year_col].replace({2021: 2022, 2023: 2024})

    # Merge simulation CI with NPHS
    merged = pd.merge(ci_df, nphs_sub, on=year_col, how='inner')

    # Build output DataFrame
    results = []
    for _, row in merged.iterrows():
        res = {'year': int(row[year_col])}
        for col in sim_cols:
            obs = row[f'{col}_obs']
            lower = row[f'{col}_lower']
            upper = row[f'{col}_upper']
            inside = lower <= obs <= upper
            res[col] = f"{inside} [95% CI: {lower:.3f}-{upper:.3f}], obs={obs:.3f}"
        results.append(res)

    return pd.DataFrame(results)

#%%
result_gender_race = check_nphs_overlap_gender_race(ckd_incidence, nphs_df)
print(result_gender_race)
# %% compute_age_ci
nphs_df
# %%
ckd_incidence[ckd_incidence['year'] == 2022]
# %%
