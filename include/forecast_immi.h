#ifndef FORECAST_IMMI_H
#define FORECAST_IMMI_H

#include <Eigen/Dense>
#include <string>
#include <vector>

// Function to read future immigration data from binary file
// Returns a 3D vector: [8 matrices][50 age groups][27 years]
std::vector<std::vector<std::vector<int>>>
readFutureImmigration(const std::string &filename);

// Function to generate agent matrix from immigration data
// Returns a matrix where each row represents an immigrant agent
// and columns represent their age progression over years
Eigen::MatrixXi GenerateAgentsMatrix(
    int matrix_index,
    const std::vector<std::vector<std::vector<int>>> &immigration_mat);

#endif // FORECAST_IMMI_H