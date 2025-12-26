# ckd stages definition
| Stage | Description | eGFR Range (mL/min/1.73 m²) | Clinical Note |
| :--- | :--- | :--- | :--- |
| **G1** | Normal or High | **≥ 90** | Kidney damage present, but filtration is normal. |
| **G2** | Mildly Decreased | **60 – 89** | Mild reduction; requires other signs of damage for CKD diagnosis. |
| **G3a** | Mild to Moderate | **45 – 59** | Mild to moderate loss of function. |
| **G3b** | Moderate to Severe | **30 – 44** | Moderate to severe loss; risk of complications increases. |
| **G4** | Severely Decreased | **15 – 29** | Severe loss; prepare for kidney replacement therapy. |
| **G5** | Kidney Failure | **< 15** | End-Stage Renal Disease (ESRD); dialysis/transplant needed. |

# CKD Modelling Matrix Reference


This note distills how `ckd/analysis/forecast_ckd.py` assembles the matrices that ultimately feed all CKD prevalence calculations. Each list below contains **8 entries**, one per ethnicity/gender cohort defined by `impute_ckd.map_eth_str`:

| idx | cohort tag | persons (`n_people`) |
| --- | ---------- | ------------------- |
| 0 | `chn mal` | 103,903 |
| 1 | `chn fem` | 108,964 |
| 2 | `mal mal` | 21,074 |
| 3 | `mal fem` | 20,487 |
| 4 | `ind mal` | 14,978 |
| 5 | `ind fem` | 13,353 |
| 6 | `mal mal` | 5,789 |
| 7 | `mal fem` | 7,024 |

Common axes:

* `n_sim = 10` Monte-Carlo draws per group/year
* `n_year = 61` covering 1990-2050
* `n_albu = 5` albuminuria forecast cases (used by the matrices that explicitly carry this axis)

## `bmi_matrix_ls`
* **Shape** per group: `(n_sim, n_people, n_year)` e.g. `(10, 103903, 61)`
* **Source**: `future_data_1990_2050/bmi_matrix/bmi_matrix_{i}.npy`
* **Purpose**: BMI trajectories aligned to the age matrix so that BMI-dependent coefficients can be injected into the eGFR regression.

## `age_matrix_ls`
* **Shape** per group: `(n_albu, n_sim, n_people, n_year)`
* **Source**: Originally sourced from demographic projections (`age_matrix_vec_2050`), then modified by `apply_stage_mortality.py`.
* **Logic**: 
  1. **Baseline**: Contains the age of every individual for every year of the simulation (1990–2050).
  2. **Mortality Adjustment**: If an individual dies specifically due to CKD risks (calculated in `apply_stage_mortality`), their age entries for all future years are set to **`-2`**.
  3. **Masking**: Entries for years before an individual is born or after they die of natural causes remain **`-1`**.
* **Purpose**: Provides the "alive mask" for prevalence calculations. Downstream functions filter for `age >= 0` to count the active living population, while distinguishing CKD-specific deaths (`-2`) from natural population exit (`-1`).

## `albu_mat_storage`
* **Shape** per group: `(n_albu, n_sim, n_people, n_year)` e.g. `(5, 10, 103903, 61)`
* **Source**: `future_data_1990_2050/albu_matrix_forecast/albu_mat_group_{i}.npy`
* **Purpose**: Albuminuria (ACR) status forecasts for five severity cases. In `forecast_ckd.py` each case `k in {0,...,4}` is paired with the age/BMI slice to construct a matching eGFR surface and later CKD staging. Values are re-scaled to `{0,0.5,1}` to represent normal, moderate, and severe ACR when needed.

## `diabetes_mat_storage`
* **Shape** per group: `(n_sim, n_people, n_year)`
* **Source**: `future_data_1990_2050/diabetes_matrix/diabetes_mat_{i}.npy`
* **Purpose**: Diabetes status per simulated individual/year. Values take `{0, 0.5, 1}` so that the coefficient block inside the eGFR model can distinguish normoglycemia, pre-diabetes, and diabetes-right-censoring.

## `hypertension_mat_storage`
* **Shape** per group: `(n_sim, n_people, n_year)`
* **Source**: `future_data_1990_2050/hyper_matrix/hypertension_mat_{i}.npy`
* **Purpose**: Hypertension indicator histories aligned with the age/BMI grids so that the systolic burden can enter the eGFR calculation (`hypertension_coefficient = 0.1` in the current logic). Values take `{0,1}`

