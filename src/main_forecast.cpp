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

/**
 * Generates a forecast population matrix directly from current population using projected mortality rates
 * @param current_pop Vector containing current population by age (86 age groups)
 * @param projected_mortality Projected mortality rates for 2021-2050
 * @param gender_idx Gender index (0 for male, 1 for female)
 * @return Population matrix by age for years 2021-2050
 */
ArrayXXi generateForecastMatrix(
    const ArrayXXi& current_pop,
    const vector<vector<ArrayXXf>>& projected_mortality,
    int gender_idx) {
    
    const int NUM_FORECAST_YEARS = 27; // 2024-2050
    const int NUM_AGE_GROUPS = 86;
    
    // Calculate total population
    int total_population = current_pop.sum();
    
    // Create a vector of individuals with their ages
    VectorXi individual_ages(total_population);
    int idx = 0;
    for (int age = 0; age < NUM_AGE_GROUPS; ++age) {
        for (int count = 0; count < current_pop(age); ++count) {
            individual_ages(idx++) = age;
        }
    }
    
    // Initialize matrix to store individual ages over time
    ArrayXXi age_matrix = ArrayXXi::Zero(total_population, NUM_FORECAST_YEARS);
    
    // Generate mortality probability matrix for each individual and year
    ArrayXXf prob_mat = ArrayXXf::Zero(total_population, NUM_FORECAST_YEARS);
    
    // Populate the probability matrix
    for (int i = 0; i < total_population; ++i) {
        int initial_age = individual_ages(i);
        for (int year = 0; year < NUM_FORECAST_YEARS; ++year) {
            int future_age = initial_age + year;
            if (future_age >= NUM_AGE_GROUPS) {
                future_age = NUM_AGE_GROUPS - 1; // Cap at 85+
            }
            
            int mortality_year = year + 3; // Index for years 2024-2050 from the 2021-2050 data
            if (mortality_year >= 30) mortality_year = 29; // Cap at 2050
            
            prob_mat(i, year) = projected_mortality[gender_idx][future_age](mortality_year, 0);
        }
    }
    
    // Generate random matrix to compare with probability matrix
    Rand::P8_mt19937_64 urng{42}; // Fixed seed for reproducibility
    ArrayXXf rand_matrix = Rand::balanced<ArrayXXf>(total_population, NUM_FORECAST_YEARS, urng, 0, 1);
    
    // 1 means alive; 0 means death
    ArrayXXi existing_matrix = (rand_matrix > prob_mat).cast<int>();
    
    // Ensure death permanence (once dead, stays dead)
    for (int i = 0; i < existing_matrix.rows(); ++i) {
        bool found_death = false;
        for (int j = 0; j < existing_matrix.cols(); ++j) {
            if (!found_death && existing_matrix(i, j) == 0) {
                found_death = true;
            }
            if (found_death) {
                existing_matrix(i, j) = 0;
            }
        }
    }
    
    // Generate age matrix
    ArrayXi year_offsets = ArrayXi::LinSpaced(NUM_FORECAST_YEARS, 0, NUM_FORECAST_YEARS - 1);
    
    for (int i = 0; i < total_population; ++i) {
        // Calculate ages
        ArrayXi ages = individual_ages[i] + year_offsets;
        
        // Cap ages at 85+
        for (int j = 0; j < NUM_FORECAST_YEARS; ++j) {
            if (ages[j] >= NUM_AGE_GROUPS) {
                ages[j] = NUM_AGE_GROUPS - 1;
            }
        }
        
        // Apply the existing matrix mask, replacing 0s with -1s
        for (int j = 0; j < NUM_FORECAST_YEARS; ++j) {
            age_matrix(i, j) = existing_matrix(i, j) ? ages[j] : -1;
        }
    }
    
    return age_matrix;
}

