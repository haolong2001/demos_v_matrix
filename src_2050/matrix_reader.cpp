#include "matrix_reader.h"
#include "../include/utils_2050.h"
#include <filesystem>

using namespace std;

// /**
//  * MatrixReader class provides functionality to read and process 3D matrices from binary and CSV files.
//  * The matrices are stored as vectors of vectors of vectors of doubles.
//  */

// /**
//  * Reads a 3D matrix from a binary file.
//  * @param filename Path to the binary file
//  * @param dim1 First dimension size (number of matrices)
//  * @param dim2 Second dimension size (number of rows per matrix)
//  * @param dim3 Third dimension size (number of columns per row)
//  * @return 3D vector containing the matrix data
//  * @throws runtime_error if file doesn't exist or can't be opened
//  */
// vector<vector<vector<double>>> MatrixReader::readBinaryMatrix(
//     const string& filename,
//     int dim1,
//     int dim2,
//     int dim3
// ) {
//     // Check if file exists before attempting to read
//     if (!fileExists(filename)) {
//         throw runtime_error("File does not exist: " + filename);
//     }

//     // Open file in binary mode
//     ifstream file(filename, ios::binary);
//     if (!file) {
//         throw runtime_error("Error opening file: " + filename);
//     }

//     // Initialize 3D vector with specified dimensions
//     vector<vector<vector<double>>> matrix(
//         dim1, vector<vector<double>>(dim2, vector<double>(dim3))
//     );

//     // Read binary data into matrix
//     for(int i = 0; i < dim1; i++) {
//         for(int j = 0; j < dim2; j++) {
//             for(int k = 0; k < dim3; k++) {
//                 file.read(reinterpret_cast<char*>(&matrix[i][j][k]), sizeof(double));
//             }
//         }
//     }

//     file.close();
//     return matrix;
// }

/**
 * Reads a 2D matrix from a CSV file.
 * @param filename Path to the CSV file
 * @param delimiter Character used to separate values in the CSV
 * @return 2D vector containing the matrix data
 * @throws runtime_error if file doesn't exist, can't be opened, or contains invalid data
 */
vector<vector<double>> MatrixReader::readCSVMatrix(
    const string& filename,
    char delimiter
) {
    // Validate file existence
    if (!fileExists(filename)) {
        throw runtime_error("File does not exist: " + filename);
    }

    // Open CSV file
    ifstream file(filename);
    if (!file) {
        throw runtime_error("Error opening file: " + filename);
    }

    vector<vector<double>> matrix;
    string line;

    // Parse CSV file line by line
    while (getline(file, line)) {
        if (line.empty()) continue;

        vector<double> row;
        stringstream ss(line);
        string value;

        // Parse each value in the current line
        while (getline(ss, value, delimiter)) {
            try {
                row.push_back(stod(value));
            } catch (const exception& e) {
                throw runtime_error("Error parsing value in CSV: " + value);
            }
        }

        matrix.push_back(row);
    }

    file.close();
    return matrix;
}

/**
 * Prints a preview of the 2D matrix to standard output.
 * @param matrix The 2D matrix to preview
 * @param preview_rows Number of rows to show
 * @param preview_cols Number of columns to show for each row
 */
void MatrixReader::printMatrixPreview(
    const vector<vector<double>>& matrix,
    int preview_rows,
    int preview_cols
) {
    cout << "Matrix Preview:" << endl;
    for (int i = 0; i < preview_rows && i < matrix.size(); i++) {
        for (int j = 0; j < preview_cols && j < matrix[i].size(); j++) {
            cout << matrix[i][j] << " ";
        }
        cout << endl;
    }
    cout << endl;
}

/**
 * Checks if a file exists at the specified path.
 * @param filename Path to check
 * @return true if file exists, false otherwise
 */
bool MatrixReader::fileExists(const string& filename) {
    return ::fileExists(filename);
} 