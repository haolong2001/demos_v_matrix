#include "forecast_mortality_reader.h"
#include <iostream>

using namespace std;

// Test function to verify the reading
void printMatrixPreview(const vector<vector<vector<double>>>& matrix) {
    cout << "First few elements of the matrix:" << endl;
    for(int i = 0; i < 2; i++) {
        cout << "Matrix " << i << ":" << endl;
        for(int j = 0; j < 3; j++) {
            for(int k = 0; k < 3; k++) {
                cout << matrix[i][j][k] << " ";
            }
            cout << endl;
        }
        cout << endl;
    }

    cout << "Total elements: " << 2 * 18 * 27 << endl;
    cout << "Total size in bytes: " << 2 * 18 * 27 * sizeof(double) << endl;
}

int main() {
    try {
        auto matrix = readMortalityMatrix();
        printMatrixPreview(matrix);
        return 0;
    } catch (const exception& e) {
        cerr << "Error: " << e.what() << endl;
        return 1;
    }
} 