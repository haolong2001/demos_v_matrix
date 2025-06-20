# define a mapping function here 
import numpy as np


# Define the logistic function
def micro_function(x, A=0.005, x0=55, k=0.95):
    L = A + 0.01
    return A + (L - A) / (1 + np.exp(-k * (x - x0)))

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
        return 1  # Malay
    elif idx in [4, 5]:
        return 2  #Indian 
    elif idx in [6, 7]:
        return 1  #  use Malay as approximation

def accumulated_prob(ages, idx, A_idx, level): # level = 0 or 1
    # Handle array of ages
    probs = np.zeros(len(ages))
    for i, age in enumerate(ages):
        if level == 1:
            if age < 20:
                probs[i] = 0
            elif age >= 85:
                probs[i] = micro_albu_age_90[idx, A_idx, -1]
            else:
                age_idx = age - 20  # Convert age to index (age 20 maps to index 0)
                probs[i] = micro_albu_age_90[idx, A_idx, age_idx]
        else:  # level == 2
            if age < 20:
                probs[i] = 0
            elif age >= 85:
                probs[i] = healthy_prob_age_90[idx, A_idx, -1]
            else:
                age_idx = age - 20  # Convert age to index (age 20 maps to index 0)
                probs[i] = healthy_prob_age_90[idx, A_idx, age_idx]
    return probs



result = np.load('../data/albu_transit/single_year_transit.npy')
A_range = [0.001, 0.005]
coef = [1.0, 0.9,2.0,1.5,1.8,1.2, 2.0,1.5]# hyper parameters


prob_matrix_age_90 = np.zeros((2, 8, 2, 71))
# Initialize probability matrices for age 90

for idx in range(8):
    for A_idx, A in enumerate(A_range):
        for x_idx, x in enumerate(range(20, 91)):
            prob = micro_function(x, A)
            
            # store the prob in a matrix 
            prob_matrix_age_90[0,idx,A_idx,x_idx] = prob * coef[idx]

# for albu == 2
for idx in range(8):
    eth = map_eth(idx)
    gen = idx % 2
    for x_idx, x in enumerate(range(20,91)):
        if x >= 26 and x <= 74:
            prob_2 = result[gen, eth, x - 26, 2] 
        elif x > 74:
            prob_2 = result[gen, eth, 54, 2] 
        else:
            prob_2 = 0
        prob_matrix_age_90[1,idx,:,x_idx] = prob_2 * coef[idx]




# this is the accumulated probability matrix 
# Calculate probabilities for all groups

healthy_prob_age_90 = np.zeros((8, 2, 71))  # Shape: 8 groups x 2 A values x 71 ages (20-90)
micro_albu_age_90 = np.zeros((8, 2, 71))    # Shape: 8 groups x 2 A values x 71 ages (20-90)


for idx in range(8):
    for A_idx, A in enumerate(A_range):
        for age_idx in range(71):  # age 20 to 90
            transition_prob = prob_matrix_age_90[0, idx, A_idx, age_idx]  # a → b
            
            if age_idx == 0:
                # For age 20, just use initial probability of staying healthy
                healthy_prob_age_90[idx, A_idx, age_idx] = 1 - transition_prob
            else:
                # For subsequent ages, multiply previous probability by probability of staying healthy
                healthy_prob_age_90[idx, A_idx, age_idx] = healthy_prob_age_90[idx, A_idx, age_idx-1] * (1 - transition_prob)

# Calculate probability of being in microalbuminuria (state b)
for idx in range(8):
    for A_idx, A in enumerate(A_range):
        prob_in_b = 0.0
        for age_idx in range(71):  # age 20 to 90
            if age_idx == 0:
                # For age 20, just use initial transition probability
                inflow = prob_matrix_age_90[0, idx, A_idx, age_idx]
            else:
                # Inflow from a → b in current age
                inflow = healthy_prob_age_90[idx, A_idx, age_idx-1] * prob_matrix_age_90[0, idx, A_idx, age_idx]
            
            # Surviving from previous b state (did not go to c)
            prob_in_b = prob_in_b * (1 - prob_matrix_age_90[1, idx, A_idx, age_idx]) + inflow
            
            # Store result
            micro_albu_age_90[idx, A_idx, age_idx] = prob_in_b