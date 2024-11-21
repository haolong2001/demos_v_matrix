#include <iostream>
#include <string>
#include "DataLoader.h"
#include "deathages.h"
#include "migration.h"

using namespace Eigen;
using namespace std;

int main() {
    try {
        // Initialize DataLoader with mock scale
        const int mockScale = 100;
        DataLoader dataLoader(mockScale);
        
        // Read all necessary data files
        if (!dataLoader.readPopuMat("data/population.bin")) {
            cerr << "Failed to read population data" << endl;
            return 1;
        }
        
        if (!dataLoader.readDisEigMat("data/disappearance.bin")) {
            cerr << "Failed to read disappearance data" << endl;
            return 1;
        }

        // Initialize vectors to store results for all 8 ethnic groups
        vector<vector<ArrayXXi>> age_matrix(8);
        vector<ArrayXXi> existing_matrix(8);
        vector<vector<ArrayXXi>> migration_age_matrix(8);

        // Create MigrationSimulator instance
        MigrationSimulator simulator;

        // Process each ethnic group
        for (int i = 0; i < 8; ++i) {
            cout << "Processing ethnic group " << i << endl;
            
            // Process population
            VectorXi num_by_ages = dataLoader.mock_popu_mat[i].col(0);
            PopulationSimulator pop_simulator;
            age_matrix[i].push_back(pop_simulator.generateAgeMatrix(
                num_by_ages,
                existing_matrix[i]
            ));

            // Process migration
            ArrayXXi migra_mat = dataLoader.migration_in[i];
            ArrayXXi migration_result = simulator.generateMigration(
                migra_mat, 
                dataLoader.disappear_mat, 
                i
            );
            
            // Store migration result
            age_matrix[i].push_back(migration_result);

            // deal with fertility 
            // read the female index 
            generateBirth(age_matrix[i][0])


            cout << "Completed processing ethnic group " << i << endl;  
        }

        cout << "All ethnic groups processed successfully" << endl;
        return 0;

    } catch (const exception& e) {
        cerr << "Error: " << e.what() << endl;
        return 1;
    }
}
// chinese male 
// 