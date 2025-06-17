#include "../include/forecast_fertility.h"
#include "../include/utils_2050.h"
#include <iostream>
#include <fstream>
#include <filesystem>
#include <iomanip>
#include <limits>
#include <Eigen/Dense>

using namespace std;
using namespace Eigen;

vector<vector<vector<double>>> readFertilityMatrix(const string& filename) {
    if (!fileExists(filename)) {
        throw runtime_error("File does not exist: " + filename);
    }

    ifstream file(filename, ios::binary);
    if (!file) {
        throw runtime_error("Error opening file: " + filename);
    }

    // Create a 3D vector to store the matrix (12x71x35)
    // Dimensions are: [matrix_index][age_group][year]
    vector<vector<vector<double>>> matrix(12,
        vector<vector<double>>(71,
            vector<double>(35)));
    
    // Read the data directly into the matrix
    for(int i = 0; i < 12; i++) {
        for(int j = 0; j < 71; j++) {
            for(int k = 0; k < 35; k++) {
                double value;
                file.read(reinterpret_cast<char*>(&value), sizeof(double));
                matrix[i][j][k] = value;
            }
        }
    }

    file.close();
    return matrix;
}

float MapFertilityRate(int index, int year, int age, const vector<vector<vector<double>>>& fertility_rates) {
  if (age < 15 || age >= 49) {
    return 0.0f;
  }
  return fertility_rates[index][year - 1980][age - 15];
}

void printFertilityMatrixPreview(const vector<vector<vector<double>>>& matrix) {
    // Print fertility rates for index 0, year 2023, ages 15-49
    cout << "Fertility rates for index 0, year 2023, ages 15-49:" << endl;
    cout << "------------------------------------------------" << endl;
    cout << "Age\tRate" << endl;
    cout << "---\t----" << endl;

    int year_idx = 2023 - 1980; // Convert year to index
    
    for (int age = 15; age < 50; ++age) {
        cout << age << "\t" 
             << fixed << setprecision(4) 
             << matrix[0][year_idx][age - 15] << endl;
    }
}

std::pair<VectorXi, VectorXi> calculateBirths(
    const MatrixXi& popu_mat,
    const vector<vector<vector<double>>>& fertility_rates,
    int fertility_index) {
    
    const int rows = popu_mat.rows();
    const int cols = popu_mat.cols();
    
    // Step 1: Create fertility rate matrix
    MatrixXd fertility_mat = MatrixXd::Zero(rows, cols);
    
    // Map ages to fertility rates
    for(int i = 0; i < rows; i++) {
        for(int j = 0; j < cols; j++) {
            int age = popu_mat(i, j);
            if(age >= 15 && age < 49) {
                int year_idx = j + 2024 - 1980;  // Convert year to index
                fertility_mat(i, j) = fertility_rates[fertility_index][year_idx][age - 15];
            }
        }
    }
    
    // Step 2: Generate random matrix and determine births
    MatrixXd random_mat = MatrixXd::Random(rows, cols);
    random_mat = (random_mat + MatrixXd::Ones(rows, cols)) / 2.0;  // Transform to [0,1]
    
    // Determine births (1 if random < fertility rate, 0 otherwise)
    MatrixXi births = (random_mat.array() < fertility_mat.array()).cast<int>();
    
    // Step 3: Calculate column sums and split into male/female births
    VectorXd total_births = births.colwise().sum().cast<double>();
    
    // Calculate male and female births using the given ratio
    const double male_ratio = 1.06 / (1.0 + 1.06);
    const double female_ratio = 1.0 / (1.0 + 1.06);
    
    VectorXi male_births = (total_births * male_ratio).cast<int>();
    VectorXi female_births = (total_births * female_ratio).cast<int>();
    
    return {male_births, female_births};
}


MatrixXi generatePopuFromBirth(const VectorXi& births) {
    // births: length 27, each entry is number of births in that year
    // Output: population matrix with sum(births) rows, 27 columns

    int total_agents = births.sum();
    int years = births.size();
    MatrixXi agents_mat = MatrixXi::Constant(total_agents, years, -1);

    int current_row = 0;
    for (int year = 0; year < years; ++year) {
        int num_births = births[year];
        if (num_births == 0) continue;

        // For these agents, they are born in 'year', so their age in year is 0, in year+1 is 1, etc.
        // Create a matrix of shape (num_births, years - year), all 0
        MatrixXi age_mat = MatrixXi::Constant(num_births, years - year, 0);

        // Create a row vector and replicate it for all rows at once
        RowVectorXi year_progression = RowVectorXi::LinSpaced(years - year, 0, years - year - 1);
        MatrixXi batch_mat = year_progression.replicate(num_births, 1);

        // Place this batch in the correct block of the agents matrix
        agents_mat.block(current_row, year, num_births, years - year) = batch_mat;

        current_row += num_births;
    }

    return agents_mat;
}