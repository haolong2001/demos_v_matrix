#include <iostream>
#include <Eigen/Dense>

using namespace Eigen;
using namespace std;

// Function to generate age matrix
ArrayXXi generateAgeMatrix(const VectorXi& ages, int num_years) {
    int num_ages = ages.size();  // Corrected missing 'int' type
    // MatrixXf ageMatrix(num_ages, num_years);  // Initialize the matrix with correct dimensions
    ArrayXi range = ArrayXi::LinSpaced(num_years, 0, num_years - 1);  // Create a range from 0 to num_years-1
    // ArrayXXi result = ages.replicate(1, num_years) + range.transpose().replicate(num_ages, 1);  // Broadcast addition of ages and range

    ArrayXXi range_matrix = range.replicate(1,num_ages).transpose();
    cout << "range matrix: \n " << range_matrix << endl;

    ArrayXXi ages_matrix = ages.replicate(1,num_years);
    cout << "age matrix: \n " << ages_matrix << endl;

    
    ArrayXXi ageMatrix = (range_matrix + ages_matrix);  // Cast ArrayXXi to MatrixXf
    return  ageMatrix;
}
/**
 * @param ageMatrix and address of the fertility matrix
 * @return  birth matrix 
 */
void generateRawBirthMat( const ArrayXXi ageMatrix,
                            , const ArrayXXf ){

    // generate a matrix with same shape as ageMatrix
    probMatrix

    return 
}
// mapping directly 


// map the year and age to fertility 
// the outside begins from year 1980
// may optimize this part further 
float MapFer(int i, int yar_idx, int age, const float (&fer_mat)[12][71][35] ){
    
    if (age > 15 & age < 49){
        return fer_mat[i][yar_idx + 10][age - 15];
    }
    return 0.0;
    // fer begins from 1980 
}


// birth vector 
// 
void generateAgefromBirth(int eth_gen, ArrayXi& birthvec, ArrayXXi& AgeMatrix){
    // end year is 2023, 
    // start year is 2023 - length(birthvec)
    
    ncols = birthvec.size()
    // 34 columns, and we wish to align with the ending
    beginning =  34 - ncols;
    start = 0
    for (int i = 0; beginning < ncols,; 
    ++ beginning, ++ start, ++i){
        num = birthvec[i];
        
        tempage = seq(0,34 - beginning).replicate(1,num) // initialize the age matrix 
        // initialize mortality matrix as well 
        // if beginning is 32, then it's column 31 in disappear_mat
        mor_vec = disappear_mat[i](beginning -1 ,34 - beginning)//  

        // initialize 0,1 matrix 
        disappear = mor <= Rand::balanced<ArrayXXf>(n_rows, n_years, urng,0,1);
        // operate boardcasting multilication
        AgeMatrix.block(
            start, beginning, num, 34 - beginning
        ) = disappear * tempage
    }
}

void generateAgefromBirth(int eth_gen, const Eigen::ArrayXi& birthvec, Eigen::ArrayXXi& AgeMatrix, const std::vector<Eigen::ArrayXXf>& disappear_mat, std::mt19937& urng) {
    int ncols = birthvec.size();
    int beginning = 34 - ncols;
    int start = 0;

    std::uniform_real_distribution<float> dist(0.0f, 1.0f);

    for (int i = 0; i < ncols; ++i, ++beginning) {
        int num = birthvec[i];
        int age_length = 34 - beginning;

        // Create age sequence from 0 to (age_length - 1)
        Eigen::ArrayXi age_seq = Eigen::ArrayXi::LinSpaced(age_length, 0, age_length - 1);

        // Replicate the age sequence 'num' times along rows
        Eigen::ArrayXXi tempage = age_seq.transpose().replicate(num, 1);

        // Get mortality matrix for the current group
        Eigen::ArrayXXf mor_vec = disappear_mat[eth_gen].block(start, beginning, num, age_length);

        // Generate random matrix for comparison
        Eigen::ArrayXXf rand_matrix(num, age_length);
        for (int m = 0; m < num; ++m) {
            for (int n = 0; n < age_length; ++n) {
                rand_matrix(m, n) = dist(urng);
            }
        }

        // Determine if individuals disappear based on mortality rates
        Eigen::ArrayXXi disappear = (mor_vec <= rand_matrix).cast<int>();

        // Update AgeMatrix with the ages where individuals are still alive
        AgeMatrix.block(start, beginning, num, age_length) = disappear * tempage;

        // Update the starting row index for the next group
        start += num;
    }
}



void test_read(){
    VectorXi ages(3);
    ages << 25, 30, 35;

    // Number of years
    int num_years = 5;

    double fer_mat[12][71][35];
    ifstream file("../data/bin/AESFR_matrix_combine.bin", ios::binary);
    file.read(reinterpret_cast<char*>(&fer_mat[0][0][0]),sizeof(fer_mat));

    // Generate the age matrix
    ArrayXXi ageMatrix = generateAgeMatrix(ages, num_years);

    // Print the resulting matrix
    cout << "Age Matrix:\n" << ageMatrix << endl;

}


int main() {
    // Sample ages vector
    // ages should only contain the ages before 49

    vector<ArrayXXf> disappear_mat(8, ArrayXXf(119, 34));
    // test example  
    ArrayXi birthvec = (20, 23, 24) 
    ArrayXXi AgeMatrix (birthvec.sum(), 34)

    return 0;
}
