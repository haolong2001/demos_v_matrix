
analysis/results_df folder

RESULTS_DIR / "nphs_overlap_gender_race.png"
RESULTS_DIR / "comorbidities_overlap.png"
"nphs_overlap_age_strata.csv"
 RESULTS_DIR / "nphs_overlap_age_strata.png"


MORTALITY_DIR

the ckd stages matrices and 
age matrices are stored here

def load_stage_matrices() -> list[np.ndarray]:
    return [np.load(MORTALITY_DIR / f"stage_matrix_group_{idx}.npy") for idx in range(8)]


def load_age_matrices() -> list[np.ndarray]:
    return [np.load(MORTALITY_DIR / f"age_matrix_group_{idx}.npy") for idx in range(8)]
