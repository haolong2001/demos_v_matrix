import os
import numpy as np
from multiprocess import Pool
from functools import partial
from tqdm import tqdm
from impute_bmi import apply_bmi  # your custom function

def load_age_matrices(age_dir):
    age_matrix_vec = []
    for i in tqdm(range(8), desc="Loading age matrices"):
        filename = f"age_matrix_{i}.npy"
        file_path = os.path.join(age_dir, filename)
        age_matrix = np.load(file_path)
        # Filter out negative values across last two dimensions
        if len(age_matrix.shape) == 3:  # (simulations, individuals, years)
            filtered_matrix = age_matrix[:, ~np.all(age_matrix < 0, axis=2).any(axis=0)]
        else:  # fallback 2D
            filtered_matrix = age_matrix[~np.all(age_matrix < 0, axis=1)]
        age_matrix_vec.append(filtered_matrix)
        print(f"Loaded: {file_path} with shape {filtered_matrix.shape}")
    return age_matrix_vec

def process_simulation(sim, age_matrix_vec):
    """Process a single simulation across all age groups"""
    bmi_matrices_for_sim = []
    for idx in range(8):  # 8 age groups
        matrix = age_matrix_vec[idx][sim]  # select this simulation
        temp = np.apply_along_axis(lambda row: apply_bmi(row, idx), 1, matrix)
        bmi_matrices_for_sim.append(temp)
    return sim, bmi_matrices_for_sim

def main():
    age_dir = '../future_data_1990_2050/age_matrix/'
    age_matrix_vec = load_age_matrices(age_dir)

    num_sims = age_matrix_vec[0].shape[0]  # adjust as needed
    print(f"Number of simulations: {num_sims}")
    # Use partial to pass extra argument to pool
    worker = partial(process_simulation, age_matrix_vec=age_matrix_vec)

    with Pool() as pool:
        results = list(tqdm(pool.imap(worker, range(num_sims)), 
                           total=num_sims, 
                           desc="Processing simulations"))

    # Sort results by simulation index
    results.sort(key=lambda x: x[0])

    # Reorganize by age group
    bmi_matrix_ls = []
    for idx in tqdm(range(8), desc="Reorganizing by age group"):
        bmi_matrix_3d = [results[sim][1][idx] for sim in range(num_sims)]
        bmi_matrix_ls.append(np.array(bmi_matrix_3d))

    print(f"Built {len(bmi_matrix_ls)} age-group matrices")
    print(f"Shape of first age group: {bmi_matrix_ls[0].shape}")

    # 

    # modification 

    

    # Assuming 'age_matrix_vec' is available as a list of matrices matching the 8 cohorts.
    # If 'age_matrix_vec' contains the shape (n_albu, n_sim, n_people, n_year), 
    # we will slice index [0] to match the BMI shape (n_sim, n_people, n_year).

    for i in range(len(bmi_matrix_ls)):
        bmi_matrix = bmi_matrix_ls[i]
        age_raw = age_matrix_vec[i]
        
        # Handle dimensions: Ensure we have (n_sim, n_people, n_year)
        if age_raw.ndim == 4:
            # If shape is (n_albu, n_sim, n_people, n_year), take the first slice
            current_age_matrix = age_raw[0]
        else:
            current_age_matrix = age_raw

        # Get the number of years (axis 2)
        n_years = bmi_matrix.shape[2]
        
        # Iterate chronologically starting from index 1 (Year 1991 onwards)
        for t in range(1, n_years):
            # 1. Identify individuals currently strictly older than 80
            #    (Masking avoids modifying dead/non-existent people with age -1/-2)
            mask_over_80 = current_age_matrix[:, :, t] > 80
            
            # 2. For these individuals, overwrite current BMI with previous year's BMI
            #    Since we loop forward, this carries the 'Age 80' value forward indefinitely.
            bmi_matrix[:, :, t][mask_over_80] = bmi_matrix[:, :, t-1][mask_over_80]

        print(f"Applied BMI clamp (freeze > age 80) for cohort {i}")
        
        # Store the modified matrix back into the list
        bmi_matrix_ls[i] = bmi_matrix



    # Save matrices
    parent_dir = "../future_data_1990_2050/bmi_matrix"
    os.makedirs(parent_dir, exist_ok=True)
    for idx, matrix in tqdm(enumerate(bmi_matrix_ls), 
                           total=len(bmi_matrix_ls), 
                           desc="Saving matrices"):
        file_path = os.path.join(parent_dir, f"bmi_matrix_{idx}.npy")
        np.save(file_path, matrix)
        print(f"Saved: {file_path} with shape {matrix.shape}")

if __name__ == "__main__":
    main()
