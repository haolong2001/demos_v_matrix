#include <iostream>
#include <vector>
#include <string>
#include <filesystem>
#include <fstream>
#include <random>
#include <cmath>
#include <Eigen/Dense>
#include <regex>
#include <thread>
#include <mutex>

using namespace std;
using namespace Eigen;

// BMI table structure (you'll need to load this from a file)
struct BMITable {
    MatrixXd coefficients;  // Matrix of BMI coefficients
    int rows;
    int cols;
};

// Global BMI table (to be loaded from file)
BMITable bmitable;

// Global mutex for thread-safe output
mutex output_mutex;

// Function to read binary matrix file
MatrixXi readBinaryMatrix(const string& filename) {
    ifstream file(filename, ios::binary);
    if (!file) {
        throw runtime_error("Cannot open file: " + filename);
    }
    
    // Get file size
    file.seekg(0, ios::end);
    size_t file_size = file.tellg();
    file.seekg(0, ios::beg);
    
    // Calculate number of rows (27 columns, 4 bytes per int32)
    size_t num_rows = file_size / (27 * 4);
    
    // Read all data
    vector<int32_t> data(num_rows * 27);
    file.read(reinterpret_cast<char*>(data.data()), file_size);
    
    // Reshape into matrix
    MatrixXi matrix = Map<MatrixXi>(data.data(), num_rows, 27);
    
    return matrix;
}

// Function to remove dead people (rows with all negative values)
MatrixXi removeDeadPeople(const MatrixXi& matrix) {
    vector<int> valid_rows;
    
    for (int i = 0; i < matrix.rows(); ++i) {
        bool has_positive = false;
        for (int j = 0; j < matrix.cols(); ++j) {
            if (matrix(i, j) >= 0) {
                has_positive = true;
                break;
            }
        }
        if (has_positive) {
            valid_rows.push_back(i);
        }
    }
    
    if (valid_rows.empty()) {
        return MatrixXi(0, matrix.cols());
    }
    
    MatrixXi filtered_matrix(valid_rows.size(), matrix.cols());
    for (size_t i = 0; i < valid_rows.size(); ++i) {
        filtered_matrix.row(i) = matrix.row(valid_rows[i]);
    }
    
    return filtered_matrix;
}

// Function to load BMI table from CSV file
BMITable loadBMITable(const string& filename) {
    BMITable table;
    ifstream file(filename);
    if (!file) {
        throw runtime_error("Cannot open BMI table file: " + filename);
    }
    
    // Skip header line
    string header;
    getline(file, header);
    
    // Count rows and columns
    vector<string> lines;
    string line;
    while (getline(file, line)) {
        if (!line.empty()) {
            lines.push_back(line);
        }
    }
    
    table.rows = lines.size();
    if (table.rows == 0) {
        throw runtime_error("No data found in BMI table file");
    }
    
    // Count columns from first line
    string first_line = lines[0];
    table.cols = 1; // Start with 1 for the first column
    for (char c : first_line) {
        if (c == ',') table.cols++;
    }
    
    // Initialize matrix
    table.coefficients = MatrixXd(table.rows, table.cols);
    
    
    // Parse each line
    for (int i = 0; i < table.rows; ++i) {
        stringstream ss(lines[i]);
        string value;
        
        for (int j = 0; j < table.cols; ++j) {
            if (getline(ss, value, ',')) {
                table.coefficients(i, j) = stod(value);
            } else {
                throw runtime_error("Invalid CSV format in BMI table");
            }
        }
    }
    
    return table;
}

