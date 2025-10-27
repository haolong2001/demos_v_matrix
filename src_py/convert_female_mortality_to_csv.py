#!/usr/bin/env python3
"""
Convert female_mortality.csv to the requested format.
Converts age-specific death rates to individual age records with sim_year, agent_gender, agent_age, mortality_rate.
Creates continuous ages from 0 to 85.
"""

import pandas as pd
import numpy as np
import os

def convert_female_mortality_to_csv(input_file, output_file):
    """
    Convert female_mortality.csv to the requested format with continuous ages 0-85.
    
    Args:
        input_file: Path to female_mortality.csv
        output_file: Path for output CSV
    """
    
    # Read the CSV file
    print(f"Reading {input_file}...")
    df = pd.read_csv(input_file)
    
    print(f"Original data shape: {df.shape}")
    print("Original columns:", df.columns.tolist())
    
    # Clean column names by stripping extra spaces
    df.columns = df.columns.str.strip()
    
    # Filter out the summary row and get only age-specific data
    age_data = df[df['Data Series'] != 'Female Age Specific Death Rate'].copy()
    
    print(f"Age-specific data shape: {age_data.shape}")
    
    # Create age mapping with cleaned names
    age_mapping = {
        'Under 1 Year': 0,
        '1 - 4 Years': 1,
        '5 - 9 Years': 5,
        '10 - 14 Years': 10,
        '15 - 19 Years': 15,
        '20 - 24 Years': 20,
        '25 - 29 Years': 25,
        '30 - 34 Years': 30,
        '35 - 39 Years': 35,
        '40 - 44 Years': 40,
        '45 - 49 Years': 45,
        '50 - 54 Years': 50,
        '55 - 59 Years': 55,
        '60 - 64 Years': 60,
        '65 - 69 Years': 65,
        '70 - 74 Years': 70,
        '75 - 79 Years': 75,
        '80 - 84 Years': 80,
        '85 Years & Over': 85
    }
    
    # Clean the Data Series column as well
    age_data['Data Series'] = age_data['Data Series'].str.strip()
    
    print("Age groups found:")
    for age_group in age_data['Data Series'].unique():
        print(f"  '{age_group}' -> {age_mapping.get(age_group, 'NOT FOUND')}")
    
    # Create the output data with continuous ages
    output_data = []
    
    # First, collect all the age group data by year
    age_group_data = {}
    
    for _, row in age_data.iterrows():
        age_group = row['Data Series'].strip()
        
        if age_group not in age_mapping:
            print(f"Warning: Unknown age group: '{age_group}'")
            continue
            
        age = age_mapping[age_group]
        
        # Process each year column (1990-2024)
        for year in range(1990, 2025):
            year_str = str(year)
            
            if year_str in row:
                # Get mortality rate and convert from per 1000 to decimal
                mortality_rate = row[year_str]
                
                # Handle missing values (na)
                if pd.isna(mortality_rate) or str(mortality_rate).lower() == 'na':
                    continue
                
                try:
                    # Convert from per 1000 to decimal (divide by 1000)
                    mortality_rate_decimal = float(mortality_rate) / 1000
                    
                    # Store data by year
                    if year not in age_group_data:
                        age_group_data[year] = {}
                    age_group_data[year][age] = mortality_rate_decimal
                    
                except (ValueError, TypeError) as e:
                    print(f"Warning: Could not convert mortality rate '{mortality_rate}' for {age_group}, year {year}: {e}")
                    continue
    
    # Now create continuous age data from 0 to 85 for each year
    for year in age_group_data:
        year_data = age_group_data[year]
        
        # Create continuous ages 0-85
        for age in range(86):  # 0 to 85 inclusive
            mortality_rate = None
            
            # Find which age group this age belongs to and use that rate
            if age == 0:
                mortality_rate = year_data.get(0)  # Under 1 Year
            elif age >= 1 and age <= 4:
                mortality_rate = year_data.get(1)  # 1-4 Years
            elif age >= 5 and age <= 9:
                mortality_rate = year_data.get(5)  # 5-9 Years
            elif age >= 10 and age <= 14:
                mortality_rate = year_data.get(10)  # 10-14 Years
            elif age >= 15 and age <= 19:
                mortality_rate = year_data.get(15)  # 15-19 Years
            elif age >= 20 and age <= 24:
                mortality_rate = year_data.get(20)  # 20-24 Years
            elif age >= 25 and age <= 29:
                mortality_rate = year_data.get(25)  # 25-29 Years
            elif age >= 30 and age <= 34:
                mortality_rate = year_data.get(30)  # 30-34 Years
            elif age >= 35 and age <= 39:
                mortality_rate = year_data.get(35)  # 35-39 Years
            elif age >= 40 and age <= 44:
                mortality_rate = year_data.get(40)  # 40-44 Years
            elif age >= 45 and age <= 49:
                mortality_rate = year_data.get(45)  # 45-49 Years
            elif age >= 50 and age <= 54:
                mortality_rate = year_data.get(50)  # 50-54 Years
            elif age >= 55 and age <= 59:
                mortality_rate = year_data.get(55)  # 55-59 Years
            elif age >= 60 and age <= 64:
                mortality_rate = year_data.get(60)  # 60-64 Years
            elif age >= 65 and age <= 69:
                mortality_rate = year_data.get(65)  # 65-69 Years
            elif age >= 70 and age <= 74:
                mortality_rate = year_data.get(70)  # 70-74 Years
            elif age >= 75 and age <= 79:
                mortality_rate = year_data.get(75)  # 75-79 Years
            elif age >= 80 and age <= 84:
                mortality_rate = year_data.get(80)  # 80-84 Years
            elif age >= 85:
                mortality_rate = year_data.get(85)  # 85 Years & Over
            
            # Only add if we have data for this age group
            if mortality_rate is not None:
                output_row = {
                    'sim_year': year,
                    'agent_gender': 'female',
                    'agent_age': age,
                    'mortality_rate': mortality_rate
                }
                output_data.append(output_row)
    
    # Create output DataFrame
    output_df = pd.DataFrame(output_data)
    
    if len(output_df) == 0:
        print("Error: No data was converted!")
        return None
    
    # Sort by year and age
    output_df = output_df.sort_values(['sim_year', 'agent_age'])
    
    print(f"\nOutput data shape: {output_df.shape}")
    print(f"Years covered: {output_df['sim_year'].min()} - {output_df['sim_year'].max()}")
    print(f"Age range: {output_df['agent_age'].min()} - {output_df['agent_age'].max()}")
    print(f"Mortality rate range: {output_df['mortality_rate'].min():.6f} - {output_df['mortality_rate'].max():.6f}")
    
    # Verify we have all ages 0-85 for each year
    years = output_df['sim_year'].unique()
    ages = output_df['agent_age'].unique()
    print(f"\nUnique years: {len(years)} (should be 35)")
    print(f"Unique ages: {len(ages)} (should be 86)")
    print(f"Expected total records: {len(years) * len(ages)} = {35 * 86}")
    
    # Show sample data
    print("\nSample output data:")
    print(output_df.head(20))
    
    # Show data for specific ages
    print("\nSample data for age 0 (infant mortality):")
    infant_data = output_df[output_df['agent_age'] == 0].head(10)
    print(infant_data[['sim_year', 'mortality_rate']])
    
    print("\nSample data for age 85+ (elderly mortality):")
    elderly_data = output_df[output_df['agent_age'] == 85].head(10)
    print(elderly_data[['sim_year', 'mortality_rate']])
    
    # Show some intermediate ages to verify continuity
    print("\nSample data for age 3 (should use 1-4 Years rate):")
    age3_data = output_df[output_df['agent_age'] == 3].head(5)
    print(age3_data[['sim_year', 'mortality_rate']])
    
    print("\nSample data for age 7 (should use 5-9 Years rate):")
    age7_data = output_df[output_df['agent_age'] == 7].head(5)
    print(age7_data[['sim_year', 'mortality_rate']])
    
    # Save to CSV
    print(f"\nSaving to {output_file}...")
    output_df.to_csv(output_file, index=False)
    
    print(f"✓ Successfully converted to {output_file}")
    print(f"✓ Total records: {len(output_df)}")
    
    # Create summary statistics
    print("\nSummary by age groups:")
    age_summary = output_df.groupby('agent_age')['mortality_rate'].agg(['mean', 'std', 'min', 'max'])
    print(age_summary)
    
    return output_df

def main():
    """Main function to convert the female mortality data."""
    
    # File paths
    input_file = "../data/female_mortality.csv"
    output_file = "female_mortality_converted.csv"
    
    print("Converting female_mortality.csv to requested format with continuous ages 0-85...")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    
    try:
        # Check if input file exists
        if not os.path.exists(input_file):
            print(f"Error: {input_file} not found!")
            print("Please ensure the file exists in the correct location.")
            return False
        
        # Convert the data
        output_df = convert_female_mortality_to_csv(input_file, output_file)
        
        if output_df is None:
            return False
        
        print("\n" + "="*60)
        print("CONVERSION COMPLETE!")
        print("="*60)
        print(f"Output file: {output_file}")
        print(f"Total records: {len(output_df)}")
        print(f"Years: {output_df['sim_year'].min()} - {output_df['sim_year'].max()}")
        print(f"Ages: {output_df['agent_age'].min()} - {output_df['agent_age'].max()}")
        print(f"Expected records: 35 years × 86 ages = 3,010")
        print(f"Actual records: {len(output_df)}")
        
        return True
        
    except Exception as e:
        print(f"Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 