## `eGFR_matrix_ls`
* **Shape** per group: `(n_albu, n_sim, n_people, n_year)`
* **Construction**: For every albuminuria case `k`, the code iterates through the 10 simulations and evaluates  
  ```
  eGFR = beta0
         + beta1 * age * 0.5
         + beta2 * gender
         + beta3 * age * gender * 0.5
         + beta4 * log(BMI)
         + beta1 * age * 0.1 * hypertension
         + beta1 * age * diabetes_coeff(diabetes)
         + beta1 * age * albu_coeff(albu_case)
         + epsilon (sigma from ethnicity-specific coefficients)
  ```  
  where the appropriate coefficient row is picked via `map_eth_str(idx)`. Any non-existent individuals (age `-1`) are kept at `-1` to preserve masking.
* **Purpose**: Synthetic eGFR surfaces that simultaneously reflect demographic structure, BMI trends, and cardio-metabolic risk factors.

## `stage_matrix_ls`
* **Shape** per group: `(n_albu, n_sim, n_people, n_year)`
* **Source/Logic**: 
  1. **Initial Generation**: Derived directly from `eGFR_matrix_ls` by applying the stage breakpoints `>=90 -> 1`, `60-89 -> 2`, `45-59 -> 3.1`, `30-44 -> 3.2`, `15-29 -> 4`, `<15 -> 5`.
  2. **Mortality Adjustment**: Processed by `apply_stage_mortality.py`. If a simulated individual experiences an excess mortality event driven by their CKD stage (determined by hazard ratios), their stage values for all subsequent years are set to **`-2`**.
  3. **Masking**: Non-existent individuals or those who died of natural causes (non-CKD) remain as **`-1`**.
* **Purpose**: Encodes the KDIGO stage per simulation for downstream prevalence routines. Crucially, it distinguishes between active patients (`>0`), natural mortality/non-existence (`-1`), and CKD-attributed mortality (`-2`).

## `general_ckd_mat_ls`
* **Shape** per group: `(n_albu, n_sim, n_people, n_year)`
* **Construction**: Derived by combining `stage_matrix_ls` and `albu_mat_storage` with the following priority logic:
    1. **CKD Mortality (`-2`)**: If `stage_matrix_ls` is `-2` (indicating death attributed to CKD risk), the entry is set to **`-2`**.
    2. **Natural Mortality / Non-Existence (`-1`)**: If `stage_matrix_ls` is `-1`, the entry remains **`-1`**.
    3. **Active CKD (`1`)**: If the person is alive (not -1/-2) and meets the clinical criteria (`stage >= 3` OR `ACR > 0`), the entry is set to **`1`**.
    4. **Healthy (`0`)**: If the person is alive and does not have CKD (`stage <= 2` AND `ACR == 0`), the entry is set to **`0`**.
* **Purpose**: Serves as a comprehensive status mask for prevalence simulators. Unlike previous versions, it now distinguishes between the active CKD population (`1`), the healthy population (`0`), those who died specifically from CKD complications (`-2`), and those removed due to natural causes/masking (`-1`).

## Shape recap

| Variable | Stored axis order | Example shape |
| -------- | ----------------- | ------------- |
| `bmi_matrix_ls[i]`, `diabetes_mat_storage[i]`, `hypertension_mat_storage[i]` | `(sim, person, year)` | `(10, 103903, 61)` |
| `albu_mat_storage[i]`, `eGFR_matrix_ls[i]`, `stage_matrix_ls[i]`, `general_ckd_mat_ls[i]` | `(albu_case, sim, person, year)` | `(5, 10, 103903, 61)` |

These structures share consistent ordering so that slicing `[k, sim, :, year]` always refers to the same population subset, making the prevalence computations in `simulate_ckd_prevalence` and related helpers straightforward.

# workflow 
## Workflow Overview

The sequence of models and how they flow into each other is as follows:

1. **Age population**

prepare the proper age population 
(troublesome as well)

1. **BMI Model**  
   *Inputs:* Year of Birth, Gender, Ethnicity, Age  
   *Output:* BMI trajectory  
   $$
   \text{BMI Model (Year of Birth, Gender, Ethnicity, Age)} \rightarrow \text{BMI trajectory}
   $$

2. **Albuminuria Model**  
   *Inputs:* Gender, Ethnicity, Age  
   *Output:* Albuminuria incidence  
   $$
   \text{Albuminuria Model (Gender, Ethnicity, Age)} \rightarrow \text{Albuminuria incidence}
   $$

3. **Hypertension Model**  
   *Inputs:* BMI, Gender, Ethnicity, Age  
   *Output:* Hypertension incidence  
   $$
   \text{Hypertension Model (BMI, Gender, Ethnicity, Age)} \rightarrow \text{Hypertension incidence}
   $$

4. **Diabetes Model**  
   *Inputs:* BMI, Gender, Ethnicity, Age  
   *Output:* Diabetes incidence  
   $$
   \text{Diabetes Model (BMI, Gender, Ethnicity, Age)} \rightarrow \text{Diabetes incidence}
   $$

