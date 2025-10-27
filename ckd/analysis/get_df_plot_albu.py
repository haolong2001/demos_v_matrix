
#%%
from Age_BMI_loading import age_matrix_vec
import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd

#%%

def get_overall_pre_prevalence(age_matrix_vec, diabetes_mat_list, k, pre_diabete_val=0.5):
    """
    Calculate overall pre-diabetes prevalence for each ethnicity-gender group in age range 18-74.

    Parameters:
        age_matrix_vec (list): List of age matrices for different groups.

        diabetes_mat_list (list): List of diabetes matrices for different groups.
        k (int): Column index to use for ages in age_matrix_vec.(use negative index)
        pre_diabete_val (float): Value to identify pre-diabetic individuals (default: 0.5).

    Returns:
        dict: Gender-based and ethnicity-based prevalence with overall statistics and age-specific prevalence.
    """
    import numpy as np

    # Define age groups
    age_groups = [(18, 29), (30, 39), (40, 49), (50, 59), (60, 69), (70, 79),(80,200)]

    # Initialize lists for counts for each ethnicity-gender group
    total_diabetic_people = [0] * 8
    total_people = [0] * 8
    
    # Initialize matrices for age-specific prevalence
    diabetes_total_counts_mat = np.zeros((8, len(age_groups)))  # Number of people in each age group
    diabetes_counts_mat = np.zeros((8, len(age_groups)))  # Number of pre-diabetic people in each age group
    
    # Iterate over each ethnicity-gender group
    for idx in range(8):
        last_col_ages = age_matrix_vec[idx][:, k]  # Column k of age matrix
        last_col_diabetes = diabetes_mat_list[idx][:, k]  # Column k of diabetes matrix

        # Compute overall diabetes prevalence for idx in age range 18-74
        mask_all = (last_col_ages >= 18) & (last_col_ages <= 200)
        total_people[idx] = np.sum(mask_all)
        total_diabetic_people[idx] = np.sum(last_col_diabetes[mask_all] == pre_diabete_val)
        
        # Assign people to age groups and count
        for group_idx, (lower, upper) in enumerate(age_groups):
            mask = (last_col_ages >= lower) & (last_col_ages <= upper)

            diabetes_total_counts_mat[idx, group_idx] = np.sum(mask)  # Total people in age group
            diabetes_counts_mat[idx, group_idx] = np.sum(last_col_diabetes[mask] == pre_diabete_val)  # Pre-diabetic people in age group
    # Define index lists for different groups
    male_indices = [0, 2, 4, 6]
    female_indices = [1, 3, 5, 7]
    chinese_indices = [0, 1]
    malay_indices = [2, 3]
    indian_indices = [4, 5]
    
    # Calculate gender-based prevalence
    # Male groups
    male_diabetic = sum(total_diabetic_people[i] for i in male_indices)
    male_total = sum(total_people[i] for i in male_indices)
    male_prevalence = male_diabetic / male_total if male_total > 0 else 0
    
    # Female groups
    female_diabetic = sum(total_diabetic_people[i] for i in female_indices)
    female_total = sum(total_people[i] for i in female_indices)
    female_prevalence = female_diabetic / female_total if female_total > 0 else 0
    
    # Calculate ethnicity-based prevalence
    # Chinese
    chinese_diabetic = sum(total_diabetic_people[i] for i in chinese_indices)
    chinese_total = sum(total_people[i] for i in chinese_indices)
    chinese_prevalence = chinese_diabetic / chinese_total if chinese_total > 0 else 0
    
    # Malay
    malay_diabetic = sum(total_diabetic_people[i] for i in malay_indices)
    malay_total = sum(total_people[i] for i in malay_indices)
    malay_prevalence = malay_diabetic / malay_total if malay_total > 0 else 0
    
    # Indian
    indian_diabetic = sum(total_diabetic_people[i] for i in indian_indices)
    indian_total = sum(total_people[i] for i in indian_indices)
    indian_prevalence = indian_diabetic / indian_total if indian_total > 0 else 0
    
    # Calculate overall prevalence
    overall_diabetic = sum(total_diabetic_people)
    overall_total = sum(total_people)
    overall_prevalence = overall_diabetic / overall_total if overall_total > 0 else 0
    
    # Compute age-specific pre-diabetes prevalence
    diabetes_age_specific_prevalence = np.divide(
        diabetes_counts_mat.sum(axis=0),
        diabetes_total_counts_mat.sum(axis=0),
        out=np.zeros_like(diabetes_counts_mat.sum(axis=0)),  # Avoid division by zero
        where=diabetes_total_counts_mat.sum(axis=0) > 0
    )
    
    # Return comprehensive results
    return {
        'gender': {
            'male': male_prevalence,
            'female': female_prevalence
        },
        'ethnicity': {
            'chinese': chinese_prevalence,
            'malay': malay_prevalence,
            'indian': indian_prevalence
        },
        'overall': overall_prevalence,
        'age_specific': diabetes_age_specific_prevalence
    }


