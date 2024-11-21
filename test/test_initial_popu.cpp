#include <iostream>
#include <fstream>
#include <iomanip>
#include "deathages.h"
#include "DataLoader.h"
#include "fertility.h"
#include "migration.h"
#include "utils.h"
#include <chrono>
#include <Eigen/Dense>
#include <ctime>

using namespace Eigen;

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

// Helper function to get current timestamp for log
std::string getCurrentTimestamp() {
    auto now = std::chrono::system_clock::now();
    auto now_time = std::chrono::system_clock::to_time_t(now);
    std::stringstream ss;
    ss << std::put_time(std::localtime(&now_time), "%Y-%m-%d_%H-%M-%S");
    return ss.str();
}

// Helper function to write matrix to log file

void writeMatrixToLog(std::ofstream& log_file, 
                     const std::string& matrix_name, 
                     const ArrayXXi& matrix) {
    log_file << "\n=== " << matrix_name << " ===\n";
    log_file << "Shape: " << matrix.rows() << " x " << matrix.cols() << "\n";
    log_file << matrix << "\n\n";
}

void writeMatrixToLog(std::ofstream& log_file, 
                     const std::string& matrix_name, 
                     const ArrayXXf& matrix) {
    log_file << "\n=== " << matrix_name << " ===\n";
    log_file << "Shape: " << matrix.rows() << " x " << matrix.cols() << "\n";
    log_file << matrix << "\n\n";
}

