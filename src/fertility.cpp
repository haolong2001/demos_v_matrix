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





int main() {
    // Sample ages vector
    // ages should only contain the ages before 49
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

    // 

    return 0;
}