def get_pre_prevalence(age_matrix_vec, diabetes_mat_list, k):
    """
    Calculate diabetes prevalence for each ethnicity-gender group and age-specific prevalence.

    Parameters:
        age_matrix_vec (list): List of age matrices for different groups.
    """

    return get_overall_pre_prevalence(age_matrix_vec, diabetes_mat_list, k, pre_diabete_val=1)

#%% 


#%% 
#%%
# Load the saved matrices and check their sizes
albu_mat_storage = []
for i in range(8):
    filename = f'../future_data_1990_2050/albu_matrix_forecast/albu_mat_group_{i}.npy'
    loaded_array = np.load(filename) 
    albu_mat_storage.append(loaded_array)
    print(f"Loaded group {i} array from {filename}, shape: {loaded_array.shape}")



#%% save the results
# import os
# N = 8


# # Create albu_1_mat_storage: list of arrays where each array has shape (len(A_range), albu_matrix.shape[0], albu_matrix.shape[1], albu_matrix.shape[2])
# albu_mat_storage = []

# # For each group i, create an array that stacks matrices from all A values
# for i in range(N):
#     # Get the shape from the first A value's matrix for group i
#     first_matrix = albu_mat_list_overall[0][i]  # A_range[0], group i
#     matrix_shape = first_matrix.shape
    
#     # Initialize array to hold matrices for all A values for this group
#     # Shape: (len(A_range), simulation_times, individuals, years)
#     group_array = np.zeros((len(A_range), matrix_shape[0], matrix_shape[1], matrix_shape[2]))
    
#     # Fill the array with matrices from each A value
#     for A_idx in range(len(A_range)):
#         group_array[A_idx] = albu_mat_list_overall[A_idx][i]
    
#     albu_mat_storage.append(group_array)







#%% 
# Load age matrix 
age_matrix_vec = []
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
    age_matrix_vec.append(filtered_matrix)
    print(f"Loaded: {file_path} with shape {filtered_matrix.shape}")

print(f"\nLoaded {len(age_matrix_vec)} age matrices into age_matrix_vec")

# 
# Calculate pre-prevalence for each simulation and each year from -61 to 0
import pandas as pd
import matplotlib.pyplot as plt

#%%

# Create lists to store matrices for simulations
# simulation_times,years, grouped prevalence

#%%
micro_albu_mat_list = []


# For each simulation (t) and group (k), extract prevalence data
total_num_simu = albu_mat_storage[0].shape[1]
total_num_para = albu_mat_storage[0].shape[0]  # Use albu_mat_storage dimensions instead
print(f"Total number of simulations: {total_num_simu}")
print(f"Total number of parameters: {total_num_para}")

for albu_para_num in range(0, total_num_para):  # Using parameter dimension from albu_mat_storage
    for num_sim in range(0, total_num_simu):  # Using simulation dimension
        #print(f"Processing albu_para_num: {albu_para_num}, num_sim: {num_sim}")
        age_matrix_vec_sample = [matrix[num_sim,:,:] for matrix in age_matrix_vec]
        micro_albu_mat_list_sim = []
        
        # Extract matrices for this simulation
        for matrix in albu_mat_storage:
            # Extract the albu_para_num-th parameter, num_sim-th simulation slice
            matrix_2d = matrix[albu_para_num, num_sim, :, :]
            micro_albu_mat_list_sim.append(matrix_2d)

        pre_micro_albu_mat_list = []

        # Calculate prevalence for each time point
        for time_k in range(-61, 0):    
            overall_micro_prevalence = get_overall_pre_prevalence(age_matrix_vec_sample, micro_albu_mat_list_sim, time_k)   
            overall_macro_prevalence = get_pre_prevalence(age_matrix_vec_sample, micro_albu_mat_list_sim, time_k)
            # Store both prevalences together (as tuple, dict, or list as needed)
            prevalence_data = {
                'micro': overall_micro_prevalence,
                'macro': overall_macro_prevalence
            }
            pre_micro_albu_mat_list.append(prevalence_data)
        
        # Store the prevalence data for this simulation
        micro_albu_mat_list.append(pre_micro_albu_mat_list)

