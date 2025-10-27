def get_prevalence_3d(age_matrix_vec, diabetes_mat_list, k):
    """
    Calculate diabetes prevalence for each ethnicity-gender group and age-specific prevalence.

    Parameters:
        age_matrix_vec (list): List of age matrices for different groups.
        diabetes_mat_list (list): List of diabetes matrices for different groups.
        k (int): Column index to use for ages in age_matrix_vec.

    Returns:
        numpy.ndarray: Final diabetes prevalence results.
    """
    import numpy as np

    # Define age groups
    age_groups = [(18, 29), (30, 39), (40, 49), (50, 59), (60, 69), (70, 74)]

    # Initialize matrices for diabetes
    diabetes_total_counts_mat = np.zeros((8, 6))  # Number of people in each age group
    diabetes_counts_mat = np.zeros((8, 6))  # Number of diabetic people in each age group
    diabetes_prevalence_ls = []  # Prevalence for each ethnicity-gender group

    # Iterate over each ethnicity-gender group
    for idx in range(8):
        last_col_ages = age_matrix_vec[idx][:, :, k]  # Column k of age matrix
        last_col_diabetes = diabetes_mat_list[idx][:, :, k]  # Column k of diabetes matrix

        # Compute overall diabetes prevalence for idx
        mask_all = (last_col_ages >= 18) & (last_col_ages <= 74)
        total_people = np.sum(mask_all)
        diabetic_people = np.sum(last_col_diabetes[mask_all] == 1)

        # Store diabetes prevalence (avoid division by zero)
        diabetes_prevalence_ls.append(diabetic_people / total_people if total_people > 0 else 0)

        # Assign people to age groups and count
        for group_idx, (lower, upper) in enumerate(age_groups):
            mask = (last_col_ages >= lower) & (last_col_ages <= upper)

            diabetes_total_counts_mat[idx, group_idx] = np.sum(mask)  # Total people in age group
            diabetes_counts_mat[idx, group_idx] = np.sum(last_col_diabetes[mask] == 1)  # Diabetic people in age group

    # Exclude "others" if necessary
    diabetes_prevalence_ls = diabetes_prevalence_ls[:6]

    # Compute age-specific diabetes prevalence
    diabetes_age_specific_prevalence = np.divide(
        diabetes_counts_mat.sum(axis=0),
        diabetes_total_counts_mat.sum(axis=0),
        out=np.zeros_like(diabetes_counts_mat.sum(axis=0)),  # Avoid division by zero
        where=diabetes_total_counts_mat.sum(axis=0) > 0
    )

    # Concatenate the final results for diabetes
    diabetes_final_result = np.concatenate([diabetes_prevalence_ls, diabetes_age_specific_prevalence])

    # Print the results for debugging
    
    print(f"diabetes_prevalence_ls: {diabetes_prevalence_ls}")
    print(f"diabetes_age_specific_prevalence: {diabetes_age_specific_prevalence}")
    return diabetes_final_result


def get_pre_prevalence_3d(age_matrix_vec, diabetes_mat_list, k):
    """
    Calculate diabetes prevalence for each ethnicity-gender group and age-specific prevalence.

    Parameters:
        age_matrix_vec (list): List of age matrices for different groups.
        diabetes_mat_list (list): List of diabetes matrices for different groups.
        k (int): Column index to use for ages in age_matrix_vec.

    Returns:
        numpy.ndarray: Final diabetes prevalence results.
    """
    import numpy as np

    # Define age groups
    age_groups = [(18, 29), (30, 39), (40, 49), (50, 59), (60, 69), (70, 74)]

    # Initialize matrices for diabetes
    diabetes_total_counts_mat = np.zeros((8, 6))  # Number of people in each age group
    diabetes_counts_mat = np.zeros((8, 6))  # Number of diabetic people in each age group
    pre_diabetes_prevalence_ls = []  # Prevalence for each ethnicity-gender group

    # Iterate over each ethnicity-gender group
    for idx in range(8):
        last_col_ages = age_matrix_vec[idx][:, :, k]  # Column k of age matrix
        last_col_diabetes = diabetes_mat_list[idx][:, :, k]  # Column k of diabetes matrix

        # Compute overall diabetes prevalence for idx
        mask_all = (last_col_ages >= 18) & (last_col_ages <= 74)
        total_people = np.sum(mask_all)
        pre_diabetic_people = np.sum(last_col_diabetes[mask_all] == 0.5)

        # Store diabetes prevalence (avoid division by zero)
        pre_diabetes_prevalence_ls.append(pre_diabetic_people / total_people if total_people > 0 else 0)

        # Assign people to age groups and count
        for group_idx, (lower, upper) in enumerate(age_groups):
            mask = (last_col_ages >= lower) & (last_col_ages <= upper)

            diabetes_total_counts_mat[idx, group_idx] = np.sum(mask)  # Total people in age group
            diabetes_counts_mat[idx, group_idx] = np.sum(last_col_diabetes[mask] == 1)  # Diabetic people in age group

    # Exclude "others" if necessary
    pre_diabetes_prevalence_ls = pre_diabetes_prevalence_ls[:6]

    # Compute age-specific diabetes prevalence
    diabetes_age_specific_prevalence = np.divide(
        diabetes_counts_mat.sum(axis=0),
        diabetes_total_counts_mat.sum(axis=0),
        out=np.zeros_like(diabetes_counts_mat.sum(axis=0)),  # Avoid division by zero
        where=diabetes_total_counts_mat.sum(axis=0) > 0
    )

    # Concatenate the final results for diabetes
    pre_diabetes_final_result = np.concatenate([pre_diabetes_prevalence_ls, diabetes_age_specific_prevalence])

    

    return pre_diabetes_final_result



