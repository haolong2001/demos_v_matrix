



// float MapFer(int i, int yar_idx, int age, const float (&fer_mat)[12][71][35] ){
    
//     if (age != -1){
//         return fer_mat[i][yar_idx + 10][age - 15];
//     }
//     return 0.0;
//     // fer begins from 1980 
// }

// input age matrix
// 15, 16, 17,...49
// build a fertility matrix 
// finally return a newborn vector 

// to do 17 Nov;
// build a fertility matrix -- > new born matrix 
// new born matrix * existing matrix 
// calculate the column sum as vector 


// O(n)
// age_vec: 1990  0- 49 years old females 
// output: 1990 - 2023 female matrix;
// ArrayXi generateBirth(
//     int index,
//     ArrayXXi age_vec, 
//     const float (&fer_mat)[12][71][35] 

// ){
//     // iterate the rows of the matrix;
//     // only begins when the start value is larger or equal to 15 
//     int len = age_vec.len();
//     for (int i = 0; i < len; ++i){
//         // iterares the values of the row vector, 
//         // break when meet -1 or larger than 49;
//         // otherwise, continue 

//         // obtain the value
//         // start_year; end_year
//         // start_age, end_age
//         int age = age_vec[i];
//         int start_age, start_year; 
//         if (age < 15){
//             start_age = 15;
//             start_year = 1990 + 15 - age
        
//         } else {
//             start_age = age;
//             start_year = 1990


//         }
//         end_age = 49;
//         end_year = 49 - age + 
    
//         year_idx = start_year - 1990;
//         // 18 , for loop is slow;
//         // fertility matrix 
//         fer = MapFer(index,year_idx, age);

//         // think one step first, don't think of three steps together 


        
// // 

//     }

//     return 
// }

// immigration; 
// 15; 20;25

// O(n) mapping
// one by one mapping
// use dictionary to 
// ArrayXi generateBirth(
//     int index,
//     ArrayXXi age_mat, 
//     const float (&fer_mat)[12][71][35] 
    
// ) {

//     ArrayXXi fermat; // should be the same shape as age_mat, initialize with 0 
//     for (int i = 0; i < fermat.nrows; ++i){
//         // in the other function, age is different 
//         age = fermat(i,0);
//         if (age > 48 || age == -1 ){
//             continue;
//         }
//         int start = age <15 ? 15 - age , 0
//         for ( start < fermat.ncols; ++ start){
//             age = fermat(i,j);
//             // target is 15


//             year_idx = j;
//             // if find death, goes to next column 
//             if (age == -1){
//                 break;

//             }
//             // 15; 49 
//             fermat(i,j) = MapFer(index,year_idx, age);
            

//         }
//     }
//     // initialize a random matrix between 0 and 1;
//     // use matrix comparsion to get fertility matrix 

        
//     // finally calculate colsum vector 
//     // use a map to store the result; map<j> = sum for column j  


// }
// write me a sample test cpp file
// initialize a 



// fertility.cpp
#include "global.h"
#include "utils.h"
#include "fertility.h"
#include <iostream>
#include <vector>


