#include <iostream>
#include <Eigen/Dense>
#include <vector>
#include <EigenRand/EigenRand>
#include "deathages.h"

using namespace Eigen;
using namespace std;


PopulationSimulator:: PopulationSimulator()
 : random_generator(42){}
        


    /**
     * Generates death matrix based on age distribution and mortality rates
     * @param num_by_ages Vector containing number of people in each age group
     * @param gender_index Gender index for mortality rates
     * @param disappear_mat Mortality rates matrix
     * @return Pair of matrices: death matrix and existing matrix (1 = alive, 0 = dead)
     */

ArrayXXi PopulationSimulator::generateDeathMatrix(
        const VectorXi& num_by_ages,
        int index,
        const vector<ArrayXXf>& disappear_mat) {
        
        Rand::P8_mt19937_64 urng{42}; // Fixed seed for reproducibility
        int total_population = num_by_ages.sum();
        
        // Initialize matrices
        ArrayXXf prob_mat(total_population, NUM_YEARS);
        
        std::cout << "Step 2: okay" << std::endl;
        // Fill probability matrix
        int current_row = 0;
        for (int age = 0; age < num_by_ages.size(); ++age) {
            int num_people = num_by_ages[age];
            if (num_people > 0) {
                VectorXf mortality_rates = disappear_mat[index].row(age);
                prob_mat.block(current_row, 0, num_people, NUM_YEARS) = 
                    mortality_rates.replicate(1, num_people).transpose();
                current_row += num_people;
            }
        }
        std::cout <<"step 3 okay" << endl;
        // Generate random matrix and compare with probability matrix
        ArrayXXf rand_matrix = Rand::balanced<ArrayXXf>(total_population, NUM_YEARS, urng, 0, 1);
        // 1 means alive; 0 means death
        ArrayXXi existing_matrix = (rand_matrix > prob_mat).cast<int>();

        // Ensure death permanence (once dead, stays dead)
        for (int i = 0; i < existing_matrix.rows(); ++i) {
            bool found_death = false;
            for (int j = 0; j < existing_matrix.cols(); ++j) {
                if (!found_death && existing_matrix(i, j) == 0) {
                    found_death = true;
                }
                if (found_death) {
                    existing_matrix(i, j) = 0;
                }
            }
        }

        // Generate death matrix (inverse of existing matrix)
        // then 1 means 
        // ArrayXXi death_matrix = !(existing_matrix.cast<bool>()).cast<int>();
        
        return existing_matrix;
    }

    /**
     * Generates age matrix based on initial ages and existing matrix
     * @param num_by_ages Vector containing number of people in each age group
     * @param existing_matrix Matrix indicating alive (1) or dead (0) status
     * @return Age matrix with ages for each person at each year
     */
    ArrayXXi PopulationSimulator::generateAgeMatrix(
        const VectorXi& num_by_ages,
        const ArrayXXi& existing_matrix) {
        
        int total_population = num_by_ages.sum();
        ArrayXXi age_matrix = ArrayXXi::Zero(total_population, NUM_YEARS);
        
        // Create initial age vector
        VectorXi initial_ages(total_population);
        int current_index = 0;
        for (int age = 0; age < num_by_ages.size(); ++age) {
            initial_ages.segment(current_index, num_by_ages[age]).setConstant(age);
            current_index += num_by_ages[age];
        }
        
        // Generate year offsets
        ArrayXi year_offsets = ArrayXi::LinSpaced(NUM_YEARS, 0, NUM_YEARS - 1);
        
        // Fill age matrix
        for (int i = 0; i < total_population; ++i) {
            age_matrix.row(i) = (initial_ages[i] + year_offsets) * existing_matrix.row(i);
        }
        
        return age_matrix;
    }