def get_overall_prevalence_3d(age_matrix_vec, diabetes_mat_list, k):
    """
    Calculate overall diabetes prevalence for each ethnicity-gender group in age range 18-74.

    Parameters:
        age_matrix_vec (list): List of age matrices for different groups.
        diabetes_mat_list (list): List of diabetes matrices for different groups.
        k (int): Column index to use for ages in age_matrix_vec.

    Returns:
        numpy.ndarray: Overall diabetes prevalence for each ethnicity-gender group (18-74 age range).
    """
    import numpy as np

    # Initialize accumulators for total counts across all groups
    total_diabetic_people = 0
    total_people = 0
    
    # Iterate over each ethnicity-gender group
    for idx in range(8):
        last_col_ages = age_matrix_vec[idx][:, :, k]  # Column k of age matrix
        last_col_diabetes = diabetes_mat_list[idx][:, :, k]  # Column k of diabetes matrix

        # Compute overall diabetes prevalence for idx in age range 18-74
        mask_all = (last_col_ages >= 18) & (last_col_ages <= 74)
        group_total_people = np.sum(mask_all)
        group_diabetic_people = np.sum(last_col_diabetes[mask_all] == 1)

        # Accumulate counts across all groups
        total_diabetic_people += group_diabetic_people
        total_people += group_total_people
        
    # Calculate overall diabetes prevalence (avoid division by zero)
    diabetes_prevalence = total_diabetic_people / total_people if total_people > 0 else 0
    
    # Return overall prevalence across all ethnicities
    return diabetes_prevalence



def get_overall_pre_prevalence_3d(age_matrix_vec, diabetes_mat_list, k):
    """
    Calculate overall diabetes prevalence for each ethnicity-gender group in age range 18-74.

    Parameters:
        age_matrix_vec (list): List of age matrices for different groups.
        diabetes_mat_list (list): List of diabetes matrices for different groups.
        k (int): Column index to use for ages in age_matrix_vec.

    Returns:
        numpy.ndarray: Overall diabetes prevalence for each ethnicity-gender group (18-74 age range).
    """
    import numpy as np

    # Initialize list for diabetes prevalence
    # Initialize accumulators for total counts across all groups
    total_diabetic_people = 0
    total_people = 0
    
    # Iterate over each ethnicity-gender group
    for idx in range(8):
        last_col_ages = age_matrix_vec[idx][:, :, k]  # Column k of age matrix
        last_col_diabetes = diabetes_mat_list[idx][:, :, k]  # Column k of diabetes matrix

        # Compute overall diabetes prevalence for idx in age range 18-74
        mask_all = (last_col_ages >= 18) & (last_col_ages <= 74)
        group_total_people = np.sum(mask_all)
        group_diabetic_people = np.sum(last_col_diabetes[mask_all] == 0.5)

        # Accumulate counts across all groups
        total_diabetic_people += group_diabetic_people
        total_people += group_total_people
        
    # Calculate overall diabetes prevalence (avoid division by zero)
    diabetes_prevalence = total_diabetic_people / total_people if total_people > 0 else 0
    
    # Return overall prevalence across all ethnicities
    return diabetes_prevalence