// Function to calculate BMI for a row (person)
VectorXd calculateBMIRow(const VectorXi& row, int index, const BMITable& bmitable) {
    // Find first nonnegative index
    int first_nonzero_idx = -1;
    int first_nonzero_value = -1;
    
    for (int i = 0; i < row.size(); ++i) {
        if (row(i) >= 0) {
            first_nonzero_idx = i;
            first_nonzero_value = row(i);
            break;
        }
    }
    
    if (first_nonzero_idx == -1) {
        // All values are negative, return -1 for all
        return VectorXd::Constant(row.size(), -1.0);
    }
    
    // Calculate yearborn
    int yearborn = 1989 + first_nonzero_idx - first_nonzero_value;
    
    // Initialize random number generator
    static random_device rd;
    static mt19937 gen(rd());
    static normal_distribution<double> norm(0.0, 1.0);
    
    // Generate random numbers (once per row)
    double r0 = norm(gen);
    double r1 = norm(gen);
    double r2 = norm(gen);
    double r3 = norm(gen);
    
    // Calculate hyperparameters (once per row)
    double M1 = bmitable.coefficients(index, 0) + bmitable.coefficients(index, 6) * r0;
    double M2 = bmitable.coefficients(index, 1) + bmitable.coefficients(index, 7) * r0 + bmitable.coefficients(index, 8) * r1;
    double M3 = bmitable.coefficients(index, 2) + bmitable.coefficients(index, 9) * r0 + bmitable.coefficients(index, 10) * r1 + bmitable.coefficients(index, 11) * r2;
    double M4 = bmitable.coefficients(index, 3) + bmitable.coefficients(index, 12) * r0 + bmitable.coefficients(index, 13) * r1 + bmitable.coefficients(index, 14) * r2 + bmitable.coefficients(index, 15) * r3;
    
    // Calculate coefficients (once per row)
    double y0 = M2 + bmitable.coefficients(index, 4) * (yearborn - 1950) + M1 * (35 - 18);
    double y1 = M2 + bmitable.coefficients(index, 4) * (yearborn - 1950);
    double y2 = M2 + bmitable.coefficients(index, 4) * (yearborn - 1950) + M3 * (55 - 35);
    double y3 = M2 + bmitable.coefficients(index, 4) * (yearborn - 1950) + M3 * (55 - 35) + M4 * (75 - 55);
    
    double m1 = 6 * (0.014492754 * ((y2 - y1) / 20 - (y1 - y0) / 17) - 0.003623188 * ((y3 - y2) / 20 - (y2 - y1) / 20));
    double m2 = 6 * (-0.003623188 * ((y2 - y1) / 20 - (y1 - y0) / 17) + 0.013405797 * ((y3 - y2) / 20 - (y2 - y1) / 20));
    double b0 = (y1 - y0) / 17 - 17.0 / 6 * m1;
    double b1 = (y2 - y1) / 20 - 10 * m1 - 20.0 / 6 * (m2 - m1);
    double b2 = (y3 - y2) / 20 - 10 * m2 + 20.0 / 6 * m2;
    double d0 = m1 / (6 * 17);
    double d1 = (m2 - m1) / (6 * 20);
    double d2 = (-m2) / (6 * 20);
    
    // Get scale for this person
    double scale = bmitable.coefficients(index, 5);
    
    // Calculate BMI for each age in the row
    VectorXd bmi_values(row.size());
    for (int i = 0; i < row.size(); ++i) {
        int age = row(i);
        
        // Calculate BMI based on age
        double bmi_value;
        if (age == -1) {
            bmi_value = -1.0;
        } else if (age > 80) {
            bmi_value = 0;
        } else if (age >= 55 && age <= 80) {
            bmi_value = y2 + b2 * (age - 55) + d2 * pow(age - 55, 3) + m2 / 2 * pow(age - 55, 2);
        } else if (age >= 35 && age < 55) {
            bmi_value = y1 + b1 * (age - 35) + d1 * pow(age - 35, 3) + m1 / 2 * pow(age - 35, 2);
        } else if (age >= 0 && age < 35) {
            bmi_value = y0 + b0 * (age - 18) + d0 * pow(age - 18, 3);
        } else {
            bmi_value = -1.0;
        }
        
        // Apply random noise and exponential transformation
        if (bmi_value >= 0) {
            double noise = norm(gen);
            bmi_values(i) = exp(bmi_value + scale * noise);
        } else {
            bmi_values(i) = -1.0;
        }
    }
    
    return bmi_values;
}

