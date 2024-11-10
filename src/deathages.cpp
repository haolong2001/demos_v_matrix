#include <iostream>
#include <Eigen/Dense>
#include <vector>
#include <EigenRand/EigenRand>

using namespace Eigen;
using namespace std;

int target_end = 2023;
int n_years = target_end - 1990;


/**
 * @param num_by_ages, gender, reference to death table 
 * deleted: @param deathNumMatrix ,MatrixXi& deathNumMatrix
 */
void generateDeath(VectorXi num_by_ages,int g, 
                   const vector<ArrayXXf>& disappear_mat,
                   ArrayXXi AgeMatrix,
                   ArrayXXi ExistingMatrix

                    ) {
    
    Rand::P8_mt19937_64 urng{42};
    int cur_start = 0;
    int n_rows = num_by_ages.sum();
    MatrixXf prob_mat(n_rows, n_years);

    for (int j = 0; j < num_by_ages.size(); ++j) {
        int num = num_by_ages[j]; // this is the number of age j
        int cur_end = cur_start + num -1;
        // construct the age matrix as well 

        // extract the mortality vector 
        VectorXf mor_vec = disappear_mat[g](j,all);

        MatrixXf replicated = mor_vec.replicate(1,num).transpose();

        prob_mat.block(cur_start, 0, num, n_years) = replicated;

        // matrix comparsion 
        // MatrixXi death_by_age =

    }
   ArrayXXf randMatrix = Rand::balanced<ArrayXXf>(n_rows, n_years, urng,0,1);

    // 1 means alive and 0 means death 
    MatrixXi result = (randMatrix.array() > prob_mat.array()).cast<int>();
    
    // delete later , make sure once death, no longer alive anymore
    for (int i = 0; i < result.rows(); ++i) {
        if (result.row(i).sum() == n_years)
            break;
        // backward finding 
        for (int j = 0; j < result.cols(); ++j) {
            if (result(i, j) == 0) {
                // Set all subsequent elements in the row to 0
                result.block(i, j, 1, result.cols() - j).setZero();
                break; // Exit the inner loop after modifying the row
            }
        }
    }

    // VectorXXf result;
}

/**
 * write a hashmap to store the death people in each year; 
 * notice that we will update the hash map/ dictionary as well. 
 */



int main() {
    // here 
    MatrixXi deathNumMatrix(86,n_years);






    // Example sizes (adjust to your actual input data)
    vector<int> num_ages = {5, 6, 4}; // Example age group sizes
    int end_idx = 3; // This represents the number of years or the end index for mortality data
    int n_rows = accumulate(num_ages.begin(), num_ages.end(), 0); // Total number of rows (sum of age group sizes)
    int n_years = end_idx + 1; // Number of years

    // Initialize the matrix to store probabilities
    MatrixXf prob_mat(n_rows, n_years); // prob_mat with dimensions [total rows, n_years]

    // Example mortality matrix mor_mat, with 2 dimensions for your use case
    // Adjust dimensions and values according to your actual data structure
    vector<vector<MatrixXf>> mor_mat(2, vector<MatrixXf>(num_ages.size(), MatrixXf::Zero(n_years, 1)));

    // Fill mor_mat with example data (replace with your actual mortality data)
    for (int i = 0; i < 2; ++i) {
        for (int j = 0; j < num_ages.size(); ++j) {
            mor_mat[i][j] = MatrixXf::Random(n_years, 1); // Random example data, replace with actual data
        }
    }

    int cur_start = 0; // Track the current start index in the prob_mat

    for (int j = 0; j < num_ages.size(); ++j) {
        int num_age = num_ages[j]; // Get the number of rows for the current age group
        int cur_end = cur_start + num_age - 1; // Calculate the end index

        // Get the mortality vector for the current age group
        MatrixXf mor_vec = mor_mat[0][j].transpose(); // Example for i = 0, adjust as needed

        // Replicate mor_vec for the number of rows (age group size)
        MatrixXf replicated_mor_vec = mor_vec.replicate(num_age, 1);

        // Assign the replicated matrix to the appropriate block in prob_mat
        prob_mat.block(cur_start, 0, num_age, n_years) = replicated_mor_vec;

        // Update the start index for the next age group
        cur_start = cur_end + 1;
    }

    // Output the resulting prob_mat for verification
    cout << "Resulting prob_mat:\n" << prob_mat << endl;

    return 0;
}
