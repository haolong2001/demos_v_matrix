#pragma once

#include <Eigen/Dense>
#include <string>
#include <utility> // for std::pair
#include <vector>

using namespace Eigen;

// Function to read fertility matrix from binary file
// Returns a 3D vector: [12 matrices][71 age groups][35 years]
std::vector<std::vector<std::vector<double>>>
readFertilityMatrix(const std::string &filename);

// Helper function to map fertility rates based on age and year
float MapFertilityRate(
    int index, int year, int age,
    const std::vector<std::vector<std::vector<double>>> &fertility_rates);

// Helper function to print matrix preview and statistics
void printFertilityMatrixPreview(
    const std::vector<std::vector<std::vector<double>>> &matrix);

// Function to calculate births from population matrix and fertility rates
// Returns two vectors: number of male and female births for each year
std::pair<VectorXi, VectorXi> calculateBirths(
    const MatrixXi &popu_mat,
    const std::vector<std::vector<std::vector<double>>> &fertility_rates,
    int fertility_index);

Eigen::MatrixXi generatePopuFromBirth(const Eigen::VectorXi &births);