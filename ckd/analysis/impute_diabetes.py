import numpy as np


def schedule_pre_diabetes_probability(age_mat, i, bmi_mat):
    beta = 0.18
    theta = np.array([
        -10.73568597 * 1.01,
        -11.11297803 * 0.98,
        -10.594319 * 1.02,
        -10.97161203 * 1.02,
        -10.15266278 * 1.0,
        -10.52995483 * 1.02,
        -10.73568597,
        -11.11297803
    ])
    
    # age = np.asarray(age)
    # bmi = np.asarray(bmi)
    
    # Create the output array
    prob = np.zeros_like(age_mat, dtype=float)
    
    # Set invalid values first
    prob[age_mat == -1] = -1
    
    # Set <18 to 0
    prob[(age_mat < 18) & (age_mat != -1)] = 0
    
    # Set 18 <= age < 25 to 0.0001
    mask_18_25 = (age_mat >= 18) & (age_mat < 25)
    prob[mask_18_25] = 0.002
    
    # For age >= 25, apply logistic regression formula
    mask = (age_mat >= 25) 
    
    alpha = np.where(age_mat[mask] < 70, 0.045, 0.04)
    linear_term = theta[i] + alpha * age_mat[mask] + beta * bmi_mat[mask]
    prob[mask] = 1 - 1 / (1 + np.exp(linear_term))
    
    return prob


def schedule_diabetes_probability(age_mat, i, bmi_mat):
    beta = 0.19
    theta = np.array([
        -10.73568597 * 1.0,
        -11.11297803 * 0.97,
        -10.59431997 * 1.,
        -10.971612 * 1.01,
        -10.15266278 * 1.0,
        -10.52995483 * 1.03,
        -10.59431997 * 1.01,
        -10.971612 * 1.01,
    ])
    
    # Create the output array
    prob = np.zeros_like(age_mat, dtype=float)
    
    # Set invalid values first
    prob[age_mat == -1] = -1
    
    # Set <25 to 0.00015
    mask_25 = (age_mat < 25) & (age_mat != -1)
    prob[mask_25] = 0.002
    
    # For age >= 25, apply logistic regression formula
    mask = (age_mat >= 25)
    
    alpha = np.where(age_mat[mask] < 70, 0.045, 0.035)
    linear_term = theta[i] + alpha * age_mat[mask] + beta * bmi_mat[mask]
    prob[mask] = 1 - 1 / (1 + np.exp(linear_term))
    
    return prob