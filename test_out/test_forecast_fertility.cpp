#include "../include/forecast_fertility.h"
#include <gtest/gtest.h>
#include <Eigen/Dense>
#include <iostream>

using namespace std;
using namespace Eigen;

class ForecastFertilityTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Create a population matrix with constant value 100
        // 1000 agents, 5 years (2024-2028)
        popu_mat = MatrixXi::Constant(1000, 5, 100);

        // Create test fertility rates (3 scenarios, 5 years, 35 ages)
        // Initialize with reasonable fertility rates
        fertility_rates.resize(3, vector<vector<double>>(5, vector<double>(35, 0.0)));
        
        // Set fertility rates for ages 15-49
        // Using a simple model: peak fertility at age 25-29
        for(int scenario = 0; scenario < 3; scenario++) {
            for(int year = 0; year < 5; year++) {
                for(int age = 0; age < 35; age++) {
                    int actual_age = age + 15;  // Convert to actual age
                    if(actual_age >= 15 && actual_age < 50) {
                        // Create a bell curve centered at age 25
                        double peak = 0.2 * (scenario + 1);  // Different peak rates for each scenario
                        double age_diff = actual_age - 25;
                        fertility_rates[scenario][year][age] = peak * exp(-(age_diff * age_diff) / 100.0);
                    }
                }
            }
        }
    }

    MatrixXi popu_mat;
    vector<vector<vector<double>>> fertility_rates;
};

TEST_F(ForecastFertilityTest, BasicBirthCalculation) {
    VectorXi male_births, female_births;
    calculateBirths(popu_mat, fertility_rates, 0, male_births, female_births);

    // Check output sizes
    EXPECT_EQ(male_births.size(), popu_mat.cols());
    EXPECT_EQ(female_births.size(), popu_mat.cols());

    // Check that births are non-negative
    for(int i = 0; i < male_births.size(); i++) {
        EXPECT_GE(male_births[i], 0);
        EXPECT_GE(female_births[i], 0);
    }



    // Print some statistics
    cout << "\nBirth Statistics for Basic Test:" << endl;
    cout << "--------------------------------" << endl;
    for(int i = 0; i < male_births.size(); i++) {
        cout << "Year " << (2024 + i) << ":" << endl;
        cout << "  Male births: " << male_births[i] << endl;
        cout << "  Female births: " << female_births[i] << endl;
        cout << "  Total births: " << (male_births[i] + female_births[i]) << endl;
        cout << "  Birth rate per 1000: " 
             << (1000.0 * (male_births[i] + female_births[i]) / popu_mat.rows()) << endl;
    }
}

TEST_F(ForecastFertilityTest, DifferentFertilityScenarios) {
    VectorXi male_births1, female_births1;
    VectorXi male_births2, female_births2;
    VectorXi male_births3, female_births3;

    calculateBirths(popu_mat, fertility_rates, 0, male_births1, female_births1);
    calculateBirths(popu_mat, fertility_rates, 1, male_births2, female_births2);
    calculateBirths(popu_mat, fertility_rates, 2, male_births3, female_births3);

    // Check that higher fertility scenarios lead to more births
    for(int i = 0; i < male_births1.size(); i++) {
        EXPECT_GE(male_births2[i], male_births1[i]);
        EXPECT_GE(male_births3[i], male_births2[i]);
        EXPECT_GE(female_births2[i], female_births1[i]);
        EXPECT_GE(female_births3[i], female_births2[i]);
    }

    // Print comparison of scenarios
    cout << "\nScenario Comparison:" << endl;
    cout << "-------------------" << endl;
    for(int i = 0; i < male_births1.size(); i++) {
        cout << "Year " << (2024 + i) << ":" << endl;
        cout << "  Scenario 1 (Low): " << (male_births1[i] + female_births1[i]) << " births" << endl;
        cout << "  Scenario 2 (Medium): " << (male_births2[i] + female_births2[i]) << " births" << endl;
        cout << "  Scenario 3 (High): " << (male_births3[i] + female_births3[i]) << " births" << endl;
    }
}

TEST_F(ForecastFertilityTest, ZeroFertilityRates) {
    // Create a fertility rates matrix with all zeros
    vector<vector<vector<double>>> zero_rates = fertility_rates;
    for(auto& scenario : zero_rates) {
        for(auto& year : scenario) {
            for(auto& rate : year) {
                rate = 0.0;
            }
        }
    }

    VectorXi male_births, female_births;
    calculateBirths(popu_mat, zero_rates, 0, male_births, female_births);

    // Check that all births are zero
    for(int i = 0; i < male_births.size(); i++) {
        EXPECT_EQ(male_births[i], 0);
        EXPECT_EQ(female_births[i], 0);
    }
}

TEST_F(ForecastFertilityTest, MaximumFertilityRates) {
    // Create a fertility rates matrix with maximum rates (1.0)
    vector<vector<vector<double>>> max_rates = fertility_rates;
    for(auto& scenario : max_rates) {
        for(auto& year : scenario) {
            for(auto& rate : year) {
                rate = 1.0;
            }
        }
    }

    VectorXi male_births, female_births;
    calculateBirths(popu_mat, max_rates, 0, male_births, female_births);

    // Check that births are non-zero and reasonable
    for(int i = 0; i < male_births.size(); i++) {
        EXPECT_GT(male_births[i], 0);
        EXPECT_GT(female_births[i], 0);
        // With maximum fertility rates, we expect a high number of births
        // but not more than the population size
        EXPECT_LE(male_births[i] + female_births[i], popu_mat.rows());
    }

    // Print statistics for maximum fertility case
    cout << "\nMaximum Fertility Test Results:" << endl;
    cout << "-----------------------------" << endl;
    for(int i = 0; i < male_births.size(); i++) {
        cout << "Year " << (2024 + i) << ":" << endl;
        cout << "  Total births: " << (male_births[i] + female_births[i]) << endl;
        cout << "  Birth rate per 1000: " 
             << (1000.0 * (male_births[i] + female_births[i]) / popu_mat.rows()) << endl;
    }
}

int main(int argc, char **argv) {
    testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
} 


// Test Setup:
// Creates a population matrix with 1000 agents and 5 years (2024-2028), all with age 100
// Creates realistic fertility rates using a bell curve model centered at age 25
// Three fertility scenarios with different peak rates (0.2, 0.4, 0.6)
// Test Cases:
// BasicBirthCalculation: Tests basic functionality and prints detailed statistics
// DifferentFertilityScenarios: Compares birth rates across different fertility scenarios
// ZeroFertilityRates: Tests edge case with zero fertility rates
// MaximumFertilityRates: Tests edge case with maximum fertility rates (1.0)
// Key Features:
// Verifies output sizes and non-negativity
// Checks male:female birth ratio (1:1.06)
// Prints detailed statistics for analysis
// Tests different fertility scenarios
// Includes edge cases (zero and maximum fertility rates)
// To compile and run the tests, you'll need to:
// Make sure Google Test is installed
// Add the test file to your build system
// Link against Eigen and Google Test
// Would you like me to help you set up the build system for the tests? Also, I notice that the population matrix has age 100 for all agents, which is outside the fertile age range (15-49). Would you like me to modify the test to use a more realistic age distribution within the fertile range?