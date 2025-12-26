"""Driver script that reuses utility helpers to compare CKD prevalence with NPHS."""
# %%
from __future__ import annotations

import os
from pathlib import Path
from typing import Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# %%
SCRIPT_DIR = Path(__file__).resolve().parent
os.chdir(SCRIPT_DIR)

# %%

from utilis import (
    build_general_ckd_matrices,
    check_nphs_overlap_gender_race,
    plot_nphs_overlap_gender_race,
    simulate_ckd_prevalence,
)

# %%
CKD_DIR = SCRIPT_DIR.parent
REPO_ROOT = SCRIPT_DIR.parents[1]
FUTURE_DATA_DIR = CKD_DIR / "future_data_1990_2050"
MORTALITY_DIR = FUTURE_DATA_DIR / "mortality_adjusted"
RESULTS_DIR = SCRIPT_DIR / "results_df"


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

# %%
def build_general_ckd_matrices(
    stage_matrix_ls: Sequence[np.ndarray],
    acr_matrix_ls: Sequence[np.ndarray],
    healthy_stage_threshold: int = 2,
) -> list[np.ndarray]:
    """
    Create CKD indicator matrices for each ethnicity/gender group.

    Each value is 1 if the person is "CKD" (not healthy), or 0 if "healthy" (stage <= threshold and ACR == 0).

    Parameters
    ----------
    stage_matrix_ls : Sequence[np.ndarray]
        Sequence of stage matrices, shape (n_albu, n_sim, n_people, n_years).
    acr_matrix_ls : Sequence[np.ndarray]
        Sequence of corresponding ACR/albumin matrices (same shape as stage matrices).
    healthy_stage_threshold : 2, optional
        CKD stages at or below this (with ACR==0) are considered healthy (default 2).

    Returns
    -------
    list[np.ndarray]
        List of new CKD matrices (same shape as input) with entries 0 (healthy) or 1 (CKD).
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
        # exclude death people
        ckd_matrix[stage_matrix == -1] = -1
        ckd_matrix[stage_matrix == -2] = -2
        general_ckd_mat_ls.append(ckd_matrix)

    return general_ckd_mat_ls
# %%
stage_matrix_ls = load_stage_matrices()
age_matrix_ls = load_age_matrices()
albu_mat_storage = load_albu_matrices()
hypertension_mat_storage = load_hypertension_matrices()
diabetes_mat_storage = load_diabetes_matrices()

# %%
general_ckd_ls = build_general_ckd_matrices(stage_matrix_ls, albu_mat_storage)


# %%
len(stage_matrix_ls)
# %%
# np.unique(stage_matrix_ls[0])
# # %%
# np.unique(general_ckd_ls[0])

# # %%
# np.unique(age_matrix_ls[0])
# %%

def simulate_ckd_prevalence(
    age_matrix_vec: Sequence[np.ndarray],
    ckd_mat_list: Sequence[np.ndarray],
    ckd_level: int = 1,
    min_age: int = 18,
    max_age: int = 74,
) -> pd.DataFrame:
    """Compute CKD prevalence across simulations, years, demographics, and age groups."""

    age_groups: Tuple[Tuple[int, int], ...] = (
        # (18, 29),
        # (30, 39),
        # (40, 49),
        # (50, 59),
        # (60, 69),
        # (70, 79),
        # (80, 200),
        (18,39),
        (40,54),
        (55,69),
        (70,74)
    )

    n_groups = len(age_matrix_vec)
    if not n_groups:
        raise ValueError("No age matrices were provided.")

    n_albu, n_sims, _, n_years = ckd_mat_list[0].shape

    male_idx = [0, 2, 4, 6]
    female_idx = [1, 3, 5, 7]
    chinese_idx = [0, 1]
    malay_idx = [2, 3]
    indian_idx = [4, 5]

    records = []
    for albu in range(n_albu):
        for sim in range(n_sims):
            total_people = np.zeros((n_groups, n_years))
            total_ckd = np.zeros((n_groups, n_years))
            age_totals = np.zeros((n_groups, len(age_groups), n_years))
            age_ckd = np.zeros((n_groups, len(age_groups), n_years))

            for g in range(n_groups):
                ages = age_matrix_vec[g][albu, sim, :,:]
                ckd_status = ckd_mat_list[g][albu, sim, :, :]

                mask_all = (ages >= min_age) & (ages <= max_age)
                total_people[g, :] = np.sum(mask_all, axis=0)
                ckd_mask = (ckd_status == ckd_level) & mask_all
                total_ckd[g, :] = np.sum(ckd_mask, axis=0)

                for a_idx, (lower, upper) in enumerate(age_groups):
                    mask = (ages >= lower) & (ages <= upper)
                    age_totals[g, a_idx, :] = np.sum(mask, axis=0)
                    age_ckd[g, a_idx, :] = np.sum((ckd_status == ckd_level) & mask, axis=0)

            total_people_sum = total_people.sum(axis=0)
            total_ckd_sum = total_ckd.sum(axis=0)

            male_people = total_people[male_idx, :].sum(axis=0)
            male_ckd = total_ckd[male_idx, :].sum(axis=0)
            female_people = total_people[female_idx, :].sum(axis=0)
            female_ckd = total_ckd[female_idx, :].sum(axis=0)

            chinese_people = total_people[chinese_idx, :].sum(axis=0)
            chinese_ckd = total_ckd[chinese_idx, :].sum(axis=0)
            malay_people = total_people[malay_idx, :].sum(axis=0)
            malay_ckd = total_ckd[malay_idx, :].sum(axis=0)
            indian_people = total_people[indian_idx, :].sum(axis=0)
            indian_ckd = total_ckd[indian_idx, :].sum(axis=0)

            age_totals_sum = age_totals.sum(axis=0)
            age_ckd_sum = age_ckd.sum(axis=0)

            for year in range(n_years):
                record = {
                    "albu": albu,
                    "year": 1990 + year,
                    "sim": sim,
                    "overall": (total_ckd_sum[year] / total_people_sum[year])
                    if total_people_sum[year] > 0
                    else 0,
                    "male": (male_ckd[year] / male_people[year]) if male_people[year] > 0 else 0,
                    "female": (female_ckd[year] / female_people[year])
                    if female_people[year] > 0
                    else 0,
                    "chinese": (chinese_ckd[year] / chinese_people[year])
                    if chinese_people[year] > 0
                    else 0,
                    "malay": (malay_ckd[year] / malay_people[year]) if malay_people[year] > 0 else 0,
                    "indian": (indian_ckd[year] / indian_people[year])
                    if indian_people[year] > 0
                    else 0,
                }

                for a_idx, age_range in enumerate(age_groups):
                    den = age_totals_sum[a_idx, year]
                    num = age_ckd_sum[a_idx, year]
                    record[str(age_range)] = num / den if den > 0 else 0

                records.append(record)

    return pd.DataFrame(records)


def simulate_overall_ckd_prevalence(
    age_matrix_vec,
    ckd_mat_list,
    hypertension_mat_storage=None,
    diabetes_mat_storage=None,
    ckd_level=1,
    hypertension_only=False,
    diabetes_only=False
):
    """
    Compute overall CKD prevalence (optionally restricted to hypertensive or diabetic CKD)
    across simulations, years, and outer iterations.

    Parameters:
        age_matrix_vec (list): list of age matrices, each (n_albu,n_sims, n_persons, n_years)
        ckd_mat_list (list): list of CKD status matrices, each (n_albu, n_sims, n_persons, n_years)
        hypertension_mat_storage (list): list of hypertension matrices, each (n_sims, n_persons, n_years)
        diabetes_mat_storage (list): list of diabetes matrices, each (n_sims, n_persons, n_years)
        ckd_level (int): Value representing CKD presence (default=1)
        hypertension_only (bool): If True, include only individuals with hypertension == 1
        diabetes_only (bool): If True, include only individuals with diabetes == 1

    Returns:
        pd.DataFrame: columns = [albu, year, sim, overall]
    """

    n_groups = len(age_matrix_vec)
    n_albu, n_sims, _, n_years = ckd_mat_list[0].shape

    records = []

    for albu in range(n_albu):
        for sim in range(n_sims):
            total_people = np.zeros((n_groups, n_years))
            total_ckd = np.zeros((n_groups, n_years))

            for g in range(n_groups):
                ages = age_matrix_vec[g][albu, sim, :,:]                # (n_persons, n_years)
                ckd_status = ckd_mat_list[g][albu, sim, :, :]      # (n_persons, n_years)

                # Optional disease masks
                hyper_mask = hypertension_mat_storage[g][sim, :, :] == 1 if hypertension_mat_storage is not None else np.ones_like(ckd_status, dtype=bool)
                diab_mask = diabetes_mat_storage[g][sim, :, :] == 1 if diabetes_mat_storage is not None else np.ones_like(ckd_status, dtype=bool)

                # Apply conditions
                mask_all = (ages >= 18) & (ages <= 74)

                # Apply filters if needed
                if hypertension_only:
                    mask_all &= hyper_mask
                if diabetes_only:
                    mask_all &= diab_mask

                total_people[g, :] = np.sum(mask_all, axis=0)

                ckd_mask = (ckd_status == ckd_level) & mask_all
                total_ckd[g, :] = np.sum(ckd_mask, axis=0)

            total_people_sum = total_people.sum(axis=0)
            total_ckd_sum = total_ckd.sum(axis=0)

            for year in range(n_years):
                record = {
                    "albu": albu,
                    "year": 1990 + year,
                    "sim": sim,
                    "overall": (total_ckd_sum[year] / total_people_sum[year])
                    if total_people_sum[year] > 0 else 0
                }
                records.append(record)

    return pd.DataFrame(records)

   
# %%
nphs_path = REPO_ROOT / "data" / "nphs.csv"
nphs_df = pd.read_csv(nphs_path)

# # %%
# ckd_prevalence

# # %%
# ckd_prevalence.columns

# Index(['albu', 'year', 'sim', 'overall', 'male', 'female', 'chinese', 'malay',
#        'indian', '(18, 29)', '(30, 39)', '(40, 49)', '(50, 59)', '(60, 69)',
#        '(70, 79)', '(80, 200)']
# %%
nphs_df.columns


# %%
nphs_df

# %%
ckd_prevalence = simulate_ckd_prevalence(age_matrix_ls, general_ckd_ls)
overlap_df = check_nphs_overlap_gender_race(ckd_prevalence, nphs_df)
# %%
print("NPHS overlap check:\n", overlap_df)

RESULTS_DIR.mkdir(exist_ok=True)
overlap_path = RESULTS_DIR / "nphs_overlap_gender_race.csv"
overlap_df.to_csv(overlap_path, index=False)

# %%

def plot_nphs_overlap_gender_race(
    ckd_prevalence: pd.DataFrame,
    nphs_df: pd.DataFrame,
    year_col: str = "year",
    factor: float = 100.0,
    sim_years: Tuple[int, int] = (1990, 2050)
):
    """
    Create the 2x3 panel plot.
    - Simulation CI: Plotted as a band for the full range (default 1990-2024).
    - NPHS: Plotted as scatter points for whichever years they exist.
    - Simulation median: Always plot the median line, but only add label to the legend ONCE.
    """

    sim_cols = ["male", "female", "chinese", "malay", "indian"]
    
    # 1. Prepare Simulation Data (Continuous Range)
    mask_sim = (ckd_prevalence[year_col] >= sim_years[0]) & (ckd_prevalence[year_col] <= sim_years[1])
    ckd_sub = ckd_prevalence.loc[mask_sim].copy()
    
    ci_df = compute_age_ci(ckd_sub, sim_cols)
    ci_df = ci_df.sort_values(year_col)
    years_sim = ci_df[year_col].values

    # 2. Prepare NPHS Data (Discrete Points)
    nphs_sub = nphs_df[[year_col, "male", "female", "chn", "mal", "ind"]].copy()
    nphs_sub = nphs_sub.rename(
        columns={
            "chn": "chinese",
            "mal": "malay",
            "ind": "indian",
            # "male" and "female" already exist
        }
    )

    # 3. Setup Plot
    fig, axes = plt.subplots(2, 3, figsize=(14, 8), sharex=True)
    fig.suptitle(f"CKD Prevalence: Simulation 95% CI ({sim_years[0]}-{sim_years[1]}) vs NPHS Point Estimates")

    panel_defs = [
        ("male", "Male", 0, 0),
        ("female", "Female", 0, 1),
        ("chinese", "Chinese", 1, 0),
        ("malay", "Malay", 1, 1),
        ("indian", "Indian", 1, 2),
    ]

    # Helper to calculate y-limits based on BOTH the full sim range and obs
    def get_row_ylim(cols: list) -> Tuple[float, float]:
        vals = []
        for col in cols:
            if f"{col}_upper" in ci_df.columns:
                vals.append(ci_df[f"{col}_upper"].values * factor)
            if col in nphs_sub.columns:
                vals.append(nphs_sub[col].dropna().values * factor)
        if not vals:
            return 0.0, 10.0
        stacked = np.concatenate(vals)
        return 0.0, stacked.max() * 1.1

    row0_cols = ["male", "female"]
    row1_cols = ["chinese", "malay", "indian"]
    y0_min, y0_max = get_row_ylim(row0_cols)
    y1_min, y1_max = get_row_ylim(row1_cols)

    # Flag/logic so we only put "Simulation median" in the legend ONCE per row
    median_label_used_row = [False, False]

    # 4. Plotting Loop
    for col, title, r, c in panel_defs:
        ax = axes[r, c]

        # A. Plot Simulation CI (Full Range)
        if f"{col}_lower" in ci_df.columns:
            lower = ci_df[f"{col}_lower"].values * factor
            upper = ci_df[f"{col}_upper"].values * factor
            mean = ci_df[f"{col}_mean"].values * factor if f"{col}_mean" in ci_df.columns else None

            # Plot confidence interval band
            ax.fill_between(years_sim, lower, upper, alpha=0.3, label="Simulation 95% CI", color="#5088C4")
            # Always plot mean line if available
            if mean is not None:
                add_label = not median_label_used_row[r]
                ax.plot(
                    years_sim,
                    mean,
                    color="#193366",
                    linestyle=":",
                    linewidth=2,
                    label="Simulation mean" if add_label else None
                )
                if add_label:
                    median_label_used_row[r] = True

        # B. Plot NPHS Points (Discrete)
        obs_data = nphs_sub[[year_col, col]].dropna()
        if not obs_data.empty:
            ax.scatter(
                obs_data[year_col], 
                obs_data[col] * factor, 
                marker="x", s=60, label="NPHS", color="#D55E00", zorder=10
            )

        ax.set_title(title)

        # Set Limits
        # Optionally keep differentiated y-limits by row if wanted:
        if r == 0:
            ax.set_ylim(0, 60)
        else:
            ax.set_ylim(0, 60)

        if c == 0:
            ax.set_ylabel("Prevalence (%)")
        if r == 1:
            ax.set_xlabel("Year")

        # Legend logic: Only for first column (r, c) == (0, 0) and (1, 0)
        if (r, c) in [(0, 0), (1, 0)]:
            ax.legend(loc="upper left", fontsize=9)

    axes[0, 2].axis("off")
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    return fig, axes

# %%

import pandas as pd
import numpy as np

def compute_age_ci_table(
    ckd_prevalence: pd.DataFrame, 
    nphs_df: pd.DataFrame, 
    years: list = [2019, 2022, 2024],
    factor: float = 1.0  # Set to 100.0 if Sim is 0-1 and Obs is 0-100%
) -> pd.DataFrame:
    
    # Map Simulation Columns -> NPHS Columns
    age_map = {
        '(18, 39)': '18-39',
        '(40, 54)': '40-54',
        '(55, 69)': '55-69',
        '(70, 74)': '70-74'
    }

    records = []

    for year in years:
        # 1. Filter Simulation Data for the specific year
        sim_subset = ckd_prevalence[ckd_prevalence["year"] == year]
        
        # 2. Check if we have NPHS data for this year
        # (We check if the year exists in the NPHS dataframe)
        obs_row = nphs_df[nphs_df["year"] == year]
        
        if sim_subset.empty or obs_row.empty:
            continue

        # 3. Iterate through each age group
        for sim_col, obs_col in age_map.items():
            if obs_col not in nphs_df.columns:
                continue

            # Calculate Simulation 95% CI
            # We apply the factor here (e.g., *100 if converting ratio to %)
            lower = np.percentile(sim_subset[sim_col], 2.5) * factor
            upper = np.percentile(sim_subset[sim_col], 97.5) * factor
            
            # Get Observation Value
            # We assume NPHS is already in the target unit (e.g., %)
            obs = float(obs_row[obs_col].iloc[0])
            
            # Check overlap
            inside = lower <= obs <= upper
            
            # Format text
            text = f"{inside} [95% CI: {lower:.3f}-{upper:.3f}], obs={obs:.3f}"
            
            records.append({
                "category": obs_col, # Using the cleaner string name '18-39'
                "year": year,
                "result": text
            })

    return pd.DataFrame.from_records(records)

# --- Usage Example ---
# If your Simulation data is 0-1 and NPHS is 0-100%, set factor=100.0
age_ci_table = compute_age_ci_table(ckd_prevalence, nphs_df, factor=1.0)
print(age_ci_table)
age_ci_save_path = RESULTS_DIR / "nphs_overlap_age_strata.csv"
age_ci_table.to_csv(age_ci_save_path, index=False)
# %% 
def compute_age_ci(df: pd.DataFrame, cols: SimCols) -> pd.DataFrame:
    """Return mean and 95% CI per year for the provided columns."""

    years = sorted(df["year"].unique())
    records = []
    for year in years:
        vals = df[df["year"] == year]
        record = {"year": int(year)}
        for col in cols:
            record[f"{col}_mean"] = vals[col].mean()
            record[f"{col}_lower"] = vals[col].quantile(0.025)
            record[f"{col}_upper"] = vals[col].quantile(0.975)
        records.append(record)
    return pd.DataFrame(records)
# %%
fig, _ = plot_nphs_overlap_gender_race(ckd_prevalence, nphs_df)
fig_path = RESULTS_DIR / "nphs_overlap_gender_race.png"
fig.savefig(fig_path, dpi=300, bbox_inches="tight")
plt.show()
plt.close(fig)
# %%
# print("Unique values in general_ckd_ls[0]:", np.unique(general_ckd_ls[0]))


########################################
#  hypertension diabetes plotting 
########################################
# %%
df_hyper = simulate_overall_ckd_prevalence(
    age_matrix_ls,
    general_ckd_ls,
    hypertension_mat_storage=hypertension_mat_storage,
    hypertension_only=True,
)

df_diab = simulate_overall_ckd_prevalence(
    age_matrix_ls,
    general_ckd_ls,
    diabetes_mat_storage=diabetes_mat_storage,
    diabetes_only=True,
)

# %%
# df_diab

# %% Calculate and print CKD prevalence changes from 2025 to 2050 for hypertensive and diabetic subgroups

# def get_prevalence_change(df, label):
#     """
#     Print prevalence in 2025 and 2050 and difference for given dataframe (should have columns 'year' and 'overall')
#     """
#     summary = df.groupby("year")["overall"].mean()
#     prev_2025 = summary.get(2025, np.nan)
#     prev_2050 = summary.get(2050, np.nan)
#     change = prev_2050 - prev_2025 if not (np.isnan(prev_2025) or np.isnan(prev_2050)) else np.nan
#     print(f"{label} CKD prevalence change (2025 to 2050):")
#     print(f"  2025: {prev_2025:.3%}, 2050: {prev_2050:.3%}, Change: {change:.3%}")

