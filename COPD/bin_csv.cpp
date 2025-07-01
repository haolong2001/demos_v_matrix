#include <iostream>
#include <fstream>
#include <vector>
#include <string>

int main() {
    // Open binary file for reading
    std::ifstream inFile("/Users/zhanghaobo/Documents/GitHub/demos_v_matrix/output/20250620_101235_2940/BMI/bmi_matrix_0.bin", std::ios::binary);
    std::ofstream outFile("/Users/zhanghaobo/Documents/GitHub/demos_v_matrix/output/20250620_101235_2940/BMI/bmi_matrix_0.csv");
    if (!inFile) {
        std::cerr << "Could not open input file" << std::endl;
        return 1;
    }

    // Get file size
    inFile.seekg(0, std::ios::end);
    size_t fileSize = inFile.tellg();
    inFile.seekg(0, std::ios::beg);

    // Calculate number of rows (27 columns, 4 bytes per int32)
    size_t numRows = fileSize / (27 * 4);

    // Read data into vector
    std::vector<float> data(numRows * 27);
    inFile.read(reinterpret_cast<char*>(data.data()), fileSize);
    inFile.close();

    // Open CSV file for writing
    if (!outFile) {
        std::cerr << "Could not open output file" << std::endl;
        return 1;
    }

    // Write data as CSV
    for (size_t row = 0; row < numRows; row++) {
        for (size_t col = 0; col < 27; col++) {
            outFile << data[row * 27 + col];
            if (col < 26) outFile << ",";
        }
        outFile << "\n";
    }
    outFile.close();

    std::cout << "Successfully converted binary file to CSV" << std::endl;
    return 0;
}