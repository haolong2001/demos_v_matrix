#%% 
import os 
import numpy as np
import matplotlib.pyplot as plt

#%% 


def schedule_pre_diabetes_probability(age, index, bmi, theta=None):
    beta = 0.2
    if theta is None:
        theta = np.array([-10.73568597 * 1.01, -11.11297803* 0.98, -10.594319 * 1.02, -10.97161203 * 1.02, -10.15266278 * 1.0, -10.52995483 * 1.02, -10.73568597, -11.11297803])
        theta = theta 
    if age < 25 and age > 18:
        prediabetesprob = 0.0001
        return prediabetesprob
    if age < 40:
        alpha = 0.045
    elif age < 50:
        alpha = 0.045
    elif age < 60:
        alpha = 0.045
    elif age < 70:
        alpha = 0.045
    else:
        alpha = 0.04
    # Compute the logistic regression probability
    exp_term = np.exp(theta[index] + alpha * age + beta * bmi)
    prediabetesprob = 1 - 1 / (1 + exp_term)
    
    return prediabetesprob 

def schedule_diabetes_probability(age, index, bmi, theta=None):
    beta = 0.18
    if theta is None:
        theta = np.array([-10.73568597 * 1.01, -11.11297803 * 0.98, -10.59431997 * 1.02, -10.971612 * 1.02, -10.15266278 * 1.02, -10.52995483 * 1.05, -10.73568597, -11.11297803* 1.03])
    if age < 18:
        diabetesprob = 0
        return diabetesprob
    if age < 25:
        diabetesprob = 0.00015
        return diabetesprob
    if age < 40:
        alpha = 0.045
    elif age < 50:
        alpha = 0.045
    elif age < 60:
        alpha = 0.045
    elif age < 70:
        alpha = 0.045
    else:
        alpha = 0.035
    # Compute the logistic regression probability
    exp_term = np.exp(theta[index] + alpha * age + beta * bmi)
    diabetesprob = 1 - 1 / (1 + exp_term)
    
    return diabetesprob 

#%% what age -- from 18 




#%% read population matrices
import os
import numpy as np

# Path to the folder containing the binary files
folder_path = "../../output/20250620_101235_2940/population"

# Initialize a list to store the matrices
forecast_matrices = []

# Loop through the binary files (forecast_matrix_0.bin to forecast_matrix_7.bin)
for i in range(8):
    file_path = os.path.join(folder_path, f"forecast_matrix_{i}.bin")
    
    # Read the binary file
    with open(file_path, "rb") as f:
        data = np.fromfile(f, dtype=np.int32)
        x = data.size // 27
    
        # Print the number of elements in the loaded data
        print(f"Number of elements in {file_path}: {data.size}")

        # Reshape the data into a matrix with 27 columns
        matrix = data.reshape((x, 27))
        filtered_matrix = matrix[~np.all(matrix < 0, axis=1)]
        forecast_matrices.append(filtered_matrix)

    print(f"File {file_path} loaded with shape: {matrix.shape}")

# check the shape of the first matrix
forecast_matrices[0].shape  # Check the shape of the first matrix



#%% read BMI matrices
import os
import numpy as np

# Path to the folder containing the binary files
folder_path = "../../output/20250620_101235_2940/BMI"

# Initialize a list to store the BMI matrices
bmi_matrices = []

# Loop through the binary files (bmi_matrix_0.bin to bmi_matrix_7.bin)
for i in range(8):
    file_path = os.path.join(folder_path, f"bmi_matrix_{i}.bin")
    
    # Read the binary file
    with open(file_path, "rb") as f:
        data = np.fromfile(f, dtype=np.int32)
        x = data.size // 27
    
        # Print the number of elements in the loaded data
        print(f"Number of elements in {file_path}: {data.size}")

        # Reshape the data into a matrix with 27 columns
        matrix = data.reshape((x, 27))
        filtered_matrix = matrix[~np.all(matrix < 0, axis=1)]
        bmi_matrices.append(filtered_matrix)

    print(f"File {file_path} loaded with shape: {matrix.shape}")