# get_prevalence_change(df_hyper, "Hypertensive")
# get_prevalence_change(df_diab, "Diabetic")

# %%
def compute_ci_table(df: pd.DataFrame, label: str, obs_column: str) -> pd.DataFrame:
    years_of_interest = [2019, 2022, 2024]
    records = []
    for year in years_of_interest:
        subset = df[df["year"] == year]
        if subset.empty or obs_column not in nphs_df.columns:
            continue
        lower = np.percentile(subset["overall"], 2.5)
        upper = np.percentile(subset["overall"], 97.5)
        obs_series = nphs_df.loc[nphs_df["year"] == year, obs_column]
        if obs_series.empty:
            continue
        obs = float(obs_series.iloc[0])
        inside = lower <= obs <= upper
        text = f"{inside} [95% CI: {lower:.3f}-{upper:.3f}], obs={obs:.3f}"
        records.append({"category": label, "year": year, "result": text})
    return pd.DataFrame.from_records(records)


ci_diab = compute_ci_table(df_diab, "Diabetes", "Diabetes")
ci_hyper = compute_ci_table(df_hyper, "Hyper", "Hyper")
ci_table = pd.concat([ci_diab, ci_hyper], ignore_index=True)
print("95% CI comparison with observed prevalence:")
print(ci_table)

