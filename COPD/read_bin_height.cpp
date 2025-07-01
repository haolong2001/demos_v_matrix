#include <iostream>
#include <fstream>
#include <vector>
#include <filesystem>
#include <cassert>

int main() {

    const std::string input_file = "./output/20250620_101235_2940/Height/height_matrix_0.bin";
    const std::string output_file = "./output/20250620_101235_2940/Height/height_matrix_0.csv";
    const int cols = 27;
    const int float_size = 4;

    // 1. Get file size
    std::ifstream bin(input_file, std::ios::binary | std::ios::ate);
    if (!bin) {
        std::cerr << "Error opening binary file: " << input_file << std::endl;
        return 1;
    }
    std::streamsize file_size = bin.tellg();
    bin.seekg(0, std::ios::beg);

    // 2. Calculate number of rows
    assert(file_size % (cols * float_size) == 0); // sanity check
    std::size_t rows = file_size / (cols * float_size);

    std::cout << "Reading " << rows << " rows of " << cols << " columns" << std::endl;

    // 3. Read all data into buffer
    std::vector<float> data(rows * cols);
    bin.read(reinterpret_cast<char*>(data.data()), file_size);
    bin.close();

    // 4. Write to CSV
    std::ofstream csv(output_file);
    if (!csv) {
        std::cerr << "Error opening CSV output file: " << output_file << std::endl;
        return 1;
    }

    for (std::size_t i = 0; i < rows; ++i) {
        for (int j = 0; j < cols; ++j) {
            csv << data[i * cols + j];
            if (j < cols - 1) csv << ",";
        }
        csv << "\n";
    }

    csv.close();
    std::cout << "CSV file written to: " << output_file << std::endl;
    
    return 0;
}
