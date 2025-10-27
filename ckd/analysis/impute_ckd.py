import numpy as np

coefficients = {
    'chn mal': np.array([130.84 , -0.4671, 14.9112, 0, -5.3749 , 13.3742], dtype=object),
    'chn fem':np.array([130.84, -0.4671, 14.9112, -0.2066, -5.3749, 13.3742], dtype=object),
    'ind mal': np.array([118.31, -0.3034, 19.8534, 0, -4.6831, 14.4905], dtype=object),
    'ind fem': np.array([118.31, -0.3034, 19.8534, 0, -4.6831 , 14.4905], dtype=object),
    'mal mal': np.array([121.98, -0.3741, 18.7098, 0, -4.5513, 14.2774], dtype=object),
    'mal fem': np.array([121.98, -0.3741, 18.7098, -0.2948, -4.5513, 14.2774], dtype=object)
}

print(coefficients)

def map_eth_str(idx):
    ethnic_keys = ['chn mal','chn fem','mal mal','mal fem','ind mal','ind fem','mal mal','mal fem']  # Mapping indices to dictionary keys
    return ethnic_keys[idx ]