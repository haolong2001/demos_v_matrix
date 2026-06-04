
"""
Screening Analysis Driver (Cell-Based)
--------------------------------------
1. Loads raw .npy data.
2. Builds General CKD matrices.
3. Runs Screening Analysis with:
   - Competing Risk: Hospitalization (modified for ACR check).
   - Participation Rates (0.6, 0.8, 1.0).
"""

# %% [markdown]
# # 1. Imports & Setup

# %%
import os
from pathlib import Path
from typing import Sequence
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Define Paths
SCRIPT_DIR = Path(__file__).resolve().parent
# Adjust these relative paths if your folder structure differs
CKD_DIR = SCRIPT_DIR.parent
REPO_ROOT = SCRIPT_DIR.parents[1]
FUTURE_DATA_DIR = CKD_DIR / "future_data_1990_2050"
MORTALITY_DIR = FUTURE_DATA_DIR / "mortality_adjusted"
RESULTS_DIR = SCRIPT_DIR / "results_df"

RESULTS_DIR.mkdir(exist_ok=True)

# %% [markdown]
# # 2. Data Loading Functions

# %%
def load_stage_matrices() -> list[np.ndarray]:
    return [np.load(MORTALITY_DIR / f"stage_matrix_group_{idx}.npy") for idx in range(8)]

def load_age_matrices() -> list[np.ndarray]:
    return [np.load(MORTALITY_DIR / f"age_matrix_group_{idx}.npy") for idx in range(8)]

def load_albu_matrices() -> list[np.ndarray]:
    albu_dir = FUTURE_DATA_DIR / "albu_matrix_forecast"
    return [np.load(albu_dir / f"albu_mat_group_{idx}.npy") for idx in range(8)]

def load_hypertension_matrices() -> list[np.ndarray]:
    hyper_dir = FUTURE_DATA_DIR / "hyper_matrix"
    return [np.load(hyper_dir / f"hypertension_mat_{idx}.npy") for idx in range(8)]

def load_diabetes_matrices() -> list[np.ndarray]:
    diab_dir = FUTURE_DATA_DIR / "diabetes_matrix"
    return [np.load(diab_dir / f"diabetes_mat_{idx}.npy") for idx in range(8)]

# %% [markdown]
# # 3. Data Processing Helpers

# %%
def build_general_ckd_matrices(
    stage_matrix_ls: Sequence[np.ndarray],
    acr_matrix_ls: Sequence[np.ndarray],
    healthy_stage_threshold: int = 2,
) -> list[np.ndarray]:
    """
    Constructs the binary CKD indicator (1=CKD, 0=Healthy).
    Healthy if (stage <= 2 AND acr == 0).
    """
    if len(stage_matrix_ls) != len(acr_matrix_ls):
        raise ValueError("Stage and ACR matrix collections must have the same length.")

    general_ckd_mat_ls = []
    for i in range(len(stage_matrix_ls)):
        stage_matrix = stage_matrix_ls[i]
        acr_matrix = acr_matrix_ls[i]

        # CKD is default (set to 1 everywhere)
        ckd_matrix = np.ones_like(stage_matrix, dtype=int)
        
        # Healthy if (stage <= threshold AND acr == 0)
        healthy_mask = (stage_matrix <= healthy_stage_threshold) & (acr_matrix == 0)
        ckd_matrix[healthy_mask] = 0
        
        # Maintain death markers
        ckd_matrix[stage_matrix == -1] = -1
        ckd_matrix[stage_matrix == -2] = -2
        general_ckd_mat_ls.append(ckd_matrix)

    return general_ckd_mat_ls

# %% [markdown]
# # 4. Screening Logic Helpers