# %%

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def plot_comorbidities_overlap(
    df_diab: pd.DataFrame,
    df_hyper: pd.DataFrame,
    nphs_df: pd.DataFrame,
    year_range: tuple = (1990, 2050),
    factor: float = 100.0
):
    """
    Creates a 1x2 plot for Diabetic CKD and Hypertensive CKD.
    - Simulation: 95% CI band (default 1990-2050).
    - Simulation: Mean line (dark purple, dotted).
    - NPHS: Point estimates.
    """
    
    # Configuration for the two panels
    # Format: (Dataframe, NPHS_Col_Name, Title, Axis_Index)
    panels = [
        (df_diab, "Diabetes", "Diabetic CKD", 0),
        (df_hyper, "Hyper", "Hypertensive CKD", 1)
    ]
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=False)
    fig.suptitle(f"Projected Prevalence: Simulation ({year_range[0]}-{year_range[1]}) vs NPHS")

    # Helper to calculate CI and mean efficiently using groupby
    def get_sim_ci_mean(df, start, end):
        mask = (df["year"] >= start) & (df["year"] <= end)
        sub = df.loc[mask]
        grouped = sub.groupby("year")["overall"]
        lower = grouped.quantile(0.025) * factor
        upper = grouped.quantile(0.975) * factor
        mean = grouped.mean() * factor
        return lower.index, lower.values, upper.values, mean.values

    for df_sim, obs_col, title, idx in panels:
        ax = axes[idx]
        
        # 1. Plot Simulation Band and Mean
        years_sim, lower, upper, mean = get_sim_ci_mean(df_sim, year_range[0], year_range[1])
        # 1a. CI Band
        ax.fill_between(
            years_sim, lower, upper, 
            alpha=0.3, color="#957DAD", label="Simulation 95% CI"
        )
        # 1b. Mean Line (dark purple, dotted)
        ax.plot(
            years_sim, mean, 
            linestyle=":", color="#3F007D", linewidth=2, marker=None,
            label="Simulation Mean"
        )
        
        # 2. Plot NPHS Points
        if obs_col in nphs_df.columns:
            obs_data = nphs_df[["year", obs_col]].dropna()
            ax.scatter(
                obs_data["year"], 
                obs_data[obs_col] * factor if obs_data[obs_col].max() < 10 else obs_data[obs_col], # Auto-detect if factor needed
                marker="x", s=60, color="#D55E00", label="NPHS", zorder=10
            )
            
        # 3. Set fixed Y-Limits as requested
        ax.set_ylim(0, 100)

        ax.set_title(title)
        ax.set_xlabel("Year")
        if idx == 0:
            ax.set_ylabel("Prevalence (%)")
            ax.legend(loc="upper left")
        
    plt.tight_layout()
    return fig, axes

# Example usage:
# %%
fig, axes = plot_comorbidities_overlap(df_diab, df_hyper, nphs_df)
plt.show()
fig_path = RESULTS_DIR / "comorbidities_overlap.png"
fig.savefig(fig_path, dpi=300, bbox_inches="tight")
plt.close(fig)




#########################################
# age prevalence plotting
# %% 



# %% plotting 

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List

# Assumption: The helper function 'compute_age_ci' defined in previous turns exists in scope.
# If not, it needs to be defined before running this function.

def plot_nphs_overlap_age_strata(
    ckd_prevalence: pd.DataFrame,
    nphs_df: pd.DataFrame,
    year_col: str = "year",
    factor: float = 100.0,
    sim_years: Tuple[int, int] = (1990, 2050),
    fill_color: str = "#8FBC8F" # A "grey green" (DarkSeaGreen) color hex
):
    """
    Create a 1x4 panel plot comparing simulation CI with NPHS point estimates for Age Strata.
    """

    # Define the mappings: (Simulation Column Name, NPHS Column Name, Plot Title, Axis Index)
    # Note: Sim columns are weird strings like '(18, 39)', NPHS are '18-39'
    panel_defs = [
        ('(18, 39)', '18-39', 'Age 18-39', 0),
        ('(40, 54)', '40-54', 'Age 40-54', 1),
        ('(55, 69)', '55-69', 'Age 55-69', 2),
        ('(70, 74)', '70-74', 'Age 70-74', 3),
    ]
    
    # Extract just the simulation columns needed for CI computation
    sim_cols_to_compute = [p[0] for p in panel_defs]

    # 1. Prepare Simulation Data (Continuous Range)
    mask_sim = (ckd_prevalence[year_col] >= sim_years[0]) & (ckd_prevalence[year_col] <= sim_years[1])
    ckd_sub = ckd_prevalence.loc[mask_sim].copy()
    
    # Compute CIs using the external helper function
    ci_df = compute_age_ci(ckd_sub, sim_cols_to_compute)
    ci_df = ci_df.sort_values(year_col)
    years_sim = ci_df[year_col].values

    # 2. Prepare NPHS Data (subsetting relevant columns)
    nphs_obs_cols = [p[1] for p in panel_defs if p[1] in nphs_df.columns]
    nphs_sub = nphs_df[[year_col] + nphs_obs_cols].copy()

    # 3. Setup Plot (1 row, 4 columns)
    # Using sharey=True feels appropriate for comparing age groups side-by-side, 
    # but prevalence varies wildly by age, so let's calculate limits dynamically instead.
    fig, axes = plt.subplots(1, 4, figsize=(20, 5), sharex=True, sharey=False)
    fig.suptitle(f"CKD Prevalence by Age: Simulation 95% CI ({sim_years[0]}-{sim_years[1]}) vs NPHS")

    # Helper to calculate global y-limits across all age groups for consistent scaling
    def get_global_ylim() -> Tuple[float, float]:
        vals = []
        for sim_col, obs_col, _, _ in panel_defs:
            # Add Simulation Upper Bound
            if f"{sim_col}_upper" in ci_df.columns:
                vals.append(ci_df[f"{sim_col}_upper"].values * factor)
            # Add Observation Points
            if obs_col in nphs_sub.columns:
                vals.append(nphs_sub[obs_col].dropna().values * factor)
        
        if not vals:
             # Fallback if data is missing
            return 0.0, 10.0
            
        stacked = np.concatenate(vals)
        # Add 10% padding at the top
        return 0.0, stacked.max() * 1.1

    y_min, y_max = get_global_ylim()

    # 4. Plotting Loop
    for sim_col, obs_col, title, ax_idx in panel_defs:
        ax = axes[ax_idx]

        # A. Plot Simulation CI (Full Range) and Mean (Dark Green, Dotted)
        lower_col_name = f"{sim_col}_lower"
        upper_col_name = f"{sim_col}_upper"
        mean_col_name = f"{sim_col}_mean"

        if lower_col_name in ci_df.columns and mean_col_name in ci_df.columns:
            lower = ci_df[lower_col_name].values * factor
            upper = ci_df[upper_col_name].values * factor
            mean = ci_df[mean_col_name].values * factor
            # CI band: "grey green"
            ax.fill_between(
                years_sim, lower, upper, 
                alpha=0.4, label="Simulation 95% CI", color=fill_color
            )
            # Mean line: dark green, dotted
            ax.plot(
                years_sim, mean, 
                linestyle=":", color="#006400", linewidth=2, marker=None, 
                label="Simulation Mean"
            )

        # B. Plot NPHS Points (Discrete)
        if obs_col in nphs_sub.columns:
            obs_data = nphs_sub[[year_col, obs_col]].dropna()
            if not obs_data.empty:
                ax.scatter(
                    obs_data[year_col], 
                    obs_data[obs_col] * factor, 
                    marker="x", s=60, label="NPHS", color="#D55E00", zorder=10
                )

        ax.set_title(title)
        # Set consistent Y-limits across all panels for easier comparison
        ax.set_ylim(0, 100)
        ax.set_xlabel("Year")

        # Axis labels and Legend only on the first plot
        if ax_idx == 0:
            ax.set_ylabel("Prevalence (%)")
            ax.legend(loc="upper left", fontsize=9)
        
    plt.tight_layout(rect=[0, 0, 1, 0.95]) # Adjust rect to make room for suptitle
    return fig, axes

