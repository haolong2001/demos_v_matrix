cmake_minimum_required(VERSION 3.10)
project(demos_v_matrix)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add include directory
include_directories(${CMAKE_SOURCE_DIR}/../include)

# Set output directory
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/../build)

# Option to build specific components
option(BUILD_RECONSTRUCT "Build population reconstruction (1990-2023)" ON)
option(BUILD_FORECAST "Build population forecast (2024-2050)" ON)
option(BUILD_MIGRATION "Build migration matrix calculation" ON)

# Build population reconstruction (1990-2023)
if(BUILD_RECONSTRUCT)
    set(SOURCES_RECONSTRUCT
        ${CMAKE_SOURCE_DIR}/../src/deathages.cpp
        ${CMAKE_SOURCE_DIR}/../src/DataLoader.cpp
        ${CMAKE_SOURCE_DIR}/../src/fertility.cpp
        ${CMAKE_SOURCE_DIR}/../src/migration.cpp
        ${CMAKE_SOURCE_DIR}/../src/utils.cpp
        ${CMAKE_SOURCE_DIR}/../src/validate.cpp
        ${CMAKE_SOURCE_DIR}/../src/main.cpp
    )
    add_executable(reconstruct_1990_2023 ${SOURCES_RECONSTRUCT})
endif()

# Build population forecast (2024-2050)
if(BUILD_FORECAST)
    set(SOURCES_FORECAST
        ${CMAKE_SOURCE_DIR}/../src_2050/forecast_2050.cpp
        ${CMAKE_SOURCE_DIR}/../src_2050/forecast_fertility.cpp
        ${CMAKE_SOURCE_DIR}/../src_2050/forecast_death.cpp
        ${CMAKE_SOURCE_DIR}/../src_2050/forecast_immi.cpp
        ${CMAKE_SOURCE_DIR}/../src_2050/forecast_mortality_reader.cpp
        ${CMAKE_SOURCE_DIR}/../src_2050/matrix_reader.cpp
    )
    add_executable(forecast_2024_2050 ${SOURCES_FORECAST})
endif()

# Build migration matrix calculation
if(BUILD_MIGRATION)
    set(SOURCES_MIGRATION
        ${CMAKE_SOURCE_DIR}/../src/deathages.cpp
        ${CMAKE_SOURCE_DIR}/../src/DataLoader.cpp
        ${CMAKE_SOURCE_DIR}/../src/fertility.cpp
        ${CMAKE_SOURCE_DIR}/../src/migration.cpp
        ${CMAKE_SOURCE_DIR}/../src/utils.cpp
        ${CMAKE_SOURCE_DIR}/../src/validate.cpp
        ${CMAKE_SOURCE_DIR}/../src/Get_migration_matrix.cpp
    )
    add_executable(get_migration_matrix ${SOURCES_MIGRATION})
    
    # Migration test
    add_executable(test_migration 
        ${CMAKE_SOURCE_DIR}/../src/deathages.cpp
        ${CMAKE_SOURCE_DIR}/../src/DataLoader.cpp
        ${CMAKE_SOURCE_DIR}/../src/fertility.cpp
        ${CMAKE_SOURCE_DIR}/../src/migration.cpp
        ${CMAKE_SOURCE_DIR}/../src/utils.cpp
        ${CMAKE_SOURCE_DIR}/../src/validate.cpp
        ${CMAKE_SOURCE_DIR}/../test/Test_migration.cpp
    )
endif()

# Print build configuration
message(STATUS "Build Configuration:")
message(STATUS "  BUILD_RECONSTRUCT: ${BUILD_RECONSTRUCT}")
message(STATUS "  BUILD_FORECAST: ${BUILD_FORECAST}")
message(STATUS "  BUILD_MIGRATION: ${BUILD_MIGRATION}") 