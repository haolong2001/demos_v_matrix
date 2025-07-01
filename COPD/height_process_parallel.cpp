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

struct HeightTable {
    MatrixXd coefficients;  // Matrix of Height coefficients
    int rows;
    int cols;
};

// Global BMI table (to be loaded from file)
HeightTable heighttable;

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

    typedef Eigen::Matrix<int, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> MatrixXiRowMajor;
    Eigen::Map<MatrixXiRowMajor> matrix(data.data(), num_rows, 27);
    return MatrixXi(matrix);
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
HeightTable loadHeightTable(const string& filename) {
    HeightTable table;
    ifstream file(filename);
    if (!file) {
        throw runtime_error("Cannot open Height table file: " + filename);
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
        throw runtime_error("No data found in Height table file");
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
                throw runtime_error("Invalid CSV format in Height table");
            }
        }
    }
    
    return table;
}

// Function to calculate Height for a row (male)
VectorXd calculateHeightRow_Male(const VectorXi& row, int index, const HeightTable& heighttable) {
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

    static random_device rd;
    static mt19937 gen(rd()); 
    normal_distribution<float> norm(176.5, 6.97); // Default for male adults
    float height_value_at_18 = norm(gen);
    
    // Calculate Height for each age in the row
    VectorXd height_values(row.size());
    for (int i = 0; i < row.size(); ++i) {
        int age = row(i);
        // Calculate height based on age
        float height_value;

        if (age == -1) {
            height_value = -1.0;
        } 
        else {
            if (age <= 18){
                static random_device rd;
                static mt19937 gen(rd());   
                float mean = heighttable.coefficients(age, 1);
                float sd = heighttable.coefficients(age, 2);
                normal_distribution<float> norm(mean, sd);
                height_value = norm(gen);
                if (i > 0 && age <= 16 && height_value < height_values(i - 1) && height_values(i - 1) >= 0){
                    height_value = height_values(i - 1) + 4.0;
                }
                else if (i > 0 && age >= 17 && height_value < height_values(i - 1) && height_values(i - 1) >= 0){
                    height_value = height_values(i - 1);
                }
            }
            else if (age >= 40){
                height_value = height_value_at_18 - 0.12*( age - 40); // Decrease height by 0.12 cm per year after 40
            }
            else{
                height_value = height_value_at_18; 
            }

        }

        if (height_value >= 0) {
            height_values(i) = height_value;
        } else {
            height_values(i) = -1.0;
        }
        
    }
    
    return height_values;
}

// Function to calculate Height for a row (female)
VectorXd calculateHeightRow_Female(const VectorXi& row, int index, const HeightTable& heighttable) {
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

    static random_device rd;
    static mt19937 gen(rd()); 
    normal_distribution<float> norm(163.5, 6.41); // Default for female adults
    float height_value_at_18 = norm(gen);
    

    // Calculate Height for each age in the row
    VectorXd height_values(row.size());
    for (int i = 0; i < row.size(); ++i) {
        int age = row(i);
        // Calculate height based on age
        float height_value;

        if (age == -1) {
            height_value = -1.0;
        } 
        else {
            if (age <= 18){
                static random_device rd;
                static mt19937 gen(rd());   
                float mean = heighttable.coefficients(age, 1);
                float sd = heighttable.coefficients(age, 2);
                normal_distribution<float> norm(mean, sd);
                height_value = norm(gen);
               if (i > 0 && age <= 16 && height_value < height_values(i - 1) && height_values(i - 1) >= 0){
                    height_value = height_values(i - 1) + 4.0;
                }
                else if (i > 0 && age >= 17 && height_value < height_values(i - 1) && height_values(i - 1) >= 0){
                    height_value = height_values(i - 1);
                }
            }
            else if (age >= 40){
                height_value = height_value_at_18-0.12*(age-40); // Decrease height by 0.12 cm per year after 40
            }
            else{
                height_value = height_value_at_18; 
            }
        }

        if (height_value >= 0) {
            height_values(i) = height_value;
        } else {
            height_values(i) = -1.0;
        }
        
    }
    
    return height_values;
}

