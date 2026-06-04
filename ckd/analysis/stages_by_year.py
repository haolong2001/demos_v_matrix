import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Tuple

MORTALITY_DIR = Path("../future_data_1990_2050/mortality_adjusted")
STAGE_KEYS = [1.0, 2.0, 3.1, 3.2, 4.0, 5.0]
STAGE_LABELS = ["G1", "G2", "G3a", "G3b", "G4", "G5"]

def load_adjusted_matrices(name: str) -> List[np.ndarray]:
    mats = []
    for idx in range(8):
        path = MORTALITY_DIR / f"{name}_matrix_group_{idx}.npy"
        mats.append(np.load(path))
    return mats

def build_stage_year_tables(start_year: int, end_year: int, max_age: int = 74) -> Tuple[pd.DataFrame, pd.DataFrame]:
    stage_mats = load_adjusted_matrices("stage")
    age_mats = load_adjusted_matrices("age")
    
    years = list(range(start_year, end_year + 1))
    year0 = 1990
    
    # Initialize TWO DataFrames: one for start state (0), one for end state (-1)
    df_start = pd.DataFrame(0.0, index=STAGE_LABELS, columns=years)
    df_end = pd.DataFrame(0.0, index=STAGE_LABELS, columns=years)

    for year in years:
        year_index = year - year0
        
        for idx in range(8):
            # --- 1. Get the Slices (Start and End) ---
            # Start: index 0
            stage_slice_start = stage_mats[idx][0, :, :, [year_index]]
            # End: index -1
            stage_slice_end = stage_mats[idx][-1, :, :, [year_index]]
            
            n_simu = stage_mats[idx].shape[1]
            
            # --- 2. Get Age Mask (Using existing logic) ---
            current_age_mat = age_mats[idx]
            if current_age_mat.ndim == 3:
                age_slice = current_age_mat[:, :, [year_index]]
            else:
                # Defaulting to index 0 for age if it has 4 dims, 
                # assuming age is consistent for the filtering step
                age_slice = current_age_mat[0, :, :, [year_index]]

            # Flatten arrays
            s_flat_start = stage_slice_start.reshape(-1)
            s_flat_end = stage_slice_end.reshape(-1)
            a_flat = age_slice.reshape(-1)
            
            # Create Age Filter
            age_mask = (a_flat >= 18) & (a_flat <= max_age)
            
            # Apply Filter
            s_valid_start = s_flat_start[age_mask]
            s_valid_end = s_flat_end[age_mask]
            
            # --- 3. Count and Accumulate for Both Tables ---
            for s_val, s_label in zip(STAGE_KEYS, STAGE_LABELS):
                # Process Start
                count_start = np.sum(np.isclose(s_valid_start, s_val))
                df_start.loc[s_label, year] += (count_start / n_simu)
                
                # Process End
                count_end = np.sum(np.isclose(s_valid_end, s_val))
                df_end.loc[s_label, year] += (count_end / n_simu)

    # Add Totals row to both
    df_start.loc["Total"] = df_start.sum()
    df_end.loc["Total"] = df_end.sum()
    
    return df_start, df_end

if __name__ == "__main__":
    print("Processing years 2013 - 2023...")
    # Tuple unpacking for the two returned DataFrames
    result_start, result_end = build_stage_year_tables(2013, 2023, max_age=74)
    
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    
    print("\n=== CKD Stage Counts (START [0]) ===")
    print(result_start.round(2))
    
    print("\n=== CKD Stage Counts (END [-1]) ===")
    print(result_end.round(2))
    
    # Save both files
    result_start.to_csv("stage_year_summary_start.csv")
    result_end.to_csv("stage_year_summary_end.csv")
    print("\nSaved 'stage_year_summary_start.csv' and 'stage_year_summary_end.csv'")