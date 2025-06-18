# define a mapping function here 


prob_matrix_age_90 = np.zeros((2, 8, 2, 71))
A_range = [0.001, 0.005]
coef = [1.14, 0.94, 1.86,1.66, 1.76,1.56, 1.86,1.66]


for idx in range(8):
    for A_idx, A in enumerate(A_range):
        for x_idx, x in enumerate(range(20, 91)):
            prob = logistic_function(x, A)
            
            # store the prob in a matrix 
            prob_matrix_age_90[0,idx,A_idx,x_idx] = prob * coef[idx]

# for albu == 2
for idx in range(8):
    eth = map_eth(idx)
    gen = idx % 2
    for x_idx, x in enumerate(range(20,91)):
        if x >= 26 and x <= 74:
            prob_2 = result[gen, eth, x - 26, 2] 
        if x >= 74:
            prob_2 = result[gen, eth, 54, 2] 
        else:
            prob_2 = 0
        prob_matrix_age_90[1,idx,:,x_idx] = prob_2 * coef[idx]


# Define the logistic function
def logistic_function(x, A=0.005, x0=55, k=0.95):
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
        return 1  # Indian
    elif idx in [4, 5]:
        return 2  # Malay
    elif idx in [6, 7]:
        return 0  #  use Chn

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