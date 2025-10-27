
import numpy as np


new_array = np.load('../data/albu_transit/single_year_transit.npy')
result = new_array 
coef = np.array([0.9, 1.1, 1.5 , 1.3 , 1.3, 0.9 , 0.9, 1.1]) 


def map_eth(idx):
    """
    Maps an index to an ethnicity category based on the specified ranges.
    
    Args:
        idx (int): The index to be mapped.
        
    Returns:
        int: The ethnicity category (0 for Chinese, 1 for Indian, 2 for Malay).
    """
    if idx in [0, 1]:
        return 0  # Chinese
    elif idx in [2, 3]:
        return 1  # Indian
    elif idx in [4, 5]:
        return 2  # Malay
    elif idx in [6, 7]:
        return 0  #  use Chn
    
# Define a function to take an array and return a matrix mapping function
def schedule_pre_albuminuria_probability(x_array, idx,A, x0=55, k=0.95):
    
    prob = A + 0.01 / (1 + np.exp(-k * (x_array - x0)))
    return  prob * coef[idx]

def schedule_albuminuria_probability(age_mat, idx):
    """
    Calculate albuminuria probability based on age matrix.

    Parameters:
    age_mat (numpy.ndarray): Input age matrix.
    idx (int): Index to determine ethnicity and gender.

    Returns:
    numpy.ndarray: Albuminuria probability matrix.
    """
    eth = map_eth(idx)  # Map ethnicity
    gen = idx % 2       # Determine gender (0 or 1)
    
    # Calculate albuminuria probability

    # Clip ages > 80 to 80
    # age > 80 ; deal with prob of 80 
    age_mat = np.clip(age_mat, None, 80)



    albuminuria_prob = result[gen, eth, age_mat - 26, 2] 

    # set age < 26 to 0
    albuminuria_prob = np.where(age_mat < 26, 0, albuminuria_prob)
    
    return albuminuria_prob
