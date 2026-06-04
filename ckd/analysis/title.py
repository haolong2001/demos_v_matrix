
# %% 
import numpy as np

def get_good_control_rate(age, ethnicity, gender):
    """
    Returns estimated Good Control Rate (%) using sigmoid fit,
    adjusted by ethnicity and gender factors from Table 11.6.
    """
    # 1. Base Sigmoid for Poor Control (based on age)
    # Parameters: L=27.55, k=0.32, x0=45.19, b=57.52
    base_poor = 27.55 / (1 + np.exp(0.32 * (age - 45.19))) + 57.52
    
    # 2. Scaling Factors (Rate / Baseline Total of 60.4%)
    # Data sourced from Table 11.6 in "unnamed.jpg"
    ethnicity_map = {'Chinese': 58.7 / 60.4, 'Malay': 66.0 / 60.4, 'Indian': 64.9 / 60.4}
    gender_map = {'Male': 63.5 / 60.4, 'Female': 56.7 / 60.4}
    
    e_factor = ethnicity_map.get(ethnicity.capitalize(), 1.0)
    g_factor = gender_map.get(gender.capitalize(), 1.0)
    
    # 3. Calculate Adjusted Poor Control
    adj_poor_control = base_poor * e_factor * g_factor
    
    # 4. Return Good Control (Inverse)
    return round(100 - adj_poor_control, 2)

# %% 

import numpy as np
import matplotlib.pyplot as plt

# 1. Define Model Parameters
L, k, x0, b = 27.55, 0.32, 45.19, 57.52

def get_good_control(age):
    """Calculates 100 - Poor Control Sigmoid"""
    poor_control = L / (1 + np.exp(k * (age - x0))) + b
    return 100 - poor_control

# 2. Prepare Actual Data from Table 11.6 in "unnamed.jpg"
# Age groups: 30-39, 40-49, 50-59, 60-69, 70-74
# Values are 100 - poor control rates
age_midpoints = [34.5, 44.5, 54.5, 64.5, 72.0]
actual_poor = [84.0, 71.7, 58.7, 57.7, 57.4]
actual_good = [100 - p for p in actual_poor]

# 3. Generate Model Curve
age_range = np.linspace(18, 75, 100)
model_good = get_good_control(age_range)

# 4. Create the Visualization
plt.figure(figsize=(10, 6), dpi=100)

# Plot actual data points
plt.scatter(age_midpoints, actual_good, color='#2ca02c', label='NPHS', zorder=5)

# Plot the sigmoid model line
plt.plot(age_range, model_good, color='#1b5e20', linewidth=2.5, label='Sigmoid Model')

# Add data labels to points
for i, val in enumerate(actual_good):
    plt.annotate(f"{val:.1f}%", (age_midpoints[i], actual_good[i]), 
                 textcoords="offset points", xytext=(0, 10), ha='center', fontsize=9)

# Formatting
plt.title('Validation: Age-Specific Good BP Control Rates', fontsize=14, pad=15)
plt.xlabel('Age (Years)', fontsize=12)
plt.ylabel('Good Control Rate (%)', fontsize=12)
plt.ylim(0, 50)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(loc='lower right')

# Final Display
plt.tight_layout()
plt.show()

# %% 

