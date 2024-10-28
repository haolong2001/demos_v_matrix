#include <iostream>
#include <fstream>
#include <Eigen/Dense>

int main() {
    // Create a 2x2 matrix and initialize it
    Eigen::ArrayXi arrange(10);
    Eigen::ArrayXXf  m(2,2);
    Eigen::Matrix2d matrix;
    matrix(0, 0) = 1;
    matrix(0, 1) = 2;
    matrix(1, 0) = 3;
    matrix(1, 1) = 4;

    std::cout << "Here is the matrix:\n" << matrix << std::endl;

    // Perform a simple operation (matrix addition)
    Eigen::Matrix2d matrix2;
    matrix2 << 5, 6, 7, 8;

    Eigen::Matrix2d result = matrix + matrix2;

    std::cout << "The result of matrix addition is:\n" << result << std::endl;

    

    // check current directory code 
    char cwd[1024];
    if (getcwd(cwd, sizeof(cwd)) != NULL) {
        cout << "Current working directory: " << cwd << endl;
    } else {
        cerr << "Error getting current working directory" << endl;
    }

    return 0;
}
// test eigen 
//  in terminal, use ./ to run the code 


// firstly put in the same file