#!/usr/bin/env python3
"""
Convert mortality binary file to CSV format.

This script reads the binary file '../preprocess_py/mortality_forecast_from_24.bin'
and converts it to a CSV file with headers: sim_year,agent_gender,agent_age,mortality_rate

The binary file contains a 3D matrix with dimensions [2][18][27]:
- 2 genders (0=male, 1=female)
- 18 age groups (0-4, 5-9, 10-14, ..., 80-84, 85+)
- 27 years (2024-2050)

Output CSV will have continuous ages from 0 to 84, 85+ for each gender and year.
"""

import numpy as np
import pandas as pd
import os
from typing import List, Tuple

def read_mortality_binary(filename: str) -> np.ndarray:
    """
    Read the mortality binary file.
    
    Args:
        filename: Path to the binary file
        
    Returns:
        3D numpy array with shape (2, 18, 27)
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File not found: {filename}")
    
    # Read binary file
    data = np.fromfile(filename, dtype=np.float64)
    
    # Reshape to 3D array: [gender][age_group][year]
    # Total elements: 2 * 18 * 27 = 972
    data = data.reshape(2, 18, 27)
    
    print(f"Successfully read binary file: {filename}")
    print(f"Data shape: {data.shape}")
    print(f"Data type: {data.dtype}")
    print(f"Data range: {data.min():.6f} to {data.max():.6f}")
    
    return data

def map_age_groups_to_continuous_ages() -> List[int]:
    """
    Map the 18 age groups to continuous ages.
    
    Returns:
        List of ages: [0, 1, 2, ..., 84, 85]
    """
    ages = []
    # Age groups: 0-4, 5-9, 10-14, ..., 80-84, 85+
    for i in range(18):
        if i < 17:  # 0-4, 5-9, ..., 80-84
            start_age = i * 5
            ages.extend(range(start_age, start_age + 5))
        else:  # 85+
            ages.append(85)
    
    return ages

def convert_to_dataframe(mortality_data: np.ndarray) -> pd.DataFrame:
    """
    Convert 3D mortality array to DataFrame with specified format.
    
    Args:
        mortality_data: 3D numpy array with shape (2, 18, 27)
        
    Returns:
        DataFrame with columns: sim_year, agent_gender, agent_age, mortality_rate
    """
    # Get age mapping
    age_groups = map_age_groups_to_continuous_ages()
    
    # Prepare data for DataFrame
    data_rows = []
    
    # Years: 2024-2050 (27 years)
    years = list(range(2024, 2051))
    
    # Genders: 0=male, 1=female
    gender_labels = ['male', 'female']
    
    for gender_idx in range(2):
        gender = gender_labels[gender_idx]
        
        for year_idx, year in enumerate(years):
            for age_group_idx in range(18):
                # Get mortality rate for this gender, age group, and year
                mortality_rate = mortality_data[gender_idx, age_group_idx, year_idx]
                
                # Apply mortality_rate / 1000 conversion
                mortality_rate_converted = mortality_rate / 1000.0
                
                # Map age group to continuous ages
                if age_group_idx < 17:  # 0-4, 5-9, ..., 80-84
                    start_age = age_group_idx * 5
                    for age in range(start_age, start_age + 5):
                        data_rows.append({
                            'sim_year': year,
                            'agent_gender': gender,
                            'agent_age': age,
                            'mortality_rate': mortality_rate_converted
                        })
                else:  # 85+
                    data_rows.append({
                        'sim_year': year,
                        'agent_gender': gender,
                        'agent_age': 85,
                        'mortality_rate': mortality_rate_converted
                    })
    
    # Create DataFrame
    df = pd.DataFrame(data_rows)
    
    print(f"Created DataFrame with {len(df)} rows")
    print(f"Columns: {list(df.columns)}")
    print(f"Year range: {df['sim_year'].min()} to {df['sim_year'].max()}")
    print(f"Age range: {df['agent_age'].min()} to {df['agent_age'].max()}")
    print(f"Genders: {df['agent_gender'].unique()}")
    
    return df

def main():
    """Main function to convert binary file to CSV."""
    # Input and output file paths - updated for src_py folder location
    input_file = "../preprocess_py/mortality_forecast_from_24.bin"
    output_file = "mortality_forecast_2024_2050.csv"
    
    try:
        # Read binary file
        print(f"Reading binary file: {input_file}")
        mortality_data = read_mortality_binary(input_file)
        
        # Convert to DataFrame
        print("Converting to DataFrame...")
        df = convert_to_dataframe(mortality_data)
        
        # Save to CSV with 4 decimal places formatting
        print(f"Saving to CSV: {output_file}")
        df.to_csv(output_file, index=False, float_format='%.4f')
        
        print(f"Successfully converted binary file to CSV!")
        print(f"Output file: {output_file}")
        print(f"Total rows: {len(df)}")
        
        # Display sample data
        print("\nSample data:")
        print(df.head(10))
        
        # Display summary statistics
        print("\nSummary statistics:")
        print(df.groupby(['agent_gender', 'agent_age'])['mortality_rate'].describe())
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 