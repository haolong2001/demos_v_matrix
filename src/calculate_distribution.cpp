#include <iostream>
#include <fstream>
#include <iomanip>
#include "deathages.h"
#include "DataLoader.h"
#include "fertility.h"
#include "migration.h"
#include "utils.h"
#include "global.h"
#include "validate.h"
#include <string>
#include <chrono>
#include <Eigen/Dense>
#include <ctime>

using namespace Eigen;
using namespace std;

ArrayXXi lazyUpdates(const ArrayXXi& mat) {
    int rows = mat.rows();
    int cols = mat.cols();

    // Initialize the people_need matrix with zeros
    ArrayXXi people_need = ArrayXXi::Zero(rows, cols);

    // Traverse the matrix diagonally
    for (int diag = 1; diag < rows + cols - 1; ++diag) {
        for (int i = max(0, diag - cols + 1); i <= min(diag, rows - 1); ++i) {
            int j = diag - i;

            if (i > 0 && j > 0 && i <51) {
                int diff = mat(i, j) - mat(i - 1, j - 1);
                if (diff > 0) {
                    people_need(i, j) = diff;
                } else {
                    people_need(i, j) = 0;
                }
            }
        }
    }

    return people_need;
}

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

int main() {
    auto start = std::chrono::high_resolution_clock::now();

    const int mockScale = 20;
    DataLoader dataLoader(mockScale);

    if (!dataLoader.readAllData()) {
        std::cerr << "Failed to read data files" << std::endl;
        return -1;
    }

    // Initialize vectors to store results for all 8 ethnic groups
    vector<vector<ArrayXXi>> age_matrix_vec(8);

    // Create MigrationSimulator instance
    MigrationSimulator mig_simulator;
    PopulationSimulator pop_simulator;
    float fertility_rates[12][71][35];  // 1980 - 2050
    copyToArray(dataLoader.fer_mat, fertility_rates);
    demographic::Fertility fertility(fertility_rates);

    // Process each ethnic group
    for (int i = 0; i < 8; ++i) {
        cout << "Processing ethnic group " << i << endl;
        
        // Process 1990 population
        VectorXi num_by_ages = dataLoader.mock_popu_mat[i].col(0);
    
        ArrayXXi existing_matrix = pop_simulator.generateDeathMatrix(
            num_by_ages, i, dataLoader.mor_eig_mat);

        age_matrix_vec[i].push_back(pop_simulator.generateAgeMatrix(
            num_by_ages,
            existing_matrix
        ));

        // Handle fertility for female indices
        if (i % 2) {
                Eigen::ArrayXi births = fertility.GenerateBirth(0, age_matrix_vec[i][0]);

                // the 1990 is calculated twice
                births(0) = 0;

                Eigen::ArrayXi existing_births = dataLoader.mock_popu_mat[i].row(0)
                + dataLoader.mock_popu_mat[i-1].row(0)
                ;
                existing_births(0) = 0;


                Eigen::ArrayXi males_int, females_int;
                males_int = dataLoader.mock_popu_mat[i-1].leftCols(34).row(0);
                females_int = dataLoader.mock_popu_mat[i].leftCols(34).row(0);
                males_int(0) = 0;
                females_int(0) = 0;

                ArrayXXi malebirthAge = fertility.generateAgefromBirth(
                        i, males_int, dataLoader.disappear_mat);
                ArrayXXi femalebirthAge = fertility.generateAgefromBirth(
                        i, females_int, dataLoader.disappear_mat);
                
                age_matrix_vec[i-1].push_back(malebirthAge);
                age_matrix_vec[i].push_back(femalebirthAge);
            
        }
    }

    // Create matrix to store distributions (8 ethnic groups × 86 age groups)
    ArrayXXf distributions(8, 86);
    distributions.setZero();

    // Calculate distributions for each ethnic group
    for (size_t i = 0; i < 8; ++i) {
        ArrayXXi popu_mat = ArrayXXi::Zero(86, 34);
        int len = age_matrix_vec[i].size();
        for (size_t j = 0; j < len; ++j) {
            calculate_popu(age_matrix_vec[i][j], popu_mat);
        }

        ArrayXXi mock_popu_ref = dataLoader.mock_popu_mat[i].leftCols(34);
        ArrayXXi diff = (mock_popu_ref - popu_mat);
        ArrayXXi people_need = lazyUpdates(diff);

        // Get the distribution for year 2019 (index 29)
        // get index 29 column of people_need matrix
        ArrayXf sum_people_need = people_need.col(29).cast<float>();
        ArrayXf migration_rate = sum_people_need / sum_people_need.sum();

        // Store the distribution for this ethnic group
        distributions.row(i) = migration_rate;
    }

    // Save the distributions to a CSV file
    std::ofstream file("output/distributions_2019.csv");
    if (!file.is_open()) {
        std::cerr << "Error opening file for writing" << std::endl;
        return 1;
    }

    // Write header
    file << "Ethnic_Group";
    for (int age = 0; age < 86; ++age) {
        file << ",Age_" << age;
    }
    file << std::endl;

    // Write data
    for (int i = 0; i < 8; ++i) {
        file << i;
        for (int j = 0; j < 86; ++j) {
            file << "," << std::fixed << std::setprecision(4) << distributions(i, j);
        }
        file << std::endl;
    }

    file.close();
    std::cout << "Successfully wrote distributions to output/distributions_2019.csv" << std::endl;

    

    // Calculate runtime
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::seconds>(end - start);
    std::cout << "Program runtime: " << duration.count() << " seconds" << std::endl;

    return 0;
} 