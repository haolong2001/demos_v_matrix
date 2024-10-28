import numpy as np


# Create a 3x3x3 matrix of doubles
my_matrix = np.random.rand(3, 3, 3)  # Generate random double values
print(my_matrix)
# Save the matrix in binary format
my_matrix.tofile('matrix_double.bin')  # This saves in row-major order

