#include <fstream>
#include <Eigen/Dense>
#include <vector>
#include <random>
#include <iostream>

using namespace Eigen;
using namespace std;
// Function to generate age matrix from birth vector
ArrayXXi generateAgefromBirth(const Eigen::ArrayXi& birthvec) {
    int ncols = 34; // Maximum age is 34
    int total_births = birthvec.sum();
    Eigen::ArrayXXi AgeMatrix = Eigen::ArrayXXi::Constant(total_births, ncols, -1);

    int start_row = 0;

    for (int i = 0; i < birthvec.size(); ++i) {
        int num_births = birthvec[i];

        if (num_births == 0) continue;

        int start_col = 34 - birthvec.size()+ i;
        int age_length = ncols - start_col;

        Eigen::ArrayXi age_seq = Eigen::ArrayXi::LinSpaced(age_length, 0, age_length - 1);

        Eigen::ArrayXXi tempage = age_seq.transpose().replicate(num_births, 1);

        AgeMatrix.block(start_row, start_col, num_births, age_length) = tempage;

        start_row += num_births;
    }

    return AgeMatrix;
}

// Mapping function for fertility rate
float MapFer(int year_idx, int age) {
    if (age == -1 || age < 15 || age > 49) {
        return 0.0f;
    } else {
        return 1.0f; // Example fertility rate
    }
}

// Function to simulate population
void simulatePopulation(const ArrayXi& births, int eth_gen, std::vector<std::vector<ArrayXXi>>& matrices) {
    const int simulationEndYear = 2023;
    const int childbearingStartAge = 15;
    int birth_start = 1991;

    Eigen::ArrayXi newnewborn = births;

    // Calculate number of males and females
    Eigen::ArrayXf males = newnewborn.cast<float>() * 1.06f / 2.06f;
    Eigen::ArrayXf females = newnewborn.cast<float>() * 2.0f / 2.06f;

    Eigen::ArrayXi males_int = males.cast<int>();
    Eigen::ArrayXi females_int = females.cast<int>();

    // Generate age matrices for males and females
    ArrayXXi malebirthAge = generateAgefromBirth(males_int);
    ArrayXXi femalebirthAge = generateAgefromBirth(females_int);

    matrices[eth_gen - 1].push_back(malebirthAge);
    matrices[eth_gen].push_back(femalebirthAge);

    // Simulate population over years
    while (birth_start <= simulationEndYear ) {
        std::cout << "birth start" << birth_start << endl;
        std::cout <<  "female vec" << females_int.transpose() << endl; 
        int nrows = femalebirthAge.rows(); // Number of females
        int ncols = simulationEndYear - (birth_start + childbearingStartAge) + 1; // Years they can give birth

        // Get the age columns starting from childbearing age
        int startCol = 34 - ncols ;
        int ageCols = ncols;

        if (ageCols <= 0) break;

        ArrayXXi Newborn = femalebirthAge.block(0, startCol, nrows, ageCols);

        // Initialize the fertility matrix
        ArrayXXf ferferMat = ArrayXXf::Zero(nrows, ageCols);
        for (int col = 0; col < Newborn.cols(); ++col) {
            for (int row = 0; row < Newborn.rows(); ++row) {
                int age = Newborn(row, col);
                int year_idx = birth_start + col;
                ferferMat(row, col) = MapFer(year_idx, age);
            }
        }
        
        // Generate random values between 0 and 1
        std::random_device rd;
        std::mt19937 urng(rd());
        std::uniform_real_distribution<float> dist(0.0f, 1.0f);
        ArrayXXf random_values = ArrayXXf::NullaryExpr(nrows, ageCols, [&]() { return dist(urng); });

        ArrayXXi birthMat = (ferferMat.array() > random_values.array()).cast<int>();
        ArrayXi newnewborn = birthMat.colwise().sum();
        std::cout << "newnewborn" << newnewborn << endl;
        // Calculate new male and female births
        Eigen::ArrayXf males = newnewborn.cast<float>() * 1.06f / 2.06f;
        Eigen::ArrayXf females = newnewborn.cast<float>() * 1.0f / 2.0f;

        males_int = males.cast<int>();
        females_int = females.cast<int>();

        // Generate age matrices for the new births
        ArrayXXi newMaleBirthAge = generateAgefromBirth(males_int);
        ArrayXXi newFemaleBirthAge = generateAgefromBirth(females_int);

        matrices[eth_gen - 1].push_back(newMaleBirthAge);
        matrices[eth_gen].push_back(newFemaleBirthAge);

        // Update femalebirthAge for the next iteration
        femalebirthAge = newFemaleBirthAge;
        
        // Begin the next round
        birth_start += 15;
    }
}

int main() {
    // Create births array of ones from 1991 to 2023
    int num_years = 2023 - 1991 + 1; // 33 years
    //ArrayXi births = ArrayXi::Ones(num_years);
    ArrayXi births = ArrayXi::Constant(num_years, 5);
    int eth_gen = 1; // Example value

    // Initialize matrices for two ethnic generations
    std::vector<std::vector<ArrayXXi>> matrices(3); // Indexing from 0 to 2

    simulatePopulation(births, eth_gen, matrices);

    // Print matrices into a logging file
    std::ofstream logfile("output.txt", std::ios::out | std::ios::trunc);

    for (size_t i = 1; i < matrices.size(); ++i) {
        logfile << "Matrices for eth_gen " << i << ":\n";
        for (size_t j = 0; j < matrices[i].size(); ++j) {
            logfile << "Matrix " << j << ":\n";
            logfile << matrices[i][j] << "\n\n";
        }
    }

    logfile.close();

    std::cout << "Simulation complete. Results written to output.txt\n";

    return 0;
}
