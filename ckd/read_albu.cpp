#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <map>
#include <sstream>
#include <unistd.h>

std::string get_current_dir() {
    char buff[FILENAME_MAX];
    getcwd(buff, FILENAME_MAX);
    return std::string(buff);
}

std::vector<std::vector<std::vector<double>>> read_transition_data(const std::string& filename) {

    // Initialize 3D vector [6][65][2]
    std::vector<std::vector<std::vector<double>>> data(
        6, std::vector<std::vector<double>>(
            65, std::vector<double>(2, 0.0)
        )
    );
    
    // Map to convert type names to indices
    std::map<std::string, int> type_to_index = {
        {"male_chn", 0},
        {"female_chn", 1},
        {"male_ind", 2},
        {"female_ind", 3},
        {"male_mal", 4},
        {"female_mal", 5}
    };

    std::ifstream file(filename); // define an input file stream 
    std::string line; // string type line
    int current_type = -1;
    int age_offset = 26; // Starting age

    // c++ use a pointer to get current line 
    while (std::getline(file, line)) {  // get the next line 
        // Skip empty lines
        if (line.empty()) continue;

        // Check for type identifier
        if (line.find("# Data from") != std::string::npos) {
            for (const auto& [type, index] : type_to_index) {
                if (line.find(type) != std::string::npos) {
                    current_type = index;
                    break;
                }
            }
            // Skip the header line
            std::getline(file, line);
            continue;
        }

        // Process data lines
        if (current_type >= 0) {
            std::stringstream ss(line);
            std::string token;
            std::vector<double> values;

            // Skip age
            // std::getline(ss, token, '\t');
            
            // Read P1 and P2
            while (std::getline(ss, token, '\t')) {
                // Remove quotes and convert to double
                token.erase(remove(token.begin(), token.end(), '"'), token.end());
                values.push_back(std::stod(token));
            }

            if (values.size() == 3) {
                int age_index = values[0] - age_offset;
                if (age_index >= 0 && age_index < 65) {
                    data[current_type][age_index][0] = values[1]; // P1
                    data[current_type][age_index][1] = values[2]; // P2
                }
            }
        }
    }

    return data;
}

// Function to access data
/**
 * measure :P1,P2
 * path: /Users/haolong/Documents/demos_v_matrix
 */



double get_transition_prob(const std::vector<std::vector<std::vector<double>>>& data,
                         int type, int age, int measure) {
    return data[type][age - 26][measure];
}

int main() {
    std::cout << "Current working directory: " << get_current_dir() << std::endl;

    // When opening file, you can debug like this:
    // ckd/data/albu_transit_rate.txt
    std::string filename = "ckd/data/albu_transit_rate.txt";
    std::cout << "Attempting to open: " << get_current_dir() << "/" << filename << std::endl;

    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Failed to open file: " << filename << std::endl;
        return 1;
    }
    auto transition_data = read_transition_data("ckd/data/albu_transit_rate.txt");
    
    // 3 decimal 
    std::cout << std::fixed << std::setprecision(3);
    // Example usage:
    // Get P1 for male_chn (type 0) at age 30 (index 4)
    double p1_male_chn_32 = get_transition_prob(transition_data, 0, 32, 0);
    std::cout << "P1 for male_chn at age 32: " << p1_male_chn_32 << std::endl;

    // Get P2 for female_ind (type 3) at age 45 (index 19)
    double p2_female_ind_45 = get_transition_prob(transition_data, 3, 45, 1);
    std::cout << "P2 for female_ind at age 45: " << p2_female_ind_45 << std::endl;

    // For file output ckd/output/ckd_logging.txt
    std::ofstream outFile("ckd/output/ckd_logging.txt");
    if (!outFile.is_open()) {
        std::cerr << "Failed to open output file" << std::endl;
        return 1;
    }
    outFile << std::fixed << std::setprecision(3);

    // Print male_chn (type 0) data
    outFile << "male_chn transition probabilities:\n";
    outFile << "Age\tP1\tP2\n";
    for (int age = 0; age < 65; ++age) {
        outFile << (age + 26) << "\t"
                << transition_data[0][age][0] << "\t"
                << transition_data[0][age][1] << "\n";
    }

    outFile.close();

    return 0;
}