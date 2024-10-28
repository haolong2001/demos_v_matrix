


#include <Eigen/Dense>
#include <random>
#include <iostream>
using namespace Eigen;

/**
 * @brief Generates a migration matrix and updates an existing population matrix.
 *
 * @param MigNumMat       Matrix containing migration numbers.
 * @param disappear_mat   Matrix containing disappearance rates.
 * @param ExistingMatrix  Matrix to update with generated migration data.
 * @param MigAgeMatrix    Matrix for age-related migration (currently unused).
 */
void generateMigration(
    const ArrayXXi& MigNumMat,
    const ArrayXXf& disappear_mat,
    ArrayXXi& ExistingMatrix,
    ArrayXXi& MigAgeMatrix
) {
    const int ncols = 34; // Total number of columns (could represent years). TODO: Confirm with Gang
    const int nrows = 86; // Represents the number of age groups

    int start = 0;       // Starting index for the block in ExistingMatrix
    int sub_immi_num = 0; // Sum of migrants in a particular year
    int num = 0;         // Number of migrants in a specific age group
    int idx = 0;         // Adjusted index for accessing disappearance rates

    ArrayXf rate;        // Array to store disappearance rates for a specific group
    ArrayXXf temp;       // Temporary array to store replicated disappearance rates

    // Iterate through each year starting from the second column
    for (int i = 1; i < ncols; ++i) {
        ArrayXi vec = MigNumMat.col(i);
        sub_immi_num = vec.sum();

        // Set a block of the ExistingMatrix to -1 to mark migrants
        ExistingMatrix.block(start, 0, sub_immi_num, i) = -1;

        // Iterate through each age group
        for (int j = 0; j < nrows; ++j) {
            num = vec[j];
            idx = j - i + 33; // Equivalent to j - i age, adjusted for indexing

            if (idx < 0 || idx >= disappear_mat.rows()) {
                continue; // Skip if the index is out of bounds
            }

            // Extract disappearance rates for the corresponding age group and year
            rate = disappear_mat.block(idx, i, 1, ncols - i);
            
            // Replicate the rate for the number of migrants and transpose
            temp = rate.replicate(1, num).transpose();

            // Generate random values for comparison
            std::random_device rd;
            std::mt19937 urng(rd());
            ArrayXXf random_values = ArrayXXf::Random(num, ncols - i).unaryExpr([](float val) { return (val + 1.0f) / 2.0f; });

            // Update the ExistingMatrix with migration data based on disappearance rates
            ExistingMatrix.block(start, i + 1, num, ncols - i) = (temp <= random_values).cast<int>();
        }
    }
}


// Example to test the function
int main() {
    // Define small matrices for testing
    ArrayXXi MigNumMat(3, 4);
    MigNumMat << 1, 2, 0, 1,
                 0, 1, 3, 0,
                 2, 0, 1, 2;

    ArrayXXf disappear_mat(3, 4);
    disappear_mat << 0.1f, 0.2f, 0.3f, 0.4f,
                     0.5f, 0.6f, 0.7f, 0.8f,
                     0.9f, 0.1f, 0.2f, 0.3f;

    ArrayXXi ExistingMatrix = ArrayXXi::Zero(10, 4);
    ArrayXXi MigAgeMatrix = ArrayXXi::Zero(3, 4); // Currently unused


    ArrayXXi ExistingMatrix = ArrayXXi::Zero(10, 4);
    ArrayXXi MigAgeMatrix = ArrayXXi::Zero(3, 4); // Currently unused

    // Call the function
    generateMigration(MigNumMat, disappear_mat, ExistingMatrix, MigAgeMatrix);

    // Print the updated ExistingMatrix
    std::cout << "Updated ExistingMatrix:\n" << ExistingMatrix << std::endl;

    return 0;
}
