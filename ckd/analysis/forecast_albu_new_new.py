#%%
from Age_BMI_loading import age_matrix_vec_2050
import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd

from impute_albu import schedule_pre_albuminuria_probability,schedule_albuminuria_probability
from Age_BMI_loading import age_dict
from prevalence import get_prevalence,get_pre_prevalence,get_overall_prevalence,get_overall_pre_prevalence
from prevalence_3d import get_prevalence_3d, get_pre_prevalence_3d, get_overall_prevalence_3d, get_overall_pre_prevalence_3d

assert max(age_dict[0].keys()) if age_dict[0] else 0 == 85


#%%
import time
# get 1990 
N = 8
albu_status_dict = {}
albu_mat_list_overall = []
 # simulate uniformly distributed

# test 

A_range = [0.002,0.006] # for testing, results should be 0.034
A_range = [0.0015,0.0025,0.0035,0.0045,0.0055]
start_time = time.time()


from multiprocessing import Pool
import functools
def logistic_growth(t, start_val, end_val, midpoint, steepness):
    """
    Computes a logistic transition from start_val to end_val.
    """
    return start_val + (end_val - start_val) / (1 + np.exp(-steepness * (t - midpoint)))

def process_single_A(A_trajectory, age_matrix_vec, age_dict):
    """
    Process a single A trajectory to compute albuminuria status matrices.
    
    Parameters:
        A_trajectory (np.array): Array of A values for each year (shape: n_years,)
        age_matrix_vec (list): List of age matrices for different groups
        age_dict (dict): Dictionary mapping groups to age distributions
    
    Returns:
        list: albu_mat_list containing matrices for all groups
    """
    N = 8
    albu_status_dict = {}
    
    # Validation to ensure A_trajectory matches years in simulation
    # Assuming age_matrix_vec[0].shape[2] is the number of years
    sim_years = age_matrix_vec[0].shape[2]
    if len(A_trajectory) != sim_years:
        # If lengths differ, assume extrapolation or slicing is needed, 
        # but for safety, lets slice or pad to match simulation years
        if len(A_trajectory) > sim_years:
            A_trajectory = A_trajectory[:sim_years]
        else:
            raise ValueError(f"A_trajectory length ({len(A_trajectory)}) < Simulation years ({sim_years})")

    # --- 1. INITIALIZATION (Base Year 1990) ---
    # We use the first value of the trajectory for the initial population setup
    A_initial = A_trajectory[0]

    for group in range(N):
        i = group
        albu_status_dict[group] = {}
        
        for age in age_dict[group]:
            n_samples = age_dict[group][age]
            age_mat = np.tile(np.arange(18, age + 1), (n_samples, 1))

            # Use A_initial for the setup phase
            prediabetes_prob_matrix = schedule_pre_albuminuria_probability(age_mat, i, A_initial)
            rand_matrix = np.random.rand(*age_mat.shape)
            prediabetes_matrix = (rand_matrix < prediabetes_prob_matrix) * 0.5
            prediabetes_matrix = np.maximum.accumulate(prediabetes_matrix, axis=1)

            albu_prob_matrix = schedule_albuminuria_probability(age_mat, i)
            rand_matrix = np.random.rand(*age_mat.shape)
            albu_matrix = np.where(rand_matrix < albu_prob_matrix, 1, 0.5)

            combined_matrix = np.where(prediabetes_matrix == 0.5, albu_matrix, prediabetes_matrix)
            combined_matrix = np.maximum.accumulate(combined_matrix, axis=1)

            albu_status_dict[group][age] = np.max(combined_matrix, axis=1)
    
    # --- 2. TIME SERIES SIMULATION ---
    albu_mat_list = []
    
    # Reshape A_trajectory for broadcasting: (1, 1, n_years)
    # This ensures it adds correctly to age_mat (sim, indiv, n_years)
    A_broadcast = A_trajectory.reshape(1, 1, -1)

    for i in range(N):
        n_simulations, n_individuals, n_years = age_matrix_vec[i].shape
        albu_status = np.zeros((n_simulations, n_individuals, n_years))  

        # Fill initial status (Year 0)
        for age, status_vec in albu_status_dict[i].items():
            try:
                positions = np.where(age_matrix_vec[i][0, :, 0] == age)[0]
                albu_status[:, positions, 0] = status_vec
            except Exception as e:
                print(f"Error group {i}, age {age}: {e}")
                raise 

        # Repeat the first column across all years to initialize
        albu_status_before = np.repeat(albu_status[:, :, 0][:, :, np.newaxis], n_years, axis=2)
        
        # Get Age Matrix
        age_mat = age_matrix_vec[i]

        # Handle Death
        albu_status_before = np.where(age_mat == -1, 0, albu_status_before)

        # --- KEY CHANGE HERE ---
        # Pass the reshaped broadcastable A array
        pre_albu_prob_matrix = schedule_pre_albuminuria_probability(age_mat, i, A_broadcast)
        
        # Determine Pre-Albuminuria
        pre_albu_prob_matrix = np.where(age_mat < 18, 0, pre_albu_prob_matrix)
        rand_matrix = np.random.rand(*age_mat.shape)
        pre_albu_matrix = (rand_matrix < pre_albu_prob_matrix) * 0.5
        
        pre_albu_matrix = np.where(albu_status_before == 0, pre_albu_matrix, albu_status_before)
        pre_albu_matrix = np.maximum.accumulate(pre_albu_matrix, axis=2)
        
        # Determine Albuminuria
        albu_prob_matrix = schedule_albuminuria_probability(age_mat, i)
        rand_matrix = np.random.rand(*age_mat.shape)
        albu_matrix = np.where(rand_matrix < albu_prob_matrix, 1, 0.5)
        
        # Combine
        combined_matrix = np.where(pre_albu_matrix == 0.5, albu_matrix, pre_albu_matrix)

        albu_status[:, :, 1:] = combined_matrix[:, :, 1:]
        albu_status = np.maximum.accumulate(albu_status, axis=2)
        albu_mat_list.append(albu_status)

    # Note: We pass A_trajectory[0] or mean just for printing, as 'A' is now a vector
    overall_prevalence = get_overall_prevalence_3d(age_matrix_vec, albu_mat_list, -28)
    overall_pre_prevalence = get_overall_pre_prevalence_3d(age_matrix_vec, albu_mat_list, -28)

    print(f"A (Start={A_trajectory[0]:.4f}, End={A_trajectory[-1]:.4f}): Overall prev 2022 = {overall_prevalence:.4f}")
    print(f"A (Start={A_trajectory[0]:.4f}, End={A_trajectory[-1]:.4f}): Overall pre-pre prev 2022 = {overall_pre_prevalence:.4f}")

    # Note: We pass A_trajectory[0] or mean just for printing, as 'A' is now a vector
    overall_prevalence = get_overall_prevalence_3d(age_matrix_vec, albu_mat_list, -26)
    overall_pre_prevalence = get_overall_pre_prevalence_3d(age_matrix_vec, albu_mat_list, -26)

    print(f"A (Start={A_trajectory[0]:.4f}, End={A_trajectory[-1]:.4f}): Overall prev 2024 = {overall_prevalence:.4f}")
    print(f"A (Start={A_trajectory[0]:.4f}, End={A_trajectory[-1]:.4f}): Overall pre-pre prev 2024 = {overall_pre_prevalence:.4f}")
    # 11.1, 1.6; 11.9 2.0
    
    return albu_mat_list

