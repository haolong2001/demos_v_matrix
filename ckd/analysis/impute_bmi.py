import numpy as np
from scipy.stats import norm
# Assuming bmitable.csv is in the current directory
file_path = '../data/bmitable.csv'

# Load the CSV file into a numpy array
bmitable = np.genfromtxt(file_path, delimiter=',', skip_header=1)

# Display the shape of the array (optional)
print("Shape of bmitable:", bmitable.shape)



def calculate_bmi(ages, yearborn, index, bmitable, height=170.0):
    """
    Calculate BMI based on age, year of birth, index, and a BMI table.

    Parameters:
        ages (int): The age of the individual.
        yearborn (int): The year the individual was born.
        index (int): The index used to access specific rows in the bmitable.
        bmitable (numpy.ndarray): A 2D array containing the necessary coefficients and hyperparameters.
        height (float): The height of the individual in centimeters (default is 170 cm).

    Returns:
        float: The calculated BMI value.
    """
    # Generate random numbers from a normal distribution
    rng = norm.rvs(loc=0, scale=1, size=4)

    # Calculate hyperparameters
    M1 = bmitable[index, 0] + bmitable[index, 6] * rng[0]
    M2 = bmitable[index, 1] + bmitable[index, 7] * rng[0] + bmitable[index, 8] * rng[1]
    M3 = bmitable[index, 2] + bmitable[index, 9] * rng[0] + bmitable[index, 10] * rng[1] + bmitable[index, 11] * rng[2]
    M4 = bmitable[index, 3] + bmitable[index, 12] * rng[0] + bmitable[index, 13] * rng[1] + bmitable[index, 14] * rng[2] + bmitable[index, 15] * rng[3]

    # Calculate coefficients
    y0 = M2 + bmitable[index, 4] * (yearborn - 1950) + M1 * (35 - 18)
    y1 = M2 + bmitable[index, 4] * (yearborn - 1950)
    y2 = M2 + bmitable[index, 4] * (yearborn - 1950) + M3 * (55 - 35)
    y3 = M2 + bmitable[index, 4] * (yearborn - 1950) + M3 * (55 - 35) + M4 * (75 - 55)
    m1 = 6 * (0.014492754 * ((y2 - y1) / 20 - (y1 - y0) / 17) - 0.003623188 * ((y3 - y2) / 20 - (y2 - y1) / 20))
    m2 = 6 * (-0.003623188 * ((y2 - y1) / 20 - (y1 - y0) / 17) + 0.013405797 * ((y3 - y2) / 20 - (y2 - y1) / 20))
    b0 = (y1 - y0) / 17 - 17 / 6 * m1
    b1 = (y2 - y1) / 20 - 10 * m1 - 20 / 6 * (m2 - m1)
    b2 = (y3 - y2) / 20 - 10 * m2 + 20 / 6 * m2
    d0 = m1 / (6 * 17)
    d1 = (m2 - m1) / (6 * 20)
    d2 = (-m2) / (6 * 20)

    # Calculate BMI based on age
    # Define conditions
    cond1 = ages > 80
    cond2 = (ages >= 55) & (ages <= 80)
    cond3 = (ages >= 35) & (ages < 55)
    cond4 = (ages >= 0) & (ages < 35)
    cond6 = ages == -1

    # Define corresponding calculations for each condition
    bmi_values = np.select(
        [cond1, cond2, cond3, cond4],# cond6
        [
            0,  # Condition: age > 80
            y2 + b2 * (ages - 55) + d2 * np.power(ages - 55, 3) + m2 / 2 * np.power(ages - 55, 2),
            y1 + b1 * (ages - 35) + d1 * np.power(ages - 35, 3) + m1 / 2 * np.power(ages - 35, 2),
            y0 + b0 * (ages - 18) + d0 * np.power(ages - 18, 3),
            # y0 + b0 * (18 - 18) + d0 * np.power(18 - 18, 3),
            # -1  # Condition: age == -1
        ],
        default=np.nan  # Optional: handle unexpected cases with NaN
    )

    # Apply random noise to the BMI value
    #thisbmi = np.exp(norm.rvs(loc=thisbmi, scale=bmitable[index, 5], size=1)[0])
    scales = bmitable[index, 5]  # Get scale values for the corresponding row

    # Generate random samples from normal distribution and apply exponential transformation
   # bmi_transformed = np.exp(norm.rvs(loc=bmi_values, scale=scales, size=bmi_values.shape))
    bmi_transformed = np.where(ages == -1, -1, np.exp(norm.rvs(loc=bmi_values, scale=scales, size=bmi_values.shape)))

    return bmi_transformed


def apply_bmi(row, idx):
    """Compute BMI using calculate_bmi, with yearborn based on the first nonzero index."""
    first_nonzero_idx = np.where(row >= 0)[0][0] # Find first nonnegative index
    first_nonzero_value = row[first_nonzero_idx]
    yearborn = 1989 + first_nonzero_idx - first_nonzero_value
    
    bmi_values = calculate_bmi(row, yearborn, idx, bmitable) 
    # print(f"Shape of returned BMI values: {bmi_values.shape}") 
    # print(f"year: {yearborn}")
    return calculate_bmi(row, yearborn, idx, bmitable)  # Use idx instead of 0