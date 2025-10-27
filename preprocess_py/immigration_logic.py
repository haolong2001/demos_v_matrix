ages = np.arange(0, 85)
fertility_ages = range(15, 50)
for i in [1,0,3,2,5,4,7,6]: # deal with female first, then male 
    # get 2023 population
    popu_2023 = scaled_popu[i][:,-1] # last column
    future_popu[i,:,0] = popu_2023
    ## print(np.sum(immigration_rates[i], axis=0))

    for j in range(1,28): # 2024 to 2050

        immi_rate = np.array([
            np.random.uniform(low, high) 
            for low, high in uniform_params[i]
        ])

        
        # for the other ages (2, 18, 27)
        
        is_female = i % 2  # 1 is female, 0 is male
        year_index = j-1 # index 0 is year 2024
        # this is for mortality rate of 1 - 84
        mortaility_rates = mortality_forecast_from_24[is_female, ages // 5, j-1] / 1000.
        
        # age 0 - 84 --> 1 -- （85）, then experience death this year
        future_popu[i,1:86,j]=  (future_popu[i,0:85,j-1] * (1- mortaility_rates)).astype(int)

        # for 85 and 85+, add those people are still alive 
        mortaility_rate = mortality_forecast_from_24[is_female, 85 // 5, j-1] / 1000.
        future_popu[i,85,j] = (future_popu[i,85,j-1] * (1-mortaility_rate)).astype(int) +  future_popu[i,85,j]

        # then calculate immigration people
        
        future_immigration[i,:,j-1] = (future_popu[i,1:51,j] * immi_rate).astype(int)

        # add immigration back 
        future_popu[i,1:51,j] += future_immigration[i,:,j-1]

        # deal wtih fertility
        if i % 2 == 1:
            year = 2023 + j
            rates = [map_fertility_rate(i // 2, year, age, fertility_matrix) for age in fertility_ages]

            births = future_popu[i,15:50,j] * rates
            boys = (births * 1/ (1+ 1.06) ).astype(int)
            girls = (births - boys).astype(int)
            future_popu[i,0,j] =  np.sum(girls)
            future_popu[i-1,0,j] = np.sum(boys)

            # use the gender ratio to determine boys and girls

        
