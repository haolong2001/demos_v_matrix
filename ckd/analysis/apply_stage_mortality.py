"""
Apply stage-specific mortality in a fully vectorized manner.

Workflow per ethnicity/gender group:
1. Start from the baseline age matrix; derive the alive mask (age >= 0).
2. Enforce that once an individual reaches stage 5, all subsequent alive years
   remain in stage 5 until death.
3. For every albumin scenario, run Bernoulli trials for all cells where
   (alive == True) and (stage >= 3). The mortality rate for each cell is read
   from the precomputed stage-specific mortality tensor.
4. Once a death occurs, zero out all later years (no stage is allowed to extend
   life beyond the baseline) and set both the stage and age matrices to -1 for
   the remainder of that trajectory.
5. Persist the adjusted life mask plus modified age/stage matrices for reuse.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd

# %%
from Age_BMI_loading import age_matrix_vec_2050
from hazard import (
    AGE_TO_BUCKET,
    MAX_TRACKED_AGE,
    BASE_YEAR,
    CKD_STAGE_DIR,
    GROUP_METADATA,
)
# GROUP_METADATA = [
#     {"agent_race": "chinese", "agent_gender": "male"},
#     {"agent_race": "chinese", "agent_gender": "female"},
#     {"agent_race": "malay", "agent_gender": "male"},
#     {"agent_race": "malay", "agent_gender": "female"},
#     {"agent_race": "indian", "agent_gender": "male"},
#     {"agent_race": "indian", "agent_gender": "female"},
#     {"agent_race": "others", "agent_gender": "male"},
#     {"agent_race": "others", "agent_gender": "female"},
# ]
from stage_mortality_table import load_stage_mortality_table


OUTPUT_DIR = Path("../future_data_1990_2050/mortality_adjusted")
STAGE_VALUE_MAP = {
    "3.1": 3.1,
    "3.2": 3.2,
    "4": 4.0,
    "5": 5.0,
}
STAGE_LABELS = list(STAGE_VALUE_MAP.keys())


def load_stage_matrices() -> list[np.ndarray]:
    matrices: list[np.ndarray] = []
    for idx in range(8):
        path = CKD_STAGE_DIR / f"stage_mat_{idx}.npy"
        matrices.append(np.load(path))
        print(f"Loaded stage matrix {path} with shape {matrices[-1].shape}")
    return matrices


def clamp_stage_five(stage_arr: np.ndarray, alive_mask: np.ndarray) -> np.ndarray:
    """
    Once stage 5 appears, keep the agent in stage 5 for all remaining alive years.
    """
    stage5_mask = np.isclose(stage_arr, STAGE_VALUE_MAP["5"])
    stage5_reached = np.maximum.accumulate(stage5_mask, axis=-1).astype(bool)
    return np.where(stage5_reached & alive_mask, STAGE_VALUE_MAP["5"], stage_arr)


def build_stage_index(stage_arr: np.ndarray, stage_index_map: Dict[str, int]) -> np.ndarray:
    """
    Map numerical stage values to the indices used by the mortality tensor.
    """
    stage_idx = np.full(stage_arr.shape, -1, dtype=int)
    for label, value in STAGE_VALUE_MAP.items():
        mask = np.isclose(stage_arr, value)
        stage_idx[mask] = stage_index_map[label]
    return stage_idx


def apply_stage_mortality(
    age_matrix: np.ndarray,
    stage_matrix: np.ndarray,
    metadata: Dict[str, str],
    mortality_table,
    rng: np.random.Generator,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Tuple[np.ndarray, np.ndarray]]:
    """
    Run mortality trials for all albumin scenarios simultaneously.

    Returns:
        life_mask: (5, n_sim, n_person, n_years) binary mask after adjustment
        adjusted_stage: stage matrix with -2 after early deaths
        adjusted_age: age matrix (per albumin) with -2 after early deaths
    """
    n_albu, n_sim, n_person, n_years = stage_matrix.shape
    sim_years = np.arange(BASE_YEAR, BASE_YEAR + n_years)
    n_stages = len(STAGE_LABELS)

    baseline_alive = (age_matrix >= 0)
    life_mask = np.repeat(baseline_alive[np.newaxis, :, :, :], repeats=n_albu, axis=0).copy()

    stage_arr = stage_matrix.copy()
    age_expanded = np.broadcast_to(age_matrix[np.newaxis, :, :, :], stage_arr.shape).copy()

    stage_arr = clamp_stage_five(stage_arr, life_mask)
    stage_idx = build_stage_index(stage_arr, mortality_table.stage_index)

    age_int = age_matrix.astype(int)
    age_bucket_core = np.full(age_int.shape, -1, dtype=int)
    valid_age_mask = (age_int >= 0) & (age_int <= MAX_TRACKED_AGE)
    age_bucket_core[valid_age_mask] = AGE_TO_BUCKET[age_int[valid_age_mask]]
    age_bucket_idx = np.broadcast_to(
        age_bucket_core[np.newaxis, :, :, :], stage_arr.shape
    )

    year_positions = np.array([mortality_table.year_index[year] for year in sim_years], dtype=int)
    year_idx_grid = np.broadcast_to(year_positions.reshape(1, 1, n_years), (n_sim, n_person, n_years))

    gender_idx = mortality_table.gender_index[metadata["agent_gender"]]
    race_idx = mortality_table.race_index[metadata["agent_race"]]
    survivor_counts = np.zeros((n_albu, n_sim, n_years, n_stages), dtype=int)
    death_counts = np.zeros_like(survivor_counts)

    stage1_index = mortality_table.stage_index["1"]

    for alb_idx in range(n_albu):
        alive = life_mask[alb_idx]
        stage_idx_alb = stage_idx[alb_idx]
        stage_mask = (stage_idx_alb >= 0) & alive
        if not np.any(stage_mask):
            continue

        stage_idx_valid = stage_idx_alb.copy()
        
        stage_values = stage_arr[alb_idx].copy()
        age_idx_alb = age_bucket_idx[alb_idx]

        mortality_slice = mortality_table.rates[:, gender_idx, race_idx, alb_idx]
        mortality_years = mortality_slice[year_positions]  # (n_years, n_stages, n_age_groups)

        rates = mortality_years[year_idx_grid, stage_idx_valid, age_idx_alb]
        rates = np.where(stage_mask, rates, 0.0)

        # death event
        base_rates = mortality_years[year_idx_grid, stage1_index, age_idx_alb]
        base_survival = np.clip(1.0 - base_rates, 0.0, 1.0)
        stage_survival = np.clip(1.0 - rates, 0.0, 1.0)
        survival_draw = rng.random(alive.shape) * base_survival

        death_events = (stage_survival < survival_draw) & stage_mask
        death_cumulative = np.cumsum(death_events, axis=-1)
        alive_after = alive & (death_cumulative == 0)

        # 1. CALCULATE THE DEATH MASK FIRST
        # We must do this BEFORE updating life_mask.
        # 'alive' currently holds the "Before" state.
        # 'alive_after' holds the "After" state.
        # The difference reveals exactly who died in this step.
        ckd_death_mask = alive & (~alive_after)

        # 2. UPDATE MATRICES
        # Apply the -2 only to those who died.
        # Safe to do now because 'stage_arr' does not affect 'alive' or 'alive_after'
        stage_arr[alb_idx] = np.where(ckd_death_mask, -2, stage_arr[alb_idx])
        age_expanded[alb_idx] = np.where(ckd_death_mask, -2, age_expanded[alb_idx])

        # 3. UPDATE THE MASTER LIFE MASK LAST
        # Now it is safe to update the master mask for the next iteration.
        # WARNING: This line updates the 'alive' variable too (because it's a view).
        # That is why this MUST be the last step in this block.
        life_mask[alb_idx] = alive_after

        for stage_pos, stage_label in enumerate(STAGE_LABELS):
            stage_val = STAGE_VALUE_MAP[stage_label]
            stage_bool = np.isclose(stage_values, stage_val)
            stage_survivors = alive_after & stage_bool
            stage_deaths = death_events & stage_bool
            survivor_counts[alb_idx, :, :, stage_pos] = stage_survivors.sum(axis=1)
            death_counts[alb_idx, :, :, stage_pos] = stage_deaths.sum(axis=1)

    return life_mask.astype(np.int8), stage_arr, age_expanded, (survivor_counts, death_counts)


def main(seed: int = 12345) -> None:
    rng = np.random.default_rng(seed)
    mortality_table = load_stage_mortality_table()
    stage_matrices = load_stage_matrices()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    sample_stage = stage_matrices[0]
    n_albu, n_sim, _, n_years = sample_stage.shape
    n_stage_tracked = len(STAGE_LABELS)
    total_survivors = np.zeros((n_albu, n_sim, n_years, n_stage_tracked), dtype=int)
    total_deaths = np.zeros_like(total_survivors)

    for idx, metadata in enumerate(GROUP_METADATA):
        # if (idx < 2):
        #     print(f"pass {metadata['agent_race']} {metadata['agent_gender']}")
        #     continue
        print(f"Processing group {idx}: {metadata['agent_race']} {metadata['agent_gender']}")
        age_matrix = age_matrix_vec_2050[idx]
        stage_matrix = stage_matrices[idx]

        (
            life_mask,
            adjusted_stage,
            adjusted_age,
            (survivor_counts, death_counts),
        ) = apply_stage_mortality(
            age_matrix,
            stage_matrix,
            metadata,
            mortality_table,
            rng,
        )

        total_survivors += survivor_counts
        total_deaths += death_counts

        np.save(OUTPUT_DIR / f"life_mask_group_{idx}.npy", life_mask)
        np.save(OUTPUT_DIR / f"stage_matrix_group_{idx}.npy", adjusted_stage)
        np.save(OUTPUT_DIR / f"age_matrix_group_{idx}.npy", adjusted_age)
        print(f"Saved adjusted artifacts for group {idx}")
    #below counts the death
    sim_years = np.arange(BASE_YEAR, BASE_YEAR + n_years)
    records = []
    for alb_idx in range(n_albu):
        for sim_idx in range(n_sim):
            for year_offset, sim_year in enumerate(sim_years):
                for stage_pos, stage_label in enumerate(STAGE_LABELS):
                    deaths = total_deaths[alb_idx, sim_idx, year_offset, stage_pos]
                    survivors = total_survivors[alb_idx, sim_idx, year_offset, stage_pos]
                    denom = deaths + survivors
                    per_death = deaths / denom if denom > 0 else 0.0
                    records.append(
                        {
                            "albumin_scenario": alb_idx,
                            "simu_number": sim_idx,
                            "sim_year": int(sim_year),
                            "eGFR_stage": stage_label,
                            "death": int(deaths),
                            "percen_death": per_death,
                        }
                    )

    df = pd.DataFrame.from_records(records)
    df.to_csv(OUTPUT_DIR / "ckd_stage_attributed_deaths.csv", index=False)
    print(f"Saved CKD-attributed death summary to {OUTPUT_DIR / 'ckd_stage_attributed_deaths.csv'}")


if __name__ == "__main__":
    main()

# stage_matrix_ls is of (n_albu, n_sim, n_people, n_year) shape;so 
# life_mask = np.repeat(baseline_alive[np.newaxis, :, :, :], repeats=n_albu, axis=0) this one is unnecessary 
