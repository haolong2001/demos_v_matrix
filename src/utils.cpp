


#include "utils.h"


Eigen::ArrayXXf Utils::generateRandomValues(int rows, int cols) {
    std::random_device rd;
    std::mt19937 urng(rd());
    return Eigen::ArrayXXf::Random(rows, cols).unaryExpr([](float val) { 
        return (val + 1.0f) / 2.0f; 
    });
}

void Utils::updateSurvivalStatus(Eigen::ArrayXXi& survival_status) {
    const int rows = survival_status.rows();
    const int cols = survival_status.cols();
    
    for (int i = 0; i < rows; ++i) {
        bool disappeared = false;

        for (int j = 0; j < cols; ++j) {
            if (!disappeared && survival_status(i, j) == 0) {
                disappeared = true;
            }
            if (disappeared) {
                survival_status.row(i).segment(j, cols - j).setZero();
                break;
            }
        }
    }
}

// normally header file contains the 