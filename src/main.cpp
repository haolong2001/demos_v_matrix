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

int main() {
    try {
        // Initialize DataLoader with mock scale
        const int mockScale = 400;
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
        for (int i = 0; i < 2; ++i) {
            cout << "use chn first " << i << endl;
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

            // Process migration
            ArrayXXi migra_mat = dataLoader.migration_in[i];
            ArrayXXi mig_age_matrix = mig_simulator.generateMigration(
                migra_mat, 
                dataLoader.disappear_mat, 
                i
            );
            
            // Store migration result
            age_matrix_vec[i].push_back(mig_age_matrix);

            // deal with fertility 
            // read the female index 
            if (i % 2){
                Eigen::ArrayXi births = fertility.GenerateBirth(0, age_matrix_vec[i][0]);

                // the 1990 is calculated twice
                births(0) = 0;

                Eigen::ArrayXi mig_births = fertility.migration_births(i, 
                                            mig_age_matrix,
                                            dataLoader.migration_in[i]);
                
                Eigen::ArrayXi existing_births = mig_births + births;

                // std::cout << "mig births" << mig_births << std::endl;
                // std::cout << "mig births size" << mig_births.size() << std::endl;

                // std::cout << " births" << births << std::endl;
                // std::cout << " births size" << births.size() << std::endl;


                int birth_start = 1991;

                Eigen::ArrayXi newnewborn = existing_births;

                while(birth_start <= simulationEndYear ) {

                    Eigen::ArrayXi males_int, females_int;
                    fertility.generateNewbornData(newnewborn, males_int, females_int);

                    // log_file.flush();
                    // Generate age matrices for males and females
                    ArrayXXi malebirthAge = fertility.generateAgefromBirth(
                        i, males_int, dataLoader.disappear_mat);
                    ArrayXXi femalebirthAge = fertility.generateAgefromBirth(
                        i, females_int, dataLoader.disappear_mat);


                    age_matrix_vec[i-1].push_back(malebirthAge);
                    age_matrix_vec[i].push_back(femalebirthAge);
                    // logging 


                    newnewborn = fertility.calculateNewborns(
                        i,
                        femalebirthAge,
                        birth_start
                    );
                    
                    birth_start += 15;

                    // write to logging file
                } // birth from birth

                // last batch
                Eigen::ArrayXi males_int, females_int;
                fertility.generateNewbornData(newnewborn, males_int, females_int);
                ArrayXXi malebirthAge = fertility.generateAgefromBirth(
                    i, males_int, dataLoader.disappear_mat);
                ArrayXXi femalebirthAge = fertility.generateAgefromBirth(
                    i, females_int, dataLoader.disappear_mat);
            


            } // new birth
            
            cout << "Completed processing ethnic group " << i << endl;  
        } // each eth + gen combination

        cout << "All ethnic groups processed successfully" << endl;
        

        // write matrices to logging file
        // for (size_t i = 0 ; i < 2; ++i){
        //     int len = age_matrix_vec[i].len();
        //     j = 0  
        //     j = 1 header "mig"


        //     for (size_t j = 2; j < len; ++j )

        // }
        // validation 
      
    ArrayXXi popu_mat;

    for (size_t i = 0; i < 2; ++i) {
        popu_mat = ArrayXXi::Zero(86, 34);

        int len = age_matrix_vec[i].size();
        for (size_t j = 0; j < len; ++j) {
            // popu_mat = ArrayXXi::Zero(86, 34);
            if (j == 1){
                ArrayXXi mig_mat = ArrayXXi::Zero(86, 34);
                calculate_popu(age_matrix_vec[i][j], mig_mat);
                string popu_filename = "output/mig_matrix_" + to_string(i) + "_popu.txt";
                ofstream mig_file(popu_filename);
                mig_file << "mig Matrix:\n" << mig_mat << endl;
                
            }

            calculate_popu(age_matrix_vec[i][j], popu_mat);
            // std::cout <<"step 1" << std::endl;
            // if (j == 0){
            //     ofstream popu_file("output/age_matrix_1990.txt");
            //     popu_file << "Simulated Matrix:\n" << popu_mat << endl;
            // }
            // else if (j == 1) {
            //     ofstream popu_file("output/age_matrix_migrate.txt");
            //     popu_file << "Simulated Matrix:\n" << popu_mat << endl;
            // }
        }

        string popu_filename = "output/age_matrix_" + to_string(i) + "_popu.txt";
        ofstream popu_file(popu_filename);

        string t_filename = "output/true_matrix_" + to_string(i) + "_popu.txt";
        ofstream true_file(t_filename);
        if (true_file.is_open()) {
            true_file << "true Matrix:\n" << dataLoader.mock_popu_mat[i].leftCols(34) << "\n\n";
            true_file.close();
        }

        if (popu_file.is_open()) {

            popu_file << "death Matrix:\n" << dataLoader.disappear_mat[i] << endl;
            popu_file << "Simulated without Matrix:\n" << popu_mat << endl;
            
            
            auto mock_popu_ref =  dataLoader.mock_popu_mat[i].leftCols(34);
            // Convert both matrices to double before performing the division
            ArrayXXd popu_mat_double = popu_mat.cast<double>();
            ArrayXXd mock_popu_ref_double = mock_popu_ref.cast<double>();

            // Calculate relative difference using simple division operator
            ArrayXXd diff = (popu_mat_double - mock_popu_ref_double) / mock_popu_ref_double;

            // Set precision for the output
            Eigen::IOFormat fmt(2, 0, ", ", "\n", "[", "]");

            popu_file << "Difference Matrix:\n" << diff.format(fmt) << "\n\n";
            // popu_file << "Maximum Absolute Difference: " << max_abs_diff << endl;
            // calculate difference 
            diff = (popu_mat_double - mock_popu_ref_double);
            popu_file << "Difference Matrix:\n" << diff.format(fmt) << "\n\n";

            // Calculate column sums of difference matrix
            Eigen::VectorXd col_sums = diff.colwise().sum();


            // Print column sums
            popu_file << "Column Sums of Difference Matrix:\n" << col_sums.format(fmt) << "\n\n";
            
            popu_file << "migration \n" <<  dataLoader.migration_in[i]  << "\n";

            popu_file.close();


        } else {
            cerr << "Error: Could not open file " << popu_filename << endl;
        }

    } 
    
    } catch (const exception& e) {
        cerr << "Error: " << e.what() << endl;
        return 1;
    }


return 0;

}
