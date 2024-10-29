#include <iostream>
#include <vector>
#include <memory>       // For smart pointers
#include <Eigen/Dense>

int main() {
    // Vector to store pointers to Eigen matrices
    std::vector<std::shared_ptr<Eigen::MatrixXd>> matrices;

    // Known number of columns
    const int numCols = 3;

    // Simulate a while loop generating matrices
    int count = 0;  // Just for demonstration; in your case, this would be your loop condition
    while (count < 5) {
        // Dynamically create a matrix with varying number of rows
        int numRows = count + 1;  // For demonstration, rows increase each iteration
        auto matrixPtr = std::make_shared<Eigen::MatrixXd>(numRows, numCols);

        // Fill the matrix with some values
        *matrixPtr = Eigen::MatrixXd::Random(numRows, numCols);

        // Store the pointer to the matrix in the vector
        matrices.push_back(matrixPtr);

        ++count;
    }

    // Now, stack all matrices vertically
    // First, calculate the total number of rows
    int totalRows = 0;
    for (const auto& matPtr : matrices) {
        totalRows += matPtr->rows();
    }

    // Create the result matrix
    Eigen::MatrixXd stackedMatrix(totalRows, numCols);

    // Copy each matrix into the result matrix
    int currentRow = 0;
    for (const auto& matPtr : matrices) {
        int rows = matPtr->rows();
        stackedMatrix.block(currentRow, 0, rows, numCols) = *matPtr;
        currentRow += rows;
    }

    // Output the final stacked matrix
    std::cout << "Stacked Matrix:" << std::endl;
    std::cout << stackedMatrix << std::endl;

    return 0;
}
// The Eigen library's operator overloading for << 
// does not support passing a vector of matrices or an unknown number of arguments
