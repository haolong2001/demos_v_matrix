# demos_v_matrix
demos matrix version 



# complie the program

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

# run the program 

./build/main_2023



the results will be wrote to output folder 

### logging file 10.23 

read the binary file to c++ 
binary file is a series file 

1. if we know the size already, we can pass the 1-d array (from binary file) to 3 d matrix 
(see tutorial for matrix types in c++ )
