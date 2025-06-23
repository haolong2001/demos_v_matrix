# CMake Build System

This directory contains the CMake build configuration for the demos_v_matrix project.

## Files

- `CMakeLists.txt` - Main build configuration (builds all components)
- `CMakeLists_reconstruct_1990_2023.txt` - Population reconstruction (1990-2023)
- `CMakeLists_forecast_2024_2050.txt` - Population forecast (2024-2050)
- `CMakeLists_migration.txt` - Migration matrix calculation

## Usage

### Build All Components
```bash
mkdir build_cmake
cd build_cmake
cmake ../cmake
make
```

### Build Specific Components
```bash
# Build only reconstruction
cmake ../cmake -DBUILD_RECONSTRUCT=ON -DBUILD_FORECAST=OFF -DBUILD_MIGRATION=OFF

# Build only forecast
cmake ../cmake -DBUILD_RECONSTRUCT=OFF -DBUILD_FORECAST=ON -DBUILD_MIGRATION=OFF

# Build only migration
cmake ../cmake -DBUILD_RECONSTRUCT=OFF -DBUILD_FORECAST=OFF -DBUILD_MIGRATION=ON
```

### Individual Component Builds
```bash
# Reconstruction only
mkdir build_reconstruct
cd build_reconstruct
cmake ../cmake/CMakeLists_reconstruct_1990_2023.txt
make

# Forecast only
mkdir build_forecast
cd build_forecast
cmake ../cmake/CMakeLists_forecast_2024_2050.txt
make

# Migration only
mkdir build_migration
cd build_migration
cmake ../cmake/CMakeLists_migration.txt
make
```

## Output

All executables are built to the `../build/` directory:
- `reconstruct_1990_2023` - Population reconstruction
- `forecast_2024_2050` - Population forecast
- `get_migration_matrix` - Migration calculation
- `test_migration` - Migration tests 