#%% Population Matrix Plot Script
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#%% Load historical data /Historical_data/
path = "/Users/haolong/Documents/demos_v_matrix/output/"
num_files = 8
age_matrix_vec = []

for i in range(num_files):
    filename = f"popu_matrix_{i}.csv"
    matrix = pd.read_csv(path + filename).to_numpy()
    filtered_matrix = matrix[~np.all(matrix < 0, axis=1)]
    age_matrix_vec.append(filtered_matrix)

#%% Initialize target array
target = np.zeros((num_files, 86, age_matrix_vec[0].shape[1]), dtype=int)
for i, matrix in enumerate(age_matrix_vec):
    for col in range(matrix.shape[1]):
        ages = matrix[:, col].astype(int)
        for a in range(85):
            target[i, a, col] = np.sum(ages == a)
        target[i, 85, col] = np.sum(ages >= 85)

print("target shape:", target.shape)

#%% Load historical data
result_matrix = np.fromfile("../../data/bin/result_matrix_data.bin", dtype=np.float64)  # Specify data type if needed
result_matrix = result_matrix.reshape(8, 86, 35)  # Reshape to correct dimensions (8 cohorts, 86 ages, 35 years)

#%% Comparison Plot (3x2 grid by ethnicity/gender)
titles = ["chn male", "chn female", "mal male", "mal female", "ind male", "ind female"]
num_years = target.shape[2]
years = np.arange(1990, 1990 + num_years)

fig, axes = plt.subplots(3, 2, figsize=(14, 10), sharey='row')
axes = axes.flatten()

for i in range(6):
    ax = axes[i]
    target_sum = target[i, :, :].sum(axis=0) * 20
    result_sum = result_matrix[i, :, :34].sum(axis=0)

    ax.plot(years, target_sum, label='Simulated', linewidth=2)
    ax.plot(years, result_sum, '--', label='Historical', linewidth=2)
    ax.set_title(titles[i], fontsize=12, fontweight='bold')
    ax.set_xlabel('Year')
    ax.set_ylabel('Population Count')
    ax.legend(fontsize=9)
    ax.grid(True, linestyle=':', alpha=0.5)

plt.tight_layout(h_pad=0.5, w_pad=0.4)
plt.show()

#%% Combined Plot (Male/Female panels by ethnicity)
male_indices = [0, 2, 4]
female_indices = [1, 3, 5]
eth_labels = ["Chinese", "Malay", "Indian"]
colors = ['tab:blue', 'tab:orange', 'tab:green']

fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

for ax, (group_indices, gender_label) in zip(axes, [(male_indices, 'Male'), (female_indices, 'Female')]):
    for j, i in enumerate(group_indices):
        target_sum = target[i, :, :].sum(axis=0) * 20
        result_sum = result_matrix[i, :, :34].sum(axis=0)

        ax.plot(years, target_sum, color=colors[j], linewidth=2, label=f'{eth_labels[j]} Simulated')
        ax.plot(years, result_sum, '--', color=colors[j], linewidth=2, label=f'{eth_labels[j]} Historical')

    ax.set_title(gender_label, fontsize=13, fontweight='bold')
    ax.set_xlabel('Year')
    ax.set_ylabel('Population Count')
    ax.grid(True, linestyle=':', alpha=0.5)
    ax.legend(fontsize=9)

plt.tight_layout()
plt.show()
#%%
#%% Age-Stratified Population Plots



#%% --- Define age bins ---
age_bins = [(0,9), (10,19), (20,29), (30,39), (40,49), (50,59), (60,69), (70,79), (80,200)]
age_labels = [f"{a}-{b}" if b < 200 else "80+" for a,b in age_bins]

#%% --- Select group to plot ---
titles = ["chn male", "chn female", "mal male", "mal female", "ind male", "ind female"]
group_index = 0  # 0–5 for different ethnicity-gender groups
group_label = titles[group_index]

