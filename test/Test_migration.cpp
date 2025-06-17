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

// time complexity o(n)
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

        // vector<ArrayXXi> existing_matrix(8);
        // vector<vector<ArrayXXi>> migration_age_matrix(8);

        // Create MigrationSimulator instance

        MigrationSimulator mig_simulator;
        PopulationSimulator pop_simulator;
        float fertility_rates[12][71][35];  // 1980 - 2050
        copyToArray(dataLoader.fer_mat, fertility_rates);
        demographic::Fertility fertility(fertility_rates);

        // initialize values
        VectorXi num_by_ages;

        // Process each ethnic group
        for (int i = 0; i < 8; ++i) {
            // cout << "use chn first " << i << endl;
            cout << "Processing ethnic group " << i << endl;
            
            // Process 1990 population
            num_by_ages = dataLoader.mock_popu_mat[i].col(0);
    
            ArrayXXi existing_matrix = pop_simulator.generateDeathMatrix(
            num_by_ages, i, dataLoader.mor_eig_mat);

            age_matrix_vec[i].push_back(pop_simulator.generateAgeMatrix(
                num_by_ages,
                existing_matrix
            ));
            // print to logging file

            // deal with fertility 
            // read the female index 
            if (i % 2){
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

            } // new birth
            
            cout << "test Completed processing ethnic group " << i << endl;  
        } // each eth + gen combination

        cout << "All test ethnic groups processed successfully" << endl;


        // 
    

    for (size_t i = 0; i < 1; ++i) {
        ArrayXXi popu_mat;
        popu_mat = ArrayXXi::Zero(86, 34);
        int len = age_matrix_vec[i].size();
        for (size_t j = 0; j < len; ++j) {
            // popu_mat = ArrayXXi::Zero(86, 34);
            calculate_popu(age_matrix_vec[i][j], popu_mat);
        }
        // modelling
        ArrayXXi mock_popu_ref =  dataLoader.mock_popu_mat[i].leftCols(34);

        ArrayXXi diff = (mock_popu_ref - popu_mat );
        cout << "mock_popu_ref" << mock_popu_ref << endl;
        cout << "popu_mat" << popu_mat << endl;
        ArrayXXi people_need = lazyUpdates(diff);

 
    
        ArrayXXi mig_age_matrix = mig_simulator.generateMigration(
                    people_need, 
                    dataLoader.disappear_mat, 
                    i
                );
        age_matrix_vec[i].push_back(mig_age_matrix);

        calculate_popu(mig_age_matrix, popu_mat);
        cout << "popu_mat" << popu_mat.col(33) << endl;
        
        cout << "mock_popu_ref" << mock_popu_ref.col(33) << endl;
    }   


        // time calculate
        auto end = std::chrono::high_resolution_clock::now();
        // 
        auto duration = std::chrono::duration_cast<std::chrono::seconds>(end - start);
        int minutes = duration.count() / 60;
        int seconds = duration.count() % 60;

        std::cout << "Program runtime: " << minutes << " minutes and " << seconds << " seconds\n";


     // eth + gender

// for an eigen arrayxxi  /Users/haolong/Documents/demos_v_matrix/src/main.cpp

}
