import numpy as np

def schedule_hypertension_probability(age, index, bmi, theta=None):
    """
    Set parameters for each individual based on ethnicity and gender (given by index).
    Logistic regression portion:
    
        alpha = 0.08207898
        beta = 0.10498145
        theta = [-8.210539, -8.380487, -8.030455, -8.065594, -8.352823, -8.645856, -8.071825, -8.254004]
        
        hyperprob = 1 - 1/(1 + exp(theta[index] + alpha * age + beta * bmi))
    
    In this implementation, we assume that `bmi` is a matrix and `age` is a matrix of the same shape.
    """
    alpha = 0.08207898 * 0.9
    beta = 0.10498145
    if theta is None:
        theta = np.array([-8.210539 * 0.92, -8.380487 * 0.95, -8.030455 * 0.95, -8.065594 * 0.99,
                          -8.352823 * 0.93, -8.645856, -8.071825, -8.254004]) * 1.2

    # Initialize the output array
    hyperprob = np.zeros_like(age, dtype=float)

    # Set probabilities to 0 for age < 10
    hyperprob[age < 10] = 0.0

    # For age > 55, use adjusted alpha
    mask_55 = (age > 55)
    alpha_55 = 0.08207898 * 0.75
    exp_term_55 = np.exp(theta[index] + alpha_55 * age[mask_55] + beta * bmi[mask_55])
    hyperprob[mask_55] = 1 - 1 / (1 + exp_term_55)

    # For 10 <= age <= 55, use default alpha
    mask_default = (age >= 10) & (age <= 55)
    exp_term_default = np.exp(theta[index] + alpha * age[mask_default] + beta * bmi[mask_default])
    hyperprob[mask_default] = 1 - 1 / (1 + exp_term_default)

    return hyperprob