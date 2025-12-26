# %% get mortality
# 
loaded_mortality_matrix_mat = np.fromfile('../../data/bin/mortality_matrix_mat.bin').reshape(2, 86, 30)


# %%
import pandas as pd

# Read the male mortality data from CSV
male_mortality_df = pd.read_csv("../../src_py/male_mortality_converted.csv")
print("Loaded male_mortality_converted.csv:")
print(male_mortality_df.head())

print(male_mortality_df.tail())

# %%
# Read the mortality_forecast_2024_2050.csv file
mortality_forecast_df = pd.read_csv("../../src_py/mortality_forecast_2024_2050.csv")
print("Loaded mortality_forecast_2024_2050.csv:")
print(mortality_forecast_df.head())
print(mortality_forecast_df.tail())

# Read the female_mortality.csv file
female_mortality_df = pd.read_csv("../../src_py/female_mortality_converted.csv")
print("Loaded female_mortality.csv:")
print(female_mortality_df.head())
print(female_mortality_df.tail())


# %%
# Concatenate the male, female, and forecast mortality DataFrames
# Optionally reset or ignore index depending on requirements
overall_mortality_df = pd.concat(
    [male_mortality_df, female_mortality_df, mortality_forecast_df],
    axis=0,
    ignore_index=True
)

# Save the concatenated DataFrame to a CSV file
overall_mortality_df.to_csv("../../data/overall_mortality.csv", index=False)
print("Saved overall_mortality.csv with shape:", overall_mortality_df.shape)

