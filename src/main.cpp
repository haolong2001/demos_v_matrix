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

                // std::cout << "mig births" << mig_births << std::endl;
                // std::cout << "mig births size" << mig_births.size() << std::endl;

                // std::cout << " births" << births << std::endl;
                // std::cout << " births size" << births.size() << std::endl;


                // int birth_start = 1991;

                // Eigen::ArrayXi newnewborn = existing_births;

                // while(birth_start <= simulationEndYear ) {

                //     Eigen::ArrayXi males_int, females_int;
                //     fertility.generateNewbornData(newnewborn, males_int, females_int);

                //     // log_file.flush();
                //     // Generate age matrices for males and females
                //     ArrayXXi malebirthAge = fertility.generateAgefromBirth(
                //         i, males_int, dataLoader.disappear_mat);
                //     ArrayXXi femalebirthAge = fertility.generateAgefromBirth(
                //         i, females_int, dataLoader.disappear_mat);


                //     age_matrix_vec[i-1].push_back(malebirthAge);
                //     age_matrix_vec[i].push_back(femalebirthAge);
                //     // logging 


                //     newnewborn = fertility.calculateNewborns(
                //         i,
                //         femalebirthAge,
                //         birth_start
                //     );
                    
                //     birth_start += 15;

                //     // write to logging file
                // } // birth from birth



                // last batch
                // Eigen::ArrayXi males_int, females_int;
                // fertility.generateNewbornData(newnewborn, males_int, females_int);
                // ArrayXXi malebirthAge = fertility.generateAgefromBirth(
                //     i, males_int, dataLoader.disappear_mat);
                // ArrayXXi femalebirthAge = fertility.generateAgefromBirth(
                //     i, females_int, dataLoader.disappear_mat);

            } // new birth
            
            cout << "test Completed processing ethnic group " << i << endl;  
        } // each eth + gen combination

        cout << "All test ethnic groups processed successfully" << endl;


        // 
    

    for (size_t i = 0; i < 8; ++i) {
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
        ArrayXXi people_need = lazyUpdates(diff);

        ArrayXXi mig_age_matrix = mig_simulator.generateMigration(
                    people_need, 
                    dataLoader.disappear_mat, 
                    i
                );
        age_matrix_vec[i].push_back(mig_age_matrix);

        // do the 2024 - 2050 projection
        // get column 34 
        // ArrayXi popu_2023 = mock_popu_ref.cols(34);
        // // 
        // ArrayXXi future_mat = 



    }   

    // Step 2: Loop over each file (popu_matrix_0.csv to popu_matrix_7.csv)
    for (size_t i = 0; i < age_matrix_vec.size(); ++i) {
        // Create the file name dynamically
        // std::string filename = "output/popu_matrix_" + std::to_string(i) + ".bin";
        std::string filename = "output/popu_matrix_" + std::to_string(i) + ".csv";
        // Open the file for writing
        std::ofstream file(filename);
        
        // Check if the file is open successfully
        if (!file.is_open()) {
            std::cerr << "Error opening file: " << filename << std::endl;
            return 1; // Exit with error
        }

        // Step 4: Write the contents of each ArrayXXi inside age_matrix_vec[i] to the file
        for (size_t j = 0; j < age_matrix_vec[i].size(); ++j) {
            // Write the matrix contents row by row
            for (int row = 0; row < age_matrix_vec[i][j].rows(); ++row) {
                for (int col = 0; col < age_matrix_vec[i][j].cols(); ++col) {
                    file << age_matrix_vec[i][j](row, col);
                    if (col != age_matrix_vec[i][j].cols() - 1) {
                        file << ","; // Add a comma unless it's the last element in the row
                    }
                }
                file << "\n"; // Newline after each row
            }
        }

        // // Step 4: Write the contents of each ArrayXXi inside age_matrix_vec[i] to the file
        // int cols = 0;
        // for (size_t j = 0; j < age_matrix_vec[i].size(); ++j) {
        //     // Get the matrix dimensions
        //     int rows = age_matrix_vec[i][j].rows();
        //     cols += age_matrix_vec[i][j].cols();

        //     // Write the dimensions to the file (important for reconstruction)
        //     file.write(reinterpret_cast<char*>(&rows), sizeof(int));
        //     file.write(reinterpret_cast<char*>(&cols), sizeof(int));

        //     // Write the matrix data to the binary file
        //     file.write(reinterpret_cast<char*>(age_matrix_vec[i][j].data()), 
        //                rows * cols * sizeof(int));
        // }

        file.close();
        std::cout << "Successfully wrote to " << filename << std::endl;
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
