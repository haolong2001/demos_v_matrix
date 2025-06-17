#pragma once

#include <string>
#include <filesystem>

// Inline helper function to check if file exists
inline bool fileExists(const std::string& filename) {
    return std::filesystem::exists(filename);
}