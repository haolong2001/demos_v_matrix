

void generate1990Age(){


}


int main() {

}

// use a class to wrap the following files reading
// and then initialize a object 
// and then write a test_read_file.cpp to test 

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

