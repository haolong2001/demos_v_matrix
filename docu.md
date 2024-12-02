result_matrix

1,1,1,1,,,1
1,1,1,1...1
;
;
1,1,1,1,..1

86 * 35 population matrix  

## disappear matrix 

0 - 84, 85& 85+
1990 - 2023
86 * 34 


disappear_data and mig_disappear are death rates for cohorts. 

disappear_data is all death  
of shape 8 * 119 * 34


fertility matrix 

# module initial popu
clang++ -std=c++11 -Iinclude src/deathages.cpp Src/DataLoader.cpp test/test_initial_popu.cpp -o build/test_initial_popu

clang++ -std=c++11 -Iinclude src/DataLoader.cpp test/test_read_file.cpp -o build/test_read_file


clang++ -std=c++11 -Iinclude src/deathages.cpp Src/DataLoader.cpp src/main.cpp -o build/main

clang++ -std=c++11 -Iinclude src/migration.cpp src/DataLoader.cpp  -o build/migration






1. 处理immigration，不太对劲; done!
2. death should be -1 / 

we dealt with death as 0, it mismatch with birth. 

3. validation 正确与否...?? 问问
3. death ages line 101; too complex




clang++ -std=c++11 \
    -Iinclude \
    src/deathages.cpp \
    src/DataLoader.cpp \
    src/fertility.cpp \
    test/test_initial_popu.cpp \
    -o build/test_initial_popu



fertility is twice


clang++ -std=c++11 \
    -Iinclude \
    src/deathages.cpp \
    src/DataLoader.cpp \
    src/fertility.cpp \
    src/migration.cpp\
    test/test_initial_popu.cpp \
    -o build/test_initial_popu




clang++ -std=c++11 \    
-Iinclude \
src/deathages.cpp \
src/DataLoader.cpp \
src/fertility.cpp \
src/migration.cpp \
src/utils.cpp \
src/validate.cpp \
src/main_test.cpp \
-o build/main_test2023
