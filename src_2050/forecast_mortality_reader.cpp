#include "forecast_mortality_reader.h"
#include "utils_2050.h"
#include <iostream>
#include <fstream>
#include <filesystem>

using namespace std;

vector<vector<vector<double>>> readForecastMortalityMatrix(const string& filename) {
    if (!fileExists(filename)) {
        throw runtime_error("File does not exist: " + filename);
    }

    ifstream file(filename, ios::binary);
    if (!file) {
        throw runtime_error("Error opening file: " + filename);
    }

    // Create a 3D vector to store the matrix (2x18x27)
    // Dimensions are: [gender][age_group][year]
    vector<vector<vector<double>>> matrix(2,
        vector<vector<double>>(18,
            vector<double>(27)));
    
    // Read the data directly into the matrix
    // i: gender index (2 genders)
    // j: age group index (18 groups)
    // k: year index (27 years)
    // The order of loops matches how the data is laid out in the binary file
    for(int i = 0; i < 2; i++) {
        for(int j = 0; j < 18; j++) {
            for(int k = 0; k < 27; k++) {
                double value;
                file.read(reinterpret_cast<char*>(&value), sizeof(double));
                matrix[i][j][k] = value / 1000.0;
            }
        }
    }

    file.close();
    return matrix;
}

// Test function to verify the reading
void printMatrixPreview(const vector<vector<vector<double>>>& matrix) {
    cout << "First few elements of the matrix:" << endl;
    // Print in the same order as we read (i,j,k)
    // i: iterates through gender (0-1)
    // j: iterates through first 3 age groups (0-2)
    // k: iterates through first 3 years (0-2)
    for(int i = 0; i < 2; i++) {
        cout << "Matrix for gender " << i << ":" << endl;
        for(int j = 0; j < 18; j++) {
            for(int k = 0; k < 27; k++) {
                // matrix[i][j][k] accesses: gender i, age_group j, year k
                cout << matrix[i][j][k] << " ";
            }
            cout << endl;
        }
        cout << endl;
    }

    cout << "Total elements: " << 2 * 18 * 27 << endl;
    cout << "Total size in bytes: " << 2 * 18 * 27 * sizeof(double) << endl;
}

// int main() {
//     try {
//         auto matrix = readForecastMortalityMatrix();
//         printMatrixPreview(matrix);
//         return 0;
//     } catch (const exception& e) {
//         cerr << "Error: " << e.what() << endl;
//         return 1;
//     }
// } 