#%%
# matrix.shape
# # (5, 11, 93313, 61)

#%%
# Check the shape and structure of micro_albu_mat_list
print(f"Shape of micro_albu_mat_list: {len(micro_albu_mat_list)}")
print(f"Type of micro_albu_mat_list: {type(micro_albu_mat_list)}")

if len(micro_albu_mat_list) > 0:
    print(f"Shape of micro_albu_mat_list[0]: {len(micro_albu_mat_list[0])}")
    print(f"Type of micro_albu_mat_list[0]: {type(micro_albu_mat_list[0])}")
    
    if len(micro_albu_mat_list[0]) > 0:
        print(f"Type of micro_albu_mat_list[0][0]: {type(micro_albu_mat_list[0][0])}")
        print(f"First element of micro_albu_mat_list[0]:")
        print(micro_albu_mat_list[0][0])
        
        # If it's a dictionary, show its keys and structure
        if isinstance(micro_albu_mat_list[0][0], dict):
            print(f"Keys in micro_albu_mat_list[0][0]: {micro_albu_mat_list[0][0].keys()}")
            for key, value in micro_albu_mat_list[0][0].items():
                print(f"  {key}: {type(value)} - {value}")
else:
    print("micro_albu_mat_list is empty")


#%%
# Check the shape of micro_albu_mat_list
print(f"Shape of micro_albu_mat_list: {len(micro_albu_mat_list)}")
print(f"Type of micro_albu_mat_list: {type(micro_albu_mat_list)}")

# Print the lengths as requested
if len(micro_albu_mat_list) > 0:
    print(f"len(micro_albu_mat_list): {len(micro_albu_mat_list)}")
    if len(micro_albu_mat_list[0]) > 0:
        print(f"len(micro_albu_mat_list[0]): {len(micro_albu_mat_list[0])}")
    else:
        print("micro_albu_mat_list[0] is empty")
else:
    print("micro_albu_mat_list is empty")



print(micro_albu_mat_list[0][0])


#%%
# Create a DataFrame with the requested structure
# Columns: year, simu_num, male, female, chinese, malay, indian, age groups (18-29), (30-39), (40-49), (50-59), (60-69), (70-79), (80+)
# Rows: each row represents one year in one simulation

# Define column names
columns = ['year', 'simu_num', 'overall', 'male', 'female', 'chinese', 'malay', 'indian', 
           '(18, 29)', '(30, 39)', '(40, 49)', '(50, 59)', 
           '(60, 69)', '(70, 79)', '(80 +)']

# Define years from 1990 to 2050
years = list(range(1990, 2051))

# Initialize list to collect all rows for micro albuminuria
rows_list_micro = []

# Fill the DataFrame with prevalence data from micro_albu_mat_list
# Each element in micro_albu_mat_list contains prevalence data for one simulation
simulation_count = len(micro_albu_mat_list)

# Loop through all simulations
for sim_idx in range(simulation_count):
    simulation_data = micro_albu_mat_list[sim_idx]
    
    # Loop through all years in this simulation
    for year_idx, year_data in enumerate(simulation_data):
        current_year = years[year_idx]
        
        # Extract micro albuminuria data from the nested structure
        micro_data = year_data['micro']
        
        # Create a row dictionary for this year and simulation
        row = {
            'year': current_year,
            'simu_num': sim_idx,
            'overall': micro_data['overall'],
            'male': micro_data['gender']['male'],
            'female': micro_data['gender']['female'],
            'chinese': micro_data['ethnicity']['chinese'],
            'malay': micro_data['ethnicity']['malay'],
            'indian': micro_data['ethnicity']['indian']
        }
        
        # Extract age-specific data
        age_specific_data = micro_data['age_specific']
        age_columns = ['(18, 29)', '(30, 39)', '(40, 49)', '(50, 59)', 
                       '(60, 69)', '(70, 79)', '(80 +)']
        
        for age_idx, age_col in enumerate(age_columns):
            row[age_col] = age_specific_data[age_idx]
        
        # Add this row to the list
        rows_list_micro.append(row)

