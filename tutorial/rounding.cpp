#include <Eigen/Dense>
#include <iostream>

using namespace Eigen;

int main() {
    ArrayXXi immi_mat(3, 3);
    immi_mat << 10, 20, 30,
                40, 50, 60,
                70, 80, 90;

    float mock_scale = 0.05;

    // Cast immi_mat to float and then multiply by mock_scale
    ArrayXXf scaled_mat = immi_mat.cast<float>() * mock_scale;
    std::cout << "Scaled matrix:\n" << scaled_mat << std::endl;

    // test 
    ArrayXXi scaled_mat2 = (immi_mat * mock_scale).cast<int>();
    std::cout << "Scaled matrix:\n" << scaled_mat << std::endl;

    return 0;
}