# Example call (assuming dataframes exist):
fig, axes = plot_nphs_overlap_age_strata(ckd_prevalence, nphs_df, sim_years=(1990, 2050))
plt.show()
# %%
fig_path = RESULTS_DIR / "nphs_overlap_age_strata.png"
fig.savefig(fig_path, dpi=300, bbox_inches="tight")
plt.close(fig)


# %%
print("Hypertensive CKD 95% CI Table vs Observed Prevalence:")
print(df_hyper)

# %%  


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def calculate_cumulative_incidence_by_age(
    age_matrix_vec,
    ckd_mat_list,
    hypertension_mat_storage,
    year_start=2025,
    year_end=2050,
    base_year=1990,
    age_thresholds=[55, 50, 45, 40, 35, 30,25]
):
    n_groups = len(age_matrix_vec)
    # Get shapes from the CKD matrix (which we know is reliable)
    n_albu, n_sims, n_persons_check, n_years = ckd_mat_list[0].shape
    
    # Calculate year indices
    idx_start = year_start - base_year
    idx_end = year_end - base_year
    idx_start = max(1, idx_start) 
    idx_end = min(n_years, idx_end)

    results = []
    print(f"Calculating incidence for years {year_start}-{year_end}...")

    for albu in range(n_albu):
        for sim in range(n_sims):
            
            counts_per_threshold = {t: 0 for t in age_thresholds}
            
            for g in range(n_groups):
                # --- FIX: Slice all 4 dimensions ---
                # age_matrix_vec shape: (n_albu, n_sim, n_person, n_year)
                # We need shape: (n_person, n_year)
                age_slice = age_matrix_vec[g][albu, sim, :, :] 

                # ckd_mat_list shape: (n_albu, n_sim, n_person, n_year)
                ckd_slice = ckd_mat_list[g][albu, sim, :, :]

                # hypertension shape: (n_sim, n_person, n_year)
                hyper_slice = hypertension_mat_storage[g][sim, :, :]
                
                # --- LOGIC REMAINS THE SAME BELOW ---
                
                # 1. Define Hypertensive CKD status (CKD >=1 AND Hyper == 1)
                is_hyper_ckd = (ckd_slice >= 1) & (hyper_slice == 1)
                
                # 2. Calculate Incidence (Transition from 0 to 1)
                incident_mask = (is_hyper_ckd[:, 1:] == 1) & (is_hyper_ckd[:, :-1] == 0)
                
                # 3. Filter for relevant years
                target_inc_mask = incident_mask[:, (idx_start-1):(idx_end-1)]
                target_ages = age_slice[:, idx_start:idx_end] 
                
                # 4. Apply Mask
                events_mask = target_inc_mask 
                
                if np.sum(events_mask) > 0:
                    # Now both arrays are (n_person, n_window_years) flattened
                    ages_at_onset = target_ages[events_mask]
                    
                    for t in age_thresholds:
                        counts_per_threshold[t] += np.sum(ages_at_onset >= t)

            for t in age_thresholds:
                results.append({
                    "albu_case": albu,
                    "sim": sim,
                    "age_threshold": t,
                    "incident_cases": counts_per_threshold[t]
                })

    return pd.DataFrame(results)

# --- Usage Example (assuming data is loaded) --- hypertension_mat_storage
df_incidence = calculate_cumulative_incidence_by_age(age_matrix_ls, general_ckd_ls, diabetes_mat_storage)

# %%
df_incidence
# %%
df_incidence.to_csv("hypertensive_ckd_incidence_by_age.csv", index=False)
print("df_incidence saved as hypertensive_ckd_incidence_by_age.csv")

# %%
age_matrix_ls[0].shape
# %%
import matplotlib.pyplot as plt
import pandas as pd

def plot_screening_yield_curve(df_incidence):
    """
    Plots the cumulative number of incident cases captured vs Age Threshold.
    Uses numeric x-axis to strictly control the 55 -> 30 ordering.
    """
    # 1. Aggregate over simulations (mean and std)
    summary = df_incidence.groupby(['age_threshold', 'albu_case'])['incident_cases'].agg(['mean', 'std']).reset_index()
    
    plt.figure(figsize=(10, 6))
    
    # 2. Plot using NUMERIC values for x (do not convert to string)
    for albu in summary['albu_case'].unique():
        subset = summary[summary['albu_case'] == albu]
        
        # Sort by threshold to ensure the line connects properly
        subset = subset.sort_values('age_threshold')
        
        plt.plot(
            subset['age_threshold'],  # Keep as numbers
            subset['mean'], 
            marker='o', 
            label=f'Albu Case {albu}'
        )
        
        # Add error bars (Confidence Interval)
        plt.fill_between(
            subset['age_threshold'],
            subset['mean'] - 1.96 * subset['std'],
            subset['mean'] + 1.96 * subset['std'],
            alpha=0.1
        )

    # 3. Formatting
    plt.title('Cumulative Incident Hypertensive CKD Cases (2025-2050)\nDetected by Screening Above Age X')
    plt.xlabel('Screening Age Threshold (Years)')
    plt.ylabel('Total Incident Cases Detected')
    
    # 4. Enforce Descending Order (High Age Left -> Low Age Right)
    # Since x is numeric, this reliably puts 55 on the left and 30 on the right.
    plt.xlim(57, 28)  # Set explicit limits with padding, ordered high to low
    # Alternatively: plt.gca().invert_xaxis() would also work on a standard numeric axis
    
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(title="Albuminuria Scenario")
    plt.tight_layout()
    
    plt.savefig('hypertensive_ckd_screening_yield.png')
    print("Plot saved as hypertensive_ckd_screening_yield.png")

# --- Run Plotting ---
plot_screening_yield_curve(df_incidence)
# %%

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def plot_marginal_yield(df_incidence):
    """
    Plots the MARGINAL number of new cases detected by lowering the age threshold.
    e.g., How many extra cases are found in the [50-55) bucket vs the [55+) bucket.
    """
    # 1. Aggregate mean across simulations first
    df_agg = df_incidence.groupby(['albu_case', 'age_threshold'])['incident_cases'].mean().reset_index()

    # 2. Sort to calculate differences
    # We sort by age descending (55, 50, 45...)
    df_agg = df_agg.sort_values(by=['albu_case', 'age_threshold'], ascending=[True, False])

    marginal_data = []
    
    # Iterate through each albuminuria scenario
    for albu in df_agg['albu_case'].unique():
        subset = df_agg[df_agg['albu_case'] == albu].copy()
        
        # Calculate diff between current threshold and the previous (higher) threshold
        # Since we sorted descending, the "next" row has a LOWER age and HIGHER count.
        # We want: Count(Age >= 50) - Count(Age >= 55) = Cases in range [50, 55)
        
        # Shift the incidence column to compare with the previous row
        subset['prev_incidence'] = subset['incident_cases'].shift(1)
        
        # The first row (highest age, e.g., 55) is the baseline. 
        # Its "marginal gain" is just its total count (screening >55).
        # Subsequent rows: Count(Current) - Count(Previous_Higher_Age)
        subset['marginal_gain'] = subset['incident_cases'] - subset['prev_incidence']
        
        # Fill NaN for the first row (Age 55) with the actual value
        subset['marginal_gain'] = subset['marginal_gain'].fillna(subset['incident_cases'])
        
        # Create a readable label for the x-axis
        # e.g., for Age 50, the label is "50-55"
        subset['prev_age'] = subset['age_threshold'].shift(1)
        
        def make_label(row):
            if pd.isna(row['prev_age']):
                return f"> {int(row['age_threshold'])}"
            else:
                return f"{int(row['age_threshold'])}-{int(row['prev_age'])}"
        
        subset['age_band'] = subset.apply(make_label, axis=1)
        marginal_data.append(subset)

    df_marginal = pd.concat(marginal_data)

    # 3. Plotting
    plt.figure(figsize=(12, 6))
    
    # Use seaborn for a clean grouped bar chart
    sns.barplot(
        data=df_marginal, 
        x='age_band', 
        y='marginal_gain', 
        hue='albu_case',
        palette='viridis'
    )

    plt.title('Marginal Yield: Extra Hypertensive CKD Cases Detected per 5-Year Age Drop')
    plt.xlabel('Age Band (Screening Expansion Step)')
    plt.ylabel('New Cases Found in This Band')
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.legend(title="Albuminuria Scenario")
    
    # Invert x-axis? No, usually we want to see the sequence: >55, 50-55, 45-50...
    # The sort order above usually puts >55 first. If not, we can explicit sort.
    
    plt.tight_layout()
    plt.savefig('marginal_yield_chart.png')
    print("Plot saved as marginal_yield_chart.png")

