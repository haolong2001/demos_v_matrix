#pragma once

// why here? 
#include <Eigen/Dense>
#include <vector>
#include <EigenRand/EigenRand>

using namespace Eigen;
using namespace std;

class PopulationSimulator {
public:
    // ? 
    explicit PopulationSimulator();
    
    ArrayXXi generateDeathMatrix(
        const VectorXi& num_by_ages,
        int gender_index,
        const vector<ArrayXXf>& disappear_mat);
        
    ArrayXXi generateAgeMatrix(
        const VectorXi& num_by_ages,
        const ArrayXXi& existing_matrix);
        
private:
    const int START_YEAR = 1990;
    const int END_YEAR= 2023;
    const int NUM_YEARS = END_YEAR - START_YEAR +1 ;
    Rand::P8_mt19937_64 random_generator;
};