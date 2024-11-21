#ifndef MIGRATION_H
#define MIGRATION_H

#include <Eigen/Dense>
#include <random>
#include <vector>
#include <fstream>
#include "DataLoader.h"

using namespace Eigen;

class MigrationSimulator {
private:
    const int NUM_AGE_GROUPS = 86;
    const int NUM_YEARS = 34;
    std::ofstream log_file;

    /**
     * @brief Generates random values between 0 and 1
     */
    ArrayXXf generateRandomValues(int rows, int cols);

    /**
     * @brief Updates survival status to ensure death is permanent
     */
    void updateSurvivalStatus(ArrayXXi& survival_status);

public:
    /**
     * @brief Constructor
     * @param log_path Path to the log file (optional)
     */
    explicit MigrationSimulator(const std::string& log_path = "");
    ~MigrationSimulator();

    /**
     * @brief Generates migration age matrix based on input parameters
     * @return Generated age matrix for migrants
     */
    ArrayXXi generateMigration(
        const ArrayXXi& MigNumMat,
        const std::vector<ArrayXXf>& disappear_mat,
        int index
    );
};

#endif // MIGRATION_H