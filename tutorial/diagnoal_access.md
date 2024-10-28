

access the values diagnoally



so a 3 * 4 matrix 



Will have 7 * 4 shape finally



```python
import numpy as np

def extract_and_pad_diagonals(matrix):
    nrows, ncols = matrix.shape
    diagonals = []

    # Extract diagonals starting from each column in the first row
    for start_col in range(ncols):
        diag = []
        row, col = 0, start_col
        while row < nrows and col < ncols:
            diag.append(matrix[row, col])
            row += 1
            col += 1
        diagonals.append(diag)

    # Extract diagonals starting from each row in the first column (excluding the first row)
    for start_row in range(1, nrows):
        diag = []
        row, col = start_row, 0
        while row < nrows and col < ncols:
            diag.append(matrix[row, col])
            row += 1
            col += 1
        diagonals.append(diag)

    # Pad each diagonal to the length of ncols (4 in this case)
    padded_diagonals = []
    for diag in diagonals:
        while len(diag) < ncols:
            diag.insert(0, 0)  # Pad with zeros at the beginning
        padded_diagonals.append(diag)

    # Convert to a NumPy array
    result_matrix = np.array(padded_diagonals)
    return result_matrix

# Example usage
input_matrix = np.array([
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12]
])

result = extract_and_pad_diagonals(input_matrix)
print(result)

```

