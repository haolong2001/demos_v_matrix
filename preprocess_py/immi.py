#!/usr/bin/env python3
"""
Convert uniform immigration parameters numpy array to CSV format.

This script reads the uniform_params array with shape (8, 50, 2) and converts it to a CSV file
with columns: ethnicity, gender, age, para_lower, para_upper

The 8 ethnic groups are:
- 0,1: Chinese (male, female)
- 2,3: Malay (male, female) 
- 4,5: Indian (male, female)
- 6,7: Other (male, female)

Ages range from 1 to 50.
"""

import numpy as np
import pandas as pd
import os

def load_uniform_params(filename: str) -> np.ndarray:
    """
    Load the uniform parameters from numpy file.
    
    Args:
        filename: Path to the numpy file
        
    Returns:
        3D numpy array with shape (8, 50, 2)
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File not found: {filename}")
    
    # Load numpy array
    uniform_params = np.load(filename)
    
    print(f"Successfully loaded uniform parameters from: {filename}")
    print(f"Data shape: {uniform_params.shape}")
    print(f"Data type: {uniform_params.dtype}")
    
    return uniform_params

def get_ethnicity_label(ethnicity_idx: int) -> str:
    """
    Convert ethnicity index to label.
    
    Args:
        ethnicity_idx: Ethnicity index (0-3)
        
    Returns:
        Ethnicity label
    """
    ethnicity_labels = ['Chinese', 'Malay', 'Indian', 'Other']
    return ethnicity_labels[ethnicity_idx]

def get_gender_label(ethnicity_idx: int) -> str:
    """
    Convert ethnicity index to gender label.
    
    Args:
        ethnicity_idx: Ethnicity index (0-7)
        
    Returns:
        Gender label ('male' or 'female')
    """
    return 'male' if ethnicity_idx % 2 == 0 else 'female'

def convert_to_dataframe(uniform_params: np.ndarray) -> pd.DataFrame:
    """
    Convert 3D uniform parameters array to DataFrame with specified format.
    
    Args:
        uniform_params: 3D numpy array with shape (8, 50, 2)
        
    Returns:
        DataFrame with columns: agent_race, agent_gender, agent_age, para_lower, para_upper
    """
    # Prepare data for DataFrame
    data_rows = []
    
    # Process each ethnic group (0-7)
    for i in range(8):
        # Calculate ethnicity index (0-3) and gender
        ethnicity_idx = i // 2
        ethnicity = get_ethnicity_label(ethnicity_idx)
        gender = get_gender_label(i)
        
        # Process each age (1-50)
        for age in range(1, 51):
            # Get parameters for this ethnic group and age
            para_lower = uniform_params[i, age-1, 0]  # age-1 because ages start from 1
            para_upper = uniform_params[i, age-1, 1]
            
            data_rows.append({
                'agent_race': ethnicity,
                'agent_gender': gender,
                'agent_age': age,
                'para_lower': para_lower,
                'para_upper': para_upper
            })
    
    # Create DataFrame
    df = pd.DataFrame(data_rows)
    
    print(f"Created DataFrame with {len(df)} rows")
    print(f"Columns: {list(df.columns)}")
    print(f"Races: {df['agent_race'].unique()}")
    print(f"Genders: {df['agent_gender'].unique()}")
    print(f"Age range: {df['agent_age'].min()} to {df['agent_age'].max()}")
    
    return df

def main():
    """Main function to convert uniform parameters to CSV."""
    # Input and output file paths
    input_file = "uniform_immigration_params.npy"  # Update this path to your actual numpy file
    output_file = "immigration_uniform_param.csv"
    
    # Since the input file path might not exist, let's try to find the actual numpy file
    # possible_files = [
    #     "../preprocess_py/uniform_params.npy",
    #     "../preprocess_py/uniform_immigration_params.npy",
    #     "uniform_params.npy",
    #     "uniform_immigration_params.npy"
    # ]
    
    # input_file = None
    # for file_path in possible_files:
    #     if os.path.exists(file_path):
    #         input_file = file_path
    #         break
    
    # if input_file is None:
    #     print("Error: Could not find uniform_params numpy file.")
    #     print("Please provide the correct path to the numpy file containing uniform_params.")
    #     print("Expected files:")
    #     for file_path in possible_files:
    #         print(f"  - {file_path}")
    #     return 1
    
    try:
        # Load uniform parameters
        print(f"Loading uniform parameters from: {input_file}")
        uniform_params = load_uniform_params(input_file)
        
        # Convert to DataFrame
        print("Converting to DataFrame...")
        df = convert_to_dataframe(uniform_params)
        
        # Save to CSV
        print(f"Saving to CSV: {output_file}")
        df.to_csv(output_file, index=False, float_format='%.6f')
        
        print(f"Successfully converted uniform parameters to CSV!")
        print(f"Output file: {output_file}")
        print(f"Total rows: {len(df)}")
        
        # Display sample data
        print("\nSample data:")
        print(df.head(10))
        
        # # Display summary by race and gender
        # print("\nSummary by race and gender:")
        # summary = df.groupby(['agent_race', 'agent_gender']).agg({
        #     'para_lower': ['count', 'mean', 'min', 'max'],
        #     'para_upper': ['mean', 'min', 'max']
        # }).round(6)
        # print(summary)
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())