# Parallel processing for different A values

if __name__ == '__main__':
    # Setup years
    n_years_sim = age_matrix_vec_2050[0].shape[2] # Should be 61 (1990-2050)
    years_idx = np.arange(n_years_sim)
    actual_years = 1990 + years_idx
    
    # --- 2. DEFINE BOUNDS WITH LOGISTIC GROWTH ---
    
    # LOWER START: You mentioned "lower value in 1990"
    # We start significantly lower to anchor the left side of the graph
    bounds_start = np.array([0.001, 0.006]) 
    
    # HIGHER END: To ensure we hit the high points in 2024
    bounds_end = np.array([0.008, 0.018])   
    
    # SHAPE PARAMETERS
    # Midpoint: The year where the curve is rising fastest (inflection point)
    # Setting this to 2018 ensures the "fast increase part" hits right around 2020
    midpoint_year = 2022 
    
    # Steepness: Controls how fast the transition is. 
    # 0.1 is slow/linear-ish, 0.5 is very steep. 0.35 is a good balance for "steep but realistic".
    k_steepness = 0.6 
    
    # Calculate bounds for every year using Logistic Function
    # shape: (n_years, 2)
    lower_bound_t = logistic_growth(actual_years, bounds_start[0], bounds_end[0], midpoint_year, k_steepness)
    upper_bound_t = logistic_growth(actual_years, bounds_start[1], bounds_end[1], midpoint_year, k_steepness)
    
    # Stack them back together
    bounds_t = np.stack([lower_bound_t, upper_bound_t], axis=1)

    # --- 3. GENERATE SCENARIOS ---
    A_scenarios = np.linspace(bounds_t[:, 0], bounds_t[:, 1], 5)
    # Convert to list of arrays
    A_range = list(A_scenarios)

    # --- Run Parallel Processing ---
    process_A_with_fixed_args = functools.partial(
        process_single_A, 
        age_matrix_vec=age_matrix_vec_2050, 
        age_dict=age_dict
    )
    
    with Pool() as pool:
        albu_mat_list_overall = pool.map(process_A_with_fixed_args, A_range)
    
    # --- Saving Logic Remains the Same ---
    output_dir = '../future_data_1990_2050/albu_matrix_forecast/'
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\nSaving albuminuria matrices to {output_dir}")
    
    for group_idx in range(8):
        group_matrices = []
        for A_idx, albu_mat_list in enumerate(albu_mat_list_overall):
            group_matrices.append(albu_mat_list[group_idx])
        
        combined_group_matrix = np.stack(group_matrices, axis=0)
        
        filename = f'albu_mat_group_{group_idx}.npy'
        filepath = os.path.join(output_dir, filename)
        np.save(filepath, combined_group_matrix)
        print(f"Saved: {filename} with shape {combined_group_matrix.shape}")
# Load albuminuria matrices for different A values

# nphs : 11.1; 1.6 ;