int main() {
    // Create log file with timestamp
    std::string log_filename = "test/simulation_log.txt";
    std::ofstream log_file(log_filename, std::ios::out | std::ios::trunc);
 
    
    if (!log_file.is_open()) {
        std::cerr << "Failed to open log file!" << std::endl;
        return 1;
    }

    // Log simulation parameters
    
    log_file << "=== Simulation Parameters ===\n";
    log_file << "Start time: " << getCurrentTimestamp() << "\n";
    log_file << "End year: 2023\n";
    log_file << "Start year: 1990\n\n";

    try {
        PopulationSimulator simulator;

        // Create sample population distribution
        
        

        // read sample files 
        DataLoader dataLoader(400);


        if (!dataLoader.readAllData()) {
        std::cerr << "Failed to read data files" << std::endl;
        return -1;
        }


        log_file << "=== reading finished  ===\n";
        log_file.flush();
        

        log_file << "=== Mortality Rates ===\n";
        log_file.flush();
        log_file << " mortality rates by age group:\n";
        for (int i = 0; i < 86; ++i) {
        log_file << "Age group " << i << ": ";
        log_file << std::fixed << std::setprecision(4) << dataLoader.mor_eig_mat[0].row(i) << "\n";
    }
        log_file << "\n";
        const vector<ArrayXXf>& mock_mortality = dataLoader.mor_eig_mat;
        // // Generate death and existing matrices
        // log_file << "Generating death and existing matrices...\n";

        VectorXi num_by_ages(86);  // Sample with 86 age groups

        int gen_idx = 1;
        num_by_ages = dataLoader.mock_popu_mat[gen_idx].col(0);

        log_file << "=== Initial Population Distribution ===\n";
        log_file << "Age groups (0-4):\n" << num_by_ages << "\n\n";
        log_file.flush();

        // check female
        ArrayXXi death_matrix = simulator.generateDeathMatrix(
            num_by_ages, gen_idx, mock_mortality);
        
        writeMatrixToLog(log_file, "Death Matrix", death_matrix);

        // // Generate age matrix
        // log_file << "Generating age matrix...\n";
        ArrayXXi age_matrix = simulator.generateAgeMatrix(num_by_ages, death_matrix);
        
        writeMatrixToLog(log_file, "Age Matrix", age_matrix);

        // migration here 
        int total_immigrants = dataLoader.migration_in[gen_idx].sum();
        ArrayXXi ExistingMatrix = ArrayXXi::Zero(total_immigrants, 34);
        ArrayXXi AgeMatrix = ArrayXXi::Zero(total_immigrants, 34);
        MigrationSimulator migra_simulator;
        
        ArrayXXi mig_age_matrix = migra_simulator.generateMigration(
            dataLoader.migration_in[1],
            dataLoader.disappear_mat,
            1
        );
        // from migration to fertility 

        log_file << " migration age matrix:\n" << mig_age_matrix << "\n\n";

       
        // fertility 




        /////////
        log_file << " fertility matrix by age group:\n";
        float fertility_rates[12][71][35];  // 1980 - 2050
        copyToArray(dataLoader.fer_mat, fertility_rates);
        log_file << " fertility rates matrix:\n" << fertility_rates[0] << "\n\n";

        demographic::Fertility fertility(fertility_rates);
        // test fertility matrix 
        

        std::cout << fertility.MapFertilityRate(0,18,30) << endl;
        // female


        Eigen::ArrayXi births = fertility.GenerateBirth(0, age_matrix);


        // migration
        Eigen::ArrayXi mig_births = fertility.migration_births(gen_idx, 
                                            mig_age_matrix,
                                            dataLoader.migration_in[1]);

        log_file << " migration births by age group:\n" << mig_births.transpose() << "\n\n";

        
        log_file << " test birth age matrix\n"  << "\n\n";
        
        

        

         // 1990 - 2023 
        Eigen::ArrayXi exising_births = mig_births + births;

        const int birth_start = 1991;
        const int simulationEndYear = 2023;
        initialization 
        Eigen::ArrayXi newnewborn = existing_births;
        while(birth_start <= simulationEndYear ) {

            Eigen::ArrayXf males = newnewborn.cast<float>() * 1.06f / 2.06f;
            Eigen::ArrayXf females = newnewborn.cast<float>() * 1.0f / 2.06f;

            Eigen::ArrayXi males_int = males.cast<int>();
            Eigen::ArrayXi females_int = females.cast<int>();

            // Generate age matrices for males and females
            ArrayXXi malebirthAge = fertility.generateAgefromBirth(1,
                males_int,
                dataLoader.disappear_mat
                );
            ArrayXXi femalebirthAge = fertility.generateAgefromBirth(1,
            females_int,
            dataLoader.disappear_mat
            );
            newnewborn = femalebirthAge[]


            birth_start += 15;

            // write to logging file





        }
        // Eigen::ArrayXXi BirthAgeMatrix(existing_births.sum(),34);



        // calculate the expectation

        // birth 2022
        // calculate expectation 
        // 2022 0.87 
        // fertility is correct 
        // 

        log_file << " female popu matrix:\n" << dataLoader.mock_popu_mat[gen_idx] << "\n\n";
        std::vector<double> total_births_vec;
        for (int year = 0; year <= 32; ++year){
            double total_births = 0;
            for (int age = 15; age <= 49; age++) {
            Eigen::VectorXi fem_by_ages = dataLoader.mock_popu_mat[gen_idx].col(year);
            total_births += fertility.MapFertilityRate(0, year, age)  * fem_by_ages(age);
            }
         total_births_vec.push_back(total_births);
        }

        log_file << " exp births:\n";
        for (const auto& birth : total_births_vec) {
            log_file << birth << " ";
        }
        log_file << "\n\n";

        // }
          
        // std::cout << "Total fertility: " << total_fertility << std::endl;

        log_file << " birth mortality:\n" << mock_mortality[0].row(0) << "\n\n";
        // the total births should be both the boys and girls 
        log_file << " fertility array by age group:\n" << births.transpose() << "\n\n";
        log_file << " true fertility array by age group:\n" << dataLoader.mock_popu_mat[0].row(0) << "\n\n";




        // 
        // std::cout << fertility.MapFertilityRate(0,18,30) << endl;
        // std::cout << fertility.MapFertilityRate(0,0,49) << endl;
        // input18 30 element193 18 0


        // // Calculate and log some basic statistics
        // log_file << "=== Basic Statistics ===\n";
        // log_file << "Total initial population: " << num_by_ages.sum() << "\n";
        // log_file << "Deaths by year:\n";
        // for (int year = 0; year < 10; ++year) {  // First 10 years
        //     int deaths = death_matrix.col(year).sum();
        //     log_file << "Year " << (1990 + year) << ": " << deaths << " deaths\n";
        // }
        // log_file << "...\n";

        // log_file << "\nSimulation completed successfully!\n";
        // std::cout << "Simulation results written to: " << log_filename << std::endl;

    } catch (const std::exception& e) {
        log_file << "\nERROR: " << e.what() << "\n";
        std::cerr << "Error occurred: " << e.what() << std::endl;
        return 1;
    }

    log_file.close();
    return 0;
}