num_years = target.shape[2]
years = np.arange(1990, 1990 + num_years)


titles = ["chn male", "chn female", "mal male", "mal female", "ind male", "ind female"]
num_years = target.shape[2]
years = np.arange(1990, 1990 + num_years)
save_dir = "plots"
os.makedirs(save_dir, exist_ok=True)

#%% --- Generate and save plots ---
for group_index, group_label in enumerate(titles):
    fig, axes = plt.subplots(3, 3, figsize=(14, 10), sharey=True)
    axes = axes.flatten()

    for k, (low, high) in enumerate(age_bins):
        ax = axes[k]
        age_idx = np.arange(low, min(high + 1, 86))

        target_sum = target[group_index, age_idx, :].sum(axis=0) * 20
        result_sum = result_matrix[group_index, age_idx, :num_years].sum(axis=0)

        ax.plot(years, target_sum, linewidth=2, label="Simulated")
        ax.plot(years, result_sum, "--", linewidth=2, label="Historical")

        ax.set_title(f"Age {age_labels[k]}", fontsize=11, fontweight="bold")
        ax.set_xlabel("Year")
        ax.set_ylabel("Population Count")
        ax.grid(True, linestyle=":", alpha=0.5)

        if k == 0:
            ax.legend(fontsize=9)

    plt.suptitle(f"Age-Stratified Population Trends ({group_label})", fontsize=14, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    # Save to ../plots folder
    filename = os.path.join(save_dir, f"age_trends_{group_label.replace(' ', '_')}.png")
    plt.savefig(filename, dpi=300)
    plt.close(fig)

    print(f"Saved: {filename}")

print("✅ All 6 plots generated and saved to ../plots/")
# %%
import os
print("Current path:", os.getcwd())

#%%
result_matrix
#%% 
from Age_BMI_loading import (
    age_matrix_vec_2050,
)
age_matrix_vec_2050[0].shape


#%% Initialize target array
target = np.zeros((num_files, 86, age_matrix_vec_2050[0][0].shape[1]), dtype=int)
for i, matrix in enumerate(age_matrix_vec_2050):
    matrix = matrix[0]
    for col in range(matrix.shape[1]):
        ages = matrix[:, col].astype(int)
        for a in range(85):
            target[i, a, col] = np.sum(ages == a)
        target[i, 85, col] = np.sum(ages >= 85)

print("target shape:", target.shape)



#%%
# Assuming target has shape (6, age, year)
age_60_idx = np.arange(60, 86)  # ages 60+
num_years = target.shape[2]

# Sum across all groups and ages >= 60
above60_total = target[:, age_60_idx, :num_years].sum(axis=(0, 1))

# Sum across all groups and all ages
overall_total = target[:, :, :num_years].sum(axis=(0, 1))

# Compute proportion (vector of length num_years)
prop_above60 = above60_total / overall_total

# Example: print last-year value and trend
print(f"Latest year proportion (≥60): {prop_above60[-1]:.2%}")
#%%

for year_idx, prop in enumerate(prop_above60):
    print(f"Year {year_idx + 1990}: Proportion (≥60) = {prop:.2%}")


#%%

#%%
# Assuming target has shape (6, age, year)
age_80_idx = np.arange(80, 86)  # ages 80+
num_years = target.shape[2]

# Sum across all groups and ages >= 80
above80_total = target[:, age_80_idx, :num_years].sum(axis=(0, 1))

# Sum across all groups and all ages
overall_total = target[:, :, :num_years].sum(axis=(0, 1))

# Compute proportion (vector of length num_years)
prop_above80 = above80_total / overall_total

# Example: print last-year value and trend
print(f"Latest year proportion (≥80): {prop_above80[-1]:.2%}")
#%%
for year_idx, prop in enumerate(prop_above80):
    print(f"Year {year_idx + 1990}: Proportion (≥80) = {prop:.2%}")

# %%