# Create DataFrame from the list of rows for micro albuminuria
df_micro_albu = pd.DataFrame(rows_list_micro, columns=columns)

print(f"Micro albuminuria DataFrame shape: {df_micro_albu.shape}")
print(f"First few rows:")
print(df_micro_albu.head())

# Initialize list to collect all rows for macro albuminuria
rows_list_macro = []

# Fill the DataFrame with prevalence data for macro albuminuria from the same data structure
# Loop through all simulations
for sim_idx in range(simulation_count):
    simulation_data = micro_albu_mat_list[sim_idx]  # Using the same list since it contains both micro and macro data
    
    # Loop through all years in this simulation
    for year_idx, year_data in enumerate(simulation_data):
        current_year = years[year_idx]
        
        # Extract macro albuminuria data from the nested structure
        macro_data = year_data['macro']
        
        # Create a row dictionary for this year and simulation
        row = {
            'year': current_year,
            'simu_num': sim_idx,
            'overall': macro_data['overall'],
            'male': macro_data['gender']['male'],
            'female': macro_data['gender']['female'],
            'chinese': macro_data['ethnicity']['chinese'],
            'malay': macro_data['ethnicity']['malay'],
            'indian': macro_data['ethnicity']['indian']
        }
        
        # Extract age-specific data
        age_specific_data = macro_data['age_specific']
        age_columns = ['(18, 29)', '(30, 39)', '(40, 49)', '(50, 59)', 
                       '(60, 69)', '(70, 79)', '(80 +)']
        
        for age_idx, age_col in enumerate(age_columns):
            row[age_col] = age_specific_data[age_idx]
        
        # Add this row to the list
        rows_list_macro.append(row)

# Create DataFrame from the list of rows for macro albuminuria
df_macro_albu = pd.DataFrame(rows_list_macro, columns=columns)

print(f"Macro albuminuria DataFrame shape: {df_macro_albu.shape}")
print(f"First few rows:")
print(df_macro_albu.head())

#%%

print(f"Micro albuminuria DataFrame after averaging across {simulation_count} simulations:")
print(df_micro_albu.head())

if not df_macro_albu.empty:
    print(f"Macro albuminuria DataFrame after averaging across {len(micro_albu_mat_list)} simulations:")
    print(df_macro_albu.head())

# Save the DataFrames to the results_df folder
import os
# Create the results_df directory if it doesn't exist
results_dir = '../results_df/'
os.makedirs(results_dir, exist_ok=True)

# Save the micro albuminuria DataFrame as CSV
output_filename_micro = 'df_micro_albu.csv'
output_filepath_micro = os.path.join(results_dir, output_filename_micro)
df_micro_albu.to_csv(output_filepath_micro)

print(f"Micro albuminuria DataFrame saved to: {output_filepath_micro}")
print(f"Micro albuminuria DataFrame shape: {df_micro_albu.shape}")

# Save the macro albuminuria DataFrame as CSV if it exists
if not df_macro_albu.empty:
    output_filename_macro = 'df_macro_albu.csv'
    output_filepath_macro = os.path.join(results_dir, output_filename_macro)
    df_macro_albu.to_csv(output_filepath_macro)
    
    print(f"Macro albuminuria DataFrame saved to: {output_filepath_macro}")
    print(f"Macro albuminuria DataFrame shape: {df_macro_albu.shape}")


#%%

# Create 4x2 plot for albuminuria prevalence from 1990 to 2050 (micro and macro)
import matplotlib.pyplot as plt
import numpy as np

# Filter data for the years 1990-2050
df_plot_micro = df_micro_albu[(df_micro_albu['year'] >= 1990) & (df_micro_albu['year'] <= 2050)].copy()
if not df_macro_albu.empty:
    df_plot_macro = df_macro_albu[(df_macro_albu['year'] >= 1990) & (df_macro_albu['year'] <= 2050)].copy()

# Calculate mean and 95% CI for each year and category
years = sorted(df_plot_micro['year'].unique())

def calculate_stats(data):
    """Calculate mean and 95% CI from simulation data"""
    mean_val = np.mean(data)
    ci_lower = np.percentile(data, 2.5)
    ci_upper = np.percentile(data, 97.5)
    return mean_val, ci_lower, ci_upper

