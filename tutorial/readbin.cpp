#include <iostream>
#include <fstream>
#include <string>

using namespace std;

// Function to read the 3D matrix from a binary file
template <typename T, size_t N, size_t M, size_t P>
void readMatrixFromFile(T (&matrix)[N][M][P], const string& filepath) {
    // Open the binary file for reading
    ifstream file(filepath, ios::binary);

    // Check if the file was opened successfully
    if (!file) {
        cerr << "Could not open the file!" << endl;
        return;
    }

    // Read the binary file into the matrix using the size of the entire matrix
    file.read(reinterpret_cast<char*>(&matrix[0][0][0]), sizeof(matrix));

    // Close the file
    file.close();
}

int main() {
    // Declare a 3D array of size 2x3x4 (or any size)
    double test_mat[2][3][4];
    string filename = "matrix_double.bin";
    
    // Call the function to read the matrix from the file
    readMatrixFromFile(test_mat, filename);

    // Print the matrix layer by layer
    for (int i = 0; i < 2; ++i) {  // Size of the first dimension
        cout << "Layer " << i + 1 << ":" << endl;
        for (int j = 0; j < 3; ++j) {  // Size of the second dimension
            for (int k = 0; k < 4; ++k) {  // Size of the third dimension
                cout << test_mat[i][j][k] << " ";
            }
            cout << endl;
        }
        cout << endl;
    }

    return 0;
}
