// fertility.h
#ifndef FERTILITY_H_
#define FERTILITY_H_

#include <Eigen/Dense>
#include <vector>
#include <map>
#include <random>
#include <fstream>

using namespace Eigen;

namespace demographic {

class Fertility {
 public:
  // Constructor taking fertility rate matrix
  explicit Fertility(const float (&fertility_rates)[12][71][35]);
  
  // Generates birth events based on age matrix and returns fertility matrix
  Eigen::ArrayXi GenerateBirth(int index, const Eigen::ArrayXXi& age_matrix);

  // Maps age and year to fertility rate
  float MapFertilityRate(int index, int year_idx, int age) const;

    Eigen::ArrayXi migration_births(int index, 
                        const Eigen::ArrayXXi& age_matrix,
                        const Eigen::ArrayXXi& migrat_mat);

    Eigen::ArrayXXi generateAgefromBirth(
    int index,
    const Eigen::ArrayXi& birthvec,
    const std::vector<ArrayXXf>& disappear_mat
    );


 private:
  
  
  // Fertility rates lookup table
  const float (&fertility_rates_)[12][71][35];
  
  // Random number generation
  std::random_device rd_;
  std::mt19937 gen_;
  std::uniform_real_distribution<> dis_;
};

}  // namespace demographic

void writeMatrixToLog(std::ofstream& log_file, 
                     const std::string& matrix_name, 
                     const ArrayXXf& matrix);

void writeMatrixToLog(std::ofstream& log_file, 
                     const std::string& matrix_name, 
                     const ArrayXXi& matrix);

#endif  // FERTILITY_H_
