import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Tuple

# --- Configuration ---
MORTALITY_DIR = Path("../future_data_1990_2050/mortality_adjusted")
ALBU_DIR = Path("../future_data_1990_2050/albu_matrix_forecast")

# Stage Mapping
STAGE_KEYS_MAP = {
    "K1": 1.0,
    "K2": 2.0,
    "K3a": 3.1,
    "K3b": 3.2,
    "K4": 4.0,
    "K5": 5.0
}
NEW_LABELS = list(STAGE_KEYS_MAP.keys())

# Ethnicity Mapping
ETHNICITY_MAP = {
    'overall': [0, 1, 2, 3, 4, 5, 6, 7],
    'chn': [0, 4],
    'mal': [1, 5],
    'ind': [2, 6]
}

# Age Groups
AGE_BINS = [
    (18, 30, '18-30'),
    (31, 40, '31-40'),
    (41, 50, '41-50'),
    (51, 60, '51-60'),
    (61, 70, '61-70'),
    (71, 80, '71-80'),
    (81, 200, '80+')
]

# --- Loading Functions ---

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

# --- Logic to Calculate Single Scenario ---

def calculate_scenario_prevalence(
    scenario_index: int,
    start_year: int, 
    end_year: int,
    stage_mats: List[np.ndarray],
    age_mats: List[np.ndarray],
    acr_mats: List[np.ndarray]
) -> pd.DataFrame:
    
    print(f"Processing scenario index {scenario_index}...")
    years = list(range(start_year, end_year + 1))
    year0 = 1990
    records = []

    for year in years:
        year_idx = year - year0
        
        # Pre-fetch and flatten group data for efficiency
        group_data = {}
        for idx in range(8):
            # Slices
            s_slice = stage_mats[idx][scenario_index, :, :, [year_idx]].reshape(-1)
            acr_slice = acr_mats[idx][scenario_index, :, :, [year_idx]].reshape(-1)
            
            # Age Handling (3D vs 4D)
            current_age_mat = age_mats[idx]
            if current_age_mat.ndim == 3:
                age_slice = current_age_mat[:, :, [year_idx]].reshape(-1)
            else:
                age_slice = current_age_mat[scenario_index, :, :, [year_idx]].reshape(-1)
            
            group_data[idx] = {
                's': s_slice,
                'acr': acr_slice,
                'age': age_slice,
                'n_simu': stage_mats[idx].shape[1]
            }

        # Helper: Calculate metrics for a subset of groups
        def calc_and_append(subset_indices, mask_func, eth_label, age_label):
            total_pop_weighted = 0.0
            stage_counts_weighted = {k: 0.0 for k in NEW_LABELS}
            
            for g_idx in subset_indices:
                g = group_data[g_idx]
                n_sim = g['n_simu']
                
                # Filter Population
                pop_mask = mask_func(g['age'])
                total_pop_weighted += (np.sum(pop_mask) / n_sim)
                
                # Filter Data
                s_valid = g['s'][pop_mask]
                acr_valid = g['acr'][pop_mask]
                
                for k in NEW_LABELS:
                    target = STAGE_KEYS_MAP[k]
                    if k in ["K1", "K2"]:
                        k_mask = np.isclose(s_valid, target) & (acr_valid >= 1)
                    else:
                        k_mask = np.isclose(s_valid, target)
                    stage_counts_weighted[k] += (np.sum(k_mask) / n_sim)

            # Store Results
            for k in NEW_LABELS:
                if total_pop_weighted == 0:
                    val = 0.0
                else:
                    val = (stage_counts_weighted[k] / total_pop_weighted) * 100
                
                records.append({
                    "stage": k,
                    "ethnicity": eth_label,
                    "age_group": age_label,
                    "year": year,
                    "val_temp": val 
                })

        # A. By Ethnicity (Age = Overall 18+)
        for eth, indices in ETHNICITY_MAP.items():
            mask_func = lambda a: (a >= 18)
            calc_and_append(indices, mask_func, eth, "Overall")

        # B. By Age Group (Ethnicity = Overall)
        overall_indices = ETHNICITY_MAP['overall']
        for (min_a, max_a, bin_label) in AGE_BINS:
            mask_func = lambda a: (a >= min_a) & (a <= max_a)
            calc_and_append(overall_indices, mask_func, "overall", bin_label)

    return pd.DataFrame(records)

# --- Main Execution ---

if __name__ == "__main__":
    start_y = 1990
    end_y = 2050
    
    print("Loading matrices...")
    stage_mats_loaded = load_adjusted_stage_matrices()
    age_mats_loaded = load_adjusted_age_matrices()
    acr_mats_loaded = load_acr_matrices()
    
    # 1. Calculate Lower Bound (Scenario 0)
    print("\n--- Calculating Lower Bound (Scenario 0) ---")
    df_lower = calculate_scenario_prevalence(
        0, start_y, end_y, stage_mats_loaded, age_mats_loaded, acr_mats_loaded
    )
    df_lower.rename(columns={'val_temp': 'lower'}, inplace=True)
    
    # 2. Calculate Upper Bound (Scenario 1)
    print("\n--- Calculating Upper Bound (Scenario 1) ---")
    df_upper = calculate_scenario_prevalence(
        1, start_y, end_y, stage_mats_loaded, age_mats_loaded, acr_mats_loaded
    )
    df_upper.rename(columns={'val_temp': 'upper'}, inplace=True)
    
    # 3. Merge
    print("\nMerging datasets...")
    merge_cols = ['stage', 'ethnicity', 'age_group', 'year']
    df_final = pd.merge(df_lower, df_upper, on=merge_cols, how='inner')
    
    # 4. Calculate Mean Prevalence
    df_final['prevalence'] = (df_final['lower'] + df_final['upper']) / 2
    
    # 5. Formatting (Round to 2 decimal places)
    cols_to_round = ['prevalence', 'lower', 'upper']
    df_final[cols_to_round] = df_final[cols_to_round].round(2)
    
    # Reorder columns
    final_cols = ['stage', 'ethnicity', 'age_group', 'year', 'prevalence', 'lower', 'upper']
    df_final = df_final[final_cols]
    
    # 6. Save
    f_out = "granular_ckd_prevalence_1990_2050.csv"
    df_final.to_csv(f_out, index=False)
    
    print(f"\nSuccessfully saved: {f_out}")
    print("\n=== Sample Preview ===")
    print(df_final.head())
    
    # Check specific sample
    mask = (df_final['stage'] == 'K1') & (df_final['ethnicity'] == 'overall') & (df_final['age_group'] == '41-50')
    if not df_final[mask].empty:
        print("\n=== Sample Row Check (K1, Overall, 41-50) ===")
        print(df_final[mask].head(1))