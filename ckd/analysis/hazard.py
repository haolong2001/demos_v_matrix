# %%
"""
Stage-specific mortality adjustment driven by CKD stage prevalence.

Workflow:
1. Load CKD stage matrices and age matrices (first simulation only) for every albuminuria
   forecast scenario.
2. Aggregate per-age, per-year stage prevalence for each ethnicity/gender cohort while
   keeping stage 3.1 and 3.2 separate.
3. Cache the prevalence tables (5 albumin scenarios × 61 years) under
   future_data_1990_2050/egfr_ to avoid recomputation.
4. Combine the prevalence with hazard ratios to back out stage-specific mortality rates
   so that weighted mortality reproduces the observed age-specific mortality curves.
5. Emit a tidy table with columns:
   sim_year, agent_gender, agent_race, albumin_scenario, eGFR_stage, agent_age, mortality_rate.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from Age_BMI_loading import age_matrix_vec_2050


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
CKD_DIR = PROJECT_ROOT / "ckd"
FUTURE_DATA_DIR = CKD_DIR / "future_data_1990_2050"
CKD_STAGE_DIR = FUTURE_DATA_DIR / "ckd_matrix"
EGFR_CACHE_DIR = FUTURE_DATA_DIR / "egfr_"
DATA_DIR = PROJECT_ROOT / "data"
MORTALITY_SOURCE = DATA_DIR / "overall_mortality.csv"
MORTALITY_OUTPUT = DATA_DIR / "stage_specific_mortality.csv"

STAGE_VALUES = [1.0, 2.0, 3.1, 3.2, 4.0, 5.0]
STAGE_LABELS = [str(int(val)) if val.is_integer() else str(val) for val in STAGE_VALUES]
HAZARD_RATIOS = {
    1.0: 1.0,
    2.0: 1.0,
    3.1: 1.2,
    3.2: 1.8,
    4.0: 3.2,
    5.0: 5.9,
}
HAZARD_VECTOR = np.array([HAZARD_RATIOS[val] for val in STAGE_VALUES])
BASE_YEAR = 1990
AGE_BUCKETS = []
AGE_BUCKETS.append({"label": "0", "lower": 0, "upper": 0})
AGE_BUCKETS.append({"label": "1-4", "lower": 1, "upper": 4})
for lower in range(5, 85, 5):
    upper = lower + 4
    AGE_BUCKETS.append({"label": f"{lower}-{upper}", "lower": lower, "upper": upper})
AGE_BUCKETS.append({"label": "85+", "lower": 85, "upper": 100})
AGE_BUCKET_LABELS = [bucket["label"] for bucket in AGE_BUCKETS]
MAX_TRACKED_AGE = 200
AGE_TO_BUCKET = np.full(MAX_TRACKED_AGE + 1, len(AGE_BUCKETS) - 1, dtype=int)
for idx, bucket in enumerate(AGE_BUCKETS):
    upper = bucket["upper"] if bucket["upper"] is not None else MAX_TRACKED_AGE
    AGE_TO_BUCKET[bucket["lower"] : upper + 1] = idx


def age_value_to_bucket_label(age_value: int) -> str:
    """Map a numeric age to the configured bucket label."""
    clipped = int(np.clip(age_value, 0, MAX_TRACKED_AGE))
    return AGE_BUCKET_LABELS[AGE_TO_BUCKET[clipped]]

# Ethnicity/gender metadata (idx follows the ordering used throughout the CKD pipeline)
GROUP_METADATA = [
    {"agent_race": "chinese", "agent_gender": "male"},
    {"agent_race": "chinese", "agent_gender": "female"},
    {"agent_race": "malay", "agent_gender": "male"},
    {"agent_race": "malay", "agent_gender": "female"},
    {"agent_race": "indian", "agent_gender": "male"},
    {"agent_race": "indian", "agent_gender": "female"},
    {"agent_race": "others", "agent_gender": "male"},
    {"agent_race": "others", "agent_gender": "female"},
]


def ensure_cache_dir() -> None:
    EGFR_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def stage_cache_path(idx: int) -> Path:
    ensure_cache_dir()
    return EGFR_CACHE_DIR / f"stage_prevalence_group_{idx}.npz"


def summary_csv_path(idx: int, stage_label: str) -> Path:
    ensure_cache_dir()
    return EGFR_CACHE_DIR / f"stage_prev_group_{idx}_stage_{stage_label}.csv"


def load_stage_matrices() -> List[np.ndarray]:
    """Load the CKD stage matrices (per ethnicity/gender group)."""
    matrices: List[np.ndarray] = []
    for idx in range(8):
        stage_path = CKD_STAGE_DIR / f"stage_mat_{idx}.npy"
        matrices.append(np.load(stage_path))
        print(f"Loaded stage_mat_{idx}.npy with shape {matrices[-1].shape}")
    return matrices


def compute_stage_counts(
    stage_matrix: np.ndarray,
    age_matrix: np.ndarray,
    n_years: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute raw per-age counts for each albumin scenario (first simulation only).

    Returns:
        stage_counts: shape (5, len(STAGE_VALUES), n_years, n_age_buckets)
        total_counts: shape (5, n_years, n_age_buckets)
    """
    n_albu = stage_matrix.shape[0]
    n_buckets = len(AGE_BUCKETS)
    stage_counts = np.zeros((n_albu, len(STAGE_VALUES), n_years, n_buckets), dtype=np.float64)
    total_counts = np.zeros((n_albu, n_years, n_buckets), dtype=np.float64)

    for alb_idx in range(n_albu):
        scenario_slice = stage_matrix[alb_idx, 0, :, :]  # (n_person, n_years)
        for year_idx in range(n_years):
            ages = age_matrix[0, :, year_idx]
            stages = scenario_slice[:, year_idx]
            valid_mask = (ages >= 0) & (stages >= 0)
            if not np.any(valid_mask):
                continue

            ages_valid = ages[valid_mask]
            stages_valid = stages[valid_mask]
            clipped_age = np.clip(ages_valid.astype(int), 0, MAX_TRACKED_AGE)
            bucket_idx = AGE_TO_BUCKET[clipped_age]

            total_counts[alb_idx, year_idx, :] += np.bincount(
                bucket_idx, minlength=n_buckets
            )

            for stage_pos, stage_val in enumerate(STAGE_VALUES):
                stage_mask = np.isclose(stages_valid, stage_val)
                if not np.any(stage_mask):
                    continue
                stage_age_idx = bucket_idx[stage_mask]
                stage_counts[alb_idx, stage_pos, year_idx, :] += np.bincount(
                    stage_age_idx, minlength=n_buckets
                )

    return stage_counts, total_counts


