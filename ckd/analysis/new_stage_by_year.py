import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Tuple

# --- Configuration ---
MORTALITY_DIR = Path("../future_data_1990_2050/mortality_adjusted")
ALBU_DIR = Path("../future_data_1990_2050/albu_matrix_forecast")

# Old keys for mapping
# Note: G1 (1.0) and G2 (2.0) logic is changed; G3a-G5 remain the same
STAGE_KEYS_MAP = {
    "K1": 1.0,
    "K2": 2.0,
    "K3a": 3.1,
    "K3b": 3.2,
    "K4": 4.0,
    "K5": 5.0
}
NEW_LABELS = list(STAGE_KEYS_MAP.keys())

# --- Loading Functions (Adapted from get_table.py) ---

def load_adjusted_stage_matrices() -> List[np.ndarray]:
    mats = []
    for idx in range(8):
        path = MORTALITY_DIR / f"stage_matrix_group_{idx}.npy"
        mats.append(np.load(path))
    return mats

def load_adjusted_age_matrices() -> List[np.ndarray]:
    mats = []
    for idx in range(8):
        path = MORTALITY_DIR / f"age_matrix_group_{idx}.npy"
        mats.append(np.load(path))
    return mats

def load_acr_matrices() -> List[np.ndarray]:
    mats = []
    for idx in range(8):
        path = ALBU_DIR / f"albu_mat_group_{idx}.npy"
        mats.append(np.load(path))
    return mats

# --- Main Processing Logic ---
# --- Main Logic ---

def build_new_standard_table(
    start_year: int, 
    end_year: int, 
    max_age: int = 74
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    
    print("Loading matrices...")
    stage_mats = load_adjusted_stage_matrices()
    age_mats = load_adjusted_age_matrices()
    acr_mats = load_acr_matrices()
    
    years = list(range(start_year, end_year + 1))
    year0 = 1990
    
    # Initialize DataFrames with explicit columns
    # We add "Total_Population" to the columns list
    columns = NEW_LABELS + ["Total_Population"]
    df_start = pd.DataFrame(0.0, index=years, columns=columns)
    df_end = pd.DataFrame(0.0, index=years, columns=columns)

    print(f"Processing years {start_year} to {end_year}...")

    for year in years:
        year_index = year - year0
        
        for idx in range(8):
            n_simu = stage_mats[idx].shape[1]

            # --- 1. Slices: Stage ---
            s_slice_start = stage_mats[idx][0, :, :, [year_index]]
            s_slice_end   = stage_mats[idx][-1, :, :, [year_index]]
            
            # --- 2. Slices: ACR ---
            acr_slice_start = acr_mats[idx][0, :, :, [year_index]]
            acr_slice_end   = acr_mats[idx][-1, :, :, [year_index]]

            # --- 3. Slices: Age ---
            current_age_mat = age_mats[idx]
            
            # Handle 3D vs 4D Age Matrix
            if current_age_mat.ndim == 3:
                # Shape: (sim, person, year)
                age_slice_start = current_age_mat[:, :, [year_index]]
                age_slice_end   = age_slice_start # Same for both
            else:
                # Shape: (scenario, sim, person, year)
                age_slice_start = current_age_mat[0, :, :, [year_index]]
                age_slice_end   = current_age_mat[-1, :, :, [year_index]]

            # Flatten Arrays
            s_flat_start = s_slice_start.reshape(-1)
            s_flat_end   = s_slice_end.reshape(-1)
            
            acr_flat_start = acr_slice_start.reshape(-1)
            acr_flat_end   = acr_slice_end.reshape(-1)
            
            a_flat_start = age_slice_start.reshape(-1)
            a_flat_end   = age_slice_end.reshape(-1)
            
            # --- 4. Age Masks (Defines Total Population) ---
            # This captures everyone alive in the age range, regardless of CKD status
            mask_pop_start = (a_flat_start >= 18) & (a_flat_start <= max_age)
            mask_pop_end   = (a_flat_end >= 18)   & (a_flat_end <= max_age)
            
            # Add to Total Population Column
            df_start.loc[year, "Total_Population"] += (np.sum(mask_pop_start) / n_simu)
            df_end.loc[year, "Total_Population"]   += (np.sum(mask_pop_end) / n_simu)

            # --- 5. Valid Subsets for Stage Classification ---
            s_valid_start = s_flat_start[mask_pop_start]
            acr_valid_start = acr_flat_start[mask_pop_start]
            
            s_valid_end = s_flat_end[mask_pop_end]
            acr_valid_end = acr_flat_end[mask_pop_end]

            # --- 6. Categorize into New Standard (K1 - K5) ---
            for label in NEW_LABELS:
                target_stage_val = STAGE_KEYS_MAP[label]
                
                # --- START SCENARIO ---
                if label in ["K1", "K2"]:
                    # Strict: Stage Match AND ACR >= 1 (A2/A3)
                    mask = np.isclose(s_valid_start, target_stage_val) & (acr_valid_start >= 1)
                else:
                    # Standard
                    mask = np.isclose(s_valid_start, target_stage_val)
                
                df_start.loc[year, label] += (np.sum(mask) / n_simu)

                # --- END SCENARIO ---
                if label in ["K1", "K2"]:
                    mask_end = np.isclose(s_valid_end, target_stage_val) & (acr_valid_end >= 1)
                else:
                    mask_end = np.isclose(s_valid_end, target_stage_val)
                
                df_end.loc[year, label] += (np.sum(mask_end) / n_simu)

    # --- 7. Add derived "Total_CKD" column ---
    # Sum only the stage columns (excluding Total_Population)
    df_start["Total_CKD"] = df_start[NEW_LABELS].sum(axis=1)
    df_end["Total_CKD"]   = df_end[NEW_LABELS].sum(axis=1)
    
    # Reorder columns for readability
    final_cols = NEW_LABELS + ["Total_CKD", "Total_Population"]
    df_start = df_start[final_cols]
    df_end   = df_end[final_cols]
    
    return df_start, df_end

if __name__ == "__main__":
    # Parameters
    start_y = 1990
    end_y = 2050
    max_age_val = 74

    print(f"Generating New Standard CKD Tables with Total Population ({start_y}-{end_y})...")
    
    result_start, result_end = build_new_standard_table(start_y, end_y, max_age=max_age_val)
    
    pd.set_option('display.max_rows', 10)
    pd.set_option('display.width', 1000)
    
    print("\n=== START SCENARIO (Preview) ===")
    print(result_start.round(0))
    
    # Save to CSV
    f_start = "new_standard_ckd_1990_2050_start.csv"
    f_end = "new_standard_ckd_1990_2050_end.csv"
    
    result_start.to_csv(f_start)
    result_end.to_csv(f_end)
    
    print(f"\nFiles saved:\n  - {f_start}\n  - {f_end}")