// Function to process a single folder
void processFolderHeight(const string& folder_path, const HeightTable& heighttable) {
    string folder_name = filesystem::path(folder_path).filename().string();
    cout << "Processing Height for folder: " << folder_name << endl;
    
    // Create Height subfolder if it doesn't exist
    string height_folder = folder_path + "/Height";
    if (!filesystem::exists(height_folder)) {
        filesystem::create_directories(height_folder);
    }
    
    // Process each male matrix (0,2,4,6)
    for (int i = 0; i < 8; i+=2) {
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
        
        // Calculate Height for each row
        MatrixXd height_matrix(filtered_matrix.rows(), filtered_matrix.cols());
        
        for (int row = 0; row < filtered_matrix.rows(); ++row) {
            VectorXd height_row = calculateHeightRow_Male(filtered_matrix.row(row), i, heighttable);
            height_matrix.row(row) = height_row;
        }
        
        // Save Height matrix to binary file
        string height_filename = height_folder + "/height_matrix_" + to_string(i) + ".bin";
        ofstream height_file(height_filename, ios::binary);
        if (!height_file) {
            throw runtime_error("Cannot create Height file: " + height_filename);
        }
        
        // Write matrix data as floats
        for (int r = 0; r < height_matrix.rows(); ++r) {
            for (int c = 0; c < height_matrix.cols(); ++c) {
                float val = height_matrix(r, c);
                height_file.write(reinterpret_cast<char*>(&val), sizeof(float));
            }
        }
        
        height_file.close();
        cout << "  Saved Height matrix " << i << " to " << height_filename << endl;
    }

    // Process each female matrix (1,3,5,7)
    for (int i = 1; i < 8; i+=2) {
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
        
        // Calculate Height for each row
        MatrixXd height_matrix(filtered_matrix.rows(), filtered_matrix.cols());
        
        for (int row = 0; row < filtered_matrix.rows(); ++row) {
            VectorXd height_row = calculateHeightRow_Female(filtered_matrix.row(row), i, heighttable);
            height_matrix.row(row) = height_row;
        }
        
        // Save Height matrix to binary file
        string height_filename = height_folder + "/height_matrix_" + to_string(i) + ".bin";
        ofstream height_file(height_filename, ios::binary);
        if (!height_file) {
            throw runtime_error("Cannot create Height file: " + height_filename);
        }
        
        // Write matrix data as floats
        for (int r = 0; r < height_matrix.rows(); ++r) {
            for (int c = 0; c < height_matrix.cols(); ++c) {
                float val = height_matrix(r, c);
                height_file.write(reinterpret_cast<char*>(&val), sizeof(float));
            }
        }
        
        height_file.close();
        cout << "  Saved Height matrix " << i << " to " << height_filename << endl;
    }
    
    cout << "Completed Height processing for: " << folder_name << endl;
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
        string height_table_file = "./COPD/height_coef.csv";  // Updated to use existing CSV file
        
        // Load BMI table
        cout << "Loading Height table from: " << height_table_file << endl;
        heighttable = loadHeightTable(height_table_file);
        cout << "Height table loaded: " << heighttable.rows << " rows x " << heighttable.cols << " columns" << endl;
        
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
        
        cout << "Using " << num_threads << " threads for parallel Height processing" << endl;
        
        // Process folders in parallel
        vector<thread> threads;
        
        // Create thread pool
        for (size_t i = 0; i < folders.size(); ++i) {
            threads.emplace_back([&, i]() {
                try {
                    processFolderHeight(folders[i], heighttable);
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
        
        cout << "\n=== Height Processing Complete ===" << endl;
        cout << "Processed " << folders.size() << " folders in parallel" << endl;
        
        return 0;
        
    } catch (const exception& e) {
        cerr << "Error in main: " << e.what() << endl;
        return 1;
    }
}