namespace demographic {

Fertility::Fertility(const float (&fertility_rates)[12][71][35])
    : fertility_rates_(fertility_rates),
      gen_(rd_()),
      dis_(0.0, 1.0) {}

float Fertility::MapFertilityRate(int index, int year_idx, int age) const {
  if (age < 15 || age >= 49) {
    return 0.0f;
  }
  return fertility_rates_[index][year_idx + 10][age - 15];
}

Eigen::ArrayXi Fertility::GenerateBirth(int index, 
                                      const Eigen::ArrayXXi& age_matrix) {
  // Initialize fertility matrix with same shape as age_matrix
  Eigen::ArrayXXf fertility_matrix = Eigen::ArrayXXf::Zero(age_matrix.rows(), 
                                                          age_matrix.cols());
  
  // Calculate fertility rates for each person
  for (int i = 0; i < age_matrix.rows(); ++i) {
    int start_age = age_matrix(i, 0);
    if (start_age > 49 || start_age == -1) {
      continue;
    }
    
    int start = (start_age < 15) ? (15 - start_age) : 0;
    for (int j = start; j < age_matrix.cols(); ++j) {
      int age = age_matrix(i, j);
      
      // Break if person has died
      if (age == -1 || age > 49) {
        break;
      }
      //std::cout << "input " << j << " " << age << " "<< std::endl;
      //std::cout << "vale " << MapFertilityRate(index, j, age) << std::endl;
      fertility_matrix(i, j) = MapFertilityRate(index / 2, j, age);
      //
      
      // 
    // std::cout << "element" << i << " "<< j <<" "<< fertility_matrix(i, j) << std::endl;
    }

  }

    // std::string log_filename = "test/fer_log.txt";
    // std::ofstream log_fil(log_filename,std::ios::out | std::ios::trunc);
    // log_fil << fertility_matrix << "\n\n";
//   write the matrix to logging file
//   log_file << " fertility array by age group:\n" << births << "\n\n";

  
  // Generate random matrix for comparison
  Eigen::ArrayXXf random_matrix = Eigen::ArrayXXf::Zero(age_matrix.rows(), 
                                                       age_matrix.cols());
  for (int i = 0; i < random_matrix.rows(); ++i) {
    for (int j = 0; j < random_matrix.cols(); ++j) {
      random_matrix(i, j) = dis_(gen_);
    }
  }
  
  // Compare random values with fertility rates
  Eigen::ArrayXXi birth_matrix = (random_matrix < fertility_matrix)
                                    .cast<int>();
  
  // Calculate column sums
  Eigen::ArrayXi column_sums = Eigen::ArrayXi::Zero(age_matrix.cols());
  for (int j = 0; j < birth_matrix.cols(); ++j) {
    column_sums(j) = birth_matrix.col(j).sum();
  }
  
  return column_sums;
}


Eigen::ArrayXi Fertility::migration_births(int index, 
                        const Eigen::ArrayXXi& age_matrix,
                        const Eigen::ArrayXXi& migrat_mat) {
    std::string log_filename = "test/mig_fer_log.txt";
    std::ofstream log_mig(log_filename, std::ios::out | std::ios::trunc);
    
    // Initialize fertility matrix
    Eigen::ArrayXXf fertility_matrix = Eigen::ArrayXXf::Zero(age_matrix.rows(), 
                                                            age_matrix.cols());
    
    // Calculate immigration numbers
    Eigen::ArrayXi num_imm_ary = Eigen::ArrayXi::Zero(migrat_mat.cols());
    for (int j = 0; j < migrat_mat.cols(); ++j) {
        num_imm_ary(j) = migrat_mat.col(j).sum();
    }
    
    // Build boundary indices
    std::vector<int> boundaries;
    int sum = 0;
    for (const auto& val : num_imm_ary) {
        sum += val;
        boundaries.push_back(sum);  // Changed to push sum instead of val
    }
    // Write boundaries to log
    log_mig << "Boundaries: ";
    for (const auto& b : boundaries) {
        log_mig << b << " ";
    }
    log_mig << "\n\n";

    
    // Calculate fertility rates
    for (int k = 0; k < boundaries.size() - 1; ++k) {  // Changed size() check
    // for (int k = 0; k < 3; ++k) {
        int imm_year = k +1; // start with 1
        for (int i = boundaries[k]; i < boundaries[k + 1]; ++i) {

            int start_age = age_matrix(i, imm_year);
            // std::cout << "start_age " << start_age << " " << i << " "<< std::endl;
            if (start_age > 49 || start_age == -1) {
                continue;
            }
            if (start_age < 15 && 15 - start_age + imm_year > age_matrix.cols() ){
                continue;
            }

            int start = (start_age < 15) ? 
                       (15 - start_age + imm_year) : 
                       imm_year;
            
            for (int j = start; j < age_matrix.cols(); ++j) {
                int age = age_matrix(i, j);
                if (age == -1 || age > 49) {
                    break;
                }
                fertility_matrix(i, j) = MapFertilityRate(index /2, j, age) ;
                // 
                // std::cout << "input " << j << " " << age << " "<< std::endl;
                // std::cout << "vale " << MapFertilityRate(index, j, age) << std::endl;
            }
        }
    }
    // log_mig << "fertility_matrix"<< "\n";
    // log_mig << fertility_matrix<< "\n";
    writeMatrixToLog(
        log_mig,
        "migration_fertility",
        fertility_matrix
    );
    
    // Generate random matrix and compare
    Eigen::ArrayXXf random_matrix = Eigen::ArrayXXf::Zero(age_matrix.rows(), 
                                                         age_matrix.cols());
    for (int i = 0; i < random_matrix.rows(); ++i) {
        for (int j = 0; j < random_matrix.cols(); ++j) {
            random_matrix(i, j) = dis_(gen_);
        }
    }
    
    // Compare and calculate births
    Eigen::ArrayXXi birth_matrix = (random_matrix < fertility_matrix).cast<int>();
    
    // Calculate column sums
    Eigen::ArrayXi column_sums = Eigen::ArrayXi::Zero(age_matrix.cols());
    for (int j = 0; j < birth_matrix.cols(); ++j) {
        column_sums(j) = birth_matrix.col(j).sum();
    }
    
    return column_sums;
}


Eigen::ArrayXXi Fertility::generateAgefromBirth(
    int index,
    const Eigen::ArrayXi& birthvec,
    const std::vector<ArrayXXf>& disappear_mat
    ) {
    int ncols = 34; // 1990 - 2023
    int total_births = birthvec.sum();
    Eigen::ArrayXXi AgeMatrix = Eigen::ArrayXXi::Constant(total_births, ncols, -1);

    int start_row = 0;

    for (int i = 0; i < birthvec.size(); ++i) {
        int num_births = birthvec[i];

        if (num_births == 0) continue;
        // size 3 means 2021 - 2023
        // 
        int start_col = 34 - birthvec.size()+ i;
        int age_length = ncols - start_col;
        // age 0 in year 2021 coresponding to  31 
        int year = start_col;
        int disappear_idx = start_col;
        VectorXf mortality_rates = 
            disappear_mat[index].row(disappear_idx).segment(year, 34 - year);
        ArrayXXf replicated_rates = mortality_rates.replicate(1, num_births).transpose();
        
        Eigen::ArrayXXf random_values = Utils::generateRandomValues(num_births, NUM_YEARS - year);
        //1 means okay, 0 means death; logic here a bit strange
        ArrayXXi survival_status = (random_values >= replicated_rates).cast<int>();

        // std::cout <<survival_status << std::endl;
        Utils::updateSurvivalStatus(survival_status);
        // std::cout << "updated" << std::endl <<  survival_status << std::endl;

        ArrayXXi age_block = ArrayXXi::Zero(num_births, NUM_YEARS - year);
            for (int t = 0; t < NUM_YEARS - year; ++t) {
                age_block.col(t).setConstant(t);
            }
        age_block = (survival_status.array() > 0).select(age_block, -1);


        AgeMatrix.block(start_row, start_col, num_births, age_length) = age_block;

        start_row += num_births;
    }

    return AgeMatrix;
}


Eigen::ArrayXi Fertility::calculateNewborns(
  int index,
  const ArrayXXi& femalebirthAge, 
  int birth_start
){
  int nrows = femalebirthAge.rows();

  // suppose start 1991, then we wish to have 1991 + 15 till 2023
  int ncols = simulationEndYear - (birth_start + childbearingStartAge) + 1;

    // Get the age columns starting from childbearing age
    int startCol = 34 - ncols;
    int ageCols = ncols;
  
  // Early return if no valid columns
    if (ageCols <= 0) {
        return ArrayXi();  // Return empty array
    }
  
  // Extract relevant block of ages
  ArrayXXi Newborn = femalebirthAge.block(0, startCol, nrows, ageCols);

  // Initialize fertility matrix
    ArrayXXf ferferMat = ArrayXXf::Zero(nrows, ageCols);
    for (int col = 0; col < Newborn.cols(); ++col) {
        // std::cout << "col succes" << col << std::endl;
        for (int row = 0; row < Newborn.rows(); ++row) {
            int age = Newborn(row, col);
            int year_idx = birth_start + 15 + col - 1990;
            ferferMat(row, col) = MapFertilityRate(index/2, year_idx, age);
        }
    }

  Eigen::ArrayXXf random_values = Utils::generateRandomValues(nrows, ageCols);
        

  // Calculate births
    ArrayXXi birthMat = (ferferMat.array() > random_values.array()).cast<int>();
    return birthMat.colwise().sum();
  

}

void Fertility::generateNewbornData(const Eigen::ArrayXi& newnewborn,
                         Eigen::ArrayXi& males_int,
                         Eigen::ArrayXi& females_int) {
    Eigen::ArrayXf males = newnewborn.cast<float>() * 1.06f / 2.06f;
    Eigen::ArrayXf females = newnewborn.cast<float>() * 1.0f / 2.06f;
    males_int = males.cast<int>();
    females_int = females.cast<int>();
}




}  // namespace demographic




