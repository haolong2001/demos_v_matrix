#include "../include/forecast_fertility.h"
#include <iostream>
#include <fstream>
#include <vector>
#include <iomanip>
#include <filesystem>
#include <Eigen/Dense>
#include <random>

using namespace std;
using namespace Eigen;

int main() {
    try {
        int Test = 3;
        // Load fertility matrix
        
        string filename = "data/bin/AESFR_matrix_combine.bin";
        
        // Get file size
        ifstream file(filename, ios::binary);
        if (!file) {
            cerr << "Failed to open " << filename << endl;
            return -1;
        }

        file.seekg(0, ios::end);
        size_t file_size = file.tellg();
        file.seekg(0, ios::beg);
        file.close();

        cout << "File size: " << file_size << " bytes" << endl;
        cout << "Expected size (double): " << (12 * 71 * 35 * sizeof(double)) << " bytes" << endl;
        cout << "Size of double: " << sizeof(double) << " bytes" << endl << endl;

        // Read the fertility matrix
        auto fertility_matrix = readFertilityMatrix(filename);


        if (Test == 1) {
        // Print preview and statistics
        cout << "\nFertility Rates Preview:" << endl;
        cout << "=======================" << endl;
        printFertilityMatrixPreview(fertility_matrix);

        // Print sum of fertility rates for each year
        cout << "\nYearly sums of fertility rates (scenario 0):" << endl;
        cout << "Year\tSum of Rates" << endl;
        cout << "----\t------------" << endl;
        for(int year = 2024; year <= 2050; year++) {
            int year_idx = year - 1980;
            double sum = 0.0;
            for(int age_idx = 0; age_idx < fertility_matrix[0][year_idx].size(); age_idx++) {
                sum += fertility_matrix[0][year_idx][age_idx];
            }
            cout << year << "\t" 
                 << fixed << setprecision(4) 
                 << sum << endl;
        }
        } // END OF TEST 1

        // test fertility mapping function
        // Create a population matrix for testing
        // Using a matrix with ages in fertile range (15-49)
        if (Test == 2) {
        const int num_agents = 1000;    // 100 agents
        const int num_years = 27;      // 27 years
        MatrixXi popu_mat = MatrixXi::Constant(num_agents, num_years, 30);  // All agents age 30

        // Print fertility rates for index 0, age 30 (index 15) across all years
        
        cout << "\nFertility rates for scenario 0, age 30 across all years:" << endl;
        cout << "Year\tRate" << endl;
        cout << "----\t----" << endl;
        for(int year = 2024; year < 2051; year++) {
            cout << (year) << "\t" 
                 << fixed << setprecision(4) 
                 << fertility_matrix[0][year-1980][30 - 15] << endl;
        }
        // correct
              
        for(int idx = 0; idx < 1; idx++) {
            cout << "\nFertility Scenario " << (idx + 1) << ":" << endl;
            cout << "-------------------" << endl;
            
            auto [male_births, female_births] = calculateBirths(popu_mat, fertility_matrix, idx);
            
            // Print birth statistics
            cout << "Male births by year:   " << male_births.transpose() << endl;
            cout << "Female births by year: " << female_births.transpose() << endl;

            // Print sum of births for each year
            cout << "Sum of births by year: " << (male_births + female_births).transpose() << endl;
            cout << "Length of births: " << male_births.size() << endl;
            
            
            cout << endl;
            
        }

        } // END OF TEST 2

        // test calculateBirths
        if (Test == 3) {  
        // though small difference, still correct and pass the code. 

        // Test generatePopuFromBirth with a test vector
        VectorXi test_births = VectorXi::Constant(27, 2);
        test_births[0] = 0; // First year has 0 births

        cout << "\nTesting generatePopuFromBirth:" << endl;
        cout << "Test births vector: " << test_births.transpose() << endl;

        MatrixXi birth_popu = generatePopuFromBirth(test_births);
        
        // cout << "\nGenerated population matrix dimensions: " 
        //      << birth_popu.rows() << " rows x " 
        //      << birth_popu.cols() << " columns" << endl;

        cout << "\nFirst 5 rows of generated population matrix:" << endl;
        cout << birth_popu.topRows(10) << endl;

        return 0;
        } // END OF TEST 3


    } catch (const exception& e) {
        cerr << "Error: " << e.what() << endl;
        return 1;
    }
} 