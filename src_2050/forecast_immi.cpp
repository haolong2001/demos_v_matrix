#include "../include/forecast_immi.h"
#include <fstream>
#include <stdexcept>
#include <numeric>

std::vector<std::vector<std::vector<int>>> readFutureImmigration(const std::string& filename) {
    std::ifstream file(filename, std::ios::binary);
    if (!file) {
        throw std::runtime_error("Error opening file: " + filename);
    }

    // Create 3D vector with dimensions 8x50x27
    std::vector<std::vector<std::vector<int>>> immigration(8,
        std::vector<std::vector<int>>(50,
            std::vector<int>(27)));

    // Read the binary data directly into the 3D vector
    for (int i = 0; i < 8; i++) {
        for (int j = 0; j < 50; j++) {
            for (int k = 0; k < 27; k++) {
                int32_t value;
                file.read(reinterpret_cast<char*>(&value), sizeof(int32_t));
                immigration[i][j][k] = value;
            }
        }
    }

    file.close();
    return immigration;
}

Eigen::MatrixXi GenerateAgentsMatrix(int matrix_index, 
                                   const std::vector<std::vector<std::vector<int>>>& immigration_mat) {
    // Calculate total number of immigrants across all age groups and years
    int total_immigrants = 0;
    for (int age = 0; age < 50; ++age) {
        for (int year = 0; year < 27; ++year) {
            total_immigrants += immigration_mat[matrix_index][age][year];
        }
    }

    // Create matrix with -1s: each row represents one immigrant
    Eigen::MatrixXi agents_mat = Eigen::MatrixXi::Constant(total_immigrants, 27, -1);
    
    int current_row = 0;
    // For each age group
    for (int age = 0; age < 50; ++age) {
        // becuse the immigration start with age 1, therefore later we put age to age + 1;
        // For each year
        for (int year = 0; year < 27; ++year) {
            int num_immigrants = immigration_mat[matrix_index][age][year];
            if (num_immigrants > 0) {
                // Create matrices for the valid columns from year onwards
                Eigen::MatrixXi year_progression = Eigen::MatrixXi::Constant(num_immigrants, 27 - year, 0);
                // Use age directly since it represents current age group
                Eigen::MatrixXi age_mat = Eigen::MatrixXi::Constant(num_immigrants, 27 - year, age + 1);
                
                // Fill progression - add j to get increasing ages
                for (int j = 0; j < 27 - year; ++j) {
                    year_progression.col(j).array() = j;
                }
                
                // Combine age and progression
                Eigen::MatrixXi batch_mat = age_mat + year_progression;
                
                // Copy batch into main matrix starting at the year column
                // Only copy the valid columns (27-year)
                agents_mat.block(current_row, year, num_immigrants, 27-year) = batch_mat;
                
                current_row += num_immigrants;
            }
        }
    }

    return agents_mat;
}

