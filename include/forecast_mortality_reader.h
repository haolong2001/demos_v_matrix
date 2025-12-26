#pragma once

#include <string>
#include <vector>

using namespace std;

// Read mortality data from binary file into a 3D matrix (2x18x27)
vector<vector<vector<double>>> readForecastMortalityMatrix(
    const string &filename = "preprocess_py/mortality_forecast_from_24.bin");
