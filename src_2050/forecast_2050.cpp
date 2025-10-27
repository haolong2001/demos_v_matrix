#include "matrix_reader.h"
#include "forecast_mortality_reader.h"
#include "forecast_death.h"
#include "forecast_immi.h"
#include "forecast_fertility.h"
#include <vector>
#include <string>
#include <iostream>
#include <Eigen/Dense>
#include <algorithm>
#include <fstream>
#include <filesystem>
#include <random>
#include <iomanip>

using namespace std;
using namespace Eigen;

// Function to read all population matrices (0-7)
vector<vector<vector<int>>> readPopulationMatrices() {
    vector<vector<vector<int>>> matrices;
    matrices.reserve(8);  // We know there are 8 matrices

    for (int i = 0; i < 8; i++) {
        string filename = "output/Historical_data/popu_matrix_" + to_string(i) + ".csv";
        try {
            auto matrix = MatrixReader::readCSVMatrix(filename);
            // Convert double matrix to int matrix
            vector<vector<int>> int_matrix;
            for (const auto& row : matrix) {
                vector<int> int_row;
                for (const auto& val : row) {
                    int_row.push_back(static_cast<int>(val));
                }
                int_matrix.push_back(int_row);
            }
            matrices.push_back(int_matrix);
            cout << "Successfully read " << filename << endl;
            // Print dimensions of each matrix
            cout << "Matrix " << i << " dimensions: " 
                 << int_matrix.size() << " rows x " 
                 << (int_matrix.empty() ? 0 : int_matrix[0].size()) << " columns" << endl;
            
        } catch (const exception& e) {
            cerr << "Error reading " << filename << ": " << e.what() << endl;
            throw;
        }
    }

    cout << "Total matrices read: " << matrices.size() << endl;
    return matrices;
}

// Function to generate population matrix for forecasting
MatrixXi generateAgesWithouDeath(const vector<int>& base_population, int start_year, int end_year) {
    const int years = end_year - start_year + 1;
    const int num_age_groups = base_population.size();
    
    MatrixXi popu_mat(num_age_groups, years);
    MatrixXi temp_mat = MatrixXi::Zero(num_age_groups, years);
    MatrixXi increase_age = MatrixXi::Zero(num_age_groups, years);

    for (int j = 0; j < years; ++j) {
        // Create a non-const copy of the data for Map
        vector<int> temp_pop = base_population;
        temp_mat.col(j) = Map<VectorXi>(temp_pop.data(), temp_pop.size());
        increase_age.col(j).array() = j + 1;
    }

    return temp_mat + increase_age;
}