# %%
def slice_window_data(
    age_matrix, ckd_matrix, stage_matrix, hyper_matrix, diab_matrix, 
    acr_matrix,  # <--- NEW: Raw Albuminuria Matrix
    idx_start, idx_end, albu_idx, sim_idx
):
    """
    Extracts data for the specific analysis window (e.g. 2026-2050).
    """
    # Handle Age (sometimes 3D, sometimes 4D in your datasets)
    if age_matrix.ndim == 4:
        age_win = age_matrix[albu_idx, sim_idx, :, idx_start : idx_end + 1]
    else:
        age_win = age_matrix[sim_idx, :, idx_start : idx_end + 1]

    ckd_win = ckd_matrix[albu_idx, sim_idx, :, idx_start : idx_end + 1]
    stage_win = stage_matrix[albu_idx, sim_idx, :, idx_start : idx_end + 1]
    
    # Slice the Raw Albuminuria Matrix for the hospitalization check
    acr_win = acr_matrix[albu_idx, sim_idx, :, idx_start : idx_end + 1]

    # Risk factors are (sim, person, year)
    hyper_win = hyper_matrix[sim_idx, :, idx_start : idx_end + 1]
    diab_win = diab_matrix[sim_idx, :, idx_start : idx_end + 1]
    
    return age_win, ckd_win, stage_win, hyper_win, diab_win, acr_win


def define_hospitalization_events(stage_win, acr_win, rand_hosp_matrix):
    """
    Determines if and when a person is identified by hospitalization.
    Rates: 
      - Stage 1-2: 0.5% (ONLY IF ACR != 0)
      - Stage 3:   7.0% 
      - Stage 4:   49.5%
      - Stage 5:   97.5%
    """
    # Map stages to probability of being hospitalized/identified
    prob_map = np.zeros_like(stage_win, dtype=float)
    
    # --- MODIFIED LOGIC: Check ACR for Early Stages ---
    # Rate 0.5% for Stage 1-2, BUT ONLY if ACR is not 0
    mask_early_risk = (stage_win >= 1) & (stage_win <= 2) & (acr_win != 0)
    prob_map[mask_early_risk] = 0.005  
    
    # Standard rates for later stages
    prob_map[(stage_win == 3)] = 0.070                     
    prob_map[(stage_win == 4)] = 0.495                     
    prob_map[(stage_win == 5)] = 0.975                     
    
    # Determine events: True if Random Draw < Probability
    hosp_event_mask = rand_hosp_matrix < prob_map
    
    # Find the FIRST year of hospitalization
    # argmax returns index of first True. If all False, returns 0.
    first_hosp_idx = np.argmax(hosp_event_mask, axis=1)
    
    # Create a mask for people who were NEVER hospitalized
    any_hosp = hosp_event_mask.any(axis=1)
    
    # Set index to 9999 (infinity) if never hospitalized
    final_hosp_idx = np.where(any_hosp, first_hosp_idx, 9999)
    
    return final_hosp_idx


def precompute_age_bands(age_win, hyper_win, diab_win, age_steps):
    """
    Creates boolean masks for age bands to speed up strategy testing.
    """
    band_masks = {}
    sorted_steps = sorted(age_steps, reverse=True)
    
    for i, step in enumerate(sorted_steps):
        lower_bound = step
        upper_bound = sorted_steps[i-1] if i > 0 else 999
        
        in_band = (age_win >= lower_bound) & (age_win < upper_bound)
        
        band_masks[step] = {
            'All': in_band,
            'Union': in_band & ((diab_win == 1) | (hyper_win == 1)),
            'Hyper': in_band & (hyper_win == 1)
        }
    
    return band_masks, sorted_steps

# %% [markdown]
# # 5. Simulation Engine

