# demos_v_matrix  

A matrix-based demographic simulation program. This project models population dynamics using fertility, mortality, and migration data.

## 📦 Features  
- Simulates population changes based on demographic factors  
- Processes data using a structured matrix approach  
- Outputs results to the `output/` folder  

## 🚀 Compilation  

Ensure you have `clang++` installed, then compile the program using:  

```sh
clang++ -std=c++11 \
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
    
## ▶️ Running the Program
After compilation, run:

./build/main_2023

The results will be saved in the `output/` folder.

## Project Structure

├── include/        # Header files  
├── src/            # Source code files  
├── build/          # Compiled binary output  
├── output/         # Generated results  
├── README.md       # Project documentation 