5. **eGFR Model**  
   *Inputs:* Albuminuria incidence, BMI, Hypertension incidence, Diabetes incidence, Gender, Ethnicity, Age  
   *Output:* eGFR trajectory  
   $$
   \text{eGFR Model (Albuminuria, BMI, Hypertension, Diabetes, Gender, Ethnicity, Age)} \rightarrow \text{eGFR trajectory}
   $$

6. **CKD Model**  
   *Inputs:* Albuminuria incidence, eGFR  
   *Output:* CKD incidence  
   $$
   \text{CKD Model (Albuminuria, eGFR)} \rightarrow \text{CKD incidence}
   $$

```bash
python forecast_albu_new.py
python forecast_ckd.py
python hazard.py
python apply_stage_mortality.py
```

# age-specific Mortality adjustment 


1. The Inputs 

Total_Mortality_Table (The Target):


overall_mortality_loaded_df = pd.read_csv("../../data/overall_mortality.csv")
print("Loaded overall_mortality.csv with shape:", overall_mortality_loaded_df.shape)
print(overall_mortality_loaded_df.head())

Index(['sim_year', 'agent_gender', 'agent_age', 'mortality_rate'], dtype='object')

We assume all the ethnicities share the same gender specific mortality parameters. 
##

Hazard_Ratios (The Multipliers):

A dictionary or small list of risk multipliers for each stage.

Example: HR = {Stage1 - 2: 1.0,
 Stage3.1: 1.2, 
 stage3.2: 1.8
 Stage4: 3.2, 
 Stage5: 5.9}.



2. The Logic Flow (The Algorithm)

Step 1:  Initial Guess Base_Mortality to be Total_Mortality_Table. 

Step 2: The "While" Loop Keep looping until the numbers stop changing (Convergence).

Inside the Loop:

A. Run the Model and get prevalence 

Run your simulation using the current Base_Mortality.

Count how many people are in each stage at every age.

Save this as Prevalence_Matrix[Age][Stage].

Example: Prevalence[50][Stage3] = 0.10 (10% of 50-year-olds are Stage 3).

B. Calculate the Correction, and get stage specific mortality

For each Age, calculate the "Correction Factor": Weighted_Risk = (Prev_Stage1 * HR_1) + (Prev_Stage2 * HR_2) + ...

Update the Base Rate: New_Base_Mortality[Age] = Total_Mortality[Age] / Weighted_Risk

C. Check the Difference

Now we have new base_mortality 

Compare New_Base_Mortality vs. Old_Base_Mortality.

If the difference is tiny (e.g., < 0.001), BREAK the loop.

Else, set Old = New and repeat Step A.


## apply stage mortality
```bash
python apply_stage_mortality.py
```

death_events = (stage_survival < survival_draw) & stage_mask

suppose stage_survival rate 0.8
survival_draw 0.9, therefore it does not live successfully. 

	•	Worse health → lower stage_survival
	•	Same survival_draw distribution
	•	Lower survival → more likely to be below the threshold

use survival_draw instead of random number is because we 
assume them already live in this age. 



# for validation purpose 
18 - 74

# for projection purpose 
18 - 85

we would like to get 


# summary plot

get_stage_table_ACR_eGFR.py 

get eGFR * ACR table 
                                      A1                               A2  \
G1     1198490 (73.63%), 1051453 (64.61%)    64483 (3.96%), 187169 (11.5%)   
G2       286584 (17.61%), 236929 (14.56%)      34253 (2.1%), 81095 (4.98%)   
G3a           22864 (1.4%), 17767 (1.09%)        4736 (0.29%), 9751 (0.6%)   
G3b            4170 (0.26%), 3118 (0.19%)       1188 (0.07%), 2247 (0.14%)   
G4               304 (0.02%), 222 (0.01%)          98 (0.01%), 198 (0.01%)   
G5                   29 (0.0%), 21 (0.0%)              8 (0.0%), 19 (0.0%)   
Total  1512441 (92.92%), 1309510 (80.47%)  104766 (6.44%), 280479 (17.24%)   

                                 A3                               Total  
G1       1222 (0.08%), 5404 (0.33%)  1264195 (77.67%), 1244026 (76.45%)  
G2      5140 (0.32%), 18775 (1.15%)     325977 (20.03%), 336799 (20.7%)  
G3a      2205 (0.14%), 7207 (0.44%)        29805 (1.83%), 34725 (2.13%)  
G3b      1152 (0.07%), 3518 (0.22%)           6510 (0.4%), 8883 (0.55%)  
G4        452 (0.03%), 1332 (0.08%)           854 (0.05%), 1752 (0.11%)  
G5        348 (0.02%), 1042 (0.06%)           385 (0.02%), 1082 (0.07%)  