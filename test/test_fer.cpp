
// sample_fertility.cpp
#include <iostream>
#include <fstream>
#include <iomanip>
#include "deathages.h"
#include "DataLoader.h"
#include "fertility.h"
#include "migration.h"
#include "utils.h"
#include <chrono>
#include <Eigen/Dense>
#include <ctime>

// delete later 
void copyToArray(const std::unique_ptr<float[]>& fer_mat, float (&fertility_rates)[12][71][35]) {
    for (int year = 0; year < 12; ++year) {
        for (int age = 0; age < 71; ++age) {
            for (int ethnicity = 0; ethnicity < 35; ++ethnicity) {
                size_t index = year * (71 * 35) + age * 35 + ethnicity;
                fertility_rates[year][age][ethnicity] = fer_mat[index];
            }
        }
    }
}

int main() {
  // Sample fertility rates matrix (12x71x35)
  const int mockScale = 400;
  DataLoader dataLoader(mockScale);

  if (!dataLoader.readAllData()) {
        std::cerr << "Failed to read data files" << std::endl;
        return -1;
    }
    
    // fertility 
    Eigen::ArrayXi sample_birth = Eigen::ArrayXi::Constant(5, 5);
        ArrayXXi test_birth = fertility.generateAgefromBirth( 
            1,
            sample_birth,
            dataLoader.disappear_mat
            );
        log_file << " disappear matrix"  << "\n\n";
        log_file << dataLoader.disappear_mat[0]  << "\n\n";
        log_file << " test_birth"  << "\n\n";
        log_file << test_birth  << "\n\n";


 
  
  return 0;
}