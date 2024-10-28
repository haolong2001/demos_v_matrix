#include <iostream>
#include <fstream>
#include <vector>
using namespace std;


// vector<vector<vector<double>>> read_binary_file(const string& filename, int n_eth, int rows, int cols) {
//     // Initialize the 3D vector
//     vector<vector<vector<double>>> result_matrix(n_eth, 
//         vector<vector<double>>(rows, vector<double>(cols)));

//     // Open the file in binary mode
//     ifstream file(filename, ios::binary);
//     if (!file) {
//         cerr << "Error opening file: " << filename << endl;
//         return result_matrix; // Return empty result if file not found
//     }
//     // Read data from the file
//     file.read(reinterpret_cast<char*>(&result_matrix[0][0][0]), n_eth * rows * cols * sizeof(double));

//     // Close the file
//     file.close();

//     return result_matrix;
// }
#include <iostream>
#include <fstream>
#include <vector>
using namespace std;

// Function to read a binary file and load it into a 3D vector
vector<vector<vector<double>>> read_binary_file(const string& filename, int n_eth, int rows, int cols) {
    // Initialize the 3D vector
    vector<vector<vector<double>>> result_matrix(n_eth, 
        vector<vector<double>>(rows, vector<double>(cols)));

    // Open the file in binary mode
    ifstream file(filename, ios::binary);
    if (!file) {
        cerr << "Error opening file: " << filename << endl;
        return result_matrix; // Return empty result if file not found
    }

    // Read the binary data into the 3D matrix
    for (int i = 0; i < n_eth; ++i) {
        for (int j = 0; j < rows; ++j) {
            for (int k = 0; k < cols; ++k) {
                file.read(reinterpret_cast<char*>(&result_matrix[i][j][k]), sizeof(double));
            }
        }
    }

    // Close the file
    file.close();

    return result_matrix;
}

// correct version

int main() {
    double test_mat[2][3][4];
    string filename = "matrix_double.bin";
    ifstream file(filename, ios::binary);

    file.read(reinterpret_cast<char*>(&test_mat[0][0][0]), 2 * 3 * 4 * sizeof(double));

    // Close the file
    file.close();

    // Print the matrix layer by layer
    for (int i = 0; i < 2; ++i) {
        cout << "Layer " << i + 1 << ":" << endl;  // Print layer header
        for (int j = 0; j < 3; ++j) {
            for (int k = 0; k < 4; ++k) {
                cout << test_mat[i][j][k] << " ";
            }
            cout << endl;  // Newline after each row
        }
        cout << endl;  // Newline after each layer
    }

    return 0;   

}




// int main() {
//     // Define the dimensions of the matrix
//     int n_eth = 3, rows = 3, cols = 3;

//     // Open the binary file for reading
//     vector<vector<vector<double>>> my_matrix = read_binary_file("matrix_double.bin", n_eth, rows, cols);

//     // Print the entire matrix
//     for (int i = 0; i < n_eth; ++i) {
//         cout << "Layer " << i << ":" << endl;
//         for (int j = 0; j < rows; ++j) {
//             for (int k = 0; k < cols; ++k) {
//                 cout << my_matrix[i][j][k] << " ";
//             }
//             cout << endl;
//         }
//         cout << endl;
//     }

//     return 0;
// }


// 
// Function to read the 3D matrix from a binary file
// template <typename T, size_t N, size_t M, size_t P>
// void readMatrixFromFile(T (&matrix)[N][M][P], const string& filepath) {
//     // Open the binary file for reading
//     ifstream file(filepath, ios::binary);

//     // Check if the file was opened successfully
//     if (!file) {
//         cerr << "Could not open the file!" << endl;
//         return;
//     }

//     // Read the binary file into the matrix using the size of the entire matrix
//     file.read(reinterpret_cast<char*>(&matrix[0][0][0]), sizeof(matrix));

//     // Close the file
//     file.close();
// }