// Function to process a single folder
void processFolderBMI(const string& folder_path, const BMITable& bmitable) {
    string folder_name = filesystem::path(folder_path).filename().string();
    cout << "Processing BMI for folder: " << folder_name << endl;
    
    // Create BMI subfolder if it doesn't exist
    string bmi_folder = folder_path + "/BMI";
    if (!filesystem::exists(bmi_folder)) {
        filesystem::create_directories(bmi_folder);
    }
    
    // Process each matrix (0-7)
    for (int i = 0; i < 8; ++i) {
        string filename = folder_path + "/forecast_matrix_" + to_string(i) + ".bin";
        
        if (!filesystem::exists(filename)) {
            cerr << "File not found: " << filename << endl;
            continue;
        }
        
        // Read and filter matrix
        MatrixXi matrix = readBinaryMatrix(filename);
        MatrixXi filtered_matrix = removeDeadPeople(matrix);
        
        cout << "  Matrix " << i << ": " << matrix.rows() << " -> " 
             << filtered_matrix.rows() << " rows" << endl;
        
        // Calculate BMI for each row
        MatrixXd bmi_matrix(filtered_matrix.rows(), filtered_matrix.cols());
        
        for (int row = 0; row < filtered_matrix.rows(); ++row) {
            VectorXd bmi_row = calculateBMIRow(filtered_matrix.row(row), i, bmitable);
            bmi_matrix.row(row) = bmi_row;
        }
        
        // Save BMI matrix to binary file
        string bmi_filename = bmi_folder + "/bmi_matrix_" + to_string(i) + ".bin";
        ofstream bmi_file(bmi_filename, ios::binary);
        if (!bmi_file) {
            throw runtime_error("Cannot create BMI file: " + bmi_filename);
        }
        
        // Write matrix data as doubles
        for (int r = 0; r < bmi_matrix.rows(); ++r) {
            for (int c = 0; c < bmi_matrix.cols(); ++c) {
                double val = bmi_matrix(r, c);
                bmi_file.write(reinterpret_cast<char*>(&val), sizeof(double));
            }
        }
        
        bmi_file.close();
        cout << "  Saved BMI matrix " << i << " to " << bmi_filename << endl;
    }
    
    cout << "Completed BMI processing for: " << folder_name << endl;
}

// Function to find all forecast folders
vector<string> findForecastFolders(const string& output_dir) {
    vector<string> folders;
    
    for (const auto& entry : filesystem::directory_iterator(output_dir)) {
        if (entry.is_directory()) {
            string folder_name = entry.path().filename().string();
            
            // Check if it's a forecast folder (matches pattern: YYYYMMDD_HHMMSS_RRRR)
            regex forecast_pattern(R"(\d{8}_\d{6}_\d{4})");
            if (regex_match(folder_name, forecast_pattern)) {
                folders.push_back(entry.path().string());
            }
        }
    }
    
    return folders;
}

int main() {
    try {
        string output_dir = "./output";
        string bmi_table_file = "./data/bmitable.csv";  // Updated to use existing CSV file
        
        // Load BMI table
        cout << "Loading BMI table from: " << bmi_table_file << endl;
        bmitable = loadBMITable(bmi_table_file);
        cout << "BMI table loaded: " << bmitable.rows << " rows x " << bmitable.cols << " columns" << endl;
        
        // Find all forecast folders
        vector<string> folders = findForecastFolders(output_dir);
        
        if (folders.empty()) {
            cout << "No forecast folders found in " << output_dir << endl;
            return 1;
        }
        
        cout << "Found " << folders.size() << " forecast folders to process" << endl;
        
        // Determine number of threads (use all available cores)
        unsigned int num_threads = thread::hardware_concurrency();
        if (num_threads == 0) num_threads = 4;  // Fallback
        
        cout << "Using " << num_threads << " threads for parallel BMI processing" << endl;
        
        // Process folders in parallel
        vector<thread> threads;
        
        // Create thread pool
        for (size_t i = 0; i < folders.size(); ++i) {
            threads.emplace_back([&, i]() {
                try {
                    processFolderBMI(folders[i], bmitable);
                } catch (const exception& e) {
                    lock_guard<mutex> lock(output_mutex);
                    cerr << "Error processing folder " << folders[i] << ": " << e.what() << endl;
                }
            });
            
            // Limit number of concurrent threads
            if (threads.size() >= num_threads) {
                for (auto& t : threads) {
                    t.join();
                }
                threads.clear();
            }
        }
        
        // Wait for remaining threads
        for (auto& t : threads) {
            t.join();
        }
        
        cout << "\n=== BMI Processing Complete ===" << endl;
        cout << "Processed " << folders.size() << " folders in parallel" << endl;
        
        return 0;
        
    } catch (const exception& e) {
        cerr << "Error in main: " << e.what() << endl;
        return 1;
    }
}