def build_stage_summary(
    stage_counts: np.ndarray, total_counts: np.ndarray
) -> np.ndarray:
    """
    Aggregate per-year stage prevalence (5 albumin scenarios × len(STAGE_VALUES) × 61 years).
    """
    year_totals = total_counts.sum(axis=2)  # (5, 61)
    stage_year_counts = stage_counts.sum(axis=3)  # (5, len(stage), 61)
    with np.errstate(divide="ignore", invalid="ignore"):
        stage_year_prev = np.divide(
            stage_year_counts,
            year_totals[:, np.newaxis, :],
            out=np.zeros_like(stage_year_counts),
            where=year_totals[:, np.newaxis, :] > 0,
        )
    return stage_year_prev  # (5, len(stage), 61)


def save_stage_summary_tables(
    idx: int, summary: np.ndarray, sim_years: np.ndarray
) -> None:
    """
    Persist 5×61 tables (albumin scenario × year) for every stage so other scripts
    can reuse them without recomputation.
    """
    for stage_pos, stage_label in enumerate(STAGE_LABELS):
        df = pd.DataFrame(
            summary[:, stage_pos, :],
            columns=sim_years,
        )
        df.index.name = "albumin_scenario"
        df.to_csv(summary_csv_path(idx, stage_label))


def load_stage_counts_from_cache(idx: int) -> Tuple[np.ndarray, np.ndarray] | None:
    cache_path = stage_cache_path(idx)
    if not cache_path.exists():
        return None
    data = np.load(cache_path, allow_pickle=True)
    stage_counts = data["stage_counts"]
    total_counts = data["total_counts"]
    return stage_counts, total_counts


