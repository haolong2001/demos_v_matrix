#ifndef MIGRATION_UTILS_H
#define MIGRATION_UTILS_H


#include <Eigen/Dense>
#include <random>
#include "global.h"


class Utils {
public:
    // Only declare the functions (prototypes)
    static Eigen::ArrayXXf generateRandomValues(int rows, int cols);
    static void updateSurvivalStatus(Eigen::ArrayXXi& survival_status);
};

#endif // MIGRATION_UTILS_H 