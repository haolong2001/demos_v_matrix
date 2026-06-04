# %% diabetes in above 51

print(f"Calculating annual diabetes prevalence for Age 51+ ({years[0]}-{years[-1]})...")

n_groups = 8
for i in range(n_groups):
    # 1. Load the matrices
    # Shape: (n_sim, n_people, n_year)
    diab_mat = diabetes_mat_storage[i]
    
    # Shape: (n_albu, n_sim, n_people, n_year)
    age_mat = age_matrix_vec[i]

    # 2. Broadcast Diabetes to match Age Matrix (n_albu axis)
    # Expand dims to (1, n_sim, n_people, n_year) then broadcast

    # 3. Create the Masks
    # Filter: Age >= 51 (automatically excludes -1 and -2)
    diab_cases = (diab_mat == 1) & (age_mat >= 51)

    yearly_population_51_plus += np.sum(age_mat >= 51, axis=(0, 1))
    yearly_diabetes_51_plus += np.sum(diab_cases, axis=(0, 1))
        # 4. Calculate Prevalence
prevalence_series = np.zeros(n_years)
valid_years = yearly_population_51_plus > 0

prevalence_series[valid_years] = (
    yearly_diabetes_51_plus[valid_years] / yearly_population_51_plus[valid_years]
) * 100

# 5. Output Results
results_df = pd.DataFrame({
    'Year': years,
    'Population_50_Plus': yearly_population_51_plus,
    'Diabetes_Cases': yearly_diabetes_51_plus,
    'Prevalence_Percentage': prevalence_series
})

print("\n--- Results Summary (First 5, Middle, Last 5) ---")
print(results_df.iloc[np.r_[0:5, 30, 56:61]])

# %% save results
# Only keep the 'Prevalence_Percentage' column, rounded to two decimals
# results_df = results_df[['Year', 'Prevalence_Percentage']].copy()
results_df['Prevalence_Percentage'] = results_df['Prevalence_Percentage'].round(2)


results_df.to_csv("results_df/diabetes_prevalence_50_plus.csv", index=False)

# %%
import matplotlib.pyplot as plt

# Ensure results_df is sorted by Year (it should be, but good practice)
results_df = results_df.sort_values('Year')

# 1. Setup the plot
plt.figure(figsize=(12, 6))

# 2. Draw the line
plt.plot(
    results_df['Year'], 
    results_df['Prevalence_Percentage'], 
    color='#2c7bb6',      # Nice blue color
    marker='o',           # Circle markers for data points
    markersize=4, 
    linestyle='-', 
    linewidth=2,
    label='Age 50+ Prevalence'
)

# 3. Styling and Labels
plt.title('Projected Diabetes Prevalence for Population Aged 50+ (1990–2050)', fontsize=14, pad=15)
plt.xlabel('Year', fontsize=12)
plt.ylabel('Prevalence (%)', fontsize=12)
plt.grid(False)

# 4. Format Axis Ticks
# Show ticks every 5 years for clarity
plt.xticks(np.arange(1990, 2051, 5), fontsize=10)
plt.yticks(fontsize=10)

# 5. Set limits to make the plot tight but readable
plt.xlim(1989, 2051)
# Optional: Set Y-axis to start at 0 if you want to see absolute scale
plt.ylim(10, max(results_df['Prevalence_Percentage']) * 1.1)

# 6. Save or Show
plt.tight_layout()
plt.legend()
plt.savefig("diabetes_prevalence_51_plus_trend.png", dpi=300)
print("Plot saved as 'diabetes_prevalence_51_plus_trend.png'")
# plt.show() # Uncomment if running in a notebook/IDE with display support



# %% diabetes plotting

import numpy as np
import matplotlib.pyplot as plt

# 1. Define Cohort Indices based on your reference file
# Note: Indices 6 & 7 are labeled 'mal mal'/'mal fem' in the text, 
# but often represent 'Others' in SG datasets. 
# Adjust 'malay_idxs' to [2, 3, 6, 7] if 6/7 are indeed Malay sub-cohorts.
cohort_map = {
    'Total':   [0, 1, 2, 3, 4, 5, 6, 7],
    'Chinese': [0, 1],
    'Malay':   [2, 3], 
    'Indian':  [4, 5]
}

# 2. Setup Data Storage
# Assuming diabetes_mat_storage is a list of 8 arrays of shape (n_sim, n_people, n_year)
# And assuming you have a matching age_matrix_ls to determine who is alive
prevalence_data = {
    'Total': [], 'Chinese': [], 'Malay': [], 'Indian': []
}

years = np.arange(1990, 2050 + 1)  # 61 years
n_years = len(years)

