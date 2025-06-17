#include <iostream>
#include <fstream>
#include <vector>

int main() {
    // Open the binary file
    std::ifstream file("../preprocess_py/mortality_forecast_from_24.bin", std::ios::binary);
    if (!file) {
        std::cerr << "Error opening file" << std::endl;
        return 1;
    }

    // Create a 3D vector to store the matrix (2x18x27)
    std::vector<std::vector<std::vector<double>>> matrix(2, 
        std::vector<std::vector<double>>(18, 
            std::vector<double>(27)));
    
    // Read the data directly into the matrix
    for(int i = 0; i < 2; i++) {
        for(int j = 0; j < 18; j++) {
            for(int k = 0; k < 27; k++) {
                file.read(reinterpret_cast<char*>(&matrix[i][j][k]), sizeof(double));
            }
        }
    }

    // Print the first few elements to verify
    std::cout << "First few elements of the matrix:" << std::endl;
    for(int i = 0; i < 2; i++) {
        for(int j = 0; j < 3; j++) {
            for(int k = 0; k < 3; k++) {
                std::cout << matrix[i][j][k] << " ";
            }
            std::cout << std::endl;
        }
        std::cout << std::endl;
    }

    file.close();
    return 0;
}