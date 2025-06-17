#include "forecast_death.h"
#include "forecast_mortality_reader.h"
#include <Eigen/Dense>
#include <iostream>
#include <fstream>

using namespace Eigen;
using namespace std;

int main() {
    try {
        // Clear and open log file for testing
        std::ofstream log_file("logging/forecast_death.log", std::ios::trunc);
        if (!log_file.is_open()) {
            cerr << "Error: Could not open log file for writing" << endl;
            return 1;
        }

        // Initialize test population matrix
        int is_female = 1;  // Test with female population
        int years = 2050 - 2024 + 1;
        MatrixXi popu_mat = MatrixXi::Constant(87, years, -1);
        for(int i = 1; i <= 85; i++) {
            popu_mat.row(i) = i * MatrixXi::Ones(1, years);
        }

        // Read mortality matrix
        log_file << "Reading mortality matrix..." << endl;
        vector<vector<vector<double>>> mortality_mat;
        try {
            mortality_mat = readForecastMortalityMatrix();
            log_file << "Successfully read mortality matrix" << endl;
        } catch (const std::exception& e) {
            cerr << "Error reading mortality matrix: " << e.what() << endl;
            log_file << "Error reading mortality matrix: " << e.what() << endl;
            return 1;
        }

        // Log initial population matrix
        log_file << "\nInitial population matrix:\n" << popu_mat << endl;

        // Call forecast_death with logging enabled
        log_file << "\nRunning death forecast..." << endl;
        MatrixXi result = forecast_death(popu_mat, mortality_mat, is_female, &log_file);
        
        // Log final result
        log_file << "\nFinal population matrix after death forecast:\n" << result << endl;
        log_file.close();

        cout << "Test completed successfully. Results written to logging/forecast_death.log" << endl;
        return 0;

    } catch (const std::exception& e) {
        cerr << "Unexpected error during test: " << e.what() << endl;
        return 1;
    }
}