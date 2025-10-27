#!/usr/bin/env python3
"""
Test script for the modified fertility parameter generation.
This script tests the functions that read the AESFR_matrix_combine.bin file.
"""

import sys
import os

# Add the current directory to the path so we can import from generate_test_params
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generate_test_params import (
    read_aesfr_binary_file, 
    map_fertility_rate, 
    print_fertility_matrix,
    test_fertility_mapping,
    export_fertility_matrix_to_csv
)

def main():
    print("Testing Fertility Matrix Reading Functions")
    print("=" * 50)
    
    # Test file path (relative to project root)
    binary_filepath = "../data/bin/AESFR_matrix_combine.bin"
    
    # Check if file exists
    if not os.path.exists(binary_filepath):
        print(f"Error: {binary_filepath} not found!")
        print("Please ensure the binary file exists in the correct location.")
        print("Current working directory:", os.getcwd())
        return False
    
    print(f"Found binary file: {binary_filepath}")
    
    # Test reading the binary file
    print("\n1. Testing binary file reading...")
    fertility_matrix = read_aesfr_binary_file(binary_filepath)
    
    if fertility_matrix is None:
        print("Failed to read fertility matrix!")
        return False
    
    print("✓ Successfully read fertility matrix")
    
    # Test matrix information display
    print("\n2. Testing matrix information display...")
    print_fertility_matrix(fertility_matrix)
    print("✓ Matrix information displayed")
    
    # Test fertility rate mapping
    print("\n3. Testing fertility rate mapping...")
    test_fertility_mapping(fertility_matrix)
    
    # Test export functionality
    print("\n4. Testing export functionality...")
    export_fertility_matrix_to_csv(fertility_matrix, "test_fertility_export.csv")
    
    # Test specific fertility rate calculations
    print("\n5. Testing specific fertility rate calculations...")
    test_cases = [
        (1990, 15, 'chinese'),
        (1990, 20, 'malay'),
        (2024, 35, 'indian'),
        (2030, 25, 'other'),
    ]
    
    race_to_idx = {'chinese': 1, 'malay': 3, 'indian': 5, 'other': 7}  # Female indices
    
    for year, age, race in test_cases:
        race_idx = race_to_idx[race]
        year_idx = year - 1990
        rate = map_fertility_rate(fertility_matrix, race_idx, year_idx, age)
        print(f"  {race.capitalize()}, year {year}, age {age}: {rate:.6f}")
    
    # # Test age 15 Chinese fertility rates from 1990 to 2010
    # print("\n6. Testing age 15 Chinese fertility rates (1990-2010)...")
    # chinese_idx = race_to_idx['chinese']
    # for year in range(1990, 2011):
    #     year_idx = year - 1990
    #     rate = map_fertility_rate(fertility_matrix, chinese_idx, year_idx, 15)
    #     print(f"  Chinese, year {year}, age 15: {rate:.6f}")
    
    # # Test Chinese fertility matrix for ages 15-20, years 1990-2010
    # print("\n7. Chinese Fertility Matrix (Ages 15-20, Years 1990-2010)...")
    # print("Age\\Year", end="")
    # for year in range(1990, 2011):
    #     print(f"\t{year}", end="")
    # print()
    
    # chinese_idx = race_to_idx['chinese']
    # for age in range(15, 21):
    #     print(f"{age}", end="")
    #     for year in range(1990, 2011):
    #         year_idx = year - 1990
    #         rate = map_fertility_rate(fertility_matrix, chinese_idx, year_idx, age)
    #         print(f"\t{rate:.6f}", end="")
    #     print()
    
    # 
    # print("\n")
    # print (fertility_matrix[0, 10, 0]) 
    # expected 0 
    return True

    

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 