#include <iostream>
#include <fstream>
#include <vector>
#include <Eigen/Dense>

using Eigen::ArrayXXi;


int main() {
    // Vector to store all matrices from all files
    std::vector<ArrayXXi> age_matrix_vec;

    size_t num_files = 8; // Change this to the actual number of files to read
    for (size_t i = 0; i < num_files; ++i) {
        // Create the filename dynamically
        std::string filename = "output/popu_matrix_" + std::to_string(i) + ".csv";
        
        // Open the file for reading
        std::ifstream file(filename);
        if (!file.is_open()) {
            std::cerr << "Error opening file: " << filename << std::endl;
            return 1; // Exit with error
        }

        std::vector<std::vector<int>> matrix_data; // To store the CSV data temporarily
        std::string line;
        
        // Read the entire file line by line
        while (std::getline(file, line)) {
            if (!line.empty()) {
                std::vector<int> row_data;
                std::stringstream ss(line);
                std::string value;
                while (std::getline(ss, value, ',')) {
                    row_data.push_back(std::stoi(value));
                }
                matrix_data.push_back(row_data);
            }
        }

        // Convert the CSV data into an Eigen::ArrayXXi matrix
        if (!matrix_data.empty()) {
            int rows = matrix_data.size();
            int cols = matrix_data[0].size();
            ArrayXXi matrix(rows, cols);
            for (int row = 0; row < rows; ++row) {
                for (int col = 0; col < cols; ++col) {
                    matrix(row, col) = matrix_data[row][col];
                }
            }
            age_matrix_vec.push_back(matrix);
            std::cout << "Successfully read matrix from " << filename << std::endl;
        } else {
            std::cerr << "Warning: No data found in " << filename << std::endl;
        }
   

        file.close();
   
    }

    std::cout << "Successfully read " << age_matrix_vec.size() << " files." << std::endl;
    return 0;
}




// ArrayXXi readBinaryMatrix(const std::string& filename) {
//     std::ifstream file(filename, std::ios::binary);
//     if (!file.is_open()) {
//         std::cerr << "Error opening file: " << filename << std::endl;
//         exit(1);
//     }

//     // Read dimensions of the matrix
//     int rows, cols;
//     file.read(reinterpret_cast<char*>(&rows), sizeof(int));
//     file.read(reinterpret_cast<char*>(&cols), sizeof(int));

//     // Resize the matrix and read its data
//     ArrayXXi matrix(rows, cols);
//     file.read(reinterpret_cast<char*>(matrix.data()), rows * cols * sizeof(int));

//     file.close();
//     return matrix;
// }


// int main() {
//     std::vector<ArrayXXi> age_matrix_vec; // Vector to store all the matrices

//     size_t num_files = 8; // Replace this with the actual number of files
//     for (size_t i = 0; i < num_files; ++i) {
//         // Create the file name dynamically
//         std::string filename = "output/popu_matrix_" + std::to_string(i) + ".bin";
        
//         // Read the matrix from the binary file
//         ArrayXXi matrix = readBinaryMatrix(filename);
        
//         // Store the matrix in the vector
//         age_matrix_vec.push_back(matrix);
//     }

//     // Optional: Log the contents of the first matrix to a log file
//     std::ofstream log_file("matrix_log.txt");
//     if (!log_file.is_open()) {
//         std::cerr << "Error opening log file: matrix_log.txt" << std::endl;
//         return 1;
//     }

//     log_file << "First matrix from the file: \n";
//     log_file << age_matrix_vec[0] << std::endl;

//     log_file.close();
//     std::cout << "Matrix successfully logged to matrix_log.txt" << std::endl;


//     return 0;
// }
