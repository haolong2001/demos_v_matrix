# demos_v_matrix  

An age, gender, ethnicity-specific high dimensional stochastic probability matrix-based demographic simulation program. 
This program models population transitions from 1990 to 2023 using fertility, mortality, and migration data.

## 📦 Features  
- Simulates population changes based on demographic factors  
- Processes data using a structured matrix approach  
- Outputs results to the `output/` folder  
- Parallel processing of forecast data for disease analysis

## 🚀 Compilation  

Ensure you have c++, `clang++`,  Eigen, and the EigenRand library installed, then compile the program using: 


install page for Eigen https://eigen.tuxfamily.org/index.php?title=Main_Page

EigenRand: https://github.com/bab2min/EigenRand/releases

check the path you need to install to : clang++ -E -x c++ - -v < /dev/null

the path on mac:
/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/include


## ▶️ Complie the Program

To run the population construction code 
```sh
clang++ -std=c++17 \
    -Iinclude \
    src/deathages.cpp \
    src/DataLoader.cpp \
    src/fertility.cpp \
    src/migration.cpp \
    src/utils.cpp \
    src/validate.cpp \
    src/main.cpp \
    -o build/main_2023
```    

To run the population forecast code 

```
clang++ -std=c++17 -Iinclude \
src_2050/forecast_2050.cpp \
src_2050/forecast_fertility.cpp \
src_2050/forecast_death.cpp \
src_2050/forecast_immi.cpp \
src_2050/forecast_mortality_reader.cpp \
src_2050/matrix_reader.cpp \
-o build/forecast_2050
```

To compile the disease processing module
```bash
cd src_disease
make -f Makefile.disease
```
    
## ▶️ Run the Program
After compilation, run:

./build/main_2023

The results will be saved in the `output/` folder.

./build/forecast_2050

Results are saved in timestamped folders with random numbers: `output/YYYYMMDD_HHMMSS_RRRR/`

**Disease Processing:**
```bash
./src_disease/disease_processor
```

0 - 7 means (chn, mal, ind and others) * (male female)

chn mal 0 chn fem 1;
mal mal 2,mal, fem 3...

## 🔄 Running Multiple Iterations

### Option 1: Simple Sequential Loop
```bash
for i in {1..10}; do echo "Running iteration $i/10..."; ./forecast_2050; done
```

### Option 2: Using the Provided Script
```bash
# Make the script executable
chmod +x run_multiple_times.sh

# Run 10 times (default)
./run_multiple_times.sh

# Run a specific number of times
./run_multiple_times.sh 20
```

### Option 3: Parallel Execution (if you want faster runs)
If you want to run multiple instances in parallel (assuming your system can handle it):

```bash
# Run 5 instances in parallel
for i in {1..5}; do ./forecast_2050 & done; wait

# Run 10 instances in parallel
for i in {1..10}; do ./forecast_2050 & done; wait
```

**Note**: Each run creates unique timestamped output directories, so parallel execution won't cause conflicts.

## 📋 Usage Workflow

### Complete Analysis Pipeline

1. **Run multiple forecast simulations:**
```bash
# Run 10 forecast simulations
./run_multiple_times.sh 10

# Or run manually
for i in {1..10}; do echo "Running iteration $i/10..."; ./forecast_2050; done
```

2. **Process all results in parallel:**
```bash
# Process all forecast folders for disease analysis
./src_disease/disease_processor
```

### Typical Workflow Example

```bash
# Step 1: Generate multiple forecast scenarios
./run_multiple_times.sh 5

# Step 2: Process all results for analysis
./src_disease/disease_processor

# Step 3: Check results
ls output/ | grep -E "^[0-9]{8}_[0-9]{6}_[0-9]{4}$"
```

This workflow creates multiple forecast scenarios and then processes them all in parallel for disease analysis.

## Project Structure

├── include/        # Header files  
├── src/            # Source code files for population construction between 1990 and 2023
├── build/          # Compiled binary output
├── src_2050/       # Source code files for population forecast between 2024 and 2050
├── src_disease/    # Disease processing module for parallel analysis (BMI included)
├── output/         # Generated results  
├── README.md       # Project documentation 


## forecast part 

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
* Immigration calculations are performed in `preprocess_py/cal_immi.ipynb`
* Final immigration projections are saved to `data/migration/future_immigration.bin`

### Methodology
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




