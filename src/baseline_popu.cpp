#include <iostream>
#include <fstream> // for reading file 
#include <vector>
#include <unistd.h> 
#include <Eigen/Dense>
#include <EigenRand/EigenRand>
#include <cmath>
// for random matrix generation 
using namespace std;
using namespace Eigen;

// global variable 
int num_years = 34; // from 1990 - 2023

vector<vector<vector<double>>> read_binary_file(const string& filename, int n_ary, int rows, int cols) {
    // Initialize the 3D vector
    vector<vector<vector<double>>> result_matrix n_ary, 
        vector<vector<double>>(rows, vector<double>(cols)));

    std::array<std::array<double, 4>, 3> arr;

    // Open the file in binary mode
    ifstream file(filename, ios::binary);
    if (!file) {
        cerr << "Error opening file: " << filename << endl;
        return result_matrix; // Return empty result if file not found
    }

    // Read data from the file
    file.read(reinterpret_cast<char*>(&result_matrix[0][0][0]), n_ary * rows * cols * sizeof(double));

    // Close the file
    file.close();

    return result_matrix;
}


MatrixXi generate_death_tre(const VectorXi& ages, const MatrixXd& death_age_matrix) {
    // Input: ages vector (Eigen vector), shape 86 
    // death_age_matrix (Eigen matrix) 86 * 34; 
    // Output: comparison matrix (Eigen matrix of ints in 1990 )

    int total_rows = ages.sum();
    int start_index = 0;

    MatrixXi result(total_rows, 34);
    MatrixXd randMatrix = Rand::balanced<MatrixXf>(total_rows, 34, urng,0,1);
    for (int i = 0; i < ages.size(); ++i) {
        int num = ages[i];
        if (num > 0) {

            VectorXd vec = death_age_matrix.row(i);
            // ?? type double or type float 
            // Compare the block and assign result
            result.block(start_index, 0, num, 34) = 
                (randMatrix.block(start_index, 0, num, 34).array() 
                <= vec.transpose().array())
                .cast<int>();
            
            // Update the start index for the next section
            start_index += num;


        }
        return result;
    }




}
// Eigen matrix generate_death_tre(ages,death_age_matrix){
//     // input ages vector of Eigen vector , eigen matrix  

//     // output eigen matrix 
//     // convert below python code to cpp code 
//     age_matrix = np.arange(10) + ages[:, None]
//     category_matrix = age_matrix / 5
//     // Step 3: Bound the values by len(average_death_rates) - 1
//     category_matrix = np.minimum(category_matrix, len_death - 1)
//     //Step 4: Map these bounded categories to the average death rates
//     death_age_matrix 

//     // get the death age
//     random_matrix = np.random.rand(num,10)

//     comparison_matrix = (random_matrix < death_age_matrix).astype(int)

//     return comparison_matrix;

// }

ArrayXXi scaleMatrix(const ArrayXXi& mat, float scale) {
    return (mat.cast<float>() * scale).array().round().cast<int>();
}

float mock_scale = 0.05;
int target_end = 2023;

