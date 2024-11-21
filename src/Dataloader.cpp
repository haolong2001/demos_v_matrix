#include "DataLoader.h"
#include <cmath>

namespace {
    // Helper function modified to use integer math
    Eigen::ArrayXXf scaleMatrix(const Eigen::ArrayXXf& mat, int scale) {
        return mat * static_cast<float>(scale);
    }
}


DataLoader::DataLoader(int mockScale) 
    : mockScale(mockScale)
    , popu_mat(new float[POPU_MAT_SIZE])   // This is correct for vector // Initialize vector with size and default value
    , fer_mat(new float[FER_MAT_SIZE]())    // () zero-initializes the array
    , mock_popu_mat(8)                  // Pre-allocate vectors
    , mor_eig_mat(8)
    , disappear_mat(8)
    , migration_in(8)
{
    // Initialize Eigen matrices
    for (size_t i = 0; i < 8; ++i) {
        mock_popu_mat[i] = Eigen::MatrixXi::Zero(86, 35);  // Initialize with zeros
        mor_eig_mat[i] = Eigen::ArrayXXf::Zero(86, 34);
        disappear_mat[i] = Eigen::ArrayXXf::Zero(119, 34);
        migration_in[i] = Eigen::ArrayXXi::Zero(86, 34);
    }
}

bool DataLoader::readAllData() {
    bool success = true;
    
    success &= readPopuMat();
    success &= readMorEigMat();
    success &= readDisEigMat();
    success &= readFerMat();
    success &= readImmiEigMat();
    
    return success;
}

bool DataLoader::readPopuMat(const std::string& filename) {
    std::ifstream file(filename, std::ios::binary);
    if (!file) {
        std::cerr << "Failed to open " << filename << std::endl;
        return false;
    }

    // Create temporary buffer for double data
    std::vector<double> temp_buffer(POPU_MAT_SIZE);
    
    // Read into temporary double buffer
    file.read(reinterpret_cast<char*>(temp_buffer.data()), 
              POPU_MAT_SIZE * sizeof(double));

    if (!file) {
        std::cerr << "Failed to read population matrix data" << std::endl;
        return false;
    }

    for (size_t i = 0; i < POPU_MAT_SIZE; ++i) {
        popu_mat[i] = static_cast<float>(temp_buffer[i]);
    }

    // debug 
    // std::cout << "First few values from popu_mat:" << std::endl;
    // for (size_t i = 0; i < size_t(10); ++i) {
    //     std::cout << std::fixed << std::setprecision(2) << popu_mat[i] << " ";
    // }
    // std::cout << std::endl;

    // Process popu_mat into mock_popu_mat
    for (int i = 0; i < 8; ++i) {
        for (int j = 0; j < 86; ++j) {
            for (int k = 0; k < 35; ++k) {
                size_t idx = i * (86 * 35) + j * 35 + k;
                mock_popu_mat[i](j, k) = static_cast<int>(popu_mat[idx]) / mockScale;
            }
        }
    }

    return true;
}

bool DataLoader::readMorEigMat(const std::string& filename) {
    std::ifstream file(filename, std::ios::binary);
    if (!file) {
        std::cerr << "Failed to open " << filename << std::endl;
        return false;
    }

    const size_t matrix_size = 86 * 34 * 8;
    std::vector<double> temp_buffer(matrix_size);
 
    file.read(reinterpret_cast<char*>(temp_buffer.data()), POPU_MAT_SIZE * sizeof(double) );
 
    // Now reshape into your matrix (assuming mor_eig_mat is your target container)
    // The data should naturally be in the correct 8 x 86 x 34 layout
    for (size_t i = 0; i < 8; ++i) {
        for (size_t row = 0; row < 86; ++row) {
            for (size_t col = 0; col < 34; ++col) {
                size_t idx = i * (86 * 34) + row * 34 + col;
                mor_eig_mat[i](row, col) = static_cast<float>(temp_buffer[idx]);
            }
        }
    }

    return true;
}
    // for (size_t i = 0; i < mor_eig_mat.size(); ++i) {
    //     // c++ read with an auto pointer 
    //     file.read(reinterpret_cast<char*>(temp_buffer.data()),
    //              matrix_size * sizeof(double));
                 
    //     if (!file) {
    //         std::cerr << "Failed to read mortality matrix data" << std::endl;
    //         return false;
    //     }

    //     // Convert and copy to Eigen array
    //     // for (size_t j = 0; j < matrix_size; ++j) {
    //     //     mor_eig_mat[i].data()[j] = static_cast<float>(temp_buffer[j]);
    //     // }

    //     for (size_t i = 0; i < 8; ++i) {
    //         for (size_t row = 0; row < 86; ++row) {
    //             for (size_t col = 0; col < 34; ++col) {
    //                 size_t idx = i * (86 * 34) + row * 34 + col;
    //                 mor_eig_mat[i](row, col) = static_cast<float>(temp_buffer[idx]);
    //         }
    //     }
    // }
    // }