# 3. Calculation Loop
# We iterate through each ethnic group requested
for group, indices in cohort_map.items():
    
    # Storage for this group's aggregated counts per year
    total_diabetes_counts = np.zeros(n_years)
    total_alive_counts = np.zeros(n_years)
    
    for idx in indices:
        # Load diabetes data
        # diabetes_mat shape: (n_sim, n_people, n_year)
        d_mat = diabetes_mat_storage[idx] 
        
        # Load Age/Alive Mask (CRITICAL STEP)
        # You need the corresponding age matrix to know who is alive (age >= 0)
        # If age_matrix is unavailable, this defaults to n_people (INACCURATE for long projections)
        try:
            # path = f'../future_data_1990_2050/age_matrix/age_matrix_{idx}.npy'
            # age_mat = np.load(path) 
            age_mat = age_matrix_vec[idx]
            alive_mask = (age_mat >= 0) & (age_mat != -2)
            pass 
        except:
            # Fallback if age_matrix isn't loaded: assumes everyone is alive (for testing only)
            alive_mask = np.ones_like(d_mat, dtype=bool)

        # Apply logic: Diabetes is defined as value == 1
        is_diabetic = (d_mat == 1)
        
        # We average across simulations (axis 0) or sum across all dims depending on desired output.
        # Here we sum across people (axis 1) and simulations (axis 0) for the grand total
        
        # Count diabetics per year (sum over sim and people)
        # Masking: is_diabetic must be true AND alive_mask must be true
        valid_diabetics = is_diabetic & alive_mask
        
        total_diabetes_counts += np.sum(valid_diabetics, axis=(0, 1))
        total_alive_counts += np.sum(alive_mask, axis=(0, 1))

    # Calculate Prevalence
    # Avoid division by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        prev = total_diabetes_counts / total_alive_counts
        prev = np.nan_to_num(prev) # handle 0/0
    
    prevalence_data[group] = prev

# 4. Plotting
# %%
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()
titles = ['Total', 'Chinese', 'Malay', 'Indian']

for ax, title in zip(axes, titles):
    data = prevalence_data[title] * 100 # Convert to percentage
    
    ax.plot(years, data, color='tab:blue', linewidth=2)
    ax.set_title(f'{title} Diabetes Prevalence', fontsize=12, fontweight='bold')
    ax.set_xlabel('Year')
    ax.set_ylabel('Prevalence (%)')
    ax.grid(False)
    
    # Optional: Set limits if you want uniform scales
    ax.set_ylim(0, 30)

plt.tight_layout()
plt.show()

# %%
import numpy as np
import matplotlib.pyplot as plt

# 1. Setup Cohorts
# Adjust 'Malay' indices if 6 & 7 are also Malay sub-cohorts
cohort_map = {
    'Total':   [0, 1, 2, 3, 4, 5, 6, 7],
    'Chinese': [0, 1],
    'Malay':   [2, 3], 
    'Indian':  [4, 5]
}

years = np.arange(1990, 2050 + 1)
n_years = len(years)
n_sim = 10  # Standard simulation count from reference

# Container for plotting data
plot_data = {}
global_max_y = 0  # To ensure consistent ylim later

# 2. Calculation Loop
for group, indices in cohort_map.items():
    
    # Track numerator and denominator PER SIMULATION to calculate variance
    # Shape: (n_sim, n_years)
    group_numerators = np.zeros((n_sim, n_years))
    group_denominators = np.zeros((n_sim, n_years))
    
    for idx in indices:
        # Load Diabetes Data
        # diabetes_mat shape: (n_sim, n_people, n_year)
        # Values: 0 (Normal), 0.5 (Pre-diabetes), 1 (Diabetes)
        d_mat = diabetes_mat_storage[idx] 
        
        # Load Age Matrix / Alive Mask
        # If age_matrix is available, use it to mask out dead/unborn (-1/-2)
        alive_mask = (age_matrix_vec[idx] >= 0) 
        
        # Fallback if specific age matrix isn't loaded in this context:
        if 'alive_mask' not in locals(): 
            alive_mask = np.ones_like(d_mat, dtype=bool)

        # Logic: Diabetes is value == 1 (Excluding pre-diabetes 0.5)
        is_diabetic = (d_mat == 1)
        valid_cases = is_diabetic & alive_mask
        
        # Sum across PEOPLE (axis 1), preserving SIMULATIONS (axis 0)
        group_numerators += np.sum(valid_cases, axis=1)
        group_denominators += np.sum(alive_mask, axis=1)
        
    # Calculate Prevalence Trace per Simulation
    with np.errstate(divide='ignore', invalid='ignore'):
        sim_prevalence = group_numerators / group_denominators
        sim_prevalence = np.nan_to_num(sim_prevalence)

    # 3. Calculate Mean and CI
    mean_prev = np.mean(sim_prevalence, axis=0) * 100
    std_prev = np.std(sim_prevalence, axis=0) * 100
    
    # 95% Confidence Interval
    ci_lower = np.maximum(0, mean_prev - 1.96 * std_prev)
    ci_upper = mean_prev + 1.96 * std_prev
    
    # Track max value for consistent ylim
    current_max = np.max(ci_upper)
    if current_max > global_max_y:
        global_max_y = current_max
    
    plot_data[group] = {
        'mean': mean_prev,
        'lower': ci_lower,
        'upper': ci_upper
    }

