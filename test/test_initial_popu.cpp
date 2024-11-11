#include <iostream>
#include <fstream>
#include <iomanip>
#include "deathages.h"
#include "DataLoader.h"
#include <chrono>
#include <ctime>

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
        VectorXi num_by_ages(86);  // Sample with 86 age groups
        num_by_ages.setConstant(10); 
        
        log_file << "=== Initial Population Distribution ===\n";
        log_file << "Age groups (0-4):\n" << num_by_ages << "\n\n";
        log_file.flush();
        // read sample files 
        DataLoader dataLoader(100);

        // Load the mortality data first(included disappear rates already)
    if (!dataLoader.readMorEigMat("./data/bin/mig_disappear.bin")) {
        log_file << "Failed to read mortality data\n";
        throw std::runtime_error("Failed to read mortality data");
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
        ArrayXXi death_matrix = simulator.generateDeathMatrix(
            num_by_ages, 0, mock_mortality);
        
        writeMatrixToLog(log_file, "Death Matrix", death_matrix);

        // // Generate age matrix
        // log_file << "Generating age matrix...\n";
        // ArrayXXi age_matrix = simulator.generateAgeMatrix(num_by_ages, death_matrix);
        
        // writeMatrixToLog(log_file, "Age Matrix", age_matrix);

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
