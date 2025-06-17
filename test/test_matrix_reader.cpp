#include "matrix_reader.h" //  these are also okay ../include/matrix_reader.h
#include <cassert>
#include <iostream>

using namespace std;

void testCSVMatrix(const string& path) {
    try {
        auto matrix = MatrixReader::readCSVMatrix(path);
        
        // Test that matrix was read successfully
        assert(!matrix.empty());
        assert(!matrix[0].empty());
        
        cout << "CSV matrix test passed!" << endl;
        MatrixReader::printMatrixPreview(matrix, 2, 10);
    } catch (const exception& e) {
        cerr << "CSV matrix test failed: " << e.what() << endl;
        throw;
    }
}

int main() {
    try {
        testCSVMatrix("output/popu_matrix_0.csv");
        cout << "All tests passed!" << endl;
        return 0;
    } catch (const exception& e) {
        cerr << "Test failed: " << e.what() << endl;
        return 1;
    }
}

// clang++ -std=c++17 test/test_matrix_reader.cpp src_2050/matrix_reader.cpp -o build/test_matrix_reader
// ./build/test_matrix_reader