# 4. Plotting
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()
titles = ['Total', 'Chinese', 'Malay', 'Indian']

# Add a little buffer to the global max y for aesthetics
ylim_top = global_max_y * 1.1

for ax, title in zip(axes, titles):
    data = plot_data[title]
    
    # Plot Mean Line
    ax.plot(years, data['mean'], label='Mean', color='tab:blue', linewidth=2)
    
    # Plot Shaded CI
    ax.fill_between(years, data['lower'], data['upper'], 
                    color='tab:blue', alpha=0.3, label='95% CI')
    
    ax.set_title(f'{title} Diabetes Prevalence', fontsize=12, fontweight='bold')
    ax.set_xlabel('Year')
    ax.set_ylabel('Prevalence (%)')
    
    # Consistent ylim and No Grid
    ax.set_ylim(0, ylim_top)
    ax.grid(False)
    
    ax.legend(loc='upper left')

plt.tight_layout()
plt.show()
# %% hypertension

import numpy as np
import matplotlib.pyplot as plt

# 1. Setup Cohorts
# Based on the reference, indices 0-7 cover the cohorts. 
# Adjust 'Malay' to include [2, 3, 6, 7] if indices 6 & 7 are indeed additional Malay cohorts.
cohort_map = {
    'Total':   [0, 1, 2, 3, 4, 5, 6, 7],
    'Chinese': [0, 1],
    'Malay':   [2, 3], 
    'Indian':  [4, 5]
}

years = np.arange(1990, 2050 + 1)
n_years = len(years)
n_sim = 10  # Standard simulation count from reference

# Container for plotting data
plot_data = {}
global_max_y = 0  # To ensure consistent ylim later

# 2. Calculation Loop
for group, indices in cohort_map.items():
    
    # Track numerator and denominator PER SIMULATION to calculate variance
    # Shape: (n_sim, n_years)
    group_numerators = np.zeros((n_sim, n_years))
    group_denominators = np.zeros((n_sim, n_years))
    
    for idx in indices:
        # Load Hypertension Data
        # hypertension_mat shape: (n_sim, n_people, n_year)
        # Values are {0, 1}
        h_mat = hypertension_mat_storage[idx] 
        
        # Load Age Matrix / Alive Mask
        # If age_matrix is available, use it to mask out dead/unborn (-1/-2)
        alive_mask = (age_matrix_vec[idx] >= 0) 
        
        # Fallback if specific age matrix isn't loaded in this context:
        if 'alive_mask' not in locals(): 
            alive_mask = np.ones_like(h_mat, dtype=bool)

        # Logic: Hypertension is value == 1
        is_hypertensive = (h_mat == 1)
        valid_cases = is_hypertensive & alive_mask
        
        # Sum across PEOPLE (axis 1), preserving SIMULATIONS (axis 0)
        group_numerators += np.sum(valid_cases, axis=1)
        group_denominators += np.sum(alive_mask, axis=1)
        
    # Calculate Prevalence Trace per Simulation
    with np.errstate(divide='ignore', invalid='ignore'):
        sim_prevalence = group_numerators / group_denominators
        sim_prevalence = np.nan_to_num(sim_prevalence)

    # 3. Calculate Mean and CI
    mean_prev = np.mean(sim_prevalence, axis=0) * 100
    std_prev = np.std(sim_prevalence, axis=0) * 100
    
    # 95% Confidence Interval
    ci_lower = np.maximum(0, mean_prev - 1.96 * std_prev)
    ci_upper = mean_prev + 1.96 * std_prev
    
    # Track max value for consistent ylim
    current_max = np.max(ci_upper)
    if current_max > global_max_y:
        global_max_y = current_max
    
    plot_data[group] = {
        'mean': mean_prev,
        'lower': ci_lower,
        'upper': ci_upper
    }

# 4. Plotting
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()
titles = ['Total', 'Chinese', 'Malay', 'Indian']

# Add a little buffer to the global max y for aesthetics
ylim_top = global_max_y * 1.1

