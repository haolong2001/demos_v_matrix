#
"""
Build egfr stage-by-ACR tables using the mortality-adjusted stage/age matrices.

Updated Logic:
This script handles the "year of death" adjustment. If a subject has a value of -2 
(indicating death) in the current target year, their values (Stage, Age, ACR) are 
replaced with the values from the previous year. This ensures they are counted 
in the prevalence statistics for the year they die.

Inputs:
  - ckd/future_data_1990_2050/mortality_adjusted/stage_matrix_group_{i}.npy
  - ckd/future_data_1990_2050/mortality_adjusted/age_matrix_group_{i}.npy
  - ckd/future_data_1990_2050/albu_matrix_forecast/albu_mat_group_{i}.npy
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd


MORTALITY_DIR = Path("../future_data_1990_2050/mortality_adjusted")
ALBU_DIR = Path("../future_data_1990_2050/albu_matrix_forecast")
STAGE_KEYS = [1.0, 2.0, 3.1, 3.2, 4.0, 5.0]
STAGE_LABELS = ["G1", "G2", "G3a", "G3b", "G4", "G5"]
ACR_CATEGORIES = [0, 0.5, 1]  # mapped to A1/A2/A3
ACR_LABELS = ["A1", "A2", "A3"]


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


def build_table_for_year(year: int, max_age: int = 74) -> pd.DataFrame:
    stage_mats = load_adjusted_stage_matrices()
    age_mats = load_adjusted_age_matrices()
    acr_mats = load_acr_matrices()

    # Determine single year index from the given "calendar" year
    year0 = 1990
    n_years = stage_mats[0].shape[-1]
    year_index = year - year0
    if year_index < 0 or year_index >= n_years:
        raise ValueError(f"Year {year} is out of the available data range [{year0}, {year0 + n_years - 1}]")

    df_counts = pd.DataFrame(0, index=STAGE_KEYS, columns=ACR_CATEGORIES, dtype=int)
    df_counts_upper = pd.DataFrame(0, index=STAGE_KEYS, columns=ACR_CATEGORIES, dtype=int)

    for idx in range(8):
        # We need to access the current year. 
        # If the value is -2, we must look at year_index - 1.
        
        # --- Base Scenario (0) ---
        # Extract 2D slice: [Sim, Person] for the specific year
        stage_base = stage_mats[idx][0, :, :, year_index].copy()
        age_base = age_mats[idx][0, :, :, year_index].copy()
        acr_base = acr_mats[idx][0, :, :, year_index].copy()

        # --- Upper Scenario (-1) ---
        stage_upper = stage_mats[idx][-1, :, :, year_index].copy()
        age_upper = age_mats[idx][-1, :, :, year_index].copy()
        acr_upper = acr_mats[idx][-1, :, :, year_index].copy()

        # --- Mortality Correction Logic ---
        # If year_index > 0, we look back one year to fill in data for those who died (val == -2)
        if year_index > 0:
            # Load previous year slices
            stage_base_prev = stage_mats[idx][0, :, :, year_index - 1]
            age_base_prev   = age_mats[idx][0, :, :, year_index - 1]
            acr_base_prev   = acr_mats[idx][0, :, :, year_index - 1]

            stage_upper_prev = stage_mats[idx][-1, :, :, year_index - 1]
            age_upper_prev   = age_mats[idx][-1, :, :, year_index - 1]
            acr_upper_prev   = acr_mats[idx][-1, :, :, year_index - 1]

            # 1. Fix Base Scenario
            # Identify where death occurred this year (value is -2)
            # Note: We check Stage for -2, but we apply fix to Stage, Age, and ACR
            # to ensure the person is fully reconstructed for the table.
            mask_dead_base = (stage_base == -2)
            
            # Apply previous values where current is -2
            if np.any(mask_dead_base):
                stage_base[mask_dead_base] = stage_base_prev[mask_dead_base]
                age_base[mask_dead_base]   = age_base_prev[mask_dead_base]
                acr_base[mask_dead_base]   = acr_base_prev[mask_dead_base]

            # 2. Fix Upper Scenario
            mask_dead_upper = (stage_upper == -2)
            
            if np.any(mask_dead_upper):
                stage_upper[mask_dead_upper] = stage_upper_prev[mask_dead_upper]
                age_upper[mask_dead_upper]   = age_upper_prev[mask_dead_upper]
                acr_upper[mask_dead_upper]   = acr_upper_prev[mask_dead_upper]

        def accumulate(stage_slice, age_slice, acr_slice, df_target):
            # flattening across [sim, person] (since we already sliced year)
            stage_flat = stage_slice.reshape(-1)
            age_flat = age_slice.reshape(-1)
            acr_flat = acr_slice.reshape(-1)
            
            age_mask = (age_flat >= 18) & (age_flat <= max_age)
            stage_valid = stage_flat[age_mask]
            acr_valid = acr_flat[age_mask]
            
            for stage_val, stage_label in zip(STAGE_KEYS, STAGE_LABELS):
                # Check for floating point equality
                stage_mask = np.isclose(stage_valid, stage_val)
                if not np.any(stage_mask):
                    continue
                for acr_val in ACR_CATEGORIES:
                    # acr_valid might be floats, but categories are simple 0, 0.5, 1
                    # Using equality should be fine for these specific categorical markers
                    df_target.loc[stage_val, acr_val] += np.sum(
                        stage_mask & (acr_valid == acr_val)
                    )

        accumulate(stage_base, age_base, acr_base, df_counts)
        accumulate(stage_upper, age_upper, acr_upper, df_counts_upper)

    df_perc = df_counts / df_counts.values.sum() * 100
    df_perc_upper = df_counts_upper / df_counts_upper.values.sum() * 100

    df_counts.index = df_counts_upper.index = STAGE_LABELS
    df_perc.index = df_perc_upper.index = STAGE_LABELS
    df_counts.columns = df_counts_upper.columns = ACR_LABELS
    df_perc.columns = df_perc_upper.columns = ACR_LABELS

    df_final = (
        df_counts.astype(str)
        + " (" + df_perc.round(2).astype(str) + "%), "
        + df_counts_upper.astype(str)
        + " (" + df_perc_upper.round(2).astype(str) + "%)"
    )

    row_totals_base = df_counts.sum(axis=1)
    col_totals_base = df_counts.sum(axis=0)
    row_totals_upper = df_counts_upper.sum(axis=1)
    col_totals_upper = df_counts_upper.sum(axis=0)
    row_perc_base = df_perc.sum(axis=1)
    col_perc_base = df_perc.sum(axis=0)
    row_perc_upper = df_perc_upper.sum(axis=1)
    col_perc_upper = df_perc_upper.sum(axis=0)

    df_final["Total"] = (
        row_totals_base.astype(str)
        + " (" + row_perc_base.round(2).astype(str) + "%), "
        + row_totals_upper.astype(str)
        + " (" + row_perc_upper.round(2).astype(str) + "%)"
    )

    total_row = (
        col_totals_base.astype(str)
        + " (" + col_perc_base.round(2).astype(str) + "%), "
        + col_totals_upper.astype(str)
        + " (" + col_perc_upper.round(2).astype(str) + "%)"
    )
    df_final.loc["Total"] = total_row
    grand_base = df_counts.values.sum()
    grand_upper = df_counts_upper.values.sum()
    df_final.loc["Total", "Total"] = (
        f"{grand_base} (100.0%), {grand_upper} (100.0%)"
    )

    return df_final


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate CKD stage-ACR table with mortality adjustment.")
    parser.add_argument(
        "--year",
        type=int,
        default=2022,
        help="Calendar year to analyze (default: 2022). Only the specified year will be analyzed."
    )
    parser.add_argument(
        "--max-age",
        type=int,
        default=74,
        choices=[74, 85, 90, 95, 100],
        help="Maximum age to include (74 for validation, 85 for projection)."
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(f"Tabulating for ages 18 - {args.max_age}")
    print(f"Analyzing only single year {args.year}")
    print("Applying correction: Subjects marked as deceased (-2) in target year are counted using previous year's state.")
    
    table = build_table_for_year(args.year, max_age=args.max_age)
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    print(table)
    # Save the table to a TXT file (tab-delimited text)
    output_path = f"mortality_adjusted_stage_table_{args.year}_age{args.max_age}.txt"
    table.to_csv(output_path, sep="\t", index=True)
    print(f"\nTable saved to {output_path}")


if __name__ == "__main__":
    main()