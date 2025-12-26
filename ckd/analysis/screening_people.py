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
stage_matrix_ls = load_stage_matrices()
age_matrix_ls = load_age_matrices()
albu_mat_storage = load_albu_matrices()
hypertension_mat_storage = load_hypertension_matrices()
diabetes_mat_storage = load_diabetes_matrices()

general_ckd_ls = build_general_ckd_matrices(stage_matrix_ls, albu_mat_storage)
age_matrix_baseline = [mat[0] for mat in age_matrix_ls]




we wish to identify the people for screening from 2026 onwards;

identify the poeple for screening in the matrices

they are still in early stages stage 1 or 2 
1. when they reach age 35/40/45 
2. 

mask those people with 1

we wish to identify the poeple died in 