def compute_or_load_stage_prevalence(
    idx: int,
    stage_matrix: np.ndarray,
    age_matrix: np.ndarray,
    sim_years: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Returns:
        stage_prevalence: shape (5, len(stage), n_years, age_limit+1)
        total_counts: shape (5, n_years, age_limit+1)
    """
    cached = load_stage_counts_from_cache(idx)
    if cached is None:
        stage_counts, total_counts = compute_stage_counts(
            stage_matrix, age_matrix, len(sim_years)
        )
        summary = build_stage_summary(stage_counts, total_counts)
        np.savez(
            stage_cache_path(idx),
            stage_counts=stage_counts,
            total_counts=total_counts,
            summary=summary,
            sim_years=sim_years,
        )
        save_stage_summary_tables(idx, summary, sim_years)
    else:
        stage_counts, total_counts = cached

    with np.errstate(divide="ignore", invalid="ignore"):
        stage_prev = np.divide(
            stage_counts,
            total_counts[:, np.newaxis, :, :],
            out=np.zeros_like(stage_counts),
            where=total_counts[:, np.newaxis, :, :] > 0,
        )
    return stage_prev, total_counts


def build_stage_specific_mortality(
    stage_matrices: List[np.ndarray],
    age_matrices: List[np.ndarray],
    mortality_df: pd.DataFrame,
    output_path: Path = MORTALITY_OUTPUT,
) -> pd.DataFrame:
    """Create the tidy mortality table described in ckd_matrix_reference.md."""
    mortality_df = mortality_df.copy()
    mortality_df["agent_gender"] = mortality_df["agent_gender"].str.lower()
    mortality_df["age_group"] = mortality_df["agent_age"].apply(age_value_to_bucket_label)
    mortality_lookup = (
        mortality_df.groupby(["sim_year", "agent_gender", "age_group"])["mortality_rate"]
        .mean()
        .to_dict()
    )

    n_years = stage_matrices[0].shape[-1]
    sim_years = np.arange(BASE_YEAR, BASE_YEAR + n_years)
    records: List[Dict[str, object]] = []

    for idx, (stage_mat, age_mat) in enumerate(zip(stage_matrices, age_matrices)):
        meta = GROUP_METADATA[idx]
        stage_prev, total_counts = compute_or_load_stage_prevalence(
            idx, stage_mat, age_mat, sim_years
        )

        for alb_idx in range(stage_prev.shape[0]):
            weighted_risk = np.sum(
                stage_prev[alb_idx] * HAZARD_VECTOR[:, np.newaxis, np.newaxis],
                axis=0,
            )  # shape (n_years, n_age_buckets)

            for year_offset, sim_year in enumerate(sim_years):
                for bucket_idx, bucket_label in enumerate(AGE_BUCKET_LABELS):
                    if total_counts[alb_idx, year_offset, bucket_idx] == 0:
                        continue
                    base_rate = mortality_lookup.get(
                        (sim_year, meta["agent_gender"], bucket_label)
                    )
                    if base_rate is None:
                        continue
                    denom = weighted_risk[year_offset, bucket_idx]
                    if denom <= 0:
                        continue

                    for stage_pos, stage_val in enumerate(STAGE_VALUES):
                        prev = stage_prev[alb_idx, stage_pos, year_offset, bucket_idx]
                        if prev == 0:
                            continue
                        stage_rate = base_rate * HAZARD_RATIOS[stage_val] / denom
                        records.append(
                            {
                                "sim_year": sim_year,
                                "agent_gender": meta["agent_gender"],
                                "agent_race": meta["agent_race"],
                                "albumin_scenario": alb_idx,
                                "eGFR_stage": STAGE_LABELS[stage_pos],
                                "age_group": bucket_label,
                                "mortality_rate": stage_rate,
                            }
                        )

    stage_specific_df = pd.DataFrame.from_records(records)
    stage_specific_df.sort_values(
        [
            "sim_year",
            "agent_gender",
            "agent_race",
            "albumin_scenario",
            "age_group",
            "eGFR_stage",
        ],
        inplace=True,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    stage_specific_df.to_csv(output_path, index=False)
    print(f"Saved stage-specific mortality rates to {output_path}")

    return stage_specific_df


def main() -> None:
    stage_matrices = load_stage_matrices()
    age_matrices = age_matrix_vec_2050
    mortality_df = pd.read_csv(MORTALITY_SOURCE)
    stage_specific_df = build_stage_specific_mortality(
        stage_matrices, age_matrices, mortality_df
    )

    print("Stage-specific mortality sample:")
    print(stage_specific_df.head())


if __name__ == "__main__":
    main()