# --- Run the Plotter ---
plot_marginal_yield(df_incidence)
# %%
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def plot_marginal_yield(df_incidence, exclude_baseline=False):
    """
    Plots the MARGINAL number of new cases detected by lowering the age threshold.
    
    Parameters:
    - df_incidence: The dataframe calculated from 'calculate_cumulative_incidence_by_age'.
    - exclude_baseline: If True (or "no 55"), removes the first baseline column (e.g., '> 55') 
                        to zoom in on the marginal gains of younger groups.
    """
    
    # Allow user to pass "no 55" as a string to trigger exclusion
    if exclude_baseline == "no 55":
        exclude_baseline = True

    # 1. Aggregate mean across simulations first
    df_agg = df_incidence.groupby(['albu_case', 'age_threshold'])['incident_cases'].mean().reset_index()

    # 2. Sort to calculate differences
    # We sort by age descending (55, 50, 45...) so the "base" is the first row
    df_agg = df_agg.sort_values(by=['albu_case', 'age_threshold'], ascending=[True, False])

    marginal_data = []
    
    # Iterate through each albuminuria scenario
    for albu in df_agg['albu_case'].unique():
        subset = df_agg[df_agg['albu_case'] == albu].copy()
        
        # Calculate diff between current threshold and the previous (higher) threshold
        subset['prev_incidence'] = subset['incident_cases'].shift(1)
        
        # The first row is the baseline (Age > 55).
        # Subsequent rows: Count(Current) - Count(Previous)
        subset['marginal_gain'] = subset['incident_cases'] - subset['prev_incidence']
        
        # Fill NaN for the first row (baseline) with the actual total value
        subset['marginal_gain'] = subset['marginal_gain'].fillna(subset['incident_cases'])
        
        # Create a readable label for the x-axis
        subset['prev_age'] = subset['age_threshold'].shift(1)
        
        def make_label(row):
            if pd.isna(row['prev_age']):
                return f"> {int(row['age_threshold'])}"
            else:
                return f"{int(row['age_threshold'])}-{int(row['prev_age'])}"
        
        subset['age_band'] = subset.apply(make_label, axis=1)
        
        # --- LOGIC TO EXCLUDE BASELINE ---
        if exclude_baseline:
            # The baseline row is the one where 'prev_age' is NaN (the first row in the sorted set)
            subset = subset.dropna(subset=['prev_age'])
            
        marginal_data.append(subset)

    df_marginal = pd.concat(marginal_data)

    # 3. Plotting
    plt.figure(figsize=(12, 6))
    
    sns.barplot(
        data=df_marginal, 
        x='age_band', 
        y='marginal_gain', 
        hue='albu_case',
        palette='viridis'
    )

    title_suffix = "(Excluding Baseline > 55)" if exclude_baseline else ""
    plt.title(f'Marginal Yield: Extra Hypertensive CKD Cases Detected per 5-Year Age Drop {title_suffix}')
    plt.xlabel('Age Band (Screening Expansion Step)')
    plt.ylabel('New Cases Found in This Band')
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.legend(title="Albuminuria Scenario")
    
    plt.tight_layout()
    plt.savefig('marginal_yield_chart.png')
    print("Plot saved as marginal_yield_chart.png")

# --- Usage ---
plot_marginal_yield(df_incidence, exclude_baseline="no 55")
# %%


import numpy as np
import pandas as pd

def analyze_screening_performance(
    age_matrix_vec,
    ckd_mat_list,
    hypertension_mat_storage,
    diabetes_mat_storage,
    year_start=2025,
    year_end=2050,
    base_year=1990,
    age_thresholds=[55, 50, 45, 40, 35, 30]
):
    """
    Calculates Sensitivity and Specificity for screening three CKD etiologies 
    (Hypertensive, Diabetic, Normal) across various age thresholds.
    
    Returns:
        dict: {'hyper': df, 'diab': df, 'normal': df}
        Each dataframe contains columns: [albu_case, age_threshold, sensitivity, specificity, TP, FN, FP, TN]
    """
    
    n_groups = len(age_matrix_vec)
    n_albu, n_sims, _, n_years = ckd_mat_list[0].shape
    
    # Time indices
    idx_start = max(1, year_start - base_year)
    idx_end = min(n_years, year_end - base_year)

    print(f"Analyzing screening performance for years {year_start}-{year_end}...")

    # Storage for results
    # Structure: metrics[mode][albu][threshold] = {'TP': 0, 'FN': 0, ...}
    modes = ['hyper', 'diab', 'normal']
    metrics = {m: {} for m in modes}
    
    for albu in range(n_albu):
        for m in modes:
            metrics[m][albu] = {t: {'TP': 0, 'FN': 0, 'FP': 0, 'TN': 0} for t in age_thresholds}

    for albu in range(n_albu):
        for sim in range(n_sims):
            for g in range(n_groups):
                # --- 1. Slice Data ---
                # Handle 4D vs 3D age matrix
                raw_age = age_matrix_vec[g]
                if raw_age.ndim == 4:
                    age_slice = raw_age[albu, sim, :, :]
                else:
                    age_slice = raw_age[sim, :, :]

                ckd_slice = ckd_mat_list[g][albu, sim, :, :]
                hyper_slice = hypertension_mat_storage[g][sim, :, :]
                diab_slice = diabetes_mat_storage[g][sim, :, :]
                
                # Focus on the analysis window
                age_window = age_slice[:, idx_start:idx_end]
                
                # --- 2. Define Etiology Masks (Boolean 1/0) ---
                # Note: These are full matrix shapes (n_person, n_year)
                
                # Hypertensive CKD (CKD+Hyper)
                mask_hyper = (ckd_slice >= 1) & (hyper_slice == 1)
                
                # Diabetic CKD (CKD+Diab)
                mask_diab = (ckd_slice >= 1) & (diab_slice == 1)
                
                # Normal CKD (CKD only, no Hyper, no Diab)
                mask_normal = (ckd_slice >= 1) & (hyper_slice == 0) & (diab_slice == 0)
                
                disease_definitions = {
                    'hyper': mask_hyper,
                    'diab': mask_diab,
                    'normal': mask_normal
                }

                # --- 3. Iterate per Disease Mode ---
                for mode, mask_full in disease_definitions.items():
                    
                    # A. Identify Incident Cases (0 -> 1 transition)
                    # Slice to window, keeping incidence logic (requiring t-1)
                    # incidence check: (Current == 1) & (Previous == 0)
                    inc_window = (mask_full[:, idx_start:idx_end] == 1) & \
                                 (mask_full[:, (idx_start-1):(idx_end-1)] == 0)
                    
                    # Flatten masks for vector operations
                    # Any person who has at least one incident event in the window is a "Case"
                    is_case = inc_window.max(axis=1) # Boolean vector (n_people)
                    
                    # B. Get Age Metrics for Cases (for Sensitivity)
                    # For people who ARE cases, getting their age at ONSET
                    # We create a masked array of ages where incidence occurs
                    # Note: A person might have multiple 'incidence' blips if disease fluctuates, 
                    # but usually we take the first. Let's take the first onset.
                    
                    # Find column index of first True in each row
                    onset_idx = np.argmax(inc_window, axis=1) 
                    
                    # Extract age at that specific onset index
                    # ages_at_onset will be valid only where is_case is True
                    # We use fancy indexing: range(n_people), onset_idx
                    onset_ages = age_window[np.arange(age_window.shape[0]), onset_idx]
                    
                    valid_onset_ages = onset_ages[is_case]
                    
                    # C. Get Age Metrics for Non-Cases (for Specificity)
                    # Non-cases are those who NEVER had the event in the window
                    is_non_case = ~is_case
                    
                    # For non-cases, we screen them if their Max Age in window >= Threshold
                    max_ages_non_case = age_window[is_non_case].max(axis=1)
                    
                    # --- 4. Calculate TP/FN/FP/TN for each threshold ---
                    current_counts = metrics[mode][albu]
                    
                    for t in age_thresholds:
                        # Sensitivity Components (Cases)
                        tp = np.sum(valid_onset_ages >= t)
                        fn = np.sum(valid_onset_ages < t)
                        
                        # Specificity Components (Non-Cases)
                        # FP: Healthy but screened (Age >= Threshold)
                        fp = np.sum(max_ages_non_case >= t) 
                        # TN: Healthy and not screened (Age < Threshold)
                        tn = np.sum(max_ages_non_case < t)
                        
                        current_counts[t]['TP'] += tp
                        current_counts[t]['FN'] += fn
                        current_counts[t]['FP'] += fp
                        current_counts[t]['TN'] += tn

    # --- 5. Compile Results into DataFrames ---
    final_dfs = {}
    
    for mode in modes:
        records = []
        for albu in range(n_albu):
            for t in age_thresholds:
                d = metrics[mode][albu][t]
                tp, fn, fp, tn = d['TP'], d['FN'], d['FP'], d['TN']
                
                sens = tp / (tp + fn) if (tp + fn) > 0 else 0
                spec = tn / (tn + fp) if (tn + fp) > 0 else 0
                
                records.append({
                    "albu_case": albu,
                    "age_threshold": t,
                    "sensitivity": sens,
                    "specificity": spec,
                    "TP": tp, "FN": fn, "FP": fp, "TN": tn
                })
        
        final_dfs[mode] = pd.DataFrame(records)

    return final_dfs['hyper'], final_dfs['diab'], final_dfs['normal']

# --- Usage Example ---
df_hyper, df_diab, df_norm = analyze_screening_performance(
    age_matrix_ls, general_ckd_ls, hypertension_mat_storage, diabetes_mat_storage
)
# %%

import matplotlib.pyplot as plt
import seaborn as sns

