cmake_minimum_required(VERSION 3.10)
project(migration_matrix)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add include directory
include_directories(${PROJECT_SOURCE_DIR}/include)

# Collect all source files
set(SOURCES
    src/deathages.cpp
    src/DataLoader.cpp
    src/fertility.cpp
    src/migration.cpp
    src/utils.cpp
    src/validate.cpp
)

# Create main executable
add_executable(get_migration_matrix 
    src/Get_migration_matrix.cpp
    ${SOURCES}
)

# Create test executable
add_executable(test_migration 
    test/Test_migration.cpp
    ${SOURCES}
)

# Set output directory for both executables
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/build)

# Set default target to test_migration
set_target_properties(test_migration PROPERTIES
    EXCLUDE_FROM_ALL FALSE
)
set_target_properties(get_migration_matrix PROPERTIES
    EXCLUDE_FROM_ALL TRUE
) 