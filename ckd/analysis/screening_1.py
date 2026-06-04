"""
Screening Analysis Module
-------------------------
extracted from summerize_plotting.py

This script focuses exclusively on the optimization of age-based screening strategies 
for CKD across three risk groups:
1. General Population (G)
2. Diabetics (D)
3. Hypertensives (H)

It calculates Sensitivity, Specificity, NNS, and "Distance to Perfect" to identify 
optimal screening age thresholds.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# =============================================================================
# 1. HELPER FUNCTIONS: Data Slicing & Truth Definitions
# =============================================================================

def slice_window_data(
    age_matrix, ckd_matrix, stage_matrix, hyper_matrix, diab_matrix, 
    idx_start, idx_end, albu_idx, sim_idx
):
    """
    Extracts the time window (e.g., 2026-2050) for a specific simulation and albuminuria case.
    Returns 2D arrays: (n_people, n_years_in_window).
    """
    # Handle Age (sometimes 3D, sometimes 4D in original script)
    if age_matrix.ndim == 4:
        age_win = age_matrix[albu_idx, sim_idx, :, idx_start : idx_end + 1]
    else:
        age_win = age_matrix[sim_idx, :, idx_start : idx_end + 1]

    ckd_win = ckd_matrix[albu_idx, sim_idx, :, idx_start : idx_end + 1]
    stage_win = stage_matrix[albu_idx, sim_idx, :, idx_start : idx_end + 1]
    
    # Risk factors are usually (sim, person, year)
    hyper_win = hyper_matrix[sim_idx, :, idx_start : idx_end + 1]
    diab_win = diab_matrix[sim_idx, :, idx_start : idx_end + 1]
    
    return age_win, ckd_win, stage_win, hyper_win, diab_win


def define_ground_truth(ckd_win, stage_win):
    """
    Determines who is a 'Case', 'Non-Case', and who is 'Excluded'.
    Also creates the 'detectable_mask' (when screening is considered successful).
    
    Logic:
    - Excluded: Stage >= 4 at the start of the window.
    - Case: Has CKD (value=1) at any point and NOT excluded.
    - Detectable: Has CKD AND Stage <= 4 AND is Alive (Stage > 0).
    """
    # Check start of window (index 0)
    stage_start = stage_win[:, 0]
    is_excluded = (stage_start >= 4)
    
    # Identify Disease Presence
    ever_ckd = (ckd_win == 1).max(axis=1)
    
    is_case = ever_ckd & (~is_excluded)
    is_non_case = (~ever_ckd) & (~is_excluded)
    
    # Detectable State: CKD present, Early Stage, and Alive
    detectable_mask = (ckd_win == 1) & (stage_win <= 4.) & (stage_win > 0)
    
    return is_case, is_non_case, detectable_mask


def precompute_age_bands(age_win, hyper_win, diab_win, age_steps):
    """
    Creates boolean masks for age bands to speed up strategy testing.
    Returns a dict: { step_age: {'All': mask, 'Union': mask, 'Hyper': mask} }
    """
    band_masks = {}
    sorted_steps = sorted(age_steps, reverse=True)
    
    for i, step in enumerate(sorted_steps):
        lower_bound = step
        upper_bound = sorted_steps[i-1] if i > 0 else 999
        
        # Base Age Mask (Implicitly excludes dead people where age = -1)
        in_band = (age_win >= lower_bound) & (age_win < upper_bound)
        
        band_masks[step] = {
            'All': in_band,
            'Union': in_band & ((diab_win == 1) | (hyper_win == 1)),
            'Hyper': in_band & (hyper_win == 1)
        }
    
    return band_masks, sorted_steps


# =============================================================================
# 2. CORE SIMULATION ENGINE
# =============================================================================

def simulate_strategies(
    strategies, band_masks, sorted_steps, 
    detectable_mask, is_case, is_non_case, age_win_shape
):
    """
    Iterates through all (G, D, H) strategies and calculates metrics.
    Uses bitwise OR operations on pre-computed bands for speed.
    """
    strategy_results = []
    
    for (g_thr, d_thr, h_thr) in strategies:
        # Initialize screen mask
        final_screen_mask = np.zeros(age_win_shape, dtype=bool)
        
        # Assemble mask from bands
        for step in sorted_steps:
            masks = band_masks[step]
            if step >= g_thr:
                final_screen_mask |= masks['All']
            elif step >= d_thr:
                final_screen_mask |= masks['Union']
            elif step >= h_thr:
                final_screen_mask |= masks['Hyper']
        
        # --- Metrics ---
        # Sensitivity: Did we catch the Case while they were detectable?
        success_events = final_screen_mask & detectable_mask
        caught_mask = success_events.any(axis=1)
        
        # Screening Burden
        ever_screened_mask = final_screen_mask.any(axis=1)
        n_people_screened = np.sum(ever_screened_mask)

        tp = np.sum(caught_mask & is_case)
        fn = np.sum((~caught_mask) & is_case)
        
        # Specificity: Did we ever screen a Non-Case?
        fp = np.sum(ever_screened_mask & is_non_case)
        tn = np.sum((~ever_screened_mask) & is_non_case)
        
        strategy_results.append({
            "gen_thresh": g_thr,
            "diab_thresh": d_thr,
            "hyper_thresh": h_thr,
            "TP": tp, "FN": fn, "FP": fp, "TN": tn,
            "Total_Screened": n_people_screened               
        })
        
    return strategy_results


def analyze_screening_performance_modular(
    age_matrix_vec,
    ckd_mat_list,
    stage_matrix_ls,
    hypertension_mat_storage,
    diabetes_mat_storage,
    year_start=2026,
    year_end=2050,
    base_year=1990,
    age_steps=[60, 55, 50, 45, 40, 35],
    target_albu_indices=[0, 4] 
):
    """
    Main orchestrator for the modular screening analysis.
    """
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
                
    print(f"Running modular simulation for {len(strategies)} strategies...")
    
    n_groups = len(age_matrix_vec)
    # Assume shape structure: [n_albu, n_sims, n_people, n_years]
    n_albu, n_sims, _, _ = ckd_mat_list[0].shape
    all_results = []

    for albu in target_albu_indices:
        for sim in range(n_sims):
            for g in range(n_groups):
                
                # 1. Slice Data
                age_win, ckd_win, stage_win, hyper_win, diab_win = slice_window_data(
                    age_matrix_vec[g], ckd_mat_list[g], stage_matrix_ls[g], 
                    hypertension_mat_storage[g], diabetes_mat_storage[g],
                    idx_start, idx_end, albu, sim
                )
                
                # 2. Define Truth
                is_case, is_non_case, detectable_mask = define_ground_truth(ckd_win, stage_win)
                
                # 3. Precompute Bands
                band_masks, steps_ordered = precompute_age_bands(
                    age_win, hyper_win, diab_win, age_steps
                )
                
                # 4. Run Simulation Loop
                sim_results = simulate_strategies(
                    strategies, band_masks, steps_ordered, 
                    detectable_mask, is_case, is_non_case, age_win.shape
                )
                
                # Add metadata
                for res in sim_results:
                    res['albu'] = albu
                    res['sim'] = sim
                
                all_results.extend(sim_results)

    # 5. Aggregation
    df_res = pd.DataFrame(all_results)
    
    # Sum counts across all simulations/groups/albuminuria cases
    df_agg = df_res.groupby(['gen_thresh', 'diab_thresh', 'hyper_thresh'])[['TP', 'FN', 'FP', 'TN','Total_Screened']].sum().reset_index()
    
    # Calculate derived metrics
    df_agg['NNS'] = df_agg['Total_Screened'] / df_agg['TP']
    df_agg['sensitivity'] = df_agg['TP'] / (df_agg['TP'] + df_agg['FN'])
    df_agg['specificity'] = df_agg['TN'] / (df_agg['TN'] + df_agg['FP'])
    
    # Calculate Distance to Perfect (Optimization Metric)
    # sqrt((1-Sens)^2 + (1-Spec)^2)
    df_agg['Dist_to_Perfect'] = np.sqrt((1 - df_agg['sensitivity'])**2 + (1 - df_agg['specificity'])**2)
    
    return df_agg.fillna(0)


# =============================================================================
# 3. ANALYSIS & VISUALIZATION
# =============================================================================

def find_optimal_strategies(df_results, sensitivity_threshold=0.85, top_n=5):
    """
    Filters for strategies meeting a minimum sensitivity and ranks them 
    by 'Distance to Perfect' (closest to corner 1,1).
    """
    df_filtered = df_results[df_results['sensitivity'] >= sensitivity_threshold].copy()
    
    if df_filtered.empty:
        print(f"No strategies found with sensitivity >= {sensitivity_threshold}")
        return pd.DataFrame()
        
    top_strategies = df_filtered.sort_values('Dist_to_Perfect', ascending=True).head(top_n)
    return top_strategies


def plot_Pareto_frontier(df_results, top_strategies, threshold=0.85):
    """
    Plots Sensitivity vs (1-Specificity)
    """
    plt.figure(figsize=(10, 7))
    
    # Background points
    plt.scatter(
        1 - df_results['specificity'], 
        df_results['sensitivity'], 
        color='lightgrey', alpha=0.5, label='All Strategies'
    )
    
    # Highlight points passing threshold
    pass_thresh = df_results[df_results['sensitivity'] >= threshold]
    plt.scatter(
        1 - pass_thresh['specificity'], 
        pass_thresh['sensitivity'], 
        c=pass_thresh['NNS'], cmap='viridis', s=60, alpha=0.8,
        label=f'Sens >= {threshold}'
    )
    plt.colorbar(label='Number Needed to Screen (NNS)')
    
    # Highlight Top Winners
    plt.scatter(
        1 - top_strategies['specificity'], 
        top_strategies['sensitivity'], 
        color='red', marker='*', s=200, label='Optimal Choices'
    )
    
    plt.axhline(y=threshold, color='red', linestyle='--', alpha=0.5)
    
    plt.title(f'Screening Optimization (Min Sens {threshold})')
    plt.xlabel('1 - Specificity (False Positive Rate)')
    plt.ylabel('Sensitivity')
    plt.legend(loc='lower right')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()


# =============================================================================
# 4. MAIN EXECUTION BLOCK
# =============================================================================

if __name__ == "__main__":
    # -------------------------------------------------------------------------
    # TODO: LOAD YOUR DATA HERE
    # You need to load your .npy files into these variables:
    # 1. age_matrix_ls
    # 2. general_ckd_ls
    # 3. stage_matrix_ls
    # 4. hypertension_mat_storage
    # 5. diabetes_mat_storage
    # -------------------------------------------------------------------------
    
    print("Data loading required to run. Uncomment the loading section in the script.")
    
    # EXAMPLE EXECUTION (Assuming data variables exist):
    """
    df_results = analyze_screening_performance_modular(
        age_matrix_vec=age_matrix_ls,
        ckd_mat_list=general_ckd_ls,
        stage_matrix_ls=stage_matrix_ls,
        hypertension_mat_storage=hypertension_mat_storage,
        diabetes_mat_storage=diabetes_mat_storage,
        year_start=2026,
        year_end=2050,
        age_steps=[60, 55, 50, 45, 40, 35],
        target_albu_indices=[0, 4] 
    )
    
    # Save Raw Results
    df_results.to_csv("screening_optimization_full.csv", index=False)
    
    # Find Winners (Sens > 85%)
    top_5 = find_optimal_strategies(df_results, sensitivity_threshold=0.85, top_n=5)
    
    print("\nTop 5 Optimal Strategies:")
    print(top_5[['gen_thresh', 'diab_thresh', 'hyper_thresh', 
                 'sensitivity', 'specificity', 'NNS', 'Dist_to_Perfect']])
                 
    # Plot
    plot_Pareto_frontier(df_results, top_5, threshold=0.85)
    """