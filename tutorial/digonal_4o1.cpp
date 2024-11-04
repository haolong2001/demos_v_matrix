#include <iostream>
#include <Eigen/Dense>

int main()
{
    // Define a 4x5 matrix and initialize it with random values
    Eigen::MatrixXd A(4, 5);
    A.setRandom();

    // Print the original 4x5 matrix
    std::cout << "Original Matrix A:\n" << A << "\n\n";

    // Initialize a 9x5 matrix to store the diagonals
    Eigen::MatrixXd B = Eigen::MatrixXd::Zero(9, 5);

    // Loop over diagonal offsets from -4 to 4
    for (int offset = -4; offset <= 4; ++offset)
    {
        int row = offset + 4; // Map offset range [-4,4] to row index [0,8]

        // Check if the offset is valid for the given matrix dimensions
        if (offset >= -3 && offset <= 4)
        {
            // Extract the diagonal with the given offset
            Eigen::VectorXd diag = A.diagonal(offset);

            // Copy the diagonal into the corresponding row in B, left-aligned
            B.row(row).head(diag.size()) = diag.transpose();
        }
        // Remaining entries in B.row(row) are already zero-initialized
    }

    // Print the resulting 9x5 matrix
    std::cout << "Diagonal Matrix B:\n" << B << std::endl;

    return 0;
}
