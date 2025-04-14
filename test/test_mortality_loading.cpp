#include <iostream>
#include <fstream>
#include <vector>
#include <Eigen/Dense>
#include <iomanip>
#include <filesystem>

using namespace Eigen;
using namespace std;

int main() {
    // Load projected mortality rates (2021-2050)
    std::ifstream mor_file("data/bin/mortality_matrix_mat.bin", std::ios::binary);
    if (!mor_file) {
        std::cerr << "Failed to open mortality_matrix_mat.bin" << std::endl;
        return -1;
    }

    // Get file size
    mor_file.seekg(0, std::ios::end);
    size_t file_size = mor_file.tellg();
    mor_file.seekg(0, std::ios::beg);

    cout << "File size: " << file_size << " bytes" << endl;
    cout << "Expected size (double): " << (2 * 86 * 30 * sizeof(double)) << " bytes" << endl;
    cout << "Size of double: " << sizeof(double) << " bytes" << endl << endl;

    // Read the mortality matrix (2, 86, 30) for 2021-2050
    vector<vector<ArrayXXd>> projected_mortality(2, vector<ArrayXXd>(86, ArrayXXd::Zero(30, 1)));
    
    // Read raw data first
    vector<double> raw_data(2 * 86 * 30);
    mor_file.read(reinterpret_cast<char*>(raw_data.data()), raw_data.size() * sizeof(double));
    
    // Print first few raw values
    cout << "First 10 raw values from file:" << endl;
    for (int i = 0; i < 10; ++i) {
        cout << raw_data[i] << " ";
    }
    cout << endl << endl;

    // Now organize into the matrix structure
    for (int gender = 0; gender < 2; ++gender) {
        for (int age = 0; age < 86; ++age) {
            for (int year = 0; year < 30; ++year) {
                size_t index = gender * (86 * 30) + age * 30 + year;
                projected_mortality[gender][age](year, 0) = raw_data[index];
            }
        }
    }

    mor_file.close();

    // Print summary statistics
    cout << "Mortality Matrix Loading Test" << endl;
    cout << "============================" << endl;
    cout << "Matrix dimensions: [2 genders, 86 ages, 30 years]" << endl << endl;

    // Print sample data for verification
    cout << "Sample data for first few ages and years:" << endl;
    cout << "----------------------------------------" << endl;
    
    // Print header for years
    cout << "Age\tGender\t";
    for (int year = 0; year < 5; ++year) {
        cout << (2021 + year) << "\t";
    }
    cout << "..." << endl;

    // Print data for first 5 ages and first 5 years
    for (int age = 0; age < 5; ++age) {
        for (int gender = 0; gender < 2; ++gender) {
            cout << age << "\t" << (gender == 0 ? "Male" : "Female") << "\t";
            for (int year = 0; year < 5; ++year) {
                cout << std::fixed << std::setprecision(4) 
                     << projected_mortality[gender][age](year, 0) << "\t";
            }
            cout << "..." << endl;
        }
    }

    // Print some statistics
    cout << "\nStatistics:" << endl;
    cout << "-----------" << endl;
    
    // Calculate and print min, max, mean for each gender
    for (int gender = 0; gender < 2; ++gender) {
        double min_val = std::numeric_limits<double>::max();
        double max_val = std::numeric_limits<double>::lowest();
        double sum = 0.0;
        int count = 0;

        for (int age = 0; age < 86; ++age) {
            for (int year = 0; year < 30; ++year) {
                double val = projected_mortality[gender][age](year, 0);
                min_val = std::min(min_val, val);
                max_val = std::max(max_val, val);
                sum += val;
                count++;
            }
        }

        cout << (gender == 0 ? "Male" : "Female") << " Statistics:" << endl;
        cout << "  Minimum: " << std::fixed << std::setprecision(4) << min_val << endl;
        cout << "  Maximum: " << std::fixed << std::setprecision(4) << max_val << endl;
        cout << "  Mean: " << std::fixed << std::setprecision(4) << (sum / count) << endl;
        cout << endl;
    }

    // Verify data consistency
    cout << "Data Consistency Check:" << endl;
    cout << "----------------------" << endl;
    
    bool has_nan = false;
    bool has_inf = false;
    bool has_negative = false;

    for (int gender = 0; gender < 2; ++gender) {
        for (int age = 0; age < 86; ++age) {
            for (int year = 0; year < 30; ++year) {
                double val = projected_mortality[gender][age](year, 0);
                if (std::isnan(val)) has_nan = true;
                if (std::isinf(val)) has_inf = true;
                if (val < 0) has_negative = true;
            }
        }
    }

    cout << "Contains NaN values: " << (has_nan ? "Yes" : "No") << endl;
    cout << "Contains Inf values: " << (has_inf ? "Yes" : "No") << endl;
    cout << "Contains negative values: " << (has_negative ? "Yes" : "No") << endl;

    return 0;
} 