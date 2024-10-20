#include <iostream>
#include <fstream>
#include <vector>
#include <unistd.h> 
#include <Eigen/Dense>

using namespace std;
using namespace Eigen;

// global variable 
int num_years = 34; // from 1990 - 2023

vector<vector<vector<double>>> read_binary_file(const string& filename, int n_eth, int rows, int cols) {
    // Initialize the 3D vector
    vector<vector<vector<double>>> result_matrix(n_eth, 
        vector<vector<double>>(rows, vector<double>(cols)));

    // Open the file in binary mode
    ifstream file(filename, ios::binary);
    if (!file) {
        cerr << "Error opening file: " << filename << endl;
        return result_matrix; // Return empty result if file not found
    }

    // Read data from the file
    file.read(reinterpret_cast<char*>(&result_matrix[0][0][0]), n_eth * rows * cols * sizeof(double));

    // Close the file
    file.close();

    return result_matrix;
}


MatrixXi generate_death_tre(const VectorXi& ages, const MatrixXd& death_age_matrix) {
    // Input: ages vector (Eigen vector), death_age_matrix (Eigen matrix)
    // Output: comparison matrix (Eigen matrix of ints)

    // Step 1: Create age matrix using matrix computation
    // transpose(),converts it into a row vector with 10 elements.
    //
    MatrixXd age_matrix = ages.replicate(1, num_years) + 
    VectorXd::LinSpaced(35, 0, 34).transpose().replicate(ages.size(), 1);

    // Step 2: Create category matrix, 
    // array(); element wise operation 
    MatrixXd category_matrix = age_matrix.array() / 5.0;
    
    // Step 3: Bound the values by len_death - 1
    int len_death = death_age_matrix.cols();
    category_matrix = category_matrix.unaryExpr([len_death](double val) { return std::min(val, static_cast<double>(len_death - 1)); });

    // Step 4: Generate random matrix using Eigen and normalize to [0.0, 1.0]
    MatrixXd random_matrix = MatrixXd::Random(ages.size(), 10);
    random_matrix = (random_matrix.array() + 1.0) / 2.0; // Normalize to [0.0, 1.0]

    // Step 5: Create comparison matrix
    MatrixXi comparison_matrix = (random_matrix.array() < death_age_matrix.array()).cast<int>();
    return comparison_matrix;
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

int main() {
    const int n_eth = 8; // 0 - 7; chn, mal, ind, oth  * 0,1 
    const int rows = 86; // 0 - 85, 85+ 
    const int cols = 35; // 1990 - 2024

    char cwd[1024];
    if (getcwd(cwd, sizeof(cwd)) != NULL) {
        cout << "Current working directory: " << cwd << endl;
    } else {
        cerr << "Error getting current working directory" << endl;
    }
    // Current working directory: /Users/haolong/Documents/GitHub/demos_v_matrix/src

    // Call the function to read the binary file
    vector<vector<vector<double>>> result_matrix = read_binary_file("../result_matrix_data.bin", n_eth, rows, cols);
    // vector not good 
    //vector<vector<vector<double>>> result_matrix = read_binary_file("../result_matrix.npy", n_eth, rows, cols);

    // Test: print the first element of the matrix
    cout << "third element: " << result_matrix[0][0][2] << endl;

    // 
    

    return 0;
}
// to be solved 
// 
// create an information table 
// create a matrix of fixed length, width 4 
// width for  
sum = 0 
for i in range(8)
  sum += sum(matrix[i][:][0]) 
total_length = sum


for i in range(8):
    length = sum(matrix[i][:][0])
    gender = i/ 2 + 1 //  0 means female; 1 means male

	vec = matrix[i][:][0]// this is the line cooresponding to the first column, of length 86
	// rewrite the python code to c++ , use Eigen library 
    ages = np.arange(0,86)
    np.repeat(ages, vec) 
    // add eth, gender, age, index to the row 
    // which row? 
    // 

    // for year 1990 population 
    // create individual mortality death trejectories 
    // 

	