#include "migration.h"

using namespace Eigen;
using namespace std;

ArrayXXf MigrationSimulator::generateRandomValues(int rows, int cols) {
    std::random_device rd;
    std::mt19937 urng(rd());
    return ArrayXXf::Random(rows, cols).unaryExpr([](float val) { 
        return (val + 1.0f) / 2.0f; 
    });
}

MigrationSimulator::MigrationSimulator(const std::string& log_path) {
    if (!log_path.empty()) {
        log_file.open(log_path);
    }
}

MigrationSimulator::~MigrationSimulator() {
    if (log_file.is_open()) {
        log_file.close();
    }
}

void MigrationSimulator::updateSurvivalStatus(ArrayXXi& survival_status) {
    const int rows = survival_status.rows();
    const int cols = survival_status.cols();
    
    for (int i = 0; i < rows; ++i) {
        bool disappeared = false;
        for (int j = 0; j < cols; ++j) {
            if (!disappeared && survival_status(i, j) == 0) {
                disappeared = true;
            }
            if (disappeared) {
                survival_status(i, j) = 0;
            }
        }
    }
}

ArrayXXi MigrationSimulator::generateMigration(
    const ArrayXXi& MigNumMat,
    const vector<ArrayXXf>& disappear_mat,
    int index
) {    
    int total_immigrants = MigNumMat.sum();
    ArrayXXi ExistingMatrix = ArrayXXi::Zero(total_immigrants, NUM_YEARS);
    ArrayXXi AgeMatrix = ArrayXXi(total_immigrants, NUM_YEARS);
    AgeMatrix.setConstant(-1);
    int start_pos = 0;
    
    // Process each year starting from year 1
    for (int year = 1; year < NUM_YEARS; ++year) {
        ArrayXi immigrants_per_age = MigNumMat.col(year);
        
        // Process each age group
        for (int age = 0; age < NUM_AGE_GROUPS; ++age) {
            int num_immigrants = immigrants_per_age[age];
            if (num_immigrants == 0) continue;
            
            // Calculate adjusted index for disappearance rates
            int disappear_idx = age - year + 33;
            if (disappear_idx < 0 || disappear_idx >= disappear_mat[index].rows()) {
                continue;
            }

            // Get disappearance rates and generate survival status
            ArrayXf rates = disappear_mat[index].row(disappear_idx).segment(year, NUM_YEARS - year);
            ArrayXXf replicated_rates = rates.replicate(1, num_immigrants).transpose();
            // if rand < rate, then death, we mark 0 
            ArrayXXi survival_status = (generateRandomValues(num_immigrants, NUM_YEARS - year) > replicated_rates).cast<int>();
            
            updateSurvivalStatus(survival_status);
            ExistingMatrix.block(start_pos, year, num_immigrants, NUM_YEARS - year) = survival_status;
            
            // Generate age matrix
            ArrayXXi age_block = ArrayXXi::Zero(num_immigrants, NUM_YEARS - year);
            for (int t = 0; t < NUM_YEARS - year; ++t) {
                age_block.col(t).setConstant(age + t);
            }
            
            // Apply age only where person exists
            age_block = (survival_status.array() > 0).select(age_block, -1);
            AgeMatrix.block(start_pos, year, num_immigrants, NUM_YEARS - year) = age_block;
            
            start_pos += num_immigrants;
        }
    }
    
    return AgeMatrix;


}


// #include <Eigen/Dense>
// #include <random>
// #include <iostream>
// #include <vector>
// #include <fstream>
// #include "DataLoader.h"

// using namespace Eigen;
// using namespace std;

// class MigrationSimulator {
// private:
//     const int NUM_AGE_GROUPS = 86;
//     const int NUM_YEARS = 34;
//     std::ofstream log_file;

//     /**
//      * @brief Generates random values between 0 and 1
//      * @param rows Number of rows
//      * @param cols Number of columns
//      * @return Matrix of random values
//      */
//     ArrayXXf generateRandomValues(int rows, int cols) {
//         std::random_device rd;
//         std::mt19937 urng(rd());
//         return ArrayXXf::Random(rows, cols).unaryExpr([](float val) { 
//             return (val + 1.0f) / 2.0f; 
//         });
//     }

// public:
//     MigrationSimulator(const std::string& log_path) {
//         log_file.open(log_path);
//         if (!log_file.is_open()) {
//             throw std::runtime_error("Failed to open log file: " + log_path);
//         }
//     }

//     ~MigrationSimulator() {
//         if (log_file.is_open()) {
//             log_file.close();
//         }
//     }

//     /**
//      * @brief Updates survival status to ensure death is permanent
//      * If a person disappears (status = 0), they remain disappeared for all subsequent years
//      */
//     void updateSurvivalStatus(ArrayXXi& survival_status) {
//         const int rows = survival_status.rows();
//         const int cols = survival_status.cols();
        
//         for (int i = 0; i < rows; ++i) {
//             bool disappeared = false;
//             for (int j = 0; j < cols; ++j) {
//                 if (!disappeared && survival_status(i, j) == 0) {
//                     disappeared = true;
//                 }
//                 if (disappeared) {
//                     survival_status(i, j) = 0;
//                 }
//             }
//         }
//     }

