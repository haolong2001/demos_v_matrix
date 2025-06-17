// construct death matrix

#include <Eigen/Dense>
#include <vector>
#include <random>
#include "forecast_mortality_reader.h"
#include "forecast_death.h"

using namespace Eigen;
using namespace std;

MatrixXi forecast_death(
    MatrixXi& popu_mat,
    const vector<vector<vector<double>>>& mortality_mat,
    int is_female,
    std::ostream* log_stream
) {
    int rows = popu_mat.rows();
    int cols = popu_mat.cols();

    // Initialize death probability matrix
    MatrixXd death_mat = MatrixXd::Zero(rows, cols);

    // Map population ages to mortality matrix indices
    // O(rows * cols)
    for(int i = 0; i < rows; i++) {
        for(int j = 0; j < cols; j++) {
            int age = popu_mat(i,j);
            if(age <= 0 ) { // 0 or -1
                death_mat(i,j) = 0;
            } else {
                // Map age to mortality matrix row index (age/5, capped at 17 for ages >= 85)
                int row_idx = std::min(17, age/5);
                death_mat(i,j) = mortality_mat[is_female][row_idx][j];
            }
        }
    }
    
    // Log death probability matrix if logging is enabled
    if (log_stream) {
        *log_stream << "\nDeath probability matrix:\n" << death_mat << std::endl;
    }

    // Generate random values and determine deaths
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(0.0, 1.0);

    // Generate random matrix all at once using Eigen's random() function
    MatrixXd random_mat = MatrixXd::Random(rows, cols);
    // Transform from [-1,1] to [0,1] range
    random_mat = (random_mat + MatrixXd::Ones(rows, cols)) / 2.0;

    // Broadcast comparison to find deaths
    MatrixXi liveOrDead = (random_mat.array() < death_mat.array()).cast<int>() * -1;

    // Apply deaths to population matrix
    // find first -1, and then for all the values after -1, set popu_mat values to -1
    // then continue to next row
    for(int i = 0; i < rows; i++) {
        bool found_dead = false;
        for(int j = 0; j < cols; j++) {
            if(liveOrDead(i,j) == -1) {
                popu_mat.block(i, j, 1, cols-j) = MatrixXi::Constant(1, cols-j, -1);
                found_dead = true;
                break;
            }
        }
    }

    return popu_mat;
}

// int main() {
//     // read popu_mat
//     // read mortality_mat
//     // call forecast_death
//     int is_female = 1;
//     int years = 2050 - 2024 + 1;
//     MatrixXi popu_mat = MatrixXi::Constant(87, years, -1);
//     for(int i = 1; i <= 85; i++) {
//         popu_mat.row(i) = i * MatrixXi::Ones(1, years);
//     }
//     auto mortality_mat = readForecastMortalityMatrix();
    
//     // Open log file for testing
//     std::ofstream log_file("logging/forecast_death.log", std::ios::app);
//     MatrixXi result = forecast_death(popu_mat, mortality_mat, is_female, &log_file);
    
//     // Log final result if logging is enabled
//     if (log_file.is_open()) {
//         log_file << "Result matrix:\n" << result << endl;
//         log_file.close();
//     }
// }


   // TODO: Implement death forecast logic
    // This function will modify popu_mat directly using mortality_mat

    // will do a mapping for popu_mat
    // create row index mapping, to map the values of popu_mat to the corresponding row index of mortality_mat
    // exceptions are 0 and -1, map to value 0 directly, 
    // for other values, map to mortality_mat[row_idx][col_idx]
    // get the rowindex : map to value // 5, for values larger than 84, map to 17
    // then the column index of corresponding value is the column index of popu_mat
    // then we have a matrix called death_mat, which is the same size as popu_mat, and the value is the mortality_mat[row_idx][col_idx] 

    // generate a random number matrix with values between 0 and 1
    // then compare the random number matrix with death_mat, generate liveOrDead matrix, if the value is less than death_mat, then the value is -1, means death
    // otherwise 0

    // then for each row, locate first -1, and then for all the values after -1, set them to -1

    // for popu_mat, if the corresponding value in liveOrDead is -1, then set it to -1; otherwise, do nothing