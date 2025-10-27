import os
import numpy as np
import pandas as pd

# List to store the NumPy arrays (equivalent to std::vector<ArrayXXi> in C++)
age_matrix_vec = []

# Number of files to read
num_files = 8  # Change this to the actual number of files to read

path = "/Users/haolong/Documents/demos_v_matrix/output/Historical_data/"
for i in range(num_files):
    # Create the filename dynamically

    filename = f"popu_matrix_{i}.csv"
    matrix = pd.read_csv(path + filename).to_numpy() # convert to numpy
    
    
    filtered_matrix = matrix[~np.all(matrix < 0, axis=1)]
    age_matrix_vec.append(filtered_matrix)



# loading BMI values
N = 8 
parent_dir = "../data/bmi_matrix" 
bmi_matrix_ls = []
for idx in range(N):
    file_path = os.path.join(parent_dir, f"bmi_matrix_{idx}.npy")
    matrix = np.load(file_path)
    bmi_matrix_ls.append(matrix)

# Load pre 1990 population 
age_dict = [{} for _ in range(N)]
for i in range(N):
    ages = age_matrix_vec[i][:,0]
    # convert ages of 18 - 74 
    max_age = np.max(ages)
    for age in ages:
        if age >= 18 and age <= max_age:
            if age not in age_dict[i]:
                age_dict[i][age] = 1
            else:
                age_dict[i][age] += 1

# load 1990 BMI values 
bmi_samples_dict = {}
for group in range(N):
    bmi_samples_dict[group] = {}
    for age in age_dict[group]:
        file_path = f"../data/bmi_samples/bmi_samples_group{group}_age{age}.npy"
        try:
            bmi_samples = np.load(file_path)
            bmi_samples_dict[group][age] = bmi_samples
        except FileNotFoundError:
            print(f"File not found: {file_path}")



# Load all age matrices from the saved files
age_matrix_vec_2050 = []
age_dir = '../future_data_1990_2050/age_matrix/'

for i in range(8):
    filename = f"age_matrix_{i}.npy"
    file_path = os.path.join(age_dir, filename)
    age_matrix = np.load(file_path)
    # Handle the additional simulation dimension
    # Filter out negative values across the last two dimensions (keeping simulation dimension)
    if len(age_matrix.shape) == 3:  # (simulation_times, individuals, years)
        filtered_matrix = age_matrix[:, ~np.all(age_matrix < 0, axis=2).any(axis=0)]
    else:  # Fallback for 2D case
        filtered_matrix = age_matrix[~np.all(age_matrix < 0, axis=1)]
    age_matrix_vec_2050.append(filtered_matrix)
    print(f"Loaded: {file_path} with shape {filtered_matrix.shape}")

# print(f"\nLoaded {len(age_matrix_vec_2050)} age matrices into age_matrix_vec_2050")