# %%
def simulate_strategies_with_participation(
    strategies, participation_rates,
    band_masks, sorted_steps, 
    detectable_mask, ckd_win, stage_win,
    hosp_idx_vec, rand_part_matrix,
    age_win_shape
):
    """
    Iterates through strategies AND participation rates.
    Logic:
      - Patient must participate (Random < Rate) to be screened.
      - Patient must be screened BEFORE hospitalization to count as a 'TP'.
    """
    results = []
    
    # Basic Truth Vectors (who is a Case?)
    # Exclude those who start with Stage >= 4 (already advanced)
    start_excluded = stage_win[:, 0] >= 4
    ever_ckd = (ckd_win == 1).max(axis=1)
    
    is_case = ever_ckd & (~start_excluded)
    is_non_case = (~ever_ckd) & (~start_excluded)
    
    # --- Loop 1: Participation Rates ---
    for part_rate in participation_rates:
        
        # Determine who participates this year (Random < Participation Rate)
        is_participating = rand_part_matrix < part_rate
        
        # --- Loop 2: Screening Strategies ---
        for (g_thr, d_thr, h_thr) in strategies:
            
            # 1. Build Eligibility Mask (Who is *invited*?)
            eligible_mask = np.zeros(age_win_shape, dtype=bool)
            for step in sorted_steps:
                masks = band_masks[step]
                if step >= g_thr:
                    eligible_mask |= masks['All']
                elif step >= d_thr:
                    eligible_mask |= masks['Union']
                elif step >= h_thr:
                    eligible_mask |= masks['Hyper']
            
            # 2. Determine Screening Events (Invited AND Participated)
            screened_mask = eligible_mask & is_participating
            
            # 3. Determine Detection Events (Screened AND Detectable Condition met)
            # Detectable = CKD=1, Stage<=4, Alive
            detection_mask = screened_mask & detectable_mask
            
            # 4. Find FIRST Screening Detection Year
            first_screen_idx = np.argmax(detection_mask, axis=1)
            any_screen_detect = detection_mask.any(axis=1)
            final_screen_idx = np.where(any_screen_detect, first_screen_idx, 9999)
            
            # 5. Compare with Hospitalization (Competing Risk)
            # TP = Case AND Detected by Screening AND (Screen_Year <= Hosp_Year)
            # (If Screen_Year > Hosp_Year, the hospital found them first)
            caught_by_screening = (
                is_case & 
                any_screen_detect & 
                (final_screen_idx <= hosp_idx_vec)
            )
            
            tp = np.sum(caught_by_screening)
            
            # FN = Case AND (Not Caught OR Hospital Found First)
            fn = np.sum(is_case & (~caught_by_screening))
            
            # Specificity Logic (Healthy People)
            # FP: Healthy person who was ever screened
            ever_screened_any_reason = screened_mask.any(axis=1)
            
            fp = np.sum(is_non_case & ever_screened_any_reason)
            tn = np.sum(is_non_case & (~ever_screened_any_reason))
            
            # Burden
            n_people_screened = np.sum(ever_screened_any_reason)
            
            results.append({
                "parti": part_rate,
                "gen_thresh": g_thr,
                "diab_thresh": d_thr,
                "hyper_thresh": h_thr,
                "TP": tp, "FN": fn, "FP": fp, "TN": tn,
                "Total_Screened": n_people_screened
            })
            
    return results


