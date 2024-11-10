
#include <iostream>
#include <filesystem>
#include <fstream>
#include <unistd.h>
#include <limits.h>

#include <Eigen/Dense>
#include <EigenRand/EigenRand>
#include <cmath>
#include <queue>
#include <memory>

#include "DataLoader.h"


using namespace std;
using namespace Eigen;

int main() {
    const int mockScale = 100;
    DataLoader dataLoader(mockScale);

    std::ofstream logfile("src/main_log.txt");
    if (!logfile) {
        std::cerr << "Failed to open log file" << std::endl;
        return -1;
    }

   // C++11 compatible version of reading data files
    struct FileInfo {
        std::string filename;
        bool (DataLoader::*readFunc)(const std::string&);
    };

    const std::vector<FileInfo> dataFiles = {
        {"result_matrix_data.bin", &DataLoader::readPopuMat},
        {"./data/bin/disappear.bin", &DataLoader::readMorEigMat},
        {"./data/bin/mig_disappear.bin", &DataLoader::readDisEigMat},
        {"./data/bin/AESFR_matrix_combine.bin", &DataLoader::readFerMat},
        {"./data/bin/migration_in.bin", &DataLoader::readImmiEigMat}
    };

    // read files directly
    for (const FileInfo& fileInfo : dataFiles) {
        if (!(dataLoader.*fileInfo.readFunc)(fileInfo.filename)) {
            std::cerr << "Failed to read " << fileInfo.filename << std::endl;
            return -1;
        }
    }
    //
    

    // initialize the 1990 population
    for (int i = 0; i < 8; ++i){
        VectorXi num_by_ages = dataLoader.mock_popu_mat[i].col(0); // column 0
        generateAges(num_by_ages,i ,disappear_mat,AgeMatrix,ExistingMatrix);


    }
 

    return 0;
}