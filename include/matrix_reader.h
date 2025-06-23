#pragma once
#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <iostream>

using namespace std;

class MatrixReader {
public:
    // Read CSV file into a 2D matrix
    static vector<vector<double>> readCSVMatrix(
        const string& filename,
        char delimiter = ','
    );    // Print matrix (first few elements for verification)
    static void printMatrixPreview(
        const vector<vector<double>>& matrix,
        int preview_rows,
        int preview_cols
    );

private:
    // Helper function to check if file exists
    static bool fileExists(const string& filename);
}; 