def analyze_screening_performance_modular(
    age_matrix_vec,
    ckd_mat_list,
    stage_matrix_ls,
    hypertension_mat_storage,
    diabetes_mat_storage,
    acr_mat_list,  # <--- NEW: Raw Albuminuria Data
    year_start=2026,
    year_end=2050,
    base_year=1990,
    age_steps=[60, 55, 50, 45, 40, 35],
    participation_rates=[0.6, 0.8, 1.0],
    target_albu_indices=[0, 1] 
):
    idx_start = year_start - base_year
    idx_end = year_end - base_year 
    
    # Generate Strategies (G >= D >= H)
    strategies = []
    sorted_steps = sorted(age_steps, reverse=True)
    for g in sorted_steps:
        for d in sorted_steps:
            if d > g: continue
            for h in sorted_steps:
                if h > d: continue
                strategies.append((g, d, h))
                
    print(f"Running simulation: {len(strategies)} strategies x {len(participation_rates)} participation rates...")
    
    n_groups = len(age_matrix_vec)
    n_albu, n_sims, _, _ = ckd_mat_list[0].shape
    
    all_results = []

    for albu in target_albu_indices:
        for sim in range(n_sims):
            for g in range(n_groups):
                
                # 1. Slice Data
                # Note: We now pass acr_mat_list[g]
                age_win, ckd_win, stage_win, hyper_win, diab_win, acr_win = slice_window_data(
                    age_matrix_vec[g], 
                    ckd_mat_list[g], 
                    stage_matrix_ls[g], 
                    hypertension_mat_storage[g], 
                    diabetes_mat_storage[g],
                    acr_mat_list[g],  # <--- PASS RAW ACR
                    idx_start, idx_end, albu, sim
                )
                
                # 2. Generate Randomness for this block
                rng = np.random.default_rng(seed=sim+g+albu) 
                rand_hosp = rng.random(size=stage_win.shape)
                rand_part = rng.random(size=stage_win.shape)
                
                # 3. Determine Hospitalization Timeline (Competing Risk)
                # Note: We now pass acr_win
                hosp_idx_vec = define_hospitalization_events(stage_win, acr_win, rand_hosp)
                
                # 4. Define Detectability
                detectable_mask = (ckd_win == 1) & (stage_win <= 4.) & (stage_win > 0)
                
                # 5. Precompute Age Bands
                band_masks, steps_ordered = precompute_age_bands(
                    age_win, hyper_win, diab_win, age_steps
                )
                
                # 6. Run Simulation Loop
                sim_results = simulate_strategies_with_participation(
                    strategies, participation_rates,
                    band_masks, steps_ordered, 
                    detectable_mask, ckd_win, stage_win,
                    hosp_idx_vec, rand_part,
                    age_win.shape
                )
                
                all_results.extend(sim_results)

    # 7. Aggregation
    df_res = pd.DataFrame(all_results)
    
    # Group by Strategy AND Participation Rate
    groupby_cols = ['parti', 'gen_thresh', 'diab_thresh', 'hyper_thresh']
    df_agg = df_res.groupby(groupby_cols)[['TP', 'FN', 'FP', 'TN','Total_Screened']].sum().reset_index()
    
    # Metrics
    df_agg['NNS'] = df_agg['Total_Screened'] / df_agg['TP']
    df_agg['sensitivity'] = df_agg['TP'] / (df_agg['TP'] + df_agg['FN'])
    df_agg['specificity'] = df_agg['TN'] / (df_agg['TN'] + df_agg['FP'])
    
    # Optimization Metric (Distance to Perfect)
    df_agg['Dist_to_Perfect'] = np.sqrt((1 - df_agg['sensitivity'])**2 + (1 - df_agg['specificity'])**2)
    
    return df_agg.fillna(0)

# %% [markdown]
# # 6. Execution Block

# %%
print("Loading data files...")

# 1. Load Data
stage_matrix_ls = load_stage_matrices()
age_matrix_ls = load_age_matrices()
albu_matrices = load_albu_matrices()
hypertension_mat_storage = load_hypertension_matrices()
diabetes_mat_storage = load_diabetes_matrices()

# %%
age_matrix_ls[0].shape
# %%
# 2. Build Derived CKD Matrices
# IMPORTANT: Create the specific albuminuria subset (indices 0 and 4) first
# This maps the 8 albuminuria scenarios down to the 2 we care about.
albu_mat_subset = [albu_mat[[0,4]] for albu_mat in albu_matrices]

print("Building General CKD matrices...")
general_ckd_ls = build_general_ckd_matrices(stage_matrix_ls, albu_mat_subset)

# 3. Run Analysis
print("Starting Screening Analysis...")
df_result = analyze_screening_performance_modular(
    age_matrix_vec=age_matrix_ls,
    ckd_mat_list=general_ckd_ls,
    stage_matrix_ls=stage_matrix_ls,
    hypertension_mat_storage=hypertension_mat_storage,
    diabetes_mat_storage=diabetes_mat_storage,
    acr_mat_list=albu_mat_subset, # <--- Passing the raw ACR data
    year_start=2026,
    year_end=2050,
    age_steps=[60, 55, 50, 45, 40, 35],
    participation_rates=[0.6, 0.8, 1.0],  # 60%, 80%, 100%
    target_albu_indices=[0, 1] # indices relative to the subset (0 and 4 become 0 and 1)
)

# 4. Save Results
output_path = RESULTS_DIR / "screening_results_with_parti_v2.csv"
df_result.to_csv(output_path, index=False)

print(f"\nAnalysis Complete. Results saved to:\n{output_path}")
print("\nPreview of Results:")
print(df_result.head(10))

# %%

