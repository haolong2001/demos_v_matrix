#ifndef MIGRATION_UTILS_H
#define MIGRATION_UTILS_H


#include <Eigen/Dense>
#include <random>
#include "global.h"

using namespace Eigen;

void writeMatrixToLog(std::ofstream& log_file, 
                     const std::string& matrix_name, 
                     const ArrayXXi& matrix);

void writeMatrixToLog(std::ofstream& log_file, 
                     const std::string& matrix_name, 
                     const ArrayXXf& matrix);             

class Utils {
public:
    // Only declare the functions (prototypes)
    static Eigen::ArrayXXf generateRandomValues(int rows, int cols);
    static void updateSurvivalStatus(Eigen::ArrayXXi& survival_status);
};

#endif // MIGRATION_UTILS_H 