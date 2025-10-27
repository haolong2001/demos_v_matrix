#!/usr/bin/env python3
"""
Debug script to investigate fertility matrix structure and identify why age 15 fertility rates are always 0.
"""

import struct
import numpy as np
import os

def debug_fertility_matrix():
    """Debug the fertility matrix structure in detail."""
    
    # File path
    binary_filepath = "../data/bin/AESFR_matrix_combine.bin"
    
    if not os.path.exists(binary_filepath):
        print(f"Error: {binary_filepath} not found!")
        return
    
    print(f"Found binary file: {binary_filepath}")
    
    # Read the raw binary data
    with open(binary_filepath, 'rb') as file:
        data = file.read()
    
    print(f"Total file size: {len(data)} bytes")
    
    # Expected size: 12 * 71 * 35 * 8 = 238,560 bytes
    expected_size = 12 * 71 * 35 * 8
    print(f"Expected size: {expected_size} bytes")
    print(f"Size match: {len(data) == expected_size}")
    
    if len(data) != expected_size:
        print("WARNING: File size doesn't match expected size!")
        return
    
    # Convert to double array
    double_array = struct.unpack('d' * (len(data) // 8), data)
    print(f"Number of doubles: {len(double_array)}")
    
    # Check if all values are 0
    non_zero_count = sum(1 for x in double_array if x != 0.0)
    print(f"Non-zero values: {non_zero_count}/{len(double_array)}")
    
    # Check first few values
    print(f"\nFirst 20 values: {double_array[:20]}")
    
    # Check if the issue is with the first age group (index 0)
    print(f"\nChecking first age group values (indices 0, 1, 2, 3, 4):")
    for i in range(5):
        print(f"  Index {i}: {double_array[i]}")
    
    # Reshape to 3D array [12][71][35]
    fertility_matrix = np.array(double_array).reshape(12, 71, 35)
    print(f"\nMatrix shape: {fertility_matrix.shape}")
    
    # Check the first age group (index 0) across all ethnicities and years
    print(f"\nFirst age group (index 0) values:")
    print("Ethnicity\\Year", end="")
    for year in range(min(10, 71)):  # Show first 10 years
        print(f"\t{year}", end="")
    print()
    
    for eth in range(min(4, 12)):  # Show first 4 ethnicities
        print(f"{eth}", end="")
        for year in range(min(10, 71)):
            value = fertility_matrix[eth, year, 0]  # age index 0
            print(f"\t{value:.6f}", end="")
        print()
    
    # Check if the issue is with the reshape
    print(f"\nChecking if reshape is correct:")
    print(f"Original array first 35 values: {double_array[:35]}")
    print(f"Reshaped first ethnicity, first year: {fertility_matrix[0, 0, :]}")
    
    # Check if the data is actually stored in a different order
    print(f"\nChecking alternative reshape possibilities:")
    
    # Try different reshape orders
    # [35][71][12] - age first, then year, then ethnicity
    alt_matrix_1 = np.array(double_array).reshape(35, 71, 12)
    print(f"Alternative reshape [35][71][12] - age 15 (index 0): {alt_matrix_1[0, 10, :4]}")  # year 1990, first 4 ethnicities
    
    # [71][12][35] - year first, then ethnicity, then age
    alt_matrix_2 = np.array(double_array).reshape(71, 12, 35)
    print(f"Alternative reshape [71][12][35] - year 1990 (index 10), age 15 (index 0): {alt_matrix_2[10, :4, 0]}")
    
    # [71][35][12] - year first, then age, then ethnicity
    alt_matrix_3 = np.array(double_array).reshape(71, 35, 12)
    print(f"Alternative reshape [71][35][12] - year 1990 (index 10), age 15 (index 0): {alt_matrix_3[10, 0, :4]}")
    
    # Check if the issue is with the year offset
    print(f"\nChecking year offset issue:")
    print(f"Original matrix [0, 0, 0]: {fertility_matrix[0, 0, 0]}")
    print(f"Original matrix [0, 10, 0]: {fertility_matrix[0, 10, 0]}")  # year 1990
    print(f"Original matrix [0, 20, 0]: {fertility_matrix[0, 20, 0]}")  # year 2000
    
    # Check if the issue is with the age offset
    print(f"\nChecking age offset issue:")
    print(f"Age 15 (index 0): {fertility_matrix[0, 10, 0]}")
    print(f"Age 16 (index 1): {fertility_matrix[0, 10, 1]}")
    print(f"Age 17 (index 2): {fertility_matrix[0, 10, 2]}")
    
    # Check if the data is actually stored with age 15 at a different index
    print(f"\nChecking if age 15 data exists elsewhere:")
    for age_idx in range(35):
        if fertility_matrix[0, 10, age_idx] != 0.0:
            print(f"  Age index {age_idx} (age {age_idx + 15}) has non-zero value: {fertility_matrix[0, 10, age_idx]}")
            break

if __name__ == "__main__":
    debug_fertility_matrix() 