for ax, title in zip(axes, titles):
    data = plot_data[title]
    
    # Plot Mean Line
    ax.plot(years, data['mean'], label='Mean', color='tab:red', linewidth=2)
    
    # Plot Shaded CI
    ax.fill_between(years, data['lower'], data['upper'], 
                    color='tab:red', alpha=0.3, label='95% CI')
    
    ax.set_title(f'{title} Hypertension Prevalence', fontsize=12, fontweight='bold')
    ax.set_xlabel('Year')
    ax.set_ylabel('Prevalence (%)')
    
    # Consistent ylim and No Grid
    ax.set_ylim(0, ylim_top)
    ax.grid(False)
    
    ax.legend(loc='upper left')

plt.tight_layout()
plt.show()




import numpy as np
import matplotlib.pyplot as plt

# Simulate loading data (Since I don't have the actual .npy files)
# I will create dummy data with the shapes described in the MD file
# to demonstrate the CI plotting logic.

n_sim = 10
n_year = 61
years = np.arange(1990, 2051)
cohort_map = {
    'Total':   [0, 1, 2, 3, 4, 5, 6, 7],
    'Chinese': [0, 1],
    'Malay':   [2, 3], # Assuming 2,3 are the main Malay blocks. Add 6,7 if needed.
    'Indian':  [4, 5]
}
# Approximate sizes from the MD file
pop_sizes = {
    0: 103903, 1: 108964, 
    2: 21074, 3: 20487, 
    4: 14978, 5: 13353, 
    6: 5789, 7: 7024
}

# Container for results
stats_results = {}

# Generate synthetic prevalence traces for each cohort
# In reality, you would load the files here.
np.random.seed(42)

for group, indices in cohort_map.items():
    # We will collect traces: shape (n_sim, n_year)
    # Each trace is the weighted prevalence for that simulation
    
    group_numerators = np.zeros((n_sim, n_year))
    group_denominators = np.zeros((n_sim, n_year))
    
    for idx in indices:
        n_p = pop_sizes[idx]
        
        # Synthetic Data Generation representing:
        # 1. Increasing trend over years
        # 2. Random variation per simulation
        # 3. Random noise per year
        
        # Base trend (logistic-like growth)
        base_trend = np.linspace(0.05, 0.20, n_year) # 5% to 20%
        if group == 'Indian': base_trend += 0.05 # Higher risk
        if group == 'Chinese': base_trend -= 0.02 # Lower risk
        
        # Create simulation variations
        # Shape: (n_sim, n_year)
        # Each sim has a slightly different intercept/slope
        sim_offsets = np.random.normal(0, 0.02, (n_sim, 1)) 
        sim_trends = base_trend + sim_offsets
        
        # Add yearly noise
        sim_trends += np.random.normal(0, 0.005, (n_sim, n_year))
        sim_trends = np.clip(sim_trends, 0, 1)
        
        # Convert to counts (approximate)
        # Assume population stays roughly constant for this demo (or strictly, n_people)
        # In real code, load age_matrix to get actual alive count per year
        alive_count = np.full((n_sim, n_year), n_p) 
        
        # Make some people die off over time in the denominator (optional realism)
        # decay = np.linspace(1.0, 0.8, n_year)
        # alive_count = alive_count * decay
        
        diabetic_count = alive_count * sim_trends
        
        group_numerators += diabetic_count
        group_denominators += alive_count
        
    # Calculate prevalence for this group per simulation
    # Shape: (n_sim, n_year)
    prevalence_traces = group_numerators / group_denominators
    
    # Calculate Statistics
    mean_prev = np.mean(prevalence_traces, axis=0) * 100 # Percent
    std_prev = np.std(prevalence_traces, axis=0) * 100
    
    # 95% Confidence Interval (using 1.96 * std dev as proxy for spread of sims)
    # OR if you want CI of the mean: 1.96 * std / sqrt(n_sim)
    # Usually for projections, showing the spread (std) is more useful.
    # Let's use Mean +/- 1.96 * Std (The "Reference Range" of the simulations)
    ci_lower = mean_prev - 1.96 * std_prev
    ci_upper = mean_prev + 1.96 * std_prev
    
    stats_results[group] = {
        'mean': mean_prev,
        'lower': ci_lower,
        'upper': ci_upper
    }

# Plotting
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()
titles = ['Total', 'Chinese', 'Malay', 'Indian']

for ax, title in zip(axes, titles):
    res = stats_results[title]
    
    # Plot Mean
    ax.plot(years, res['mean'], color='#1f77b4', linewidth=2, label='Mean')
    
    # Plot CI
    ax.fill_between(years, res['lower'], res['upper'], color='#1f77b4', alpha=0.3, label='95% CI (Sims)')
    
    ax.set_title(f'{title} Diabetes Prevalence', fontsize=12, fontweight='bold')
    ax.set_xlabel('Year')
    ax.set_ylabel('Prevalence (%)')
    ax.grid(False)
    ax.legend()
    ax.set_ylim(0,35)


plt.tight_layout()
plt.savefig('diabetes_prevalence_ci.png')
print("Plot generated")
