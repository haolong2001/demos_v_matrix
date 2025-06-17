#include "matrix_reader.h"
#include <vector>
#include <string>
#include <iostream>
#include <Eigen/Dense>
#include <algorithm>

using namespace std;
using namespace Eigen;

// Function to read all population matrices (0-7)
vector<vector<vector<int>>> readPopulationMatrices() {
    vector<vector<vector<int>>> matrices;
    matrices.reserve(8);  // We know there are 8 matrices

    for (int i = 0; i < 8; i++) {
        string filename = "output/popu_matrix_" + to_string(i) + ".csv";
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

int main() {
    try {
        auto matrices = readPopulationMatrices();
        
        // Get the last column from matrices[0] and remove -1
        vector<int> last_column;
        for (const auto& row : matrices[0]) {
            if (!row.empty() && row.back() != -1) {
                last_column.push_back(row.back());
            }
        }
        
        // Print the 2023 age vector
        cout << "\n2023_age vector (size: " << last_column.size() << "):" << endl;
        for (size_t i = 0; i < min(size_t(5), last_column.size()); ++i) {
            cout << last_column[i] << " ";
        }
        cout << "... " << last_column.back() << endl;

        // Calculate years
        const int years = 2050 - 2024 + 1;  // 27 years
        
        // Create Eigen matrices
        MatrixXi popu_mat(last_column.size(), years);
        MatrixXi temp_mat = MatrixXi::Zero(last_column.size(), years);
        MatrixXi increase_age = MatrixXi::Zero(last_column.size(), years);
        
        // Initialize temp_mat with 2023_age values
        for (int j = 0; j < years; ++j) {
            temp_mat.col(j) = Map<VectorXi>(last_column.data(), last_column.size());
        }
        
        // Initialize increase_age matrix
        for (int j = 0; j < years; ++j) {
            increase_age.col(j).array() = j + 1;  // 1, 2, 3, ...
        }
        
        // Add matrices together
        popu_mat = temp_mat + increase_age;
        
        // Print preview of popu_mat
        cout << "\nPopulation matrix preview (first 5x5):" << endl;
        cout << popu_mat.block(0, 0, min(5, int(popu_mat.rows())), min(5, int(popu_mat.cols()))) << endl;
        
        cout << "\nMatrix dimensions: " << popu_mat.rows() << " x " << popu_mat.cols() << endl;

        return 0;
    } catch (const exception& e) {
        cerr << "Error in main: " << e.what() << endl;
        return 1;
    }
}
