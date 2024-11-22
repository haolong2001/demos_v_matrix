#include <iostream>
#include <fstream>
#include <iomanip>
#include "deathages.h"
#include "DataLoader.h"
#include "fertility.h"
#include "migration.h"
#include "utils.h"
#include "global.h"
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
        vector<vector<ArrayXXi>> age_matrix(8);

        // vector<ArrayXXi> existing_matrix(8);
        // vector<vector<ArrayXXi>> migration_age_matrix(8);

        // Create MigrationSimulator instance

        MigrationSimulator mig_simulator;
        PopulationSimulator pop_simulator;
        float fertility_rates[12][71][35];  // 1980 - 2050
        copyToArray(dataLoader.fer_mat, fertility_rates);
        demographic::Fertility fertility(fertility_rates);

        // Process each ethnic group
        for (int i = 0; i < 2; ++i) {
            cout << "use chn first " << i << endl;
            cout << "Processing ethnic group " << i << endl;
            
            // Process 1990 population
            VectorXi num_by_ages = dataLoader.mock_popu_mat[i].col(0);
    
            ArrayXXi existing_matrix = pop_simulator.generateDeathMatrix(
            num_by_ages, i, dataLoader.mor_eig_mat);

            age_matrix[i].push_back(pop_simulator.generateAgeMatrix(
                num_by_ages,
                existing_matrix
            ));

            // Process migration
            ArrayXXi migra_mat = dataLoader.migration_in[i];
            ArrayXXi mig_age_matrix = mig_simulator.generateMigration(
                migra_mat, 
                dataLoader.disappear_mat, 
                i
            );
            
            // Store migration result
            age_matrix[i].push_back(mig_age_matrix);

            // deal with fertility 
            // read the female index 
            if (i % 2 == 1){
                Eigen::ArrayXi births = fertility.GenerateBirth(0, age_matrix[i][0]);

                Eigen::ArrayXi mig_births = fertility.migration_births(i, 
                                            mig_age_matrix,
                                            dataLoader.migration_in[i]);
                
                Eigen::ArrayXi existing_births = mig_births + births;

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
        return 0;

    } catch (const exception& e) {
        cerr << "Error: " << e.what() << endl;
        return 1;
    }
}
