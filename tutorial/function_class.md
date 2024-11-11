 ```cpp
 // Calculator.h
 #ifndef CALCULATOR_H
 #define CALCULATOR_H
 
 class Calculator {
 private:
     double lastResult;
 
 public:
     Calculator(double initialValue = 0.0);
     double add(double x, double y);
     double subtract(double x, double y);
     double getLastResult() const;
 };
 
 #endif
 
 // Calculator.cpp
 #include "Calculator.h"
 
 Calculator::Calculator(double initialValue) : lastResult(initialValue) {}
 
 double Calculator::add(double x, double y) {
     lastResult = x + y;
     return lastResult;
 }
 
 double Calculator::subtract(double x, double y) {
     lastResult = x - y;
     return lastResult;
 }
 
 double Calculator::getLastResult() const {
     return lastResult;
 }
 
 // main.cpp (with tests)
 #include <iostream>
 #include <cassert>
 #include "Calculator.h"
 
 void runTests() {
     // Test 1: Basic addition
     Calculator calc1;
     double result1 = calc1.add(5.0, 3.0);
     assert(result1 == 8.0);
     assert(calc1.getLastResult() == 8.0);
     std::cout << "Addition test passed\n";
 
     // Test 2: Basic subtraction
     double result2 = calc1.subtract(10.0, 4.0);
     assert(result2 == 6.0);
     assert(calc1.getLastResult() == 6.0);
     std::cout << "Subtraction test passed\n";
 
     // Test 3: Custom initial value
     Calculator calc2(10.0);
     assert(calc2.getLastResult() == 10.0);
     std::cout << "Initial value test passed\n";
 }
 
 int main() {
     try {
         runTests();
         std::cout << "All tests passed successfully!\n";
     } catch (const std::exception& e) {
         std::cerr << "Test failed: " << e.what() << std::endl;
         return 1;
     }
     return 0;
 }
 ```



clang++ -std=c++11 -Iinclude src/deathages.cpp Src/DataLoader.cpp test/test_initial_popu.cpp -o build/test_initial_popu



clang++ test_initial_popu.cpp DataLoader.cpp deathages.cpp -o test_program -I/path/to/eigen