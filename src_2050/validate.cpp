









#include "validate.h"

void calculate_popu(const ArrayXXi& ind_age_mat, ArrayXXi& popu) {
    // Iterate through each row and column
    for(int i = 0; i < ind_age_mat.rows(); i++) {
        for(int j = 0; j < ind_age_mat.cols(); j++) {
            // std::cout <<"age j " << ind_age_mat(i, j) << " " << j << std::endl;

            int value = ind_age_mat(i, j);
            
            if (value > 84) {
                popu(85, j) += 1;
            }
            else if (value >= 0) {  // Assuming negative values should be ignored
                popu(value, j) += 1;
            }
        }
    }
}

// int main() {
//     // Create a sample individual age matrix (5 individuals, 3 time points)
//     ArrayXXi ind_age_mat(5, 3);
//     ind_age_mat << 0, 1, 2,  // First individual ages over time
//                    1, 2, 3,  // Second individual
//                    0, 1, 2,  // Third individual
//                    2, 3, 4,  // Fourth individual
//                    1, 2, 3;  // Fifth individual
    
//     // Create population matrix (max_age + 1 rows, same columns as ind_age_mat)
//     int max_age = ind_age_mat.maxCoeff();
//     ArrayXXi popu = ArrayXXi::Zero(max_age + 1, ind_age_mat.cols());
    
//     // Calculate population counts
//     calculate_popu(ind_age_mat, popu);
    
//     // Print results
//     cout << "Individual age matrix:\n" << ind_age_mat << "\n\n";
//     cout << "Population counts by age and time:\n" << popu << endl;
    
//     return 0;
// }