int main() {
    auto start = std::chrono::high_resolution_clock::now();

    const int mockScale = 20;
    DataLoader dataLoader(mockScale);

    if (!dataLoader.readAllData()) {
        std::cerr << "Failed to read data files" << std::endl;
        return -1;
    }

    // Load projected mortality rates (2021-2050)
    std::ifstream mor_file("data/bin/mortality_matrix_mat.bin", std::ios::binary);
    if (!mor_file) {
        std::cerr << "Failed to open mortality_matrix_mat.bin" << std::endl;
        return -1;
    }

    // Read the mortality matrix (2, 86, 30) for 2021-2050
    vector<vector<ArrayXXf>> projected_mortality(2, vector<ArrayXXf>(86, ArrayXXf::Zero(30, 1)));
    for (int gender = 0; gender < 2; ++gender) {
        for (int age = 0; age < 86; ++age) {
            mor_file.read(reinterpret_cast<char*>(projected_mortality[gender][age].data()), 30 * sizeof(float));
        }
    }
    mor_file.close();

    // Initialize vectors to store results for all 8 ethnic groups
    vector<vector<ArrayXXi>> age_matrix_vec(8);

    // Create MigrationSimulator instance
    MigrationSimulator mig_simulator;
    PopulationSimulator pop_simulator;
    float fertility_rates[12][71][35];  // 1980 - 2050
    copyToArray(dataLoader.fer_mat, fertility_rates);
    demographic::Fertility fertility(fertility_rates);

    // Load historical data from CSV files
    
    std::cout << "Processing population forecast..." << std::endl;

    for (int i = 0; i < 8; ++i) {
        cout << "Loading historical data for ethnic group " << i << endl;
        
        std::string filename = "output/popu_matrix_" + std::to_string(i) + ".csv";
        std::ifstream file(filename);
        if (!file.is_open()) {
            std::cerr << "Error opening file: " << filename << std::endl;
            return 1;
        }
        
        // Read the CSV data into a matrix
        // First count number of rows by counting newlines
        int num_rows = 0;
        std::string line;
        std::ifstream countFile(filename);
        while (std::getline(countFile, line)) {
            num_rows++;
        }
        countFile.close();

        // Reset file position
        file.clear();
        file.seekg(0);

        ArrayXXi historical_data(num_rows, NUM_YEARS);
        for (int row = 0; row < num_rows; ++row) {
            for (int col = 0; col < NUM_YEARS; ++col) {
                file >> historical_data(row, col);
                if (col < NUM_YEARS - 1) file.ignore(); // Skip comma
            }
        }
        
        file.close();

        // Get current population (2023)
        ArrayXXi current_pop = historical_data.col(NUM_YEARS - 1);
        
        // Print current population (2023) for ethnic group i
        std::cout << "\nCurrent Population (2023) for Ethnic Group " << i << ":" << std::endl;
        std::cout << "----------------------------------------" << std::endl;
        int total_pop = 0;
        for (int age = 0; age < 86; ++age) {
            total_pop += current_pop(age);
            std::cout << "Age " << std::setw(2) << age << ": " 
                     << std::setw(8) << current_pop(age) << std::endl;
        }
        std::cout << "Total population: " << total_pop << std::endl;
        std::cout << std::endl;
        
        // Get gender index (0 for male, 1 for female)
        int gender_idx = (i % 2 == 0) ? 0 : 1;
        
        // Generate forecast matrix directly from current population
        ArrayXXi forecast_matrix = generateForecastMatrix(
            current_pop,
            projected_mortality,
            gender_idx
        );
        
        // Print information about the forecast matrix
        std::cout << "Forecast Matrix for Ethnic Group " << i << ":" << std::endl;
        std::cout << "Rows (Ages): " << forecast_matrix.rows() << std::endl;
        std::cout << "Cols (Years 2021-2050): " << forecast_matrix.cols() << std::endl;
        
        // Print a sample of the forecast matrix (first 5 ages, first and last 3 years)
        std::cout << "\nSample of Forecast Matrix:" << std::endl;
        std::cout << "-------------------------" << std::endl;
        std::cout << "Age\t2021\t2022\t2023\t...\t2048\t2049\t2050" << std::endl;
        for (int age = 0; age < 5; ++age) {
            std::cout << age << "\t";
            // First 3 years
            for (int year = 0; year < 3; ++year) {
                std::cout << forecast_matrix(age, year) << "\t";
            }
            std::cout << "...\t";
            // Last 3 years
            for (int year = 27; year < 30; ++year) {
                std::cout << forecast_matrix(age, year) << "\t";
            }
            std::cout << std::endl;
        }
        std::cout << "...\t...\t...\t...\t...\t...\t...\t..." << std::endl;
        
        // Store forecast matrix for this ethnic group
        age_matrix_vec[i].push_back(forecast_matrix);
    }

    // Create output directory if it doesn't exist
    system("mkdir -p output/forecast");

    // Save forecast results
    for (size_t i = 0; i < age_matrix_vec.size(); ++i) {
        std::string filename = "output/forecast/forecast_matrix_" + std::to_string(i) + ".csv";
        std::ofstream file(filename);
        
        if (!file.is_open()) {
            std::cerr << "Error opening file: " << filename << std::endl;
            return 1;
        }

        // Write the matrix contents row by row
        for (int row = 0; row < age_matrix_vec[i][0].rows(); ++row) {
            for (int col = 0; col < age_matrix_vec[i][0].cols(); ++col) {
                file << age_matrix_vec[i][0](row, col);
                if (col != age_matrix_vec[i][0].cols() - 1) {
                    file << ",";
                }
            }
            file << "\n";
        }

        file.close();
        std::cout << "Successfully wrote forecast to " << filename << std::endl;
    }

    // Calculate and display runtime
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::seconds>(end - start);
    int minutes = duration.count() / 60;
    int seconds = duration.count() % 60;

    std::cout << "Forecast runtime: " << minutes << " minutes and " << seconds << " seconds\n";

    return 0;
} 