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

from impute_diabetes import (
    schedule_pre_diabetes_probability,
    schedule_diabetes_probability
)

#%% 
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

#%% 
# get 1990 

diabetes_status_dict = {}
diabetes_mat_list = []
for group in range(8):  # Changed from N to 8 to match the context
    i = group
    diabetes_status_dict[group] = {}
    diabetes_status = np.zeros((age_matrix_vec[i].shape[0], age_matrix_vec[i].shape[1], age_matrix_vec[i].shape[2]))  
    for age in age_dict[group]:
        bmi_samples = bmi_samples_dict[group][age]  # shape: (n_samples, n_ages)
        n_samples, n_ages = bmi_samples.shape
        # Create an age matrix with shape (n_samples, n_ages)
        n_samples = age_dict[group][age]
        age_mat = np.tile(np.arange(18, age + 1), (n_samples, 1))
        # idx = group

        # Compute prediabetes probability matrix
        prediabetes_prob_matrix = schedule_pre_diabetes_probability(age_mat, i, bmi_samples)
        rand_matrix = np.random.rand(*bmi_samples.shape)
        prediabetes_matrix = (rand_matrix < prediabetes_prob_matrix) * 0.5
        prediabetes_matrix = np.maximum.accumulate(prediabetes_matrix, axis=1)

        # Compute diabetes probability matrix
        diabetes_prob_matrix = schedule_diabetes_probability(age_mat, i, bmi_samples)
        rand_matrix = np.random.rand(*bmi_samples.shape)
        diabetes_matrix = np.where(rand_matrix < diabetes_prob_matrix, 1, 0.5)

        # Combine: take max along each row (for each sample)
        combined_matrix = np.where(prediabetes_matrix == 0.5, diabetes_matrix, prediabetes_matrix)
        combined_matrix = np.maximum.accumulate(combined_matrix, axis=1)

        diabetes_status_dict[group][age] = np.max(combined_matrix, axis=1)

diabetes_mat_list = []
prediabetes_mat_list = []
for i in range(8):
    diabetes_status = np.zeros((age_matrix_vec[i].shape[0], age_matrix_vec[i].shape[1], age_matrix_vec[i].shape[2]))  
    for age, status_vec in diabetes_status_dict[i].items():
        
        # Since positions are the same across all simulations, we only need to find them once
        positions = np.where(age_matrix_vec[i][0, :, 0] == age)[0]
        # Assign the diabetes status vector for this age group to all simulations
        if len(positions) > 0 and len(status_vec) >= len(positions):
            for sim in range(age_matrix_vec[i].shape[0]):
                diabetes_status[sim, positions, 0] = status_vec[:len(positions)]

    n_cols = age_matrix_vec[i].shape[2]
    ## ?
    diabetes_status_before = np.repeat(diabetes_status[:, :, 0][:, :, np.newaxis], n_cols, axis=2)
    # Process diabetes status
    bmi_mat = bmi_matrix_ls[i]
    age_mat = age_matrix_vec[i]

    prediabetes_prob_matrix = schedule_pre_diabetes_probability(age_mat, i, bmi_mat)
    rand_matrix = np.random.rand(*age_mat.shape)
    prediabetes_matrix = (rand_matrix < prediabetes_prob_matrix) * 0.5
    
    prediabetes_matrix = np.where(diabetes_status_before == 0, prediabetes_matrix, diabetes_status_before)
    prediabetes_matrix = np.maximum.accumulate(prediabetes_matrix, axis=2)
    prediabetes_mat_list.append(prediabetes_matrix)
    
    diabetes_prob_matrix = schedule_diabetes_probability(age_mat, i, bmi_mat)
    rand_matrix = np.random.rand(*age_mat.shape)
    diabetes_matrix = np.where(rand_matrix < diabetes_prob_matrix, 1, 0.5)
    
    combined_matrix = np.where(prediabetes_matrix == 0.5, diabetes_matrix, prediabetes_matrix)

    diabetes_status[:, :, 1:] = combined_matrix[:, :, 1:]
    diabetes_status = np.maximum.accumulate(diabetes_status, axis=2)
    diabetes_mat_list.append(diabetes_status)



