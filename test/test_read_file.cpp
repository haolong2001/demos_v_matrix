#include <iostream>
#include <filesystem>
#include <fstream>
#include <unistd.h>
#include <limits.h>
#include "DataLoader.h"

namespace {
    void printMatrix(const Eigen::MatrixXi& matrix, std::ofstream& logfile) {
        for (int i = 0; i < matrix.rows(); ++i) {
            for (int j = 0; j < matrix.cols(); ++j) {
                logfile << matrix(i, j);
                if (j < matrix.cols() - 1) {
                    logfile << ", ";
                }
            }
            logfile << '\n';
        }
    }

    void printMatrix(const Eigen::ArrayXXf& matrix, std::ofstream& logfile) {
        for (int i = 0; i < matrix.rows(); ++i) {
            for (int j = 0; j < matrix.cols(); ++j) {
                logfile << matrix(i, j);
                if (j < matrix.cols() - 1) {
                    logfile << ", ";
                }
            }
            logfile << '\n';
        }
    }
    
    void printMatrix(const Eigen::ArrayXXi& matrix, std::ofstream& logfile) {
        for (int i = 0; i < matrix.rows(); ++i) {
            for (int j = 0; j < matrix.cols(); ++j) {
                logfile << matrix(i, j);
                if (j < matrix.cols() - 1) {
                    logfile << ", ";
                }
            }
            logfile << '\n';
        }
    }

    size_t calculate3DIndex(size_t year, size_t row, size_t col) {
        const size_t ROWS_PER_YEAR = 71;
        const size_t COLS = 35;
        return year * (ROWS_PER_YEAR * COLS) + row * COLS + col;
    }

    void printFertilityMatrix(const std::unique_ptr<float[]>& fer_mat, std::ofstream& logfile) {
        if (!fer_mat) {
            std::cerr << "Fertility matrix is null" << std::endl;
            return;
        }

        for (int i = 10; i < 71; ++i) {
            for (int j = 0; j < 35; ++j) {
                size_t index = calculate3DIndex(0, i, j);
                logfile << fer_mat[index];
                if (j < 34) {
                    logfile << ", ";
                }
            }
            logfile << '\n';
        }
    }
}

int main() {
    // Print current working directory
    char cwd[PATH_MAX];
    if (getcwd(cwd, sizeof(cwd)) != nullptr) {
        std::cout << "Current working directory: " << cwd << std::endl;
    } else {
        perror("getcwd() error");
        return -1;
    }

    const int mockScale = 100;
    DataLoader dataLoader(mockScale);

    // Create log file
    std::ofstream logfile("test/test_log.txt");
    if (!logfile) {
        std::cerr << "Failed to open log file" << std::endl;
        return -1;
    }

    if (!dataLoader.readAllData()) {
        std::cerr << "Failed to read data files" << std::endl;
        return -1;
    }

   
    // Print population matrix
    logfile <<"First matrix of mock_popu_mat[0]:" << std::endl;
    if (!dataLoader.mock_popu_mat.empty()) {
        printMatrix(dataLoader.mock_popu_mat[0], logfile);
    }

    // Print disappear matrix
    logfile << "First matrix of mor_eig_mat[0]:" << std::endl;
    if (!dataLoader.mor_eig_mat.empty()) {
        printMatrix(dataLoader.mor_eig_mat[0], logfile);
    }

    logfile << "First matrix of disappear[0]:" << std::endl;
    if (!dataLoader.disappear_mat.empty()) {
        printMatrix(dataLoader.disappear_mat[0], logfile);
    }

    // Print fertility matrix
    logfile << "Fertility matrix from year 1990 (starting from row 10):" << std::endl;
    printFertilityMatrix(dataLoader.fer_mat, logfile);

    logfile << "immigration matrix from year 1991:" << std::endl;
    printMatrix(dataLoader.migration_in[0], logfile);
    return 0;
}



// // C++11 compatible version of reading data files
//     struct FileInfo {
//         std::string filename;
//         bool (DataLoader::*readFunc)(const std::string&);
//     };

//     const std::vector<FileInfo> dataFiles = {
//         {"result_matrix_data.bin", &DataLoader::readPopuMat},
//         {"./data/bin/mig_disappear.bin", &DataLoader::readMorEigMat},
//         {"./data/bin/disappear.bin", &DataLoader::readDisEigMat},
//         {"./data/bin/AESFR_matrix_combine.bin", &DataLoader::readFerMat},
//         {"./data/bin/migration_in.bin", &DataLoader::readImmiEigMat}
//     };

//     // read files directly
//     for (const FileInfo& fileInfo : dataFiles) {
//         if (!(dataLoader.*fileInfo.readFunc)(fileInfo.filename)) {
//             std::cerr << "Failed to read " << fileInfo.filename << std::endl;
//             return -1;
//         }
//     }
