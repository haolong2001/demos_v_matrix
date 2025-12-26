"""Utility helpers shared across CKD analysis notebooks and scripts."""

from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


SimCols = Sequence[str]


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


def simulate_ckd_prevalence(
    age_matrix_vec: Sequence[np.ndarray],
    ckd_mat_list: Sequence[np.ndarray],
    ckd_level: int = 1,
    min_age: int = 18,
    max_age: int = 74,
) -> pd.DataFrame:
    """Compute CKD prevalence across simulations, years, demographics, and age groups."""

    age_groups: Tuple[Tuple[int, int], ...] = (
        (18, 29),
        (30, 39),
        (40, 49),
        (50, 59),
        (60, 69),
        (70, 79),
        (80, 200),
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
                ages = age_matrix_vec[g][sim, :, :]
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


def check_nphs_overlap_gender_race(
    ckd_prevalence: pd.DataFrame,
    nphs_df: pd.DataFrame,
    year_col: str = "year",
) -> pd.DataFrame:
    """Compare NPHS observed values with simulated 95% CIs for gender/race splits."""

    sim_cols = ["male", "female", "chinese", "malay", "indian"]
    ci_df = compute_age_ci(ckd_prevalence, sim_cols)

    nphs_sub = nphs_df[[year_col, "male", "female", "chn", "mal", "ind"]].copy()
    nphs_sub = nphs_sub.rename(
        columns={
            "chn": "chinese_obs",
            "mal": "malay_obs",
            "ind": "indian_obs",
            "male": "male_obs",
            "female": "female_obs",
        }
    )

    merged = pd.merge(ci_df, nphs_sub, on=year_col, how="inner").sort_values(year_col)

    results = []
    for _, row in merged.iterrows():
        res = {"year": int(row[year_col])}
        for col in sim_cols:
            obs = row[f"{col}_obs"]
            lower = row[f"{col}_lower"]
            upper = row[f"{col}_upper"]
            inside = lower <= obs <= upper
            res[col] = f"{inside} [95% CI: {lower:.3f}-{upper:.3f}], obs={obs:.3f}"
        results.append(res)

    return pd.DataFrame(results)


def plot_nphs_overlap_gender_race(
    ckd_prevalence: pd.DataFrame,
    nphs_df: pd.DataFrame,
    year_col: str = "year",
    factor: float = 100.0,
):
    """Create the 2x3 panel plot comparing simulation CI with NPHS point estimates."""

    sim_cols = ["male", "female", "chinese", "malay", "indian"]
    ci_df = compute_age_ci(ckd_prevalence, sim_cols)

    nphs_sub = nphs_df[[year_col, "male", "female", "chn", "mal", "ind"]].copy()
    nphs_sub = nphs_sub.rename(
        columns={
            "chn": "chinese_obs",
            "mal": "malay_obs",
            "ind": "indian_obs",
            "male": "male_obs",
            "female": "female_obs",
        }
    )

    merged = pd.merge(ci_df, nphs_sub, on=year_col, how="inner").sort_values(year_col)
    years = merged[year_col].values

    fig, axes = plt.subplots(2, 3, figsize=(14, 8), sharex=True)
    fig.suptitle("CKD Prevalence: Simulation 95% CI vs NPHS Point Estimates")

    panel_defs = [
        ("male", "Male", 0, 0),
        ("female", "Female", 0, 1),
        ("chinese", "Chinese", 1, 0),
        ("malay", "Malay", 1, 1),
        ("indian", "Indian", 1, 2),
    ]

    def row_ylim(cols: Iterable[str]) -> Tuple[float, float]:
        vals = []
        for col in cols:
            vals.extend(
                [
                    merged[f"{col}_lower"].values * factor,
                    merged[f"{col}_upper"].values * factor,
                    merged[f"{col}_obs"].values * factor,
                ]
            )
        stacked = np.concatenate(vals)
        return 0.0, stacked.max() * 1.1

    row0_cols = ["male", "female"]
    row1_cols = ["chinese", "malay", "indian"]
    y0_min, y0_max = row_ylim(row0_cols)
    y1_min, y1_max = row_ylim(row1_cols)

    for col, title, r, c in panel_defs:
        ax = axes[r, c]
        lower = merged[f"{col}_lower"].values * factor
        upper = merged[f"{col}_upper"].values * factor
        obs = merged[f"{col}_obs"].values * factor

        ax.fill_between(years, lower, upper, alpha=0.3, label="Simulation 95% CI", color="#5088C4")
        ax.scatter(years, obs, marker="x", s=60, label="NPHS", color="#D55E00", zorder=10)

        ax.set_title(title)
        ax.set_xticks(years)
        if r == 0:
            ax.set_ylim(0, 50)
        else:
            ax.set_ylim(0, 50)


        if c == 0:
            ax.set_ylabel("Prevalence (%)")
        if r == 1:
            ax.set_xlabel("Year")

        if (r, c) in [(0, 0), (1, 0)]:
            ax.legend(loc="upper left", fontsize=9)

    axes[0, 2].axis("off")
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    return fig, axes