def plot_tradeoff(df, title_prefix):
    """
    Plots Sensitivity and Specificity lines against Age Thresholds.
    """
    plt.figure(figsize=(10, 6))
    
    # We aggregate over albuminuria cases (mean) for a cleaner plot, 
    # or you can plot specific scenarios.
    df_agg = df.groupby('age_threshold')[['sensitivity', 'specificity']].mean().reset_index()
    df_agg = df_agg.sort_values('age_threshold')
    
    plt.plot(df_agg['age_threshold'], df_agg['sensitivity'], 
             label='Sensitivity (Cases Caught)', marker='o', color='blue')
    
    plt.plot(df_agg['age_threshold'], df_agg['specificity'], 
             label='Specificity (Healthy Avoided)', marker='s', color='orange')
    
    plt.title(f'{title_prefix}: Screening Performance by Age')
    plt.xlabel('Screening Age Threshold')
    plt.ylabel('Probability')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.gca().invert_xaxis() # 55 -> 30
    plt.show()

# Usage
plot_tradeoff(df_hyper, "Hypertensive CKD")
plot_tradeoff(df_diab, "Diabetic CKD")
plot_tradeoff(df_norm,"Normal CKD")
# %%


import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def plot_tp_comparison(df_hyper, df_diab, df_norm):
    """
    Plots the comparison of True Positives (Detected Cases) across the three 
    CKD etiologies (Hypertensive, Diabetic, Normal) on a single axes.
    """
    
    # 1. Combine data for plotting
    # We add a 'Scenario' column to distinguish them
    df_hyper = df_hyper.copy()
    df_hyper['Scenario'] = 'Hypertensive CKD'
    
    df_diab = df_diab.copy()
    df_diab['Scenario'] = 'Diabetic CKD'
    
    df_norm = df_norm.copy()
    df_norm['Scenario'] = 'Normal CKD (No Comorbidities)'
    
    # Concatenate all into one big dataframe
    combined_df = pd.concat([df_hyper, df_diab, df_norm])
    
    # 2. Aggregate Data
    # We take the mean TP across all albuminuria cases/simulations for each age threshold
    # to get one clean line per scenario.
    summary = combined_df.groupby(['Scenario', 'age_threshold'])['TP'].mean().reset_index()
    
    # Sort for plotting (Age high -> low)
    summary = summary.sort_values('age_threshold', ascending=False)

    # 3. Plotting
    plt.figure(figsize=(10, 6))
    
    # Use seaborn lineplot which handles the aggregation/hue automatically
    sns.lineplot(
        data=summary,
        x='age_threshold',
        y='TP',
        hue='Scenario',
        style='Scenario',
        markers=True,
        dashes=False,
        palette='Set1',  # Good contrast colors
        linewidth=2.5,
        markersize=9
    )

    # 4. Formatting
    plt.title('Comparison of Screening Yield (True Positives) by Etiology', fontsize=14)
    plt.xlabel('Screening Age Threshold (Years)', fontsize=12)
    plt.ylabel('Average Number of Cases Detected (TP)', fontsize=12)
    
    # Invert X-axis to show the expansion direction (55 -> 30)
    plt.xlim(57, 28)  # High to Low
    
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(title="CKD Etiology", fontsize=11)
    plt.tight_layout()
    
    plt.savefig('tp_comparison_plot.png')
    print("Plot saved as tp_comparison_plot.png")

# --- Usage ---
#Assuming you have run the analysis function:
plot_tp_comparison(df_hyper, df_diab, df_norm)
# %%
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

