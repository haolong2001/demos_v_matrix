
#include <iostream>
#include <vector>
#include <random>
#include <algorithm>
#include <Eigen/Dense>
using namespace std;



std::vector<int> batchDeathRate_general(Eigen::ArrayXi ages) {
    // Manually create a row vector [0, 1, 2, ..., 9] because LinSpaced is for floating-point types
    Eigen::ArrayXi arrange(10,1);
    for (int i = 0; i < 10; ++i) {
        arrange(i) = i;
    }

    // Broadcasting in Eigen: Create a matrix where each row is ages + arrange
    Eigen::ArrayXXi age_matrix = ages.replicate(1, 10) + arrange.replicate(ages.size(), 1);

    // For demonstration, flatten the matrix and store it in a std::vector<int>
    std::vector<int> death_rates(age_matrix.size());

    // Map the Eigen matrix to the std::vector
    Eigen::Map<Eigen::ArrayXi>(death_rates.data(), age_matrix.size()) = Eigen::Map<const Eigen::ArrayXi>(age_matrix.data(), age_matrix.size());

    return death_rates;
}

//