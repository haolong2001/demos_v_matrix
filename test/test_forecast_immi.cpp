#include "forecast_immi.h"
#include <iostream>
#include <iomanip>

void printImmigrationData(const std::vector<std::vector<std::vector<int>>>& immigration) {
    

    // Print first 3x3 section of first matrix (index 0)
    std::cout << "\nFirst 3x3 section of matrix 0:" << std::endl;
    std::cout << "Age groups are rows, years are columns" << std::endl;
    std::cout << std::setw(5) << "Age" << " |";
    
    // Print year headers (first 3 years)
    for (int year = 0; year < 3; ++year) {
        std::cout << std::setw(6) << 2024 + year << " |";
    }
    std::cout << std::endl;

    // Print separator line
    std::cout << std::string(6, '-') << "+";
    for (int year = 0; year < 3; ++year) {
        std::cout << std::string(7, '-') << "+";
    }
    std::cout << std::endl;

    // Print data (first 3 age groups x first 3 years)
    for (int age = 0; age < 3; ++age) {
        std::cout << std::setw(5) << age << " |";
        for (int year = 0; year < 3; ++year) {
            std::cout << std::setw(6) << immigration[0][age][year] << " |";
        }
        std::cout << std::endl;
    }
}

void printAgentMatrix(const Eigen::MatrixXi& agent_mat, int num_rows = 5) {
    std::cout << "\nAgent Matrix (showing first " << num_rows << " rows):" << std::endl;
    std::cout << "Total rows (immigrants): " << agent_mat.rows() << std::endl;
    std::cout << "Years (columns): " << agent_mat.cols() << std::endl;
    
    // Print year headers
    std::cout << std::setw(5) << "Row" << " |";
    for (int year = 0; year < agent_mat.cols(); ++year) {
        std::cout << std::setw(4) << 2024 + year << " |";
    }
    std::cout << std::endl;

    // Print separator line
    std::cout << std::string(6, '-') << "+";
    for (int year = 0; year < agent_mat.cols(); ++year) {
        std::cout << std::string(6, '-') << "+";
    }
    std::cout << std::endl;

    // Print first num_rows rows
    for (int row = 0; row < 50; ++row) {
        std::cout << std::setw(5) << row << " |";
        for (int col = 0; col < agent_mat.cols(); ++col) {
            std::cout << std::setw(4) << agent_mat(row, col) << " |";
        }
        std::cout << std::endl;
    }
}

int main() {

    // Print a 3x3 test matrix
    std::cout << "\nOuutput should match:" << std::endl;
    std::cout << "36, 41, 34" << std::endl;
    std::cout << "17,  6,  9" << std::endl; 
    std::cout << " 4,  8,  5" << std::endl;
    try {
        // Read immigration data
        std::string filename = "data/migration/future_immigration.bin";
        auto immigration = readFutureImmigration(filename);
        
        // Print the immigration data
        printImmigrationData(immigration);
        std::cout << "Successfully read immigration" << std::endl;

        // Test GenerateAgentsMatrix for matrix 0
        std::cout << "\nTesting GenerateAgentsMatrix for matrix 0:" << std::endl;
        auto agent_mat = GenerateAgentsMatrix(0, immigration);
        
        // Print the generated agent matrix
        printAgentMatrix(agent_mat);

        // Print some statistics
        std::cout << "\nMatrix Statistics:" << std::endl;
        std::cout << "Total immigrants: " << agent_mat.rows() << std::endl;
        
        // Count how many immigrants start in each year
        std::vector<int> immigrants_per_year(27, 0);
        for (int row = 0; row < agent_mat.rows(); ++row) {
            for (int col = 0; col < agent_mat.cols(); ++col) {
                if (agent_mat(row, col) != -1 && (col == 0 || agent_mat(row, col-1) == -1)) {
                    immigrants_per_year[col]++;
                }
            }
        }

        std::cout << "\nImmigrants starting each year:" << std::endl;
        for (int year = 0; year < 27; ++year) {
            if (immigrants_per_year[year] > 0) {
                std::cout << "Year " << 2024 + year << ": " << immigrants_per_year[year] << " immigrants" << std::endl;
            }
        }

        return 0;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
} 