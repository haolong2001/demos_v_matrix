#ifndef READ_ALBU_H
#define READ_ALBU_H

#include <vector>
#include <string>
#include <map>

// Main function to read data from file into 3D vector
std::vector<std::vector<std::vector<double>>> read_transition_data(const std::string& filename);

// Helper function to get transition probability
double get_transition_prob(const std::vector<std::vector<std::vector<double>>>& data,
                         int type, int age, int measure);

// Directory and file handling functions
std::string get_current_dir();
std::vector<std::vector<std::vector<double>>> read_transition_data(const std::string& filename);


#endif // READ_ALBU_H 