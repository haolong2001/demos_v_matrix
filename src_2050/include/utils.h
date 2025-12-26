#pragma once

#include "global.h"
#include <Eigen/Dense>
#include <filesystem>
#include <fstream>
#include <random>
#include <string>

using namespace Eigen;

// Function declarations
bool fileExists(const std::string &filename);

Eigen::ArrayXXf generateRandomValues(int rows, int cols);

void updateSurvivalStatus(Eigen::ArrayXXi &survival_status);

void writeMatrixToLog(std::ofstream &log_file, const std::string &matrix_name,
                      const ArrayXXi &matrix);

void writeMatrixToLog(std::ofstream &log_file, const std::string &matrix_name,
                      const ArrayXXf &matrix);