int main() {
    try {
        auto matrices = readPopulationMatrices();
        
        // Read mortality matrix
        auto mortality_mat = readForecastMortalityMatrix();
        cout << "Successfully read mortality matrix" << endl;
        
        // Read immigration data
        string immi_filename = "data/migration/future_immigration.bin";
        auto immigration_mat = readFutureImmigration(immi_filename);
        cout << "Successfully read immigration matrix" << endl;

        // read fertility matrix
        string fertility_filename = "data/bin/AESFR_matrix_combine.bin";
        auto fertility_matrix = readFertilityMatrix(fertility_filename);
        cout << "Successfully read fertility matrix" << endl;
        
        const int start_year = 2024;
        const int end_year = 2050;

        // Initialize vector to store 8 population matrices
        vector<vector<MatrixXi>> population_matrices(8, vector<MatrixXi>());

        for (int i = 0; i < 8; i++) {
        //for (int i = 2; i < 4; i++) {
            // Process base population
            vector<int> agents_2023;
            for (const auto& row : matrices[i]) {
                if (!row.empty() && row.back() != -1) {
                    agents_2023.push_back(row.back());
                }
            }

            MatrixXi popu_mat = generateAgesWithouDeath(agents_2023, start_year, end_year);
            MatrixXi base_popu = forecast_death(popu_mat, mortality_mat, i % 2); // Even indices for male, odd for female

            // Process immigration
            MatrixXi agent_mat = GenerateAgentsMatrix(i, immigration_mat);
            MatrixXi immigration = forecast_death(agent_mat, mortality_mat, i % 2);
            
            if (i < 7) {
                cout << "Immigration matrix shape (i=" << i << "): "
                     << immigration.rows() << " x " << immigration.cols() << endl;
            }

            // Print some statistics about the matrices
            cout << "\nMatrix " << i << " statistics:" << endl;
            cout << "Base population size: " << base_popu.rows() << " agents" << endl;
            cout << "Immigration size: " << immigration.rows() << " agents" << endl;
            
            // Combine base population and immigration matrices
            MatrixXi combined_popu(base_popu.rows() + immigration.rows(), base_popu.cols());
            combined_popu << base_popu, immigration;
            population_matrices[i].push_back(combined_popu);
            
            
            if (i % 2 == 1) {
                // deal with fertility parts
                cout << "Calculating births for ethnicity " << i/2 << endl;
                auto [male_births, female_births] = calculateBirths(combined_popu, fertility_matrix, i/2);

                // print the male and female births
                cout << "Male births: " << male_births.transpose() << endl;
                cout << "Female births: " << female_births.transpose() << endl;
                
                // generate population from births 
                while (female_births.sum() > 0) {
                    // male
                    MatrixXi male_popu = generatePopuFromBirth(male_births);
                    male_popu = forecast_death(male_popu, mortality_mat, 0); // 0 for male
                    population_matrices[i-1].push_back(male_popu);

                    // female  
                    MatrixXi female_popu = generatePopuFromBirth(female_births);
                    female_popu = forecast_death(female_popu, mortality_mat, 1); // 1 for female
                    population_matrices[i].push_back(female_popu);

                    // Check births between 2024-2035 (first 12 years)
                    // We only care about births before 2035 since those born after won't reach fertility age by 2050
                    if (female_births.segment(0, 12).sum() == 0) break;

                    // update births for next iteration
                    std::tie(male_births, female_births) = calculateBirths(female_popu, fertility_matrix, i/2);
                    // print the male and female births
                    cout << "Male births: " << male_births.transpose() << endl;
                    cout << "Female births: " << female_births.transpose() << endl;
                }
            }
        }

        // Create timestamp-based directory with random number
        auto now = chrono::system_clock::now();
        time_t now_time = chrono::system_clock::to_time_t(now);
        stringstream ss;
        ss << put_time(localtime(&now_time), "%Y%m%d_%H%M%S");
        string timestamp = ss.str();
        
        // Generate 4-digit random number
        random_device rd;
        mt19937 gen(rd());
        uniform_int_distribution<> dis(1000, 9999);
        int random_num = dis(gen);
        
        string output_dir = "output/Forecast/" + timestamp + "_" + to_string(random_num) ;
        filesystem::create_directories(output_dir);


        // Create popu subdirectory
        string popu_dir = output_dir + "/popu";
        filesystem::create_directories(popu_dir);

        // save the population matrices to csv
        for (int i = 0; i < 8; i++) {
            string filename = popu_dir + "/forecast_matrix_" + to_string(i) + ".bin";
            ofstream file(filename, ios::binary);
            if (!file) {
                throw runtime_error("Error opening file: " + filename);
            }

            // Write each matrix in population_matrices[i]
            for (int j = 0; j < population_matrices[i].size(); j++) {
                const MatrixXi& popu = population_matrices[i][j];
                
                // Write matrix data
                for (int r = 0; r < popu.rows(); r++) {
                    for (int c = 0; c < popu.cols(); c++) {
                        int32_t val = popu(r,c);
                        file.write(reinterpret_cast<char*>(&val), sizeof(int32_t));
                    }
                }
            }
            file.close();
        }
        return 0;
    } catch (const exception& e) {
        cerr << "Error in main: " << e.what() << endl;
        return 1;
    }
}