int main() {
    // start reading 
    // chn, mal, ind, oth  * male,fem ;0 - 85, 85+ ;1990 - 2024
    double popu_mat[8][86][35];


    ifstream file("../result_matrix_data.bin", ios::binary);
    file.read(reinterpret_cast<char*>(&popu_mat[0][0][0]), sizeof(popu_mat));
    file.close();

    



    std::vector<Eigen::MatrixXi> mock_popu_mat(8);  // Initialize a vector of 8 Eigen::MatrixXd

    // Assuming popu_mat is a 3D array of doubles (8 x 86 x 35)
    for (int i = 0; i < 8; ++i) {
        mock_popu_mat[i] = Eigen::MatrixXi(86, 35);  // Resize the Eigen matrix to 86 x 35 for each index

        for (int j = 0; j < 86; ++j) {
            for (int k = 0; k < 35; ++k) {
                mock_popu_mat[i](j, k) = std::round(popu_mat[i][j][k] * mock_scale);  // Use Eigen's () operator for matrix element access
            }
        }
    }
    

    // eth * gen ; 0 - 85, 85+ ;1990 - 2023
    vector<ArrayXXf> mor_eig_mat(8, ArrayXXf(86, 34));
    file.open("../data/bin/disappear.bin", ios::binary);
    if (file.is_open()) {
        for (int i = 0; i < 8; ++i) {
            file.read(reinterpret_cast<char*>(mor_eig_mat[i].data()), 86 * 34 * sizeof(float));
        }
        file.close();
    } else {
        cerr << "Failed to open death_by_cohort.bin" << endl;
        return -1;
    }

    // (chn, mal,ind,oth) * (mean, upper, lower)
    // 1980 - 2050; age 15 - 49 
    float fer_mat[12][71][35];
    ifstream file("../data/bin/AESFR_matrix_combine.bin", ios::binary);
    file.read(reinterpret_cast<char*>(&fer_mat[0][0][0]),sizeof(fer_mat));
    file.close();
    vector<MatrixXf> fer_mat(12, MatrixXf(71, 35));
    
    // Open the binary file
    ifstream file("../data/bin/migration_in.bin", ios::binary);
    if (!file) {
        cerr << "Error opening file." << endl;
        return 1;
    }

    // migration for year 1990 - 2023 
    vector<MatrixXf> immi_mat(8, MatrixXf(86,34));
    ifstream file("../data/bin/migration_in.bin", ios::binary);
    for (int i = 0; i < 8; ++i) {
            file.read(reinterpret_cast<char*>(immi_mat[i].data()), 86 * 34 * sizeof(float));
            immi_mat[i] = scaleMatrix(immi_mat[i], mock_scale);
        }
    file.close();

    
    // Emigration matrix (emigrate_mat)
    //// (8, 119, 34)
    vector<ArrayXXf> disappear_mat(8, ArrayXXf(119, 34));
    file.open("../data/bin/mig_disappear.bin", ios::binary);
    if (file.is_open()) {
        for (int i = 0; i < 8; ++i) {
            file.read(reinterpret_cast<char*>(disappear_mat[i].data()), 86 * 34 * sizeof(float));

            // Element-wise addition with mortality matrix
            disappear_mat[i] += mor_eig_mat[i % 2];
        }
        file.close();
    } else {
        cerr << "Failed to open emigrate.bin" << endl;
        return -1;
    }

    // (8, 119, 34)

    int end_idx = target_end - 1990;

    // generate population index matrix 
    // indices and ages ; vector method 
    vector<MatrixXd> mat_list;
    int num_peo = 0;

    for (int i = 0; i < 8; ++i){
        // get 1990 age array, storing the ages 
        // popu_mat is array size 
        
        VectorXi num_by_ages = mock_popu_mat[i].col(0); // column 0
        ArrayXXi AgeMatrix;
        ArrayXXi ExistingMatrix;
        generateDeath(num_by_ages,i ,disappear_mat,AgeMatrix,ExistingMatrix);
        // deal with migration later 
        ArrayXXi MigrationMatrix;
        ArrayXXi ExistingMatrix;
        generateMigration(immi_mat[i],disappear_mat,MigrationMatrix[i]);
        
        // as final output 
        vertically combine AgeMatrix and MigrationMatrix

        if (i % 2 == 1){
            int num_childbear = num_by_ages.head(50).sum();
             // 0 - 49 years old 
            int 
        }
        MigrationMatrix[i];
        AgeMatrix 
        // intiliaze the birth matrix by Migration / ExistingMatrix
        // assume that we have birth matrix already
        // and we used colsum to get birth every year 

        VectorXi birth_per_year = repeat(20) 34 times;
        // year 1991 - 2023 
        //initialize a queue;
        // birth_queue 
        births is from  1990 to end_year - 15 
        birth_queue.add(births)
        while (!birth_queue.empty()){
            // use queue to generate death and birth matrix 
            // births from  year_a to year_b if not exist 
            // add back to birth_queue  

        }

    

        // # use ages to get death matrix as well; in this step, also get death numbers for each age strata  
        // death
        // # initialize the age matrix 
        // # initialize the fertility matrix 
        // for year in 1991 : 2023 
        //     # get age strucutre and fertility as well
        //     # calculate the data gap 
        //     # add / delete data 
        //     # get this year s data structure 
        //     # next_year_age = ...




    return 0;
    } 

    // calculate the expectation migration
    // therefore the final result may not be true 

    










    const int n_ary = 8; // 0 - 7; chn, mal, ind, oth  * 0,1 
    const int rows = 86; // 0 - 85, 85+ 
    const int cols = 35; // 1990 - 2024

    
    // Current working directory: /Users/haolong/Documents/GitHub/demos_v_matrix/src

    // binary file
    vector<vector<vector<double>>> popu_matrix = read_binary_file("../result_matrix_data.bin", n_ary, rows, cols);
    // binary file; mortality rate 
    vector<vector<vector<double>>> death_by_cohort = read_binary_file("../data/bin/death_by_cohort.bin", 2, rows, 34);
    
    death_by_cohort = death_by_cohort;
    // read npy file is not good
    //vector<vector<vector<double>>> result_matrix = read_binary_file("../result_matrix.npy", n_ary, rows, cols);

    // Test: print the first element of the matrix
    cout << "third element: " << popu_matrix[0][0][2] << endl;

    // Define the random number generator with a specific seed
    // random engine 
    // ask hu gang where to put this line 
    Rand::P8_mt19937_64 urng{42}; // Use a seed of 42 for reproducibility

    // read the files and generate 8 information matrix 
    // 
    // initialize a list of length 8 to put matrix in 
    death_list = list(8)
    VectorXi ages(86) 
    for (int i = 0; i < 8; ++i){
        // get 1990 age array, storing the ages 
        
        ages = popu_matrix[i][:][0]; // column 0
        deathmatrix = death_by_cohort[i/2]; // 0 means male ; 1 means female
        death_matrix = generate_death_tre(ages,deathmatrix);
        death_list[i] = death_matrix

    } 
    // consider the newborn, and net migration the next year



    

    return 0;
}


	