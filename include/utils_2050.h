#pragma once

#include <string>
#include <filesystem>

using namespace std;

// Inline helper function to check if file exists
inline bool fileExists(const std::string& filename) {
    return std::filesystem::exists(filename);
}