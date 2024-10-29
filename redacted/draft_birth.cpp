
        start = 0;
        length = births.length() // of length 20
        arraybirths = 0 of size (1991 - 2008)*(2006 - 2023);
        // 1991 - (2023 - 15) should be the end year 
        // simplify 
    
        
        for (i = 0; i < births.size(); i++ ){
            num = births[i];
            mig = i + 1 // mig index in existing matrix 
            // mig also serve as the colindex in the arraybirths 
            if (mig  + 15 <= 33){
                // when 15 ages out of boundary
                ArrayXXi Newborn = ExistingMatrix.block(
                    start, mig + 15, num, 33 - (mig + 15) + 1;
                )

                // should be same shape as Newborn  
                for col in Newborn.cols(){
                    for row in NewBorn.rows
                    age = Newborn(row,col)
                    year_idx = mig + 15;
                    fer = MapFer(year_idx, age);
                    ferMat(row,col) = fer
                }
                // initialize a random array
                std::random_device rd;
                std::mt19937 urng(rd());
                ArrayXXf random_values = ArrayXXf::Random(num, ncols - i).unaryExpr([](float val) { return (val + 1.0f) / 2.0f; });

                birthMat = (ferMat < random_values).cast<int>();

                // from birthMat  generate age matrix , and then add the female births to the queue
                newnewborn = birthMat.cols().sum();
                // (20, 30, 40) * 1.0 / 2.06
                females = newnewborn * 1.0/ 2.06 .cast<int>;

                // 
                arraybirths[mig,:] = females
            }



        }
         totalFemales = arraybirth.col.sum()
         birth_queue.pushback(totalFemales)
         start_year = start_year + 15  // when the females go to age 15 
      


        //initialize a queue;
        // birth_queue 
        // births is from  1990 to end_year - 15 
        birth_start = 1990 + 15; 
        birth_end = 2023;
        birth_queue.add(births)
        while (!birth_queue.empty()){
            // use queue to generate death and birth matrix 
            // births from  year_a to year_b if not exist 
            // add back to birth_queue  
            generate(births, start, end)


        }

    

        // # use ages to get death matrix as well; in this step, also get death numbers for each age strata  
        // death
        // # initialize the age matrix 
        // # initialize the fertility matrix 
        // for year in 1991 : 2023 
        //     # get age strucutre and fertility as well
        //     # calculate the data gap 
        //     # add / delete data 
        //     # get this year s data structure 
        //     # next_year_age = ...