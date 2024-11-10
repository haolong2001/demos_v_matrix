#include <iostream>
#include <fstream> // for reading file 
#include <vector>
#include <unistd.h> 
#include <Eigen/Dense>
#include <EigenRand/EigenRand>
#include <cmath>
#include <queue>
#include <memory>
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

    // initialize a vector to store the 
    // Initialize a vector of 8 elements
    std::vector<
        std::vector<
            std::shared_ptr<Eigen::MatrixXd>
                                            >> eth_matrices(8);
    for (int i = 0; i < 8; ++i){
        // get 1990 age array, storing the ages 
        // popu_mat is array size 
        std::vector<std::shared_ptr<Eigen::MatrixXd>> matrices;
        
        VectorXi num_by_ages = mock_popu_mat[i].col(0); // column 0
        ArrayXXi AgeMatrix;
        ArrayXXi ExistingMatrix;
        generateDeath(num_by_ages,i ,disappear_mat,AgeMatrix,ExistingMatrix);
        // deal with migration later 
        ArrayXXi MigrationMatrix;
        ArrayXXi ExistingMatrix;
        generateMigration(immi_mat[i],disappear_mat,MigrationMatrix[i]);
        
        // as final output 
        // vertically combine AgeMatrix and MigrationMatrix


        // generate birth from existing population
        if (i % 2 == 1){
            arrayXi births; 
            int num_childbear = num_by_ages.head(50).sum();
            // 0 - 49 years old 
            childbearMatrix = AgeMatrix.block(0,1,num_childbear,AgeMatrix.cols()-1)
            birth_matrix = generateBirth(childbearMatrix);
            births = birth_matrix.colwise().sum();
            //
            std::vector<int> childbear_sum;
            std::vector<int> rest_sum;

            // Iterate through each column starting from index 1 to the last
            for (int col = 1; col < num_col; ++col) {
                // Access the specific column
                Eigen::VectorXi current_col = immi_mat.col(col);
                
                // Calculate sum of the first 50 elements (head) and the last 36 elements (tail)
                childbear_sum.push_back(current_col.head(50).sum());
                rest_sum.push_back(current_col.tail(36).sum());
            }
          
            int start = 0;
            for (int j = 1; j < num_col; ++j) {
            // Access the block
                int index = j - 1;
                int len = childbear_sum[index];
                Eigen::MatrixXi age_mat = immi_mat.block(start, i, len, num_col - i);
                start = start + len + rest_sum[index];
                birth_matrix = generateBirth(age_mat);
                mig_births = (zeros(j), birth_matrix.colwise().sum() );// concate zero of number and birth_matrix.colsum
                
                Agematrix
                births += mig_births
            // Generate birth matrix (you need to provide implementation details here)
            // ...
            // int year = j + 1990 
            }
        // add  back to age matrix 
            males = (births * 1.06/ 2.06) .cast<int>;
            females = (births * 1.0/ 2.06) .cast<int>;

            // initialize function here 
            maleAgeMatrix = ArrayXXi( males.sum(), 2023 - 1990 + 1)
            malebirthAge = generateAgefromBirth(males);
            femalebirthAge = generateAgefromBirth(females);

            auto matrixPtr = std::make_shared<Eigen::MatrixXd>(numRows, numCols);

        // generate birth from birth 
        // intiliaze the birth matrix by Migration / ExistingMatrix
        // assume that we have birth matrix already
        // and we used colsum to get birth every year 

        // formal code for birth queue 
        queue<int> birth_queue;
        birth_queue.pushback(births);
        birth_end = 2023 - 15;
        birth_start = 1991;

        while(birth_start <= 2023 - 15){
            // birth become mother * births in the future; 
            int nrows =  birth_end - birth_start + 1 // e.g  1991 - 2008 
            int ncols = 2023 - (birth_start + 15 ) + 1 // e.g. 2006 - 2023


            arrayxxi arraybirths(nrows,ncols);

            for (i = 0; i < births.size(); ++i){
                int num_mum = births[i];
                int mig = i + 1 // mig index in existing matrix 
                
                // mig = year - 1990 
                // if go to childbearing age within our range
                if (mig  + 15 <= 33 ) {
                    ArrayXXi Newborn = ExistingMatrix.block(
                    start, mig + 15, num, 33 - (mig + 15) + 1;
                )
                    ArrayXXi ferferMat(nrows,ncols);
                    for (int col = 0; col < Newborn.cols(); ++col) {
                        for (int row = 0; row < Newborn.rows(); ++row) {
                            int age = Newborn(row, col);
                            // suppose begin 1991, then 2006 + 15 + col 
                            int year_idx = birth_start + 15 + col - 1990 ; // 16 --> 
                            int fer = MapFer(year_idx, age); // Assuming MapFer returns an int
                            ferferMat(row, col) = fer;
                        }
                    }
                    // ??? 
                    std::random_device rd;
                    std::mt19937 urng(rd());
                    ArrayXXf random_values = ArrayXXf::Random(num, ncols - i).unaryExpr([](float val) { return (val + 1.0f) / 2.0f; });

                    birthMat = (ferferMat < random_values).cast<int>();

                    newnewborn = birthMat.cols().sum();
                    // (20, 30, 40) * 1.0 / 2.06
                    males = (newnewborn * 1.06/ 2.06) .cast<int>;
                    females = (newnewborn * 1.0/ 2.06) .cast<int>;

                    // 
                    malebirthAge = generateAgefromBirth(males);
                    femalebirthAge = generateAgefromBirth(females);

                    auto matrixPtr = std::make_shared<Eigen::MatrixXd>(numRows, numCols);

                    // Fill the matrix with some values
                    *matrixPtr = malebirthAge ;

                    // Store the pointer to the matrix in the vector
                    matrices[i-1].push_back(malebirthAge);
                    
                    *matrixPtr = femalebirthAge;

                    matrices[i].push_back(femalebirthAge);


                    arraybirth[mig,:] = females

                    // 

                }
            totalFemales = arraybirth.col.sum();
            birth_queue.pop();
            birth_queue.pushback(totalFemales);
            }
            // terminal condition, the birth won't enter childbearing age
            // in our range
            birth_start += 15;
            
        }
    }

    // end of block ending



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


	