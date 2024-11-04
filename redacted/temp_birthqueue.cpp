// Assuming necessary headers are included and using the Eigen namespace



// input: the births generate from the original females 
// 





#include <fstream>
#include <Eigen/Dense>
#include <vector>
#include <random>
#include <iostream>

using namespace Eigen;

void generateAgefromBirth(int eth_gen, const Eigen::ArrayXi& birthvec, Eigen::ArrayXXi& AgeMatrix, const std::vector<Eigen::ArrayXXf>& disappear_mat, std::mt19937& urng) {
    int ncols = birthvec.size();
    int beginning = 34 - ncols;
    int start = 0;

    std::uniform_real_distribution<float> dist(0.0f, 1.0f);

    for (int i = 0; i < ncols; ++i, ++beginning) {
        int num = birthvec[i];
        int age_length = 34 - beginning;

        // Create age sequence from 0 to (age_length - 1)
        Eigen::ArrayXi age_seq = Eigen::ArrayXi::LinSpaced(age_length, 0, age_length - 1);

        // Replicate the age sequence 'num' times along rows
        Eigen::ArrayXXi tempage = age_seq.transpose().replicate(num, 1);

        // Get mortality matrix for the current group
        Eigen::ArrayXXf mor_vec = disappear_mat[eth_gen].block(start, beginning, num, age_length);

        // Generate random matrix for comparison
        Eigen::ArrayXXf rand_matrix(num, age_length);
        for (int m = 0; m < num; ++m) {
            for (int n = 0; n < age_length; ++n) {
                rand_matrix(m, n) = dist(urng);
            }
        }

        // Determine if individuals disappear based on mortality rates
        Eigen::ArrayXXi disappear = (mor_vec <= rand_matrix).cast<int>();

        // Update AgeMatrix with the ages where individuals are still alive
        AgeMatrix.block(start, beginning, num, age_length) = disappear * tempage;

        // Update the starting row index for the next group
        start += num;
    }
}

int MapFer(int year_idx, int age){
    if (age == -1){
        return 0;
    }
    else {
        return 0.5;
    }
}

void simulatePopulation( const ArrayXi& births,int eth_gen, std::vector<std::vector<MatrixXi>>& matrices) {
    const int simulationEndYear = 2023;
    const int childbearingStartAge = 15;
    const int maxAgeConsidered = 33;
    int birth_start = 1991;
    const int birth_end = simulationEndYear - 15;

    ArrayXi newnewborn = births;

    Eigen::ArrayXf males = newnewborn.cast<float>() * 1.06f / 2.06f;
        Eigen::ArrayXf females = newnewborn.cast<float>() * 1.0f / 2.06f;

        Eigen::ArrayXi males_int = males.cast<int>();
        Eigen::ArrayXi females_int = females.cast<int>();

        ArrayXXi malebirthAge = generateAgefromBirth(males_int); // Implement this function
        ArrayXXi femalebirthAge = generateAgefromBirth(females_int); // Implement this function

        matrices[eth_gen - 1].push_back(malebirthAge);
        matrices[eth_gen].push_back(femalebirthAge);

    while(birth_start <= simulationEndYear - childbearingStartAge){

        int nrows = femalebirthAge.rows(); // Number of cohorts
        int ncols = simulationEndYear - (birth_start + childbearingStartAge) + 1; // Years they can give birth
        
        ArrayXXi arraybirths = ArrayXXi::Zero(nrows, ncols);


        int startCol = ncols;
        // get the 15+ 
        ArrayXXi Newborn = femalebirthAge.block(
                0,startCol,femalebirthAge.rows(),33- ncols
             );
        // initialize the fertility matrix 
            ArrayXXi ferferMat = ArrayXXi of same shape as Newborn;
            for (int col = 0; col < Newborn.cols(); ++col) {
                for (int row = 0; row < Newborn.rows(); ++row) {
                    int age = Newborn(row, col);
                    int year_idx = birth_start + childbearingStartAge + col - 1990;
                    ferferMat(row, col) = MapFer(year_idx, age);
                }
            }

            // Generate random values between 0 and 1
            std::random_device rd;
            std::mt19937 urng(rd());
            std::uniform_real_distribution<float> dist(0.0f, 1.0f);
            ArrayXXf random_values = ArrayXXf::NullaryExpr(femalebirthAge.rows(), ncols, [&]() { return dist(urng); });

            ArrayXXi birthMat = (ferferMat.cast<float>().array() < random_values.array()).cast<int>();
            int newnewborn = birthMat.colwise().sum();

            Eigen::ArrayXf males = newnewborn.cast<float>() * 1.06f / 2.06f;
            Eigen::ArrayXf females = newnewborn.cast<float>() * 1.0f / 2.06f;

            Eigen::ArrayXi males_int = males.cast<int>();
            Eigen::ArrayXi females_int = females.cast<int>();

            ArrayXXi malebirthAge = generateAgefromBirth(males_int); // Implement this function
            ArrayXXi femalebirthAge = generateAgefromBirth(females_int); // Implement this function

            matrices[eth_gen - 1].push_back(malebirthAge);
            matrices[eth_gen].push_back(femalebirthAge);
          

            // begin the next round
            // int totalFemales = arraybirths.colwise().sum();
            // birth_queue.pop();
            // birth_queue.push_back(totalFemales);
            birth_start += childbearingStartAge;
        }
        
    }
    }
}

// do an example test using births arrayxi (1,1,1..) of length (2023 - 1991)
// std::vector<std::shared_ptr<Eigen::MatrixXd>> matrices;
//print the final result matrices[i] one by one into a logging file.
        



