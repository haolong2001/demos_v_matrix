"""
Validate that the stage-specific mortality table reproduces the baseline
age-specific mortality rates once combined with the cached stage prevalence.
"""
from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd

from hazard import (
    AGE_BUCKETS,
    AGE_BUCKET_LABELS,
    BASE_YEAR,
    DATA_DIR,
    EGFR_CACHE_DIR,
    GROUP_METADATA,
    age_value_to_bucket_label,
    STAGE_VALUES,
)

OVERALL_MORTALITY_PATH = DATA_DIR / "overall_mortality.csv"
STAGE_SPECIFIC_PATH = DATA_DIR / "stage_specific_mortality.csv"


def load_stage_prevalence(idx: int) -> np.ndarray:
    cache_path = EGFR_CACHE_DIR / f"stage_prevalence_group_{idx}.npz"
    if not cache_path.exists():
        raise FileNotFoundError(
            f"Stage prevalence cache {cache_path} missing. "
            "Run hazard.py once to generate it."
        )
    data = np.load(cache_path, allow_pickle=True)
    stage_counts = data["stage_counts"]
    total_counts = data["total_counts"]
    with np.errstate(divide="ignore", invalid="ignore"):
        stage_prev = np.divide(
            stage_counts,
            total_counts[:, np.newaxis, :, :],
            out=np.zeros_like(stage_counts),
            where=total_counts[:, np.newaxis, :, :] > 0,
        )
    return stage_prev  # shape: (5, len(stage), 61, n_age_buckets)


def validate() -> Dict[str, pd.DataFrame]:
    stage_specific_df = pd.read_csv(STAGE_SPECIFIC_PATH)
    overall_df = pd.read_csv(OVERALL_MORTALITY_PATH)

    stage_specific_df["agent_gender"] = stage_specific_df["agent_gender"].str.lower()
    overall_df["agent_gender"] = overall_df["agent_gender"].str.lower()

    stage_lookup = stage_specific_df.set_index(
        [
            "agent_gender",
            "agent_race",
            "albumin_scenario",
            "sim_year",
            "age_group",
            "eGFR_stage",
        ]
    )["mortality_rate"].to_dict()

    overall_df["age_group"] = overall_df["agent_age"].apply(age_value_to_bucket_label)
    overall_lookup = (
        overall_df.groupby(["agent_gender", "sim_year", "age_group"])["mortality_rate"]
        .mean()
        .to_dict()
    )

    n_years = int(stage_specific_df["sim_year"].max() - BASE_YEAR + 1)
    sim_years = np.arange(BASE_YEAR, BASE_YEAR + n_years)

    validation_frames: Dict[str, pd.DataFrame] = {}

    for idx, meta in enumerate(GROUP_METADATA):
        stage_prev = load_stage_prevalence(idx)
        rows: List[Dict[str, float]] = []

        for alb_idx in range(stage_prev.shape[0]):
            for year_offset, sim_year in enumerate(sim_years):
                for bucket_idx, bucket in enumerate(AGE_BUCKET_LABELS):
                    prev_vec = stage_prev[alb_idx, :, year_offset, bucket_idx]
                    if np.sum(prev_vec) == 0:
                        continue

                    reconstructed = 0.0
                    for stage_value, prev in zip(STAGE_VALUES, prev_vec):
                        if prev == 0:
                            continue
                        rate = stage_lookup.get(
                            (
                                meta["agent_gender"],
                                meta["agent_race"],
                                alb_idx,
                                sim_year,
                                bucket,
                                stage_value,
                            )
                        )
                        if rate is None:
                            continue
                        reconstructed += prev * rate

                    target = overall_lookup.get(
                        (meta["agent_gender"], sim_year, bucket), np.nan
                    )
                    rows.append(
                        {
                            "sim_year": sim_year,
                            "albumin_scenario": alb_idx,
                            "age_group": bucket,
                            "calculated_rate": reconstructed,
                            "target_rate": target,
                            "abs_error": abs(reconstructed - target)
                            if target == target
                            else np.nan,
                        }
                    )

        validation_frames[
            f"{meta['agent_race']}_{meta['agent_gender']}"
        ] = pd.DataFrame(rows)

    return validation_frames


def main() -> None:
    validation_results = validate()
    for key, df in validation_results.items():
        print(f"=== {key} ===")
        print(df.head())
        print(
            f"Mean abs error: {df['abs_error'].dropna().mean():.6f} "
            f"(rows: {len(df)})"
        )


if __name__ == "__main__":
    main()
