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
A_range = [0.001,0.002,0.003,0.004,0.005] # simulate uniformly distributed

# test 

#A_range = [0.001,0.005] # for testing, results should be 0.034

start_time = time.time()

from multiprocessing import Pool
import functools

def process_single_A(A, age_matrix_vec, age_dict):
    """
    Process a single A value to compute albuminuria status matrices.
    
    Parameters:
        A (float): The A parameter value
        age_matrix_vec (list): List of age matrices for different groups
        age_dict (dict): Dictionary mapping groups to age distributions
    
    Returns:
        list: albu_mat_list containing matrices for all groups
    """
    N = 8
    albu_status_dict = {}
    
    for group in range(N):
        i = group
        albu_status_dict[group] = {}
        # age_matrix_vec[i] now has shape (simulation_times, individuals, years)
        n_simulations, n_individuals, n_years = age_matrix_vec[i].shape
        
        for age in age_dict[group]:
            # Create an age matrix with shape (n_samples, n_ages)
            n_samples = age_dict[group][age]
            age_mat = np.tile(np.arange(18, age + 1), (n_samples, 1))

            # Compute prediabetes probability matrix
            prediabetes_prob_matrix = schedule_pre_albuminuria_probability(age_mat, i, A)
            rand_matrix = np.random.rand(*age_mat.shape)
            prediabetes_matrix = (rand_matrix < prediabetes_prob_matrix) * 0.5
            prediabetes_matrix = np.maximum.accumulate(prediabetes_matrix, axis=1)

            # Compute albu probability matrix
            albu_prob_matrix = schedule_albuminuria_probability(age_mat, i)
            rand_matrix = np.random.rand(*age_mat.shape)
            albu_matrix = np.where(rand_matrix < albu_prob_matrix, 1, 0.5)

            # Combine: take max along each row (for each sample)
            combined_matrix = np.where(prediabetes_matrix == 0.5, albu_matrix, prediabetes_matrix)
            combined_matrix = np.maximum.accumulate(combined_matrix, axis=1)

            albu_status_dict[group][age] = np.max(combined_matrix, axis=1)
    
    albu_mat_list = []
    for i in range(N):
        # age_matrix_vec[i] now has shape (simulation_times, individuals, years)
        n_simulations, n_individuals, n_years = age_matrix_vec[i].shape
        albu_status = np.zeros((n_simulations, n_individuals, n_years))  
        
        # Debug: Print shapes for the first age group to understand data structure
        # if i == 0:  # Only print for the first group to avoid too much output
        #     first_age, first_status_vec = next(iter(albu_status_dict[i].items()))
        #     positions = np.where(age_matrix_vec[i][0, :, 0] == first_age)[0]
        #     print(f"Group {i}, Age {first_age}:")
        #     print(f"  positions shape: {positions.shape}")
        #     print(f"  status_vec shape: {first_status_vec.shape}")
        #     print(f"  age_matrix_vec[{i}] shape: {age_matrix_vec[i].shape}")
        #     print(f"  albu_status shape: {albu_status.shape}")

        for age, status_vec in albu_status_dict[i].items():
            try:
                # Find positions where the first column (first year) of age_matrix_vec[i] equals 'age'
                # Since positions are the same across all simulations, we can find them once
                positions = np.where(age_matrix_vec[i][0, :, 0] == age)[0]
                # Assign the albu status vector for this age group to all simulations
                albu_status[:, positions, 0] = status_vec
            except Exception as e:
                print(f"Error occurred for group {i}, age {age}:")
                print(f"  status_vec: {status_vec}")
                print(f"  status_vec shape: {status_vec.shape}")
                print(f"  positions: {positions}")
                print(f"  positions shape: {positions.shape}")
                print(f"  Error details: {e}")
                raise  # Re-raise the exception after printing debug info
            
    

        # Repeat the first column across all years for each simulation
        albu_status_before = np.repeat(albu_status[:, :, 0][:, :, np.newaxis], n_years, axis=2)
        
        # Process albu status
        age_mat = age_matrix_vec[i]

        # Set albu_status_before to 0 where age_mat is -1 (dead)
        albu_status_before = np.where(age_mat == -1, 0, albu_status_before)


        pre_albu_prob_matrix = schedule_pre_albuminuria_probability(age_mat, i, A)
        # Set pre_albu_prob_matrix to 0 where age_mat < 18
        pre_albu_prob_matrix = np.where(age_mat < 18, 0, pre_albu_prob_matrix)
        rand_matrix = np.random.rand(*age_mat.shape)
        pre_albu_matrix = (rand_matrix < pre_albu_prob_matrix) * 0.5
        
        pre_albu_matrix = np.where(albu_status_before == 0, pre_albu_matrix, albu_status_before)
        pre_albu_matrix = np.maximum.accumulate(pre_albu_matrix, axis=2)
        
        albu_prob_matrix = schedule_albuminuria_probability(age_mat, i)
        rand_matrix = np.random.rand(*age_mat.shape)
        albu_matrix = np.where(rand_matrix < albu_prob_matrix, 1, 0.5)
        
        combined_matrix = np.where(pre_albu_matrix == 0.5, albu_matrix, pre_albu_matrix)

        albu_status[:, :, 1:] = combined_matrix[:, :, 1:]
        albu_status = np.maximum.accumulate(albu_status, axis=2)
        albu_mat_list.append(albu_status)

    overall_prevalence = get_overall_prevalence_3d(age_matrix_vec, albu_mat_list, -28)
    overall_pre_prevalence = get_overall_pre_prevalence_3d(age_matrix_vec, albu_mat_list, -28)

    print(f"A = {A}: Overall prevalence = {overall_prevalence:.4f}, Overall pre-prevalence = {overall_pre_prevalence:.4f}")
    
    return albu_mat_list

# Parallel processing for different A values
if __name__ == '__main__':
    # Create a partial function with fixed arguments
    process_A_with_fixed_args = functools.partial(
        process_single_A, 
        age_matrix_vec=age_matrix_vec_2050, 
        age_dict=age_dict
    )
    
    # Use multiprocessing Pool to process A values in parallel
    with Pool() as pool:
        albu_mat_list_overall = pool.map(process_A_with_fixed_args, A_range)
    
    # Save the results for different A values
    output_dir = '../future_data_1990_2050/albu_matrix_forecast/'
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\nSaving albuminuria matrices to {output_dir}")
    
    # Restructure to have A dimension in front: (num_A, num_simulations, individuals, years)
    # First, reorganize data by group
    for group_idx in range(8):  # 8 ethnic-gender groups
        # Collect matrices for this group across all A values
        group_matrices = []
        for A_idx, albu_mat_list in enumerate(albu_mat_list_overall):
            group_matrices.append(albu_mat_list[group_idx])
        
        # Stack along A dimension: (num_A, num_simulations, individuals, years)
        combined_group_matrix = np.stack(group_matrices, axis=0)
        
        #print(f"Combined group matrix shape: {combined_group_matrix.shape}")
        # Save combined matrix for this group
        filename = f'albu_mat_group_{group_idx}.npy'
        filepath = os.path.join(output_dir, filename)
        np.save(filepath, combined_group_matrix)
        print(f"Saved: {filename} with shape {combined_group_matrix.shape}")
    
    print(f"Successfully saved albuminuria forecast matrices for {len(A_range)} A values with shape (A, simulations, individuals, years)")

# Load albuminuria matrices for different A values

# nphs : 11.1; 1.6