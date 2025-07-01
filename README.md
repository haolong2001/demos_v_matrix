# demos_v_matrix  

An age, gender, ethnicity-specific high dimensional stochastic probability matrix-based demographic simulation program. The program can also incorporate disease progression analysis into the demographic simulations.


## 📦 Features  
- Simulates population changes based on demographic factors  
- Processes data using a structured matrix approach  
- Outputs results to the `output/` folder  
- Parallel processing of forecast data for disease analysis

## Project Structure

├── include/        # Header files  
├── src/            # Source code files for population construction between 1990 and 2023
├── src_2050/       # Source code files for population forecast between 2024 and 2050
├── src_disease/    # Disease processing module for parallel analysis
├── cmake/          # CMake build configuration files
├── build/          # Compiled binary output
├── output/         # Generated results  
├── README.md       # Project documentation

## 🚀 Compilation  

Ensure you have c++, `clang++`,  Eigen, and the EigenRand library installed, then compile the program using: 


install page for Eigen https://eigen.tuxfamily.org/index.php?title=Main_Page

EigenRand: https://github.com/bab2min/EigenRand/releases

check the path you need to install to : clang++ -E -x c++ - -v < /dev/null

the path on mac:
/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/include

## ▶️ Build Options

### Option 1: CMake Build System (Recommended)
The project now uses a CMake build system organized in the `cmake/` directory:

```bash
# Build all components
mkdir build_cmake
cd build_cmake
cmake ../cmake
make -j4

# Build specific components only

# Build reconstruction only
cmake ../cmake -DBUILD_RECONSTRUCT=ON -DBUILD_FORECAST=OFF -DBUILD_MIGRATION=OFF
make

# Build forecast only  
cmake ../cmake -DBUILD_RECONSTRUCT=OFF -DBUILD_FORECAST=ON -DBUILD_MIGRATION=OFF
make
```

**Available executables:**
- `reconstruct_1990_2023` - Population reconstruction (1990-2023)
- `forecast_2024_2050` - Population forecast (2024-2050)
- `get_migration_matrix` - Migration matrix calculation


See `cmake/README.md` for detailed build instructions.


To compile the BMI calculation module
```bash
cd src_disease
make -f Makefile.bmi
```
    
## ▶️ Run the Program
After compilation, run:

**Using CMake build:**
```bash
./build/reconstruct_1990_2023  # Population reconstruction
./build/forecast_2024_2050     # Population forecast
./build/get_migration_matrix   # Migration calculation
```
Results are saved in timestamped folders with random numbers: `output/YYYYMMDD_HHMMSS_RRRR/`


Parallel Execution (Recommended)
For faster processing, run multiple instances in parallel:

```bash
# Run 5 instances in parallel
for i in {1..5}; do ./build/forecast_2024_2050 & done; wait

# Run 10 instances in parallel
for i in {1..10}; do ./build/forecast_2024_2050 & done; wait
```
**Note**: Each run creates unique timestamped output directories, so parallel execution won't cause conflicts.



**BMI Processing:**
```bash
./build/BMI/bmi_process_parallel
```

**To View Result in csv format**
```bash
./COPD/read_bin_bmi
```


**Height Processing:**
```bash
./build/Height/height_process_parallel
```

**To View Result in csv format**
```bash
./COPD/read_bin_height
```

**Migration Matrix Calculation:(optional)**
```bash
./build/get_migration_matrix
```


## 📋 Usage Workflow

### Complete Analysis Pipeline

1. **Run multiple forecast simulations in parallel:**
```bash
# Run 10 forecast simulations in parallel
for i in {1..10}; do ./build/forecast_2024_2050 & done; wait
```

2. **Process all results in parallel:**
```bash
# Process all forecast folders for disease analysis
./build/BMI/bmi_process_parallel
```

Here we can add more diseaeses.


3. **Check results**
```
ls output/ | grep -E "^[0-9]{8}_[0-9]{6}_[0-9]{4}$"
```

This workflow creates multiple forecast scenarios in parallel and then processes them all for disease analysis.






## forecast part Methodology

basically, we wish to have the population matrix 
where the peopele influx comes from:
population_2023, immigration, births 
the order of adding to the population follows the same as above 

## add popu 2023 

initlize a matrix with base population as popu 2023


## forecast immigration
## Immigration Forecasting

### Input Data
* Historical migration data from 1990-2023 is stored in `data/migration/migration_0.csv`
* Immigration rate calculations are performed in `preprocess_py/cal_immi.ipynb`
* Final immigration projections are saved to `data/migration/future_immigration.bin`

1. Calculate age, gender and ethnicity-specific immigration rates using 10 years of pre-COVID data
2. Apply these rates to future population projections to estimate immigration numbers
3. Scale immigration numbers by a factor of 1/20 in the baseline scenario

### forecast fertility 

Fertility Forecasting Algorithm:

1. Calculate initial births from current population:
   - For each female aged 15-49:
     - Get fertility rate based on age, year and ethnicity
     - Generate random number to determine if birth occurs
   - Split total births into male/female using sex ratio

2. While female births exist:
   a. Generate population matrices from births:
      - Create male population matrix from male births
      - Create female population matrix from female births
      - Apply mortality rates to both matrices
   
   b. Add new population matrices to tracking:
      - Add male matrix to male population list
      - Add female matrix to female population list
   
   c. Calculate next generation births:
      - Check if any births occurred in first 12 years (2024-2035)
      - If no early births, end loop (won't reach fertility age by 2050)
      - Otherwise calculate births from new female population
      - Split into male/female births
      - Continue loop

### forecast mortality 

Lee Carter

## Migration Matrix Calculation

The migration matrix calculation uses a CMake-based build system to process historical migration data and generate ethnicity-specific migration matrices.

### Build and Run
```bash
# Build migration calculation
mkdir build_cmake
cd build_cmake
cmake ..
make

# Run migration calculation
./build_cmake/get_migration_matrix
```

### Output
- Generates 8 migration CSV files: `data/migration/migration_0.csv` through `data/migration/migration_7.csv`
- Each file contains ethnicity-specific migration data for demographic modeling


0 - 7 means (chn, mal, ind and others) * (male female)

chn mal 0 chn fem 1;
mal mal 2,mal, fem 3...




