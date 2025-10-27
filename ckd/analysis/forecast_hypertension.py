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

from impute_hyper import (
schedule_hypertension_probability
)

from prevalence_3d import *
from prevalence import *
#%% define data
bmi_samples_dict[0][18].shape
age_matrix_vec = age_matrix_vec_2050
#%% load BMI 
# Load BMI matrices
bmi_matrix_ls = []

parent_dir = "../future_data_1990_2050/bmi_matrix/"
for idx in range(8):
    file_path = os.path.join(parent_dir, f"bmi_matrix_{idx}.npy")
    try:
        bmi_matrix = np.load(file_path)
        bmi_matrix_ls.append(bmi_matrix)
        print(f"Loaded: {file_path} with shape {bmi_matrix.shape}")
    except FileNotFoundError:
        print(f"Warning: File not found: {file_path}")
        # Handle missing file case - could create empty matrix or skip
        continue


hypertension_status_dict = {}
N = 8

for group in range(N):
    hypertension_status_dict[group] = {}
    for age in age_dict[group]:
        bmi_samples = bmi_samples_dict[group][age]  # shape: (n_samples, n_ages)
        n_samples, n_ages = bmi_samples.shape
        # Create an age matrix with shape (n_samples, n_ages)
        age_mat = np.tile(np.arange(18, age + 1), (n_samples, 1))
        idx = group

        # Compute hypertension probability matrix
        hypertension_prob_matrix = schedule_hypertension_probability(age_mat, idx, bmi_samples)
        rand_matrix = np.random.rand(*bmi_samples.shape)
        hypertension_matrix = (rand_matrix < hypertension_prob_matrix)
        hypertension_matrix = np.maximum.accumulate(hypertension_matrix, axis=1)

        hypertension_status_dict[group][age] = np.max(hypertension_matrix, axis=1)  # vector of 0, 1


hyper_mat_list = []
for i in range(8):
    # age_matrix_vec is now 3D: (num_simulations, n_samples, n_ages)
    num_simulations, n_samples, n_ages = age_matrix_vec[i].shape
    hypertension_status = np.zeros((num_simulations, n_samples, n_ages))
    
    for age, status_vec in hypertension_status_dict[i].items():
        # Find positions where the first column of age_matrix_vec[i] equals 'age' across all simulations
        for sim in range(num_simulations):
            positions = np.where(age_matrix_vec[i][sim, :, 0] == age)[0]
            # Get the hypertension status vector for this age group
            hypertension_status[sim, positions, 0] = status_vec
    
    # deal with hypertension status 
    bmi_mat = bmi_matrix_ls[i]  # Also needs to be 3D to match age_matrix_vec
    age_mat = age_matrix_vec[i]

    hypertension_prob_matrix = schedule_hypertension_probability(age_mat, i, bmi_mat)
    rand_matrix = np.random.rand(*age_mat.shape)
    hypertension_matrix = (rand_matrix < hypertension_prob_matrix)

    # count the first vector 
    hypertension_status[:, :, 1:] = hypertension_matrix[:, :, 1:]
    hypertension_status = np.maximum.accumulate(hypertension_status, axis=2)
    hyper_mat_list.append(hypertension_status)

#%%

#%%
# Test prevalence with sample data at time index -28

get_prevalence_3d(age_matrix_vec, hyper_mat_list, -28)
# 36.5
#%%

get_overall_prevalence_3d(age_matrix_vec, hyper_mat_list, -28)

#%% save hypertension matrix
for i in range(8):
    np.save(f'../future_data_1990_2050/hyper_matrix/hypertension_mat_{i}.npy', hyper_mat_list[i])
#%% load hypertension matrix
for i in range(8):
    hyper_mat_list[i] = np.load(f'../future_data_1990_2050/hyper_matrix/hypertension_mat_{i}.npy')
    print(f'Loaded: {f'../future_data_1990_2050/hyper_matrix/hypertension_mat_{i}.npy'} with shape {hyper_mat_list[i].shape}')
#%%