#%% 
diabetes_mat_list[1].shape

#%%
from prevalence_3d import *
get_prevalence_3d(age_matrix_vec, diabetes_mat_list, -28)

get_overall_prevalence_3d(age_matrix_vec, diabetes_mat_list, -28)

#%% save diabetes matrix
for i in range(8):
    np.save(f'../future_data_1990_2050/diabetes_matrix/diabetes_mat_{i}.npy', diabetes_mat_list[i])

#%% load diabetes matrix and check shape
for i in range(8):
    diabetes_mat = np.load(f'../future_data_1990_2050/diabetes_matrix/diabetes_mat_{i}.npy')
    print(f"Loaded: diabetes_mat_{i}.npy with shape {diabetes_mat.shape}")
# %%
import matplotlib.pyplot as plt
import numpy as np
import os

diabetes_final_result = get_prevalence_3d(age_matrix_vec, diabetes_mat_list, -28)
age_labels = ["18-29", "30-39", "40-49", "50-59", "60-69", "70-74"]
targeting_diabeteslist = np.array([ 8.2, 5.8, 13.5, 12.4, 19.1, 14.4, 0.2 , 1.9, 5.0, 10.8, 21.8, 24.2])

# Extracting relevant slices
simulated_prevalence = diabetes_final_result[6:11] * 100
nphs_prevalence = targeting_diabeteslist[6:11] 
age_labels = age_labels[:-1]
# Plotting
plt.figure(figsize=(8, 5))

plt.plot(age_labels, simulated_prevalence, marker='o', linestyle='-', label="Simulated Prevalence", markersize=6)
plt.plot(age_labels, nphs_prevalence, marker='o', linestyle='-', label="2022 NPHS Prevalence", markersize=6)
plt.ylim(0,50)
plt.xlabel("Age Group")
plt.ylabel("Prevalence (%)")
plt.title("Diabetes Prevalence by Age Group")
plt.legend()


# Create the directory if it doesn't exist
plots_dir = "plots"
os.makedirs(plots_dir, exist_ok=True)

# Save the plot
plot_path = os.path.join(plots_dir, "Diabetes_2022.png")
plt.savefig(plot_path, dpi=300, bbox_inches='tight')

plt.show()
#%%
nphs_prevalence
#%%
diabetes_final_result = get_prevalence_3d(age_matrix_vec, diabetes_mat_list, -28)
targeting_diabeteslist = np.array([ 8.2, 5.8, 13.5, 12.4, 19.1, 14.4, 0.2 , 1.9, 5.0, 10.8, 21.8, 24.2])
# Extracting relevant slices
simulated_prevalence = diabetes_final_result[:6] * 100
nphs_prevalence = targeting_diabeteslist[:6] 
ethnicity_gender_labels = ['chn male', 'chn female', 'mal male' ,'mal female', 'ind male', 'ind female']
# Plotting
plt.figure(figsize=(8, 5))

x = np.arange(len(ethnicity_gender_labels))
width = 0.35

plt.bar(x - width/2, simulated_prevalence, width, label="Simulated Prevalence")
plt.bar(x + width/2, nphs_prevalence, width, label="2022 NPHS Prevalence")
plt.ylim(0,50)
plt.xlabel("Ethnicity and Gender")
plt.ylabel("Prevalence (%)")
plt.title("Diabetes Prevalence by Ethnicity and Gender")
plt.xticks(x, ethnicity_gender_labels)
plt.legend()


# Create the directory if it doesn't exist
plots_dir = "plots"
os.makedirs(plots_dir, exist_ok=True)

# Save the plot
plot_path = os.path.join(plots_dir, "Diabetes_2022.png")
plt.savefig(plot_path, dpi=300, bbox_inches='tight')

plt.show()
#%%