def plot_screening_roc(df_hyper, df_diab, df_norm):
    """
    Plots an ROC Curve treating 'Age' as the discrimination threshold.
    X-axis: 1 - Specificity (False Positive Rate) -> "Unnecessary Screening Rate"
    Y-axis: Sensitivity (True Positive Rate) -> "Case Detection Rate"
    """
    
    # 1. Prepare Data
    scenarios = {
        'Hypertensive CKD': df_hyper,
        'Diabetic CKD': df_diab,
        'Normal CKD': df_norm
    }
    
    plt.figure(figsize=(10, 8))
    
    colors = {'Hypertensive CKD': 'blue', 'Diabetic CKD': 'green', 'Normal CKD': 'gray'}
    markers = {'Hypertensive CKD': 'o', 'Diabetic CKD': 's', 'Normal CKD': '^'}
    
    for name, df in scenarios.items():
        # Aggregate mean across simulations/albuminuria
        # We need unique values per Age Threshold
        agg = df.groupby('age_threshold')[['sensitivity', 'specificity']].mean().reset_index()
        
        # Calculate FPR (1 - Specificity)
        agg['fpr'] = 1 - agg['specificity']
        
        # Sort by FPR (Low to High) so the line connects properly
        # Usually: High Age (55) -> Low FPR / Low Sens
        #          Low Age (30) -> High FPR / High Sens
        agg = agg.sort_values('fpr')
        
        # 2. Plot the Line
        plt.plot(
            agg['fpr'], 
            agg['sensitivity'], 
            label=f'{name}',
            color=colors[name],
            linewidth=2,
            alpha=0.8
        )
        
        # 3. Plot the Points (Age Markers)
        plt.scatter(
            agg['fpr'], 
            agg['sensitivity'], 
            color=colors[name],
            marker=markers[name],
            s=80,
            zorder=5
        )
        
        # 4. Annotate Specific Ages (to make the plot actionable)
        # We only label a few key ages to avoid clutter (e.g., 55, 45, 35)
        for _, row in agg.iterrows():
            age = int(row['age_threshold'])
            if age in [55, 45, 35, 30]: 
                plt.annotate(
                    f'{age}', 
                    (row['fpr'], row['sensitivity']),
                    textcoords="offset points", 
                    xytext=(0, 10), 
                    ha='center',
                    fontsize=9,
                    fontweight='bold',
                    color=colors[name]
                )

    # 5. Add "No Discrimination" Line (Diagonal)
    plt.plot([0, 1], [0, 1], color='red', linestyle='--', alpha=0.5, label='Random Guess')

    # Formatting
    plt.title('ROC Curve: Efficiency of Age-Based Screening', fontsize=14)
    plt.xlabel('False Positive Rate (1 - Specificity)\n"Fraction of Healthy People Unnecessarily Screened"', fontsize=11)
    plt.ylabel('Sensitivity (True Positive Rate)\n"Fraction of Cases Detected"', fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(loc='lower right')
    
    plt.tight_layout()
    plt.savefig('screening_roc_curve.png')
    print("Plot saved as screening_roc_curve.png")

# --- Usage ---
plot_screening_roc(df_hyper, df_diab, df_norm)
# %%
# age 45 for hyper
# age 50 for diabetes
# age ? for healthy


# %% 
import pandas as pd


# %%

import numpy as np
import pandas as pd

def analyze_screening_performance(
    age_matrix_vec,
    ckd_mat_list,
    hypertension_mat_storage,
    diabetes_mat_storage,
    year_start=2026,       # Changed default to 2026
    year_end=2050,
    base_year=1990,
    age_thresholds=[55, 50, 45, 40, 35, 30]
):
    """
    Calculates screening performance (Sensitivity/Specificity).
    
    Definition of Positive Cases (Sensitivity Denominator):
    1. Prevalent Case: Disease present in year_start (e.g., 2026).
       -> Screened if: Age[2026] >= Threshold.
    2. Incident Case: Disease develops between year_start+1 and year_end (e.g., 2027-2050).
       -> Screened if: Age[Onset] >= Threshold.
       
    Definition of Negative Cases (Specificity Denominator):
    - Never has the disease in the window.
    - Screened (False Positive) if: Max_Age[2026-2050] >= Threshold.
    """
    
    n_groups = len(age_matrix_vec)
    n_albu, n_sims, _, n_years = ckd_mat_list[0].shape
    
    # --- 1. Define Time Indices ---
    # idx_start corresponds to 2026
    idx_start = year_start - base_year
    # idx_end corresponds to 2050 (inclusive for array slicing, usually requires +1 in python if using range)
    idx_end = year_end - base_year
    
    print(f"Analyzing screening: Prevalent in {year_start} + Incident {year_start+1}-{year_end}...")

    modes = ['hyper', 'diab', 'normal']
    metrics = {m: {} for m in modes}
    
    # Initialize storage
    for albu in range(n_albu):
        for m in modes:
            metrics[m][albu] = {t: {'TP': 0, 'FN': 0, 'FP': 0, 'TN': 0} for t in age_thresholds}

    for albu in range(n_albu):
        for sim in range(n_sims):
            for g in range(n_groups):
                
                # --- 2. Slice Data Matrices ---
                raw_age = age_matrix_vec[g]
                if raw_age.ndim == 4:
                    age_slice = raw_age[albu, sim, :, :]
                else:
                    age_slice = raw_age[sim, :, :]

                ckd_slice = ckd_mat_list[g][albu, sim, :, :]
                hyper_slice = hypertension_mat_storage[g][sim, :, :]
                diab_slice = diabetes_mat_storage[g][sim, :, :]
                
                # Create Disease Masks (1 if has disease, 0 otherwise)
                mask_hyper = (ckd_slice >= 1) & (hyper_slice == 1)
                mask_diab = (ckd_slice >= 1) & (diab_slice == 1)
                mask_normal = (ckd_slice >= 1) & (hyper_slice == 0) & (diab_slice == 0)
                
                disease_definitions = {'hyper': mask_hyper, 'diab': mask_diab, 'normal': mask_normal}

                # --- 3. Process Each Disease Mode ---
                for mode, mask_full in disease_definitions.items():
                    
                    # ---------------------------------------------------
                    # A. PREVALENT CASES (Existing in 2026)
                    # ---------------------------------------------------
                    is_prev = mask_full[:, idx_start] == 1
                    
                    # Age at detection = Age in 2026
                    ages_prev = age_slice[:, idx_start]
                    valid_ages_prev = ages_prev[is_prev]
                    
                    # ---------------------------------------------------
                    # B. INCIDENT CASES (New onset 2027 - 2050)
                    # ---------------------------------------------------
                    # We look for transition 0 -> 1 between (idx_start) and (idx_end)
                    # Window logic: Compare t (2027..2050) with t-1 (2026..2049)
                    
                    # Slices for vector comparison
                    # 2027 to 2050
                    window_curr = mask_full[:, (idx_start + 1) : (idx_end + 1)] 
                    # 2026 to 2049
                    window_prev = mask_full[:, idx_start : idx_end]
                    
                    # Boolean matrix of incident events
                    incident_events = (window_curr == 1) & (window_prev == 0)
                    
                    # Identify people who have at least one incident event
                    has_incident_event = incident_events.max(axis=1)
                    
                    # STRICT RULE: Incident cases must NOT be Prevalent cases
                    # (If you had it in 2026, you are counted in Group A, not B)
                    is_incident = has_incident_event & (~is_prev)
                    
                    # Get Age at Onset for Incident Cases
                    # 1. Find the index (0 to N_years_in_window) of the first event
                    onset_idx_rel = np.argmax(incident_events, axis=1)
                    
                    # 2. Map this relative index back to the full age matrix
                    # The relative index 0 corresponds to year (idx_start + 1) -> 2027
                    # So absolute index is: idx_start + 1 + relative_index
                    onset_idx_abs = (idx_start + 1) + onset_idx_rel
                    
                    # 3. Extract ages
                    # We grab ages for everyone at their computed onset time
                    all_onset_ages = age_slice[np.arange(age_slice.shape[0]), onset_idx_abs]
                    
                    # 4. Filter for only the confirmed incident people
                    valid_ages_incident = all_onset_ages[is_incident]
                    
                    # ---------------------------------------------------
                    # C. COMBINE CASES (Total Sensitivity Pool)
                    # ---------------------------------------------------
                    # Concatenate prevalent ages and incident onset ages
                    total_case_ages = np.concatenate([valid_ages_prev, valid_ages_incident])
                    
                    # ---------------------------------------------------
                    # D. NON-CASES (Specificity Pool)
                    # ---------------------------------------------------
                    # People who were neither prevalent nor incident
                    is_non_case = (~is_prev) & (~is_incident)
                    
                    # For False Positives: Did they EVER reach the age threshold 
                    # during the screening program (2026 - 2050)?
                    # We check their MAX age in this window.
                    age_window_screening = age_slice[:, idx_start : (idx_end + 1)]
                    max_ages_non_case = age_window_screening[is_non_case].max(axis=1)
                    
                    # ---------------------------------------------------
                    # E. Calculate Metrics per Threshold
                    # ---------------------------------------------------
                    curr_counts = metrics[mode][albu]
                    
                    for t in age_thresholds:
                        # Sensitivity (Among Cases)
                        # Detected if Age_at_Detection >= Threshold
                        tp = np.sum(total_case_ages >= t)
                        fn = np.sum(total_case_ages < t)
                        
                        # Specificity (Among Non-Cases)
                        # False Positive if Max_Age_During_Screening >= Threshold
                        fp = np.sum(max_ages_non_case >= t)
                        tn = np.sum(max_ages_non_case < t)
                        
                        curr_counts[t]['TP'] += tp
                        curr_counts[t]['FN'] += fn
                        curr_counts[t]['FP'] += fp
                        curr_counts[t]['TN'] += tn

    # --- 4. Compile Results ---
    final_dfs = {}
    for mode in modes:
        records = []
        for albu in range(n_albu):
            for t in age_thresholds:
                d = metrics[mode][albu][t]
                tp, fn, fp, tn = d['TP'], d['FN'], d['FP'], d['TN']
                
                sens = tp / (tp + fn) if (tp + fn) > 0 else 0
                spec = tn / (tn + fp) if (tn + fp) > 0 else 0
                
                records.append({
                    "albu_case": albu,
                    "age_threshold": t,
                    "sensitivity": sens,
                    "specificity": spec,
                    "TP": tp, "FN": fn, "FP": fp, "TN": tn
                })
        final_dfs[mode] = pd.DataFrame(records)

    return final_dfs['hyper'], final_dfs['diab'], final_dfs['normal']

# --- Usage ---
# --- Usage Example ---
df_hyper_screen, df_diab_screen, df_norm_screen = analyze_screening_performance(
    age_matrix_vec=age_matrix_ls, 
    ckd_mat_list=general_ckd_ls, 
    hypertension_mat_storage=hypertension_mat_storage, 
    diabetes_mat_storage=diabetes_mat_storage,
    year_start=2026, 
    year_end=2050
)
# %%
plot_tp_comparison(df_hyper_screen, df_diab_screen, df_norm_screen)
# %%
print("Unique values in diabetes_mat_storage[0]:", np.unique(diabetes_mat_storage[0]))
# %%
def get_ckd_etiology_counts(
    ckd_mat_list, 
    hypertension_mat_storage, 
    diabetes_mat_storage, 
    base_year=1990
):
    """
    Calculates the total number of Hypertensive and Diabetic CKD cases
    in 2025 and 2050 based on the provided core logic.
    """
    years_of_interest = [2025, 2050]
    results = []

    n_groups = len(ckd_mat_list)
    n_albu, n_sims, n_people, _ = ckd_mat_list[0].shape

    print(f"Calculating etiology counts for {years_of_interest}...")

    for year in years_of_interest:
        idx = year - base_year
        
        for albu in range(n_albu):
            # We track counts per simulation to get an average later
            sim_hyper_counts = []
            sim_diab_counts = []

            for sim in range(n_sims):
                total_hyper_in_sim = 0
                total_diab_in_sim = 0

                for g in range(n_groups):
                    # --- 1. Slice Data for the specific Year ---
                    # ckd: [albu, sim, people, year] -> 1D vector of people
                    ckd_slice = ckd_mat_list[g][albu, sim, :, idx]
                    
                    # hyper/diab: [sim, people, year] -> 1D vector of people
                    hyper_slice = hypertension_mat_storage[g][sim, :, idx]
                    diab_slice = diabetes_mat_storage[g][sim, :, idx]

                    # --- 2. Core Logic (User Provided) ---
                    mask_hyper = (ckd_slice >= 1) & (hyper_slice == 1)
                    mask_diab = (ckd_slice >= 1) & (diab_slice == 1)

                    # --- 3. Sum cases ---
                    total_hyper_in_sim += np.sum(mask_hyper)
                    total_diab_in_sim += np.sum(mask_diab)

                sim_hyper_counts.append(total_hyper_in_sim)
                sim_diab_counts.append(total_diab_in_sim)

            # Store the average across simulations for this year/albu combo
            results.append({
                "Year": year,
                "Albu_Case": albu,
                "Hyper_CKD_Count": np.mean(sim_hyper_counts),
                "Diab_CKD_Count": np.mean(sim_diab_counts)
            })

    return pd.DataFrame(results)

# --- Usage ---
df_counts = get_ckd_etiology_counts(
    general_ckd_ls, 
    hypertension_mat_storage, 
    diabetes_mat_storage
)

print(df_counts)
# %%

import numpy as np
import pandas as pd

def analyze_etiology_burden(
    age_matrix_vec,
    ckd_mat_list,
    hypertension_mat_storage,
    diabetes_mat_storage,
    ckd_level=1,
    base_year=1990
):
    """
    Calculates the Total Count and Prevalence of Hypertensive CKD and Diabetic CKD
    for the population aged 18-74.
    
    Returns:
        pd.DataFrame: Columns include [albu, year, sim, count_hyper_ckd, prev_hyper_ckd, count_diab_ckd, prev_diab_ckd]
    """
    
    n_groups = len(age_matrix_vec)
    n_albu, n_sims, _, n_years = ckd_mat_list[0].shape
    
    records = []
    
    print("Calculating etiology burden (Counts & Prevalence) for ages 18-74...")

    for albu in range(n_albu):
        for sim in range(n_sims):
            
            # Initialize accumulators for this simulation run (summing across groups)
            # Shapes: (n_years,)
            total_pop_18_74 = np.zeros(n_years)
            total_hyper_ckd = np.zeros(n_years)
            total_diab_ckd = np.zeros(n_years)
            
            for g in range(n_groups):
                # --- 1. Slice Data ---
                # Handle 4D vs 3D age matrix input
                raw_age = age_matrix_vec[g]
                
                ages = raw_age[albu, sim, :, :]
                
                    
                ckd = ckd_mat_list[g][albu, sim, :, :]
                hyper = hypertension_mat_storage[g][sim, :, :]
                diab = diabetes_mat_storage[g][sim, :, :]
                
                # --- 2. Define Denominator Mask (Population 18-74) ---
                mask_pop = (ages >= 18) & (ages <= 74)
                
                # --- 3. Define Numerator Masks (Cases within 18-74) ---
                # Base CKD requirement
                mask_ckd = (ckd == ckd_level)
                
                # Hypertensive CKD: (CKD+) & (Hyper+) & (In Age Range)
                mask_hyper_case = mask_ckd & (hyper == 1) & mask_pop
                
                # Diabetic CKD: (CKD+) & (Diab+) & (In Age Range)
                mask_diab_case = mask_ckd & (diab == 1) & mask_pop
                
                # --- 4. Accumulate Counts ---
                # Sum across people (axis 0) to get count per year
                total_pop_18_74 += np.sum(mask_pop, axis=0)
                total_hyper_ckd += np.sum(mask_hyper_case, axis=0)
                total_diab_ckd += np.sum(mask_diab_case, axis=0)
            
            # --- 5. Calculate Rates and Store ---
            for t in range(n_years):
                pop = total_pop_18_74[t]
                
                # Avoid division by zero
                prev_hyper = (total_hyper_ckd[t] / pop) if pop > 0 else 0
                prev_diab = (total_diab_ckd[t] / pop) if pop > 0 else 0
                
                records.append({
                    "albu": albu,
                    "sim": sim,
                    "year": base_year + t,
                    "count_hyper_ckd": total_hyper_ckd[t],
                    "prev_hyper_ckd": prev_hyper,
                    "count_diab_ckd": total_diab_ckd[t],
                    "prev_diab_ckd": prev_diab,
                    "total_pop_18_74": pop # Added for verification
                })

    return pd.DataFrame(records)

# --- Usage Example ---
df_etiology_burden = analyze_etiology_burden(
    age_matrix_vec=age_matrix_ls,
    ckd_mat_list=general_ckd_ls,
    hypertension_mat_storage=hypertension_mat_storage,
    diabetes_mat_storage=diabetes_mat_storage
)

# Preview
print(df_etiology_burden[df_etiology_burden["year"] == 2025])
# %%
# overall, hypertensive people will contribute more; 
# so hypertensive indeed contributes more 
import numpy as np
import pandas as pd

# --- 1. Data Slicing Helper ---
def slice_window_data(
    age_matrix, ckd_matrix, stage_matrix, hyper_matrix, diab_matrix, 
    idx_start, idx_end, albu_idx, sim_idx
):
    """
    Extracts the time window (2026-2050) for a specific simulation and albuminuria case.
    Returns 2D arrays: (n_people, n_years_in_window).
    """
    # Handle Age (sometimes 3D, sometimes 4D)
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


# --- 2. Ground Truth & Definitions Helper ---
def define_ground_truth(ckd_win, stage_win):
    """
    Determines who is a 'Case', 'Non-Case', and who is 'Excluded'.
    Also creates the 'detectable_mask' (when screening is considered successful).
    
    Logic:
    - Excluded: Stage >= 4 at the start of the window.
    - Case: Has CKD (value=1) at any point and NOT excluded.
    - Detectable: Has CKD AND Stage <= 4. AND is Alive (Stage > 0).
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


# --- 3. Optimization Helper (Age Bands) ---
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


# --- 4. Core Simulation Engine ---
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
        # For all the CKD stages, how many did we catch when they are still in early stages
        # false negative: people can be in early stages or they move into late stages without being found 
        success_events = final_screen_mask & detectable_mask
        caught_mask = success_events.any(axis=1)
        ever_screened_mask = final_screen_mask.any(axis=1)
        n_people_screened = np.sum(ever_screened_mask) # <--- NEW: Total unique people screened

        tp = np.sum(caught_mask & is_case)
        fn = np.sum((~caught_mask) & is_case)
        
        # Specificity: Did we ever screen a Non-Case?
        # tn/(tn + fp): 
        # Out of everyone who was actually healthy, what percentage did we correctly avoid screening
        ever_screened_mask = final_screen_mask.any(axis=1)
        
        fp = np.sum(ever_screened_mask & is_non_case)
        tn = np.sum((~ever_screened_mask) & is_non_case)

        # NNS 
        
        
        strategy_results.append({
            "gen_thresh": g_thr,
            "diab_thresh": d_thr,
            "hyper_thresh": h_thr,
            "TP": tp, "FN": fn, "FP": fp, "TN": tn,
            "Total_Screened": n_people_screened
                                  
        })
        
    return strategy_results


# --- 5. Main Orchestrator ---
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
                    # res['group'] = g  # Optional: keep if you want group-specific data
                
                all_results.extend(sim_results)

    # 5. Aggregation
    df_res = pd.DataFrame(all_results)
    # nope for albu
    df_agg = df_res.groupby(['gen_thresh', 'diab_thresh', 'hyper_thresh'])[['TP', 'FN', 'FP', 'TN','Total_Screened']].sum().reset_index()
    
    df_agg['NNS'] = df_agg['Total_Screened'] / df_agg['TP']
    df_agg['sensitivity'] = df_agg['TP'] / (df_agg['TP'] + df_agg['FN'])
    df_agg['specificity'] = df_agg['TN'] / (df_agg['TN'] + df_agg['FP'])
    
    return df_agg.fillna(0)

# %%
df_results = analyze_screening_performance_modular(
            age_matrix_vec=age_matrix_ls,
            ckd_mat_list=general_ckd_ls,
            stage_matrix_ls=stage_matrix_ls,
            hypertension_mat_storage=hypertension_mat_storage,
            diabetes_mat_storage=diabetes_mat_storage,
            year_start=2026,
            year_end=2050,
            age_steps=[60,55,50,45,40,35],
            target_albu_indices=[0,1,2,3,4] 
        )

# %%
# Flip the df, so last row becomes first
df_results = df_results.iloc[::-1].reset_index(drop=True)




# %%
df_results_path = RESULTS_DIR / "screening_performance_results.csv"
df_results.to_csv(df_results_path, index=False)
print(f"Saved df_results to {df_results_path}")

# %%
df_results.columns


# %%
df_test_results
# %%
df_test_results_path = RESULTS_DIR / "screening_performance_results.csv"
df_test_results.to_csv(df_test_results_path, index=False)
print(f"Saved df_test_results to {df_test_results_path}")

# %%
# For each (gen_thresh, diab_thresh, hyper_thresh) combination, sum TP, FN, FP, TN and recalculate sensitivity/specificity

agg_df = (
    df_test_results
    .groupby(['gen_thresh', 'diab_thresh', 'hyper_thresh'], as_index=False)[['TP', 'FN', 'FP', 'TN']]
    .sum()
)
agg_df['sensitivity'] = agg_df['TP'] / (agg_df['TP'] + agg_df['FN'])
agg_df['specificity'] = agg_df['TN'] / (agg_df['TN'] + agg_df['FP'])

print("Aggregated performance by (gen_thresh, diab_thresh, hyper_thresh):")
print(agg_df)

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Load Data
# Ensure 'screening_performance_results.csv' is in your working directory
df = df_results

# 2. Calculate Distance to Perfect (Optimization Metric)
# This measures how close a point is to the top-left corner (Sens=1, Spec=1)
df['Dist_to_Perfect'] = np.sqrt((1 - df['sensitivity'])**2 + (1 - df['specificity'])**2)

# --- Analysis A: Sensitivity > 80% ---
df_80 = df[df['sensitivity'] > 0.80].copy()
top_5_80 = df_80.sort_values('Dist_to_Perfect', ascending=True).head(5)

print("\nTop 5 Scenarios (Sensitivity > 80%):")
print(top_5_80[['gen_thresh', 'diab_thresh', 'hyper_thresh', 
                'sensitivity', 'specificity', 'NNS', 'Dist_to_Perfect']])

# --- Analysis B: Sensitivity > 85% ---
df_85 = df[df['sensitivity'] > 0.85].copy()
top_5_85 = df_85.sort_values('Dist_to_Perfect', ascending=True).head(5)

print("\nTop 5 Scenarios (Sensitivity > 85%):")
print(top_5_85[['gen_thresh', 'diab_thresh', 'hyper_thresh', 
                'sensitivity', 'specificity', 'NNS', 'Dist_to_Perfect']])

# --- Plotting ---
plt.figure(figsize=(14, 6))

# Plot 1: Sensitivity > 80%
plt.subplot(1, 2, 1)
# Background points
plt.scatter(1 - df['specificity'], df['sensitivity'], color='lightgrey', alpha=0.5, label='Other Scenarios')
# Valid points
plt.scatter(1 - df_80['specificity'], df_80['sensitivity'], c=df_80['NNS'], cmap='viridis', s=60, alpha=0.8)
# Top 5
plt.scatter(1 - top_5_80['specificity'], top_5_80['sensitivity'], color='red', marker='*', s=200, label='Top 5 Optimal')
# Threshold Line
plt.axhline(y=0.80, color='red', linestyle='--', alpha=0.5, label='Min Sensitivity (80%)')

plt.title('Optimal Scenarios (Sens > 80%)')
plt.xlabel('1 - Specificity (False Positive Rate)')
plt.ylabel('Sensitivity')
plt.legend(loc='lower right')
plt.grid(True, linestyle='--', alpha=0.5)

# Plot 2: Sensitivity > 85%
plt.subplot(1, 2, 2)
# Background points
plt.scatter(1 - df['specificity'], df['sensitivity'], color='lightgrey', alpha=0.5, label='Other Scenarios')
# Valid points
plt.scatter(1 - df_85['specificity'], df_85['sensitivity'], c=df_85['NNS'], cmap='viridis', s=60, alpha=0.8)
# Top 5
plt.scatter(1 - top_5_85['specificity'], top_5_85['sensitivity'], color='purple', marker='*', s=200, label='Top 5 Optimal')
# Threshold Line
plt.axhline(y=0.85, color='purple', linestyle='--', alpha=0.5, label='Min Sensitivity (85%)')

plt.title('Optimal Scenarios (Sens > 85%)')
plt.xlabel('1 - Specificity (False Positive Rate)')
plt.ylabel('Sensitivity')
plt.legend(loc='lower right')
plt.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig('sensitivity_threshold_analysis.png')
plt.show()
# %%
top_5_85
# %%
top_10_85 = df_85.sort_values('Dist_to_Perfect', ascending=True).head(10)
top_10_85



# %%
eGFR_matrix_ls
# %%
