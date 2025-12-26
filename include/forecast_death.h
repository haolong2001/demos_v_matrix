#pragma once

#include <Eigen/Dense>
#include <iosfwd> // for std::ostream forward declaration
#include <vector>

using namespace Eigen;
using namespace std;

// Forecast death rates and modify population matrix accordingly
// log_stream: optional pointer to output stream for logging (nullptr for no
// logging)
MatrixXi forecast_death(MatrixXi &popu_mat,
                        const vector<vector<vector<double>>> &mortality_mat,
                        int is_female, std::ostream *log_stream = nullptr);