//     /**
//      * @brief Generates migration and age matrices based on input parameters
//      * 
//      * @param MigNumMat Matrix containing migration numbers per age group and year
//      * @param disappear_mat Vector of disappearance rate matrices
//      * @param index Index for selecting disappearance matrix
//      * @param ExistingMatrix Output matrix tracking existence status
//      * @param AgeMatrix Output matrix tracking ages
//      */
//     void generateMigration(
//         const ArrayXXi& MigNumMat,
//         const vector<ArrayXXf>& disappear_mat,
//         int index,
//         ArrayXXi& ExistingMatrix,
//         ArrayXXi& AgeMatrix
//     ) {
//         log_file << "Starting migration generation...\n";
        
//         int start_pos = 0;
        
//         // Process each year starting from year 1
//         for (int year = 1; year < NUM_YEARS; ++year) {
//             ArrayXi immigrants_per_age = MigNumMat.col(year);
//             int total_immigrants = immigrants_per_age.sum();
            
//             // Initialize matrices with -1 for non-immigrant status
//             ExistingMatrix.block(start_pos, 0, total_immigrants, year).setConstant(-1);
//             AgeMatrix.block(start_pos, 0, total_immigrants, year).setConstant(-1);
//             std::cout << "step 1" << std::endl;
//             // Process each age group
//             for (int age = 0; age < NUM_AGE_GROUPS; ++age) {
//                 int num_immigrants = immigrants_per_age[age];
//                 if (num_immigrants == 0) continue;
                
//                 // Calculate adjusted index for disappearance rates
//                 int disappear_idx = age - year + 33;
//                 if (disappear_idx < 0 || disappear_idx >= disappear_mat[index].rows()) {
//                     log_file << "Skipping invalid disappearance index: " << disappear_idx << "\n";
//                     continue;
//                 }
//                 if (age == 0){
//                     std::cout << "step 1.5" << std::endl;
//                 }

//                 // Get disappearance rates for this group
//                 ArrayXf rates = disappear_mat[index].row(disappear_idx).segment(year, NUM_YEARS - year);
//                 ArrayXXf replicated_rates = rates.replicate(1, num_immigrants).transpose();
//                 if (age == 0){
//                     std::cout << "step 1.7" << std::endl;
//                 }
//                 // Generate survival status based on disappearance rates
//                 ArrayXXf random_values = generateRandomValues(num_immigrants, NUM_YEARS - year);
//                 ArrayXXi survival_status = (replicated_rates <= random_values).cast<int>();
                
//                 updateSurvivalStatus(survival_status);

//                 // Update existence status
//                 ExistingMatrix.block(start_pos, year , num_immigrants, NUM_YEARS - year ) = survival_status;
//                 if (age == 0){
//                     std::cout << "step 2" << std::endl;
//                 }
                
//                 // Generate and update age matrix
//                 ArrayXXi age_block = ArrayXXi::Zero(num_immigrants, NUM_YEARS - year);
//                 for (int t = 0; t < NUM_YEARS - year; ++t) {
//                     age_block.col(t).setConstant(age + t);
//                 }
                
//                 // Apply age only where person exists (not dead)
//                 age_block = (survival_status.array() > 0).select(age_block, -1);
//                 AgeMatrix.block(start_pos, year , num_immigrants, NUM_YEARS - year) = age_block;
//                 if (age == 0){
//                     std::cout << "step 2.2" << std::endl;
//                 }
//                 start_pos += num_immigrants;
//             }
            
//             log_file << "Processed year " << year << ", total immigrants: " << total_immigrants << "\n";
//         }
        
//         // Write final age matrix to log file
//         log_file << "\nFinal Age Matrix:\n" << AgeMatrix << "\n";
//     }
// };

// int main() {
//     try {
//         MigrationSimulator simulator("test/imm.txt");
        
//         // Load data
//         DataLoader dataLoader(100);
//         if (!dataLoader.readMorEigMat("./data/bin/mig_disappear.bin")) {
//             throw std::runtime_error("Failed to read mortality data");
//         }
        
//         // Initialize matrices
//         ArrayXXi migra_mat = ArrayXXi::Constant(86, 34, 10);
//         dataLoader.readDisEigMat("./data/bin/disappear.bin");
//         vector<ArrayXXf> disappear_mat = dataLoader.disappear_mat;
        
//         // ArrayXf rates = disappear_mat[index];
        
//         // Calculate total size needed based on migration matrix
//         int total_immigrants = migra_mat.sum();
//         ArrayXXi ExistingMatrix = ArrayXXi::Zero(total_immigrants, 34);
//         ArrayXXi AgeMatrix = ArrayXXi::Zero(total_immigrants, 34);

//         std::cout << "step 0" << std::endl;
//        // Generate migration data
//         simulator.generateMigration(migra_mat, disappear_mat, 0, ExistingMatrix, AgeMatrix);
        

//         return 0;
//     } catch (const std::exception& e) {
//         std::cerr << "Error: " << e.what() << std::endl;
//         return 1;
//     }
// }