# Prepare data for plotting - micro albuminuria
plot_data_micro = {}

# Overall prevalence
overall_stats = []
for year in years:
    year_data = df_plot_micro[df_plot_micro['year'] == year]
    overall_vals = year_data['overall']
    mean_val, ci_lower, ci_upper = calculate_stats(overall_vals)
    overall_stats.append((mean_val, ci_lower, ci_upper))

plot_data_micro['overall'] = overall_stats

# Gender-based prevalence
for gender in ['male', 'female']:
    gender_stats = []
    for year in years:
        year_data = df_plot_micro[df_plot_micro['year'] == year][gender]
        mean_val, ci_lower, ci_upper = calculate_stats(year_data)
        gender_stats.append((mean_val, ci_lower, ci_upper))
    plot_data_micro[gender] = gender_stats

# Ethnicity-based prevalence
for ethnicity in ['chinese', 'malay', 'indian']:
    ethnicity_stats = []
    for year in years:
        year_data = df_plot_micro[df_plot_micro['year'] == year][ethnicity]
        mean_val, ci_lower, ci_upper = calculate_stats(year_data)
        ethnicity_stats.append((mean_val, ci_lower, ci_upper))
    plot_data_micro[ethnicity] = ethnicity_stats

# Prepare data for plotting - macro albuminuria (if available)
plot_data_macro = {}
if not df_macro_albu.empty:
    # Overall prevalence
    overall_stats_macro = []
    for year in years:
        year_data = df_plot_macro[df_plot_macro['year'] == year]
        overall_vals = year_data['overall']
        mean_val, ci_lower, ci_upper = calculate_stats(overall_vals)
        overall_stats_macro.append((mean_val, ci_lower, ci_upper))

    plot_data_macro['overall'] = overall_stats_macro

    # Gender-based prevalence
    for gender in ['male', 'female']:
        gender_stats = []
        for year in years:
            year_data = df_plot_macro[df_plot_macro['year'] == year][gender]
            mean_val, ci_lower, ci_upper = calculate_stats(year_data)
            gender_stats.append((mean_val, ci_lower, ci_upper))
        plot_data_macro[gender] = gender_stats

    # Ethnicity-based prevalence
    for ethnicity in ['chinese', 'malay', 'indian']:
        ethnicity_stats = []
        for year in years:
            year_data = df_plot_macro[df_plot_macro['year'] == year][ethnicity]
            mean_val, ci_lower, ci_upper = calculate_stats(year_data)
            ethnicity_stats.append((mean_val, ci_lower, ci_upper))
        plot_data_macro[ethnicity] = ethnicity_stats

#%%
df_macro_albu.head()



#%%
# Create the 2x4 plot (transposed from 4x2)
fig, axes = plt.subplots(2, 4, figsize=(24, 12))
fig.suptitle('Albuminuria Prevalence Trends (1990-2050): Micro vs Macro', fontsize=16, fontweight='bold')

# Helper function to plot with confidence intervals
def plot_with_ci(ax, years, stats, label, color, linestyle='-'):
    means = [s[0] for s in stats]
    ci_lower = [s[1] for s in stats]
    ci_upper = [s[2] for s in stats]
    
    ax.plot(years, means, label=label, color=color, linestyle=linestyle, linewidth=2)
    ax.fill_between(years, ci_lower, ci_upper, alpha=0.2, color=color)

# Helper function to get y-axis limits for a row
def get_row_ylim(plot_data_list):
    all_means = []
    all_ci_lower = []
    all_ci_upper = []
    
    for plot_data in plot_data_list:
        if plot_data:  # Check if data exists
            for stats in plot_data.values():
                if stats:  # Check if stats list is not empty
                    means = [s[0] for s in stats]
                    ci_lower = [s[1] for s in stats]
                    ci_upper = [s[2] for s in stats]
                    all_means.extend(means)
                    all_ci_lower.extend(ci_lower)
                    all_ci_upper.extend(ci_upper)
    
    if all_means:
        y_min = min(all_ci_lower)
        y_max = max(all_ci_upper)
        # Add 5% padding
        y_range = y_max - y_min
        return y_min - 0.05 * y_range, y_max + 0.05 * y_range
    else:
        return 0, 1