// Eigen::ArrayXi Fertility::GenerateBirth(int index, 
//                                       const Eigen::ArrayXXi& age_matrix) {
//   // Initialize fertility matrix with same shape as age_matrix
//   Eigen::ArrayXXf fertility_matrix = Eigen::ArrayXXf::Zero(age_matrix.rows(), 
//                                                           age_matrix.cols());
  
//   // Calculate fertility rates for each person
//   for (int i = 0; i < age_matrix.rows(); ++i) {
//     int start_age = age_matrix(i, 0);
//     if (start_age > 49 || start_age == -1) {
//       continue;
//     }
    
//     int start = (start_age < 15) ? (15 - start_age) : 0;
//     for (int j = start; j < age_matrix.cols(); ++j) {
//       int age = age_matrix(i, j);
      
//       // Break if person has died
//       if (age == -1 || age > 49) {
//         break;
//       }
//       //std::cout << "input " << j << " " << age << " "<< std::endl;
//       //std::cout << "vale " << MapFertilityRate(index, j, age) << std::endl;
//       fertility_matrix(i, j) = MapFertilityRate(index, j, age);
//       //
      
//       // 
//     // std::cout << "element" << i << " "<< j <<" "<< fertility_matrix(i, j) << std::endl;
//     }

//   }

//     // std::string log_filename = "test/fer_log.txt";
//     // std::ofstream log_fil(log_filename,std::ios::out | std::ios::trunc);
//     // log_fil << fertility_matrix << "\n\n";
// //   write the matrix to logging file
// //   log_file << " fertility array by age group:\n" << births << "\n\n";

  
//   // Generate random matrix for comparison
//   Eigen::ArrayXXf random_matrix = Eigen::ArrayXXf::Zero(age_matrix.rows(), 
//                                                        age_matrix.cols());
//   for (int i = 0; i < random_matrix.rows(); ++i) {
//     for (int j = 0; j < random_matrix.cols(); ++j) {
//       random_matrix(i, j) = dis_(gen_);
//     }
//   }
  
//   // Compare random values with fertility rates
//   Eigen::ArrayXXi birth_matrix = (random_matrix < fertility_matrix)
//                                     .cast<int>();
  
//   // Calculate column sums
//   Eigen::ArrayXi column_sums = Eigen::ArrayXi::Zero(age_matrix.cols());
//   for (int j = 0; j < birth_matrix.cols(); ++j) {
//     column_sums(j) = birth_matrix.col(j).sum();
//   }
  
//   return column_sums;
// }