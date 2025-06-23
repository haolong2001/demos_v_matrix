cmake_minimum_required(VERSION 3.10)
project(migration_matrix)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add include directory
include_directories(${PROJECT_SOURCE_DIR}/include)

# Collect source files
set(SOURCES
    src/deathages.cpp
    src/DataLoader.cpp
    src/fertility.cpp
    src/migration.cpp
    src/utils.cpp
    src/validate.cpp
    src/Get_migration_matrix.cpp
)

# Create executable
add_executable(get_migration_matrix ${SOURCES})

# Create test executable with the same source files
add_executable(test_migration 
    test/Test_migration.cpp
    ${SOURCES}  # Include all source files for the test
)

# Set output directory
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/build)