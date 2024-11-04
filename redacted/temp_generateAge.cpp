#include <fstream>
#include <Eigen/Dense>
#include <vector>
#include <random>
#include <iostream>

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

int main() {
    // Initialize random number generator
    std::random_device rd;
    std::mt19937 urng(rd());

    // Example birth vector
    Eigen::ArrayXi birthvec(4);
    birthvec << 5, 4, 3, 2;
    // expected to have 9 

    // Initialize AgeMatrix with zeros
    int total_population = birthvec.sum();
    // change the following initialization to every element to -1 
    Eigen::ArrayXXi AgeMatrix = Eigen::ArrayXXi::Constant(total_population, 34, -1);
    
    // Initialize disappear_mat with random mortality rates between 0 and 1
    std::vector<Eigen::ArrayXXf> disappear_mat(8, Eigen::ArrayXXf::Zero(total_population, 34));
    std::uniform_real_distribution<float> dist(0.0f, 1.0f);
    std::mt19937 rng(rd());
    // only initialize 0 and 1 
    for (int i = 0; i < 2; ++i) {
        for (int m = 0; m < total_population; ++m) {
            for (int n = 0; n < 34; ++n) {
                disappear_mat[i](m, n) =  0.0f; // //dist(rng);
            }
        }
    }

    // do the test with three things
    // a matrix with 0; a matrix with 1 and a matrix with 0.5

    int eth_gen = 0; // Example ethnic group index

    // Generate AgeMatrix
    generateAgefromBirth(eth_gen, birthvec, AgeMatrix, disappear_mat, urng);

    // Open a logging file to write the AgeMatrix
    std::ofstream logfile("agematrix_log.txt");
    if (!logfile.is_open()) {
        std::cerr << "Failed to open the logging file." << std::endl;
        return 1;
    }

    // Write the AgeMatrix to the logging file, line by line
    for (int i = 0; i < AgeMatrix.rows(); ++i) {
        for (int j = 0; j < AgeMatrix.cols(); ++j) {
            logfile << AgeMatrix(i, j);
            if (j < AgeMatrix.cols() - 1) {
                logfile << ", ";
            }
        }
        logfile << '\n';
    }

    logfile.close();

    std::cout << "AgeMatrix has been written to 'agematrix_log.txt'." << std::endl;



    return 0;
}
