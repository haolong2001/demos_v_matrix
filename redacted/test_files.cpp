#include <iostream>
#include <Eigen/Dense>
#include <vector>
#include <random>

using namespace Eigen;
using namespace std;

void generateAgefromBirth(int eth_gen, const ArrayXi& birthvec, ArrayXXi& AgeMatrix, const vector<ArrayXXf>& disappear_mat, std::default_random_engine& urng)
{
    // Number of years (columns in AgeMatrix)
    const int total_years = 34;
    // Number of birth years
    int ncols = birthvec.size();
    // Starting column index in AgeMatrix to align with the ending
    int beginning = total_years - ncols;
    // Starting row index in AgeMatrix
    int start = 0;

    // Loop over each birth cohort
    for (int i = 0; i < ncols; ++i)
    {
        int num = birthvec[i]; // Number of individuals born in this cohort
        int n_years = total_years - beginning; // Number of years to simulate for this cohort

        // Initialize the age matrix for these individuals
        // Each individual will have ages from 0 to n_years - 1
        ArrayXXi tempage = ArrayXXi::Zero(num, n_years);
        for (int col = 0; col < n_years; ++col)
        {
            tempage.col(col).setConstant(col);
        }

        // Extract mortality probabilities for these ages and years
        // Mortality data is assumed to be of size (ages x years), e.g., (119 x 34)
        ArrayXf mor(n_years);
        for (int j = 0; j < n_years; ++j)
        {
            // Age is from 0 to n_years - 1
            // Year is from beginning + j
            mor(j) = disappear_mat[eth_gen](j, beginning + j);
        }

        // Generate random numbers for survival simulation
        std::uniform_real_distribution<float> distribution(0.0f, 1.0f);
        ArrayXXf rand_vals = ArrayXXf::NullaryExpr(num, n_years, [&]() { return distribution(urng); });

        // Initialize survival matrix
        ArrayXXi survival = ArrayXXi::Ones(num, n_years);
        for (int row = 0; row < num; ++row)
        {
            for (int col = 0; col < n_years; ++col)
            {
                if (col == 0)
                {
                    survival(row, col) = (rand_vals(row, col) > mor(col)) ? 1 : 0;
                }
                else
                {
                    survival(row, col) = (survival(row, col - 1) && (rand_vals(row, col) > mor(col))) ? 1 : 0;
                }
            }
        }

        // Apply survival to the age matrix
        ArrayXXi ages = tempage * survival;

        // Insert the ages into the AgeMatrix
        AgeMatrix.block(start, beginning, num, n_years) = ages;

        // Update the starting indices for the next cohort
        start += num;
        beginning += 1;
    }
}

int main()
{
    // Example usage:

    // Initialize the birth vector
    ArrayXi birthvec(3);
    birthvec << 20, 23, 24; // Number of individuals born in each of the last 3 years

    // Initialize the AgeMatrix
    int total_individuals = birthvec.sum();
    int total_years = 34;
    ArrayXXi AgeMatrix = ArrayXXi::Zero(total_individuals, total_years);

    // Initialize the mortality data (disappear_mat)
    // For demonstration, we'll create dummy data
    vector<ArrayXXf> disappear_mat(8, ArrayXXf::Random(119, total_years).abs() * 0.05); // Mortality probabilities between 0 and 0.05

    // Initialize random number generator
    std::default_random_engine urng;

    // Generate the age matrix
    generateAgefromBirth(0, birthvec, AgeMatrix, disappear_mat, urng);

    // Print the AgeMatrix
    std::cout << "AgeMatrix:\n" << AgeMatrix << std::endl;

    return 0;
}
