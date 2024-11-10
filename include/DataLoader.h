#ifndef DATALOADER_H
#define DATALOADER_H

#include <iostream>
#include <fstream>
#include <vector>
#include <memory>
#include <Eigen/Dense>

// C++11 compatible make_unique implementation
namespace std {
    template<typename T>
    unique_ptr<T> make_unique_array(size_t size) {
        return unique_ptr<T>(new T[size]);
    }
}

class DataLoader {
public:
    explicit DataLoader(int mockScale);
    ~DataLoader() = default;

    // Deleted copy constructor and assignment operator
    DataLoader(const DataLoader&) = delete;
    DataLoader& operator=(const DataLoader&) = delete;

    // Methods to read data from files
    bool readPopuMat(const std::string& filename);
    bool readMorEigMat(const std::string& filename);
    bool readFerMat(const std::string& filename);
    bool readDisEigMat(const std::string& filename);
    bool readImmiEigMat(const std::string& filename);
    
    // Public member variables
    std::unique_ptr<float[]> popu_mat;  // [8][86][35]
    std::unique_ptr<float[]> fer_mat;   // [12][71][35] fertility 1980 - 2050
    std::vector<Eigen::MatrixXi> mock_popu_mat;  // Vector of 8 matrices
    std::vector<Eigen::ArrayXXf> mor_eig_mat;    // Vector of 8 arrays
    std::vector<Eigen::ArrayXXf> disappear_mat;  // disappear = death + emigrate
    std::vector<Eigen::ArrayXXi> migration_in;   // migration in from 1990

private:
    float mockScale;
    static constexpr size_t POPU_MAT_SIZE = 8 * 86 * 35;
    static constexpr size_t FER_MAT_SIZE = 12 * 71 * 35;
};

#endif // DATALOADER_H


// the result is not good, we try update the fertility rate and mortality rate from Singstats 
// chinese is done, we are doing test for the other ethnicities 
// the default is float 64, however, 
// c++ make calculation faster using double 32
