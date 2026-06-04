# %%
import pandas as pd
import matplotlib.pyplot as plt

# 1. Load the datasets
# 'start' represents the 95% CI lower bound
# 'end' represents the 95% CI upper bound
df_start = pd.read_csv('new_standard_ckd_1990_2050_start.csv')
df_end = pd.read_csv('new_standard_ckd_1990_2050_end.csv')

# 2. Preprocessing
# Rename the first column to 'Year'
df_start.rename(columns={'Unnamed: 0': 'Year'}, inplace=True)
df_end.rename(columns={'Unnamed: 0': 'Year'}, inplace=True)

# Combine K3a and K3b into a single K3 stage
df_start['K3'] = df_start['K3a'] + df_start['K3b']
df_end['K3'] = df_end['K3a'] + df_end['K3b']

stages = ['K1', 'K2', 'K3', 'K4', 'K5']

# 3. Calculate percentages for lower and upper bounds
pct_start = df_start[['Year']].copy()
pct_end = df_end[['Year']].copy()

for s in stages:
    # (Stage Count / Total Population) * 100
    pct_start[s] = (df_start[s] / df_start['Total_Population']) * 100
    pct_end[s] = (df_end[s] / df_end['Total_Population']) * 100

# 4. Calculate the Mean Percentage
pct_mean = pct_start.copy()
for s in stages:
    pct_mean[s] = (pct_start[s] + pct_end[s]) / 2

# 5. Visualization
plt.figure(figsize=(12, 8))
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

for i, s in enumerate(stages):
    # Plot the mean line
    plt.plot(pct_mean['Year'], pct_mean[s], label=f'{s} (Mean)', color=colors[i], linewidth=2)
    # Fill the area between lower and upper bounds (95% CI)
    plt.fill_between(pct_mean['Year'], pct_start[s], pct_end[s], color=colors[i], alpha=0.2)

plt.title('Trend of CKD Stages Percentage (1990-2050) with 95% CI', fontsize=14)
plt.xlabel('Year', fontsize=12)
plt.ylabel('Percentage of Total Population (%)', fontsize=12)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()

# Save the plot
plt.savefig('ckd_stages_trend.png')

# 6. Export the processed results to CSV
pct_mean.to_csv('ckd_stages_percentages_mean.csv', index=False)
pct_start.to_csv('ckd_stages_percentages_lower_bound.csv', index=False)
pct_end.to_csv('ckd_stages_percentages_upper_bound.csv', index=False)

print("Processing complete. Files and plot have been generated.")
# %%

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import math

# 1. Load Data
df_gran = pd.read_csv('granular_ckd_prevalence_1990_2050.csv')

# 2. Preprocessing: Combine K3a + K3b -> K3
# We need to sum 'prevalence', 'lower', and 'upper' for K3a and K3b
# Pivot to make it easier: Index keys + Columns=[Stage] -> Values=[prev, lower, upper]
# A simpler way is to just aggregate rows where stage is K3a or K3b

# Create a K3 subset and aggregate
k3_stages = ['K3a', 'K3b']
df_k3 = df_gran[df_gran['stage'].isin(k3_stages)].copy()

if not df_k3.empty:
    # Group by everything except stage, and sum the numeric columns
    df_k3_grouped = df_k3.groupby(['ethnicity', 'age_group', 'year'], as_index=False)[['prevalence', 'lower', 'upper']].sum()
    df_k3_grouped['stage'] = 'K3'
    
    # Filter out original K3a/K3b and append the new K3
    df_clean = df_gran[~df_gran['stage'].isin(k3_stages)].copy()
    df_clean = pd.concat([df_clean, df_k3_grouped], ignore_index=True)
else:
    df_clean = df_gran.copy()

# Stages to plot
stages_to_plot = ['K1', 'K2', 'K3', 'K4', 'K5']
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

# --- PLOT 1: Ethnicity Panels ---
fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharex=True, sharey=True)
axes = axes.flatten()

eth_order = ['overall', 'chn', 'mal', 'ind']
titles = ['Overall Population', 'Chinese', 'Malay', 'Indian']

for i, eth in enumerate(eth_order):
    ax = axes[i]
    
    # Filter: Specific Ethnicity AND 'Overall' Age Group
    data_subset = df_clean[
        (df_clean['ethnicity'] == eth) & 
        (df_clean['age_group'] == 'Overall')
    ].sort_values('year')
    
    if data_subset.empty:
        ax.text(0.5, 0.5, 'No Data', ha='center', va='center')
        ax.set_title(titles[i])
        continue

    # Plot each stage
    for j, stage in enumerate(stages_to_plot):
        stage_data = data_subset[data_subset['stage'] == stage]
        
        if not stage_data.empty:
            # Mean Line
            ax.plot(stage_data['year'], stage_data['prevalence'], 
                    label=stage, color=colors[j], linewidth=2)
            
            # Confidence Interval (Fill)
            ax.fill_between(
                stage_data['year'], 
                stage_data['lower'], 
                stage_data['upper'], 
                color=colors[j], 
                alpha=0.2  # Transparency
            )

    ax.set_title(titles[i], fontsize=12, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.5)
    
    if i >= 2: 
        ax.set_xlabel('Year')
    if i % 2 == 0: 
        ax.set_ylabel('Prevalence (%)')

# Legend
handles, labels = axes[0].get_legend_handles_labels()
# Filter duplicate labels if any (though loop handles it, sometimes safer to unique)
by_label = dict(zip(labels, handles))
fig.legend(by_label.values(), by_label.keys(), loc='center right', title='CKD Stage')

plt.subplots_adjust(right=0.88)
plt.savefig('ckd_trends_ethnicity_CI.png')
plt.show()

# %%
# --- PLOT 2: Age Group Panels ---
age_groups = ['18-30', '31-40', '41-50', '51-60', '61-70', '71-80', '80+']

n_cols = 4
n_rows = math.ceil(len(age_groups) / n_cols)

fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 10), sharex=True, sharey=True)
axes = axes.flatten()

for i, age_grp in enumerate(age_groups):
    ax = axes[i]
    
    # Filter: 'overall' Ethnicity AND Specific Age Group
    data_subset = df_clean[
        (df_clean['ethnicity'] == 'overall') & 
        (df_clean['age_group'] == age_grp)
    ].sort_values('year')
    
    if data_subset.empty:
        ax.text(0.5, 0.5, 'No Data', ha='center', va='center')
        ax.set_title(age_grp)
        continue

    for j, stage in enumerate(stages_to_plot):
        stage_data = data_subset[data_subset['stage'] == stage]
        
        if not stage_data.empty:
            # Mean Line
            ax.plot(stage_data['year'], stage_data['prevalence'], 
                    label=stage, color=colors[j], linewidth=2)
            
            # Confidence Interval (Fill)
            ax.fill_between(
                stage_data['year'], 
                stage_data['lower'], 
                stage_data['upper'], 
                color=colors[j], 
                alpha=0.2
            )

    ax.set_title(f"Age: {age_grp}", fontsize=11, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.5)
    
    if i >= (n_rows - 1) * n_cols: 
        ax.set_xlabel('Year')
    if i % n_cols == 0: 
        ax.set_ylabel('Prevalence (%)')

# Hide unused axes
for k in range(len(age_groups), len(axes)):
    axes[k].set_visible(False)

# Legend
handles, labels = axes[0].get_legend_handles_labels()
by_label = dict(zip(labels, handles))
fig.legend(by_label.values(), by_label.keys(), loc='center right', title='CKD Stage')

plt.subplots_adjust(right=0.90)
plt.savefig('ckd_trends_age_group_CI.png')
plt.show()
# %%
