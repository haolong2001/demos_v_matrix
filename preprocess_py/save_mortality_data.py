import numpy as np
import os

# Create data/bin directory if it doesn't exist
os.makedirs('../data/bin', exist_ok=True)

# Load the mortality data
mortality_matrix_mat = np.load('data/mortality_matrix_mat.npy')

# Save as raw binary file
mortality_matrix_mat.tofile('../data/bin/mortality_matrix_mat.bin')

print(f"Data shape: {mortality_matrix_mat.shape}")
print("Data saved successfully to ../data/bin/mortality_matrix_mat.bin") 