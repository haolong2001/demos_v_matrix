#%%
from Age_BMI_loading import (
    age_matrix_vec_2050,
)
import os
import numpy as np
from impute_ckd import *

from prevalence_3d import *



#%% load diabetes matrix

from prevalence import *
diabetes_mat_storage = []
for i in range(8):
    diabetes_mat = np.load(f'../future_data_1990_2050/diabetes_matrix/diabetes_mat_{i}.npy')
    print(f"Loaded: diabetes_mat_{i}.npy with shape {diabetes_mat.shape}")
    diabetes_mat_storage.append(diabetes_mat)


#%% get diabetes prevalence
year = [2010,2017,2020,2021]

get_overall_prevalence_3d(age_matrix_vec_2050, diabetes_mat_storage, -28)
# %%