# First row: Overall, Gender, Ethnicity, Age groups (micro albuminuria)
row1_data = []

# Column 1: Overall prevalence (micro)
ax1 = axes[0, 0]
plot_with_ci(ax1, years, plot_data_micro['overall'], 'Overall', 'black')
ax1.set_title('Micro Albuminuria - Overall', fontweight='bold')
ax1.set_ylabel('Prevalence')
ax1.grid(True, alpha=0.3)
ax1.legend()
row1_data.append({'overall': plot_data_micro['overall']})

# Column 2: Gender-based prevalence (micro)
ax2 = axes[0, 1]
gender_colors = {'male': 'blue', 'female': 'pink'}
for gender in ['male', 'female']:
    plot_with_ci(ax2, years, plot_data_micro[gender], gender.capitalize(), gender_colors[gender])
ax2.set_title('Micro Albuminuria - Gender', fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.legend()
row1_data.append({gender: plot_data_micro[gender] for gender in ['male', 'female']})

# Column 3: Ethnicity-based prevalence (micro)
ax3 = axes[0, 2]
ethnicity_colors = {'chinese': 'red', 'malay': 'green', 'indian': 'blue'}
for ethnicity in ['chinese', 'malay', 'indian']:
    plot_with_ci(ax3, years, plot_data_micro[ethnicity], ethnicity.capitalize(), ethnicity_colors[ethnicity])
ax3.set_title('Micro Albuminuria - Ethnicity', fontweight='bold')
ax3.grid(True, alpha=0.3)
ax3.legend()
row1_data.append({ethnicity: plot_data_micro[ethnicity] for ethnicity in ['chinese', 'malay', 'indian']})

# Column 4: Age group comparisons (micro)
ax4 = axes[0, 3]
age_groups_col = ['(18, 29)', '(30, 39)', '(40, 49)', '(50, 59)', '(60, 69)', '(70, 79)', '(80 +)']
age_group_labels = ['18-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']
age_group_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']

age_group_data_micro = {}
for i, (age_label, col_name) in enumerate(zip(age_group_labels, age_groups_col)):
    age_stats = []
    for year in years:
        year_data = df_plot_micro[df_plot_micro['year'] == year][col_name]
        mean_val, ci_lower, ci_upper = calculate_stats(year_data)
        age_stats.append((mean_val, ci_lower, ci_upper))
    plot_with_ci(ax4, years, age_stats, age_label, age_group_colors[i])
    age_group_data_micro[age_label] = age_stats

ax4.set_title('Micro Albuminuria - Age Groups', fontweight='bold')
ax4.grid(True, alpha=0.3)
ax4.legend()
row1_data.append(age_group_data_micro)

# Second row: Overall, Gender, Ethnicity, Age groups (macro albuminuria)
row2_data = []

# Column 1: Overall prevalence (macro)
ax5 = axes[1, 0]
if not df_macro_albu.empty:
    plot_with_ci(ax5, years, plot_data_macro['overall'], 'Overall', 'black')
    row2_data.append({'overall': plot_data_macro['overall']})
else:
    row2_data.append({})
ax5.set_title('Macro Albuminuria - Overall', fontweight='bold')
ax5.set_ylabel('Prevalence')
ax5.set_xlabel('Year')
ax5.grid(True, alpha=0.3)
ax5.legend()

# Column 2: Gender-based prevalence (macro)
ax6 = axes[1, 1]
if not df_macro_albu.empty:
    for gender in ['male', 'female']:
        plot_with_ci(ax6, years, plot_data_macro[gender], gender.capitalize(), gender_colors[gender])
    row2_data.append({gender: plot_data_macro[gender] for gender in ['male', 'female']})
else:
    row2_data.append({})
ax6.set_title('Macro Albuminuria - Gender', fontweight='bold')
ax6.set_xlabel('Year')
ax6.grid(True, alpha=0.3)
ax6.legend()

# Column 3: Ethnicity-based prevalence (macro)
ax7 = axes[1, 2]
if not df_macro_albu.empty:
    for ethnicity in ['chinese', 'malay', 'indian']:
        plot_with_ci(ax7, years, plot_data_macro[ethnicity], ethnicity.capitalize(), ethnicity_colors[ethnicity])
    row2_data.append({ethnicity: plot_data_macro[ethnicity] for ethnicity in ['chinese', 'malay', 'indian']})
else:
    row2_data.append({})
ax7.set_title('Macro Albuminuria - Ethnicity', fontweight='bold')
ax7.set_xlabel('Year')
ax7.grid(True, alpha=0.3)
ax7.legend()

# Column 4: Age group comparisons (macro)
ax8 = axes[1, 3]
if not df_macro_albu.empty:
    age_group_data_macro = {}
    for i, (age_label, col_name) in enumerate(zip(age_group_labels, age_groups_col)):
        age_stats = []
        for year in years:
            year_data = df_plot_macro[df_plot_macro['year'] == year][col_name]
            mean_val, ci_lower, ci_upper = calculate_stats(year_data)
            age_stats.append((mean_val, ci_lower, ci_upper))
        plot_with_ci(ax8, years, age_stats, age_label, age_group_colors[i])
        age_group_data_macro[age_label] = age_stats
    row2_data.append(age_group_data_macro)
else:
    row2_data.append({})

ax8.set_title('Macro Albuminuria - Age Groups', fontweight='bold')
ax8.set_xlabel('Year')
ax8.grid(True, alpha=0.3)
ax8.legend()

# Set same y-limits for each row
row1_ylim = get_row_ylim(row1_data)
row2_ylim = get_row_ylim(row2_data)

# Apply y-limits to first row
for ax in axes[0, :]:
    ax.set_ylim(row1_ylim)

# Apply y-limits to second row
for ax in axes[1, :]:
    ax.set_ylim(row2_ylim)

# Adjust layout to prevent overlapping
plt.tight_layout()
plt.subplots_adjust(top=0.95)

# Save the plot
plot_output_dir = '../results_plots/'
os.makedirs(plot_output_dir, exist_ok=True)
plot_filename = 'albuminuria_prevalence_trends_micro_macro_2x4_1990_2050.png'
plot_filepath = os.path.join(plot_output_dir, plot_filename)
plt.savefig(plot_filepath, dpi=300, bbox_inches='tight')

print(f"Plot saved to: {plot_filepath}")
plt.show()

#%%
micro_albu_mat_list_sim[0].shape
# %%
# Extract age group prevalence trends from both micro and macro albuminuria DataFrames
age_group_labels = ['18-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']
age_groups_col = ['(18, 29)', '(30, 39)', '(40, 49)', '(50, 59)', '(60, 69)', '(70, 79)', '(80 +)']

# Create a 2x4 panel plot for age group prevalence trends (micro and macro combined)
fig, axes = plt.subplots(2, 4, figsize=(20, 10))
fig.suptitle('Albuminuria Prevalence Trends by Age Group (1990-2050): Micro vs Macro', fontsize=16, fontweight='bold')

# Flatten axes for easier iteration
axes_flat = axes.flatten()

# Get years for plotting
years = sorted(df_micro_albu['year'].unique())
years_filtered = [year for year in years if 1990 <= year <= 2050]

# Colors for micro and macro albuminuria
micro_color = 'blue'
macro_color = 'red'

# First pass: collect all data to calculate y-axis limits for each age group
all_age_group_stats_micro = []
all_age_group_stats_macro = []

for i, (label, col_name) in enumerate(zip(age_group_labels, age_groups_col)):
    # Collect prevalence data for this age group across all years - micro
    age_group_stats_micro = []
    for year in years_filtered:
        year_data = df_micro_albu[df_micro_albu['year'] == year][col_name]
        mean_val, ci_lower, ci_upper = calculate_stats(year_data)
        age_group_stats_micro.append((mean_val, ci_lower, ci_upper))
    all_age_group_stats_micro.append(age_group_stats_micro)
    
    # Collect prevalence data for this age group across all years - macro
    if not df_macro_albu.empty:
        age_group_stats_macro = []
        for year in years_filtered:
            year_data = df_macro_albu[df_macro_albu['year'] == year][col_name]
            mean_val, ci_lower, ci_upper = calculate_stats(year_data)
            age_group_stats_macro.append((mean_val, ci_lower, ci_upper))
        all_age_group_stats_macro.append(age_group_stats_macro)
    else:
        all_age_group_stats_macro.append([])

# Plot each age group in a separate panel
for i, (label, col_name) in enumerate(zip(age_group_labels, age_groups_col)):
    ax = axes_flat[i]
    
    # Use pre-calculated stats for micro
    age_group_stats_micro = all_age_group_stats_micro[i]
    
    # Extract means and confidence intervals for micro
    means_micro = [s[0] for s in age_group_stats_micro]
    ci_lower_micro = [s[1] for s in age_group_stats_micro]
    ci_upper_micro = [s[2] for s in age_group_stats_micro]
    
    # Plot micro with confidence intervals
    ax.plot(years_filtered, means_micro, color=micro_color, linewidth=2, marker='o', markersize=3, label='Micro')
    ax.fill_between(years_filtered, ci_lower_micro, ci_upper_micro, alpha=0.2, color=micro_color)
    
    # Plot macro if available
    if not df_macro_albu.empty and len(all_age_group_stats_macro[i]) > 0:
        age_group_stats_macro = all_age_group_stats_macro[i]
        
        # Extract means and confidence intervals for macro
        means_macro = [s[0] for s in age_group_stats_macro]
        ci_lower_macro = [s[1] for s in age_group_stats_macro]
        ci_upper_macro = [s[2] for s in age_group_stats_macro]
        
        # Plot macro with confidence intervals
        ax.plot(years_filtered, means_macro, color=macro_color, linewidth=2, marker='s', markersize=3, label='Macro')
        ax.fill_between(years_filtered, ci_lower_macro, ci_upper_macro, alpha=0.2, color=macro_color)
    
    # Customize each panel
    ax.set_title(f'Age Group: {label}', fontweight='bold', fontsize=12)
    ax.set_xlabel('Year', fontsize=10)
    ax.set_ylabel('Prevalence', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.legend()

# Hide the 8th panel (since we only have 7 age groups)
axes_flat[7].set_visible(False)

# Adjust layout
plt.tight_layout()
plt.subplots_adjust(top=0.93)

# Save the plot
plot_output_dir = '../results_plots/'
os.makedirs(plot_output_dir, exist_ok=True)
plot_filename = 'albuminuria_age_group_prevalence_trends_micro_macro_2x4_1990_2050.png'
plot_filepath = os.path.join(plot_output_dir, plot_filename)
plt.savefig(plot_filepath, dpi=300, bbox_inches='tight')

print(f"Age group prevalence trends plot (2x4 panels, micro vs macro) saved to: {plot_filepath}")
plt.show()

# Print summary statistics for both micro and macro
print("\nMicro Albuminuria Age Group Prevalence Summary (1990 vs 2050):")
print("=" * 70)
for i, (label, col_name) in enumerate(zip(age_group_labels, age_groups_col)):
    # Get 1990 and 2050 data
    data_1990 = df_micro_albu[df_micro_albu['year'] == 1990][col_name]
    data_2050 = df_micro_albu[df_micro_albu['year'] == 2050][col_name]
    
    start_prev = np.mean(data_1990)
    end_prev = np.mean(data_2050)
    change = end_prev - start_prev
    pct_change = (change / start_prev * 100) if start_prev > 0 else 0
    print(f"{label}: {start_prev:.4f} → {end_prev:.4f} (Change: {change:+.4f}, {pct_change:+.1f}%)")

if not df_macro_albu.empty:
    print("\nMacro Albuminuria Age Group Prevalence Summary (1990 vs 2050):")
    print("=" * 70)
    for i, (label, col_name) in enumerate(zip(age_group_labels, age_groups_col)):
        # Get 1990 and 2050 data
        data_1990 = df_macro_albu[df_macro_albu['year'] == 1990][col_name]
        data_2050 = df_macro_albu[df_macro_albu['year'] == 2050][col_name]
        
        start_prev = np.mean(data_1990)
        end_prev = np.mean(data_2050)
        change = end_prev - start_prev
        pct_change = (change / start_prev * 100) if start_prev > 0 else 0
        print(f"{label}: {start_prev:.4f} → {end_prev:.4f} (Change: {change:+.4f}, {pct_change:+.1f}%)")

# %%
age_matrix_vec_sample[0].shape
# %%


# malay 
# micro_albu_mat_list_saved = micro_albu_mat_list
micro_albu_mat_list_saved[0][0]["overall"]
# %%
# Get overall prevalence from the -28th time point in the last simulation
len(micro_albu_mat_list_saved)

# # %%
# micro_albu_mat_list_saved[0][-28]["overall"]
# %%