// serve as 
bool DataLoader::readDisEigMat(const std::string& filename) {
    std::ifstream file(filename, std::ios::binary);
    if (!file) {
        std::cerr << "Failed to open " << filename << std::endl;
        return false;
    }

    const size_t matrix_size = 119 * 34 * 8 ;
    std::vector<double> temp_buffer(matrix_size);

    
    file.read(reinterpret_cast<char*>(temp_buffer.data()),
                 matrix_size * sizeof(double));
                 
    if (!file) {
            std::cerr << "Failed to read disappear matrix data" << std::endl;
            return false;
        }

    // std::cout << "step 1" << std::endl;
    // Reshape into 8 x 119 x 34 format
    for (size_t i = 0; i < 8; ++i) {
        for (size_t row = 0; row < 119; ++row) {
            for (size_t col = 0; col < 34; ++col) {
                size_t idx = i * (119 * 34) + row * 34 + col;
                // if ( idx <= 10 ){
                // std::cout << temp_buffer[idx] << std::endl;
                // }
                disappear_mat[i](row, col) = (temp_buffer[idx]);
                // disappear_mat[idx] = static_cast<float>(temp_buffer[idx]);
            }
        }
    }
    

    return true;
}

bool DataLoader::readFerMat(const std::string& filename) {
    std::ifstream file(filename, std::ios::binary);
    if (!file) {
        std::cerr << "Failed to open " << filename << std::endl;
        return false;
    }

    std::vector<double> temp_buffer(FER_MAT_SIZE);
    file.read(reinterpret_cast<char*>(temp_buffer.data()), 
              FER_MAT_SIZE * sizeof(double));

    if (!file) {
        std::cerr << "Failed to read fertility matrix data" << std::endl;
        return false;
    }

    // Reshape into 12 x 71 x 35 format
    for (size_t i = 0; i < 12; ++i) {
        for (size_t row = 0; row < 71; ++row) {
            for (size_t col = 0; col < 35; ++col) {
                size_t idx = i * (71 * 35) + row * 35 + col;
                            // debug
            
                fer_mat[idx] = static_cast<float>(temp_buffer[idx]);
            }
        }
    }

    return true;
}

bool DataLoader::readImmiEigMat(const std::string& filename) {
    std::ifstream file(filename, std::ios::binary);
    if (!file) {
        std::cerr << "Failed to open " << filename << std::endl;
        return false;
    }

    const size_t matrix_size = 86 * 34 * 8;
    std::vector<double> temp_buffer(matrix_size);

    
    file.read(reinterpret_cast<char*>(temp_buffer.data()),
                 matrix_size * sizeof(double));
                 
    if (!file) {
        std::cerr << "Failed to read immigration matrix data" << std::endl;
        return false;
    }   

    // const double mockScaleDouble = static_cast<double>(mockScale); 
        // Convert double to float, scale, and store as integer
    //     for (size_t j = 0; j < matrix_size; ++j) {
    //         // double scaled = temp_buffer[j] / mockScaleDouble;
    //         migration_in[i].data()[j] = temp_buffer[j] / mockScale;
    //    }
    for (size_t i = 0; i < 8; ++i) {
        for (size_t row = 0; row < 86; ++row) {
            for (size_t col = 0; col < 34; ++col) {
                size_t idx = i * (86 * 34) + row * 34 + col;
                // debug
                // if ( idx <= 10 ){
                //     std::cout << temp_buffer[idx] << std::endl;
                // }
                migration_in[i](row, col) = static_cast<int>(temp_buffer[idx] / mockScale);
            }
        }
    }

        

    

    // debug
        // std::cout << mockScale << " ";
        // std::cout << "First few values from popu_mat:" << std::endl;
        // for (size_t i = 0; i < size_t(10); ++i) {
        //     std::cout << migration_in[0](0,i) << " ";
        // }
        // std::cout << std::endl;

    return true;
}