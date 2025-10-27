#!/usr/bin/env python3
"""
Convert mig_disappear.bin mortality data to CSV format with pivot table structure.
The binary file contains mortality + emigration data for 8 ethnic groups, 86 ages, and 34 years.
"""

import numpy as np
import pandas as pd
import struct
import os

def read_mortality_binary_file(filepath):
    """
    Read the mig_disappear.bin file and return a 3D numpy array.
    
    Returns:
        numpy.ndarray: Array with shape (8, 86, 34) representing:
                      - 8 ethnic groups (chinese_male, chinese_female, malay_male, malay_female, 
                        indian_male, indian_female, others_male, others_female)
                      - 86 ages (0-84, 85+)
                      - 34 years (1990-2023)
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # File should contain 8 * 86 * 34 = 23,392 double values
    expected_size = 8 * 86 * 34 * 8  # 8 bytes per double
    actual_size = os.path.getsize(filepath)
    
    if actual_size != expected_size:
        print(f"Warning: Expected file size {expected_size} bytes, got {actual_size} bytes")
    
    with open(filepath, 'rb') as f:
        # Read all data as doubles
        data = f.read()
        values = struct.unpack('d' * (len(data) // 8), data)
        
        # Reshape to (8, 86, 34) - ethnic groups, ages, years
        mortality_matrix = np.array(values).reshape(8, 86, 34)
        
        return mortality_matrix

def create_pivot_table(mortality_matrix):
    """
    Convert the 3D mortality matrix to a pivot table DataFrame.
    
    Args:
        mortality_matrix: numpy array with shape (8, 86, 34)
    
    Returns:
        pandas.DataFrame: Pivot table with columns: sim_year, agent_race, agent_gender, agent_age, mortality_rate
    """
    # Define the mapping for ethnic groups
    ethnic_groups = [
        'chinese_male', 'chinese_female', 
        'malay_male', 'malay_female', 
        'indian_male', 'indian_female', 
        'others_male', 'others_female'
    ]
    
    # Define years (1990-2023)
    years = list(range(1990, 2024))
    
    # Define ages (0-84, 85+)
    ages = list(range(86))  # 0-85, where 85 represents 85+
    
    # Create lists to store the data
    data = []
    
    for ethnic_idx in range(8):
        for age_idx in range(86):
            for year_idx in range(34):
                # Extract the mortality rate
                mortality_rate = mortality_matrix[ethnic_idx, age_idx, year_idx]
                
                # Determine race and gender from ethnic group index
                if ethnic_idx % 2 == 0:  # Even indices are male
                    gender = 'male'
                    race_idx = ethnic_idx // 2
                else:  # Odd indices are female
                    gender = 'female'
                    race_idx = ethnic_idx // 2
                
                # Map race index to race name
                race_map = ['chinese', 'malay', 'indian', 'others']
                race = race_map[race_idx]
                
                # Create the row data
                row = {
                    'sim_year': years[year_idx],
                    'agent_race': race,
                    'agent_gender': gender,
                    'agent_age': age_idx,
                    'mortality_rate': mortality_rate
                }
                data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    return df

def main():
    """Main function to convert the binary file to CSV."""
    # File paths
    binary_filepath = "../data/bin/mig_disappear.bin"
    output_csv_path = "mortality_pivot_table.csv"
    
    print("Converting mig_disappear.bin to CSV pivot table...")
    print(f"Input file: {binary_filepath}")
    print(f"Output file: {output_csv_path}")
    
    try:
        # Read the binary file
        print("Reading binary file...")
        mortality_matrix = read_mortality_binary_file(binary_filepath)
        
        print(f"Successfully read mortality matrix with shape: {mortality_matrix.shape}")
        print(f"Data type: {mortality_matrix.dtype}")
        print(f"Value range: {mortality_matrix.min():.6f} to {mortality_matrix.max():.6f}")
        
        # Create pivot table
        print("Creating pivot table...")
        df = create_pivot_table(mortality_matrix)
        
        print(f"Created pivot table with {len(df)} rows")
        print("\nFirst few rows:")
        print(df.head(10))
        
        print("\nData types:")
        print(df.dtypes)
        
        print("\nSummary statistics:")
        print(df['mortality_rate'].describe())
        
        # Save to CSV
        print(f"\nSaving to {output_csv_path}...")
        df.to_csv(output_csv_path, index=False)
        
        print("✓ Successfully converted binary file to CSV!")
        print(f"✓ Output file: {output_csv_path}")
        print(f"✓ Total rows: {len(df)}")
        
        # Show some sample data by race and gender
        print("\nSample data by race and gender (age 0, year 1990):")
        sample = df[(df['agent_age'] == 0) & (df['sim_year'] == 1990)]
        print(sample[['agent_race', 'agent_gender', 'mortality_rate']])
        
        # Show age distribution for a specific year and race
        print("\nAge distribution for Chinese males in 1990 (first 10 ages):")
        chinese_male_1990 = df[(df['agent_race'] == 'chinese') & 
                              (df['agent_gender'] == 'male') & 
                              (df['sim_year'] == 1990)].head(10)
        print(chinese_male_1990[['agent_age', 'mortality_rate']])
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure the binary file exists in the correct location.")
    except Exception as e:
        print(f"Error during conversion: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 