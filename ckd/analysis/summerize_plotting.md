From apply_stage_mortality.py, we have 

np.save(OUTPUT_DIR / f"stage_matrix_group_{idx}.npy", adjusted_stage)
np.save(OUTPUT_DIR / f"age_matrix_group_{idx}.npy", adjusted_age)

in summerize_plotting.py

let's replace the input ckd_matrix and age_matrix_vec_2050 with these 


in this file, I wish to 

1. have the plots vs nphs;
2. we would also like to extend the plot from 1990 - 2023. 

