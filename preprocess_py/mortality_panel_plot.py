import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Set font size for all text elements
plt.rcParams.update({'font.size': 14})

# Load the mortality data from binary file
mortality_matrix_mat = np.load('data/bin/mortality_matrix_mat.bin')

# Create years array
future_years = np.arange(2021, 2051)  # Years from 2021 to 2050

# Create figure with two subplots side by side, sharing y-axis
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), sharey=True)

# Plot male mortality rates
for age in np.arange(0, 80, 10):
    ax1.plot(future_years, mortality_matrix_mat[0, age, :], label=f'Age {age}')
ax1.set_title("Male Mortality Rates (2021-2050)", fontsize=14)
ax1.set_xlabel("")
ax1.set_ylabel("Mortality Rate", fontsize=14)
ax1.grid(False)

# Plot female mortality rates
for age in np.arange(0, 80, 10):
    ax2.plot(future_years, mortality_matrix_mat[1, age, :], label=f'Age {age}')
ax2.set_title("Female Mortality Rates (2021-2050)", fontsize=14)
ax2.set_xlabel("")
ax2.set_ylabel("")
ax2.grid(False)

# Add a single x-label in the middle
fig.text(0.5, -0.02, "Year", ha='center', fontsize=14)

# Add legend outside the plots
handles, labels = ax1.get_legend_handles_labels()
fig.legend(handles, labels, loc='center right', bbox_to_anchor=(1.15, 0.5), fontsize=14)

# Adjust layout to prevent overlap and make room for external legend
plt.tight_layout()
plt.show() 