# check the shape of the first matrix
bmi_matrices[0].shape  # Check the shape of the first matrix


#%% transmission prob 

# First dimension: state transitions (0->1, 1->2)
# Second dimension: 8 groups (gender-ethnicity combinations)
# Third dimension: 21 different A values
# Fourth dimension: Ages 18-74 (57 values)
# 

prob_matrix = np.zeros((2, 8,2,57))
A_range = [0.001, 0.005]
for idx in range(8):
    for A in A_range:
        for i in range(2):
            for j in range(57):
                prob_matrix[i, idx, j, A] = schedule_pre_diabetes_probability(j, idx, A)
                prob_matrix[i, idx, j, A] = schedule_diabetes_probability(j, idx, A)

#%% 
# for every one, generate the probability for its ages before 1990
# use 1990 - 2023 population matrix;



#%% accumulated probability
healthy_prob = np.zeros((8, 2, 55))  # Shape: 8 groups x 2 A values x 55 ages
pre_diabetes = np.zeros((8, 2, 55))    # Shape: 8 groups x 2 A values x 55 ages

# Calculate probabilities for all groups
for idx in range(8):
    for A_idx, A in enumerate(A_range):
        for age_idx in range(55):  # age 20 to 74
            transition_prob = prob_matrix[0, idx, A_idx, age_idx]  # a → b
            
            if age_idx == 0:
                # For age 20, just use initial probability of staying healthy
                healthy_prob[idx, A_idx, age_idx] = 1 - transition_prob
            else:
                # For subsequent ages, multiply previous probability by probability of staying healthy
                healthy_prob[idx, A_idx, age_idx] = healthy_prob[idx, A_idx, age_idx-1] * (1 - transition_prob)

# Calculate probability of being in microalbuminuria (state b)
for idx in range(8):
    for A_idx, A in enumerate(A_range):
        prob_in_b = 0.0
        for age_idx in range(55):  # age 20 to 74
            if age_idx == 0:
                # For age 20, just use initial transition probability
                inflow = prob_matrix[0, idx, A_idx, age_idx]
            else:
                # Inflow from a → b in current age
                inflow = healthy_prob[idx, A_idx, age_idx-1] * prob_matrix[0, idx, A_idx, age_idx]
            
            # Surviving from previous b state (did not go to c)
            prob_in_b = prob_in_b * (1 - prob_matrix[1, idx, A_idx, age_idx]) + inflow
            
            # Store result
            pre_diabetes[idx, A_idx, age_idx] = prob_in_b


#%% plot and compare the results 


# use different age groups 
for A_idx, A in [(0,-1), (1,1)]:
    total_counts = 0
    total_micro_counts = 0 
    total_healthy_counts = 0

    for i in range(8):
        # Get age counts from age matrix for this ethnicity
        age_counts = np.zeros(75-18)  # Vector to store counts for ages 18-74
        
        # Create dictionary to count ages
        age_dict = {}
        for age_val in age_matrix_vec[i][:,-34]: # - 34 means first column
            age_dict[age_val] = age_dict.get(age_val, 0) + 1
        
        # Convert dictionary counts to vector
        for age in range(18, 75):
            age_counts[age-18] = age_dict.get(age, 0)
        
        # Get micro albuminuria and healthy rates for this ethnicity
        micro_rates = micro_albu[i,A_idx]
        healthy_rates = healthy_prob[i,A_idx,:]
        
        micro_counts = micro_rates * age_counts[2:] # 2: means from age 20
        healthy_counts = healthy_rates * age_counts[2:]
        
        
        total_micro_counts += np.sum(micro_counts)
        total_healthy_counts += np.sum(healthy_counts)
        total_healthy_counts += np.sum(age_counts[:2])
        total_counts += np.sum(age_counts)

    micro_result = total_micro_counts / total_counts * 100
    healthy_result = total_healthy_counts / total_counts * 100
    macro_result = 100 - micro_result - healthy_result

# calculate when it's limited to 0,1; 2,3;4,5;6,7

# calculate when limit the age groups 
age_groups = [(18, 29), (30, 39), (40, 49), (50, 59), (60, 69), (70, 74)] 


#%% 

