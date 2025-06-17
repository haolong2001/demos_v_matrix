#include <iostream>
#include <fstream>
#include "deathages.h"
#include "DataLoader.h"
#include "fertility.h"
#include "migration.h"
#include "utils.h"
#include "global.h"
#include "validate.h"
#include <Eigen/Dense>
#include <chrono>

using namespace Eigen;
using namespace std;

// Helper function to copy fertility matrix
void copyToArray(const std::unique_ptr<float[]>& fer_mat, float (&fertility_rates)[12][71][35]) {
    for (int year = 0; year < 12; ++year) {
        for (int age = 0; age < 71; ++age) {
            for (int ethnicity = 0; ethnicity < 35; ++ethnicity) {
                size_t index = year * (71 * 35) + age * 35 + ethnicity;
                fertility_rates[year][age][ethnicity] = fer_mat[index];
            }
        }
    }
}

// Calculate people needed for migration
ArrayXXi lazyUpdates(const ArrayXXi& mat) {
    int rows = mat.rows();
    int cols = mat.cols();
    ArrayXXi people_need = ArrayXXi::Zero(rows, cols);

    for (int diag = 1; diag < rows + cols - 1; ++diag) {
        for (int i = max(0, diag - cols + 1); i <= min(diag, rows - 1); ++i) {
            int j = diag - i;
            if (i > 0 && j > 0 && i < 51) {
                int diff = mat(i, j) - mat(i - 1, j - 1);
                people_need(i, j) = (diff > 0) ? diff : 0;
            }
        }
    }
    return people_need;
}

int main() {
    auto start = std::chrono::high_resolution_clock::now();

    // Initialize data loader and read data
    const int mockScale = 20;
    DataLoader dataLoader(mockScale);
    if (!dataLoader.readAllData()) {
        std::cerr << "Failed to read data files" << std::endl;
        return -1;
    }

    // Initialize simulation components
    vector<vector<ArrayXXi>> age_matrix_vec(8);
    MigrationSimulator mig_simulator;
    PopulationSimulator pop_simulator;
    float fertility_rates[12][71][35];
    copyToArray(dataLoader.fer_mat, fertility_rates);
    demographic::Fertility fertility(fertility_rates);

    // Process each ethnic group
    for (int i = 0; i < 8; ++i) {
        cout << "Processing ethnic group " << i << endl;
        
        // Process initial population
        VectorXi num_by_ages = dataLoader.mock_popu_mat[i].col(0);
        ArrayXXi existing_matrix = pop_simulator.generateDeathMatrix(num_by_ages, i, dataLoader.mor_eig_mat);
        age_matrix_vec[i].push_back(pop_simulator.generateAgeMatrix(num_by_ages, existing_matrix));

        // Handle fertility for female groups
        if (i % 2) {
            Eigen::ArrayXi births = fertility.GenerateBirth(0, age_matrix_vec[i][0]);
            births(0) = 0;

            Eigen::ArrayXi existing_births = dataLoader.mock_popu_mat[i].row(0) + dataLoader.mock_popu_mat[i-1].row(0);
            existing_births(0) = 0;

            Eigen::ArrayXi males_int = dataLoader.mock_popu_mat[i-1].leftCols(34).row(0);
            Eigen::ArrayXi females_int = dataLoader.mock_popu_mat[i].leftCols(34).row(0);
            males_int(0) = 0;
            females_int(0) = 0;

            ArrayXXi malebirthAge = fertility.generateAgefromBirth(i, males_int, dataLoader.disappear_mat);
            ArrayXXi femalebirthAge = fertility.generateAgefromBirth(i, females_int, dataLoader.disappear_mat);
            
            age_matrix_vec[i-1].push_back(malebirthAge);
            age_matrix_vec[i].push_back(femalebirthAge);
        }
    }

    // Calculate and save migration matrices
    for (size_t i = 0; i < 8; ++i) {
        // Calculate population matrix
        ArrayXXi popu_mat = ArrayXXi::Zero(86, 34);
        for (const auto& age_matrix : age_matrix_vec[i]) {
            calculate_popu(age_matrix, popu_mat);
        }

        // Calculate people needed for migration
        ArrayXXi mock_popu_ref = dataLoader.mock_popu_mat[i].leftCols(34);
        ArrayXXi diff = (mock_popu_ref - popu_mat);
        // to do; check here 
        ArrayXXi people_need = lazyUpdates(diff);

        // Save to CSV
        std::string filename = "./data/migration/migration_" + std::to_string(i) + ".csv";
        std::ofstream migration_file(filename);
        
        if (!migration_file.is_open()) {
            std::cerr << "Error opening file: " << filename << std::endl;
            continue;
        }

        // Write matrix to CSV
        for (int row = 0; row < people_need.rows(); ++row) {
            for (int col = 0; col < people_need.cols(); ++col) {
                migration_file << people_need(row, col);
                if (col != people_need.cols() - 1) migration_file << ",";
            }
            migration_file << "\n";
        }
        migration_file.close();
        std::cout << "Successfully wrote migration data to " << filename << std::endl;
    }

    // Print runtime
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::seconds>(end - start);
    std::cout << "Program runtime: " << duration.count() / 60 << " minutes and " 
              << duration.count() % 60 << " seconds\n";

    return 0;
}
