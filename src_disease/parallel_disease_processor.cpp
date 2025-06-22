#include <iostream>
#include <vector>
#include <string>
#include <filesystem>
#include <fstream>
#include <thread>
#include <mutex>
#include <algorithm>
#include <Eigen/Dense>
#include <regex>

using namespace std;
using namespace Eigen;

// Structure to hold processed data for each folder
struct ProcessedData {
    string folder_name;
    vector<MatrixXi> age_matrices;  // 8 matrices (0-7)
    bool success;
    string error_message;
};

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

// Function to process a single folder
ProcessedData processFolder(const string& folder_path) {
    ProcessedData result;
    result.folder_name = filesystem::path(folder_path).filename().string();
    result.success = false;
    
    try {
        {
            lock_guard<mutex> lock(output_mutex);
            cout << "Processing folder: " << result.folder_name << endl;
        }
        
        // Read each binary file (0-7)
        for (int i = 0; i < 8; ++i) {
            string filename = folder_path + "/forecast_matrix_" + to_string(i) + ".bin";
            
            if (!filesystem::exists(filename)) {
                throw runtime_error("File not found: " + filename);
            }
            
            // Read binary matrix
            MatrixXi matrix = readBinaryMatrix(filename);
            
            // Remove dead people
            MatrixXi filtered_matrix = removeDeadPeople(matrix);
            
            result.age_matrices.push_back(filtered_matrix);
            
            {
                lock_guard<mutex> lock(output_mutex);
                cout << "  Matrix " << i << ": " << matrix.rows() << " -> " 
                     << filtered_matrix.rows() << " rows" << endl;
            }
        }
        
        result.success = true;
        
        {
            lock_guard<mutex> lock(output_mutex);
            cout << "Successfully processed: " << result.folder_name << endl;
        }
        
    } catch (const exception& e) {
        result.error_message = e.what();
        {
            lock_guard<mutex> lock(output_mutex);
            cerr << "Error processing " << result.folder_name << ": " << e.what() << endl;
        }
    }
    
    return result;
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
        string output_dir = "output";
        
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
        
        cout << "Using " << num_threads << " threads for parallel processing" << endl;
        
        // Process folders in parallel
        vector<ProcessedData> results(folders.size());
        vector<thread> threads;
        
        // Create thread pool
        for (size_t i = 0; i < folders.size(); ++i) {
            threads.emplace_back([&, i]() {
                results[i] = processFolder(folders[i]);
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
        
        // Summary
        cout << "\n=== Processing Summary ===" << endl;
        int successful = 0;
        int failed = 0;
        
        for (const auto& result : results) {
            if (result.success) {
                successful++;
                cout << "✓ " << result.folder_name << " (" 
                     << result.age_matrices.size() << " matrices)" << endl;
            } else {
                failed++;
                cout << "✗ " << result.folder_name << " - " << result.error_message << endl;
            }
        }
        
        cout << "\nTotal: " << successful << " successful, " << failed << " failed" << endl;
        
        return failed > 0 ? 1 : 0;
        
    } catch (const exception& e) {
        cerr << "Error in main: " << e.what() << endl;
        return 1;
    }
} 