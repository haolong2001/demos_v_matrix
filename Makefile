# Compiler and flags
CXX = clang++
CXXFLAGS = -Wall -std=c++17

# Source files
BIRTH_SRC = birth.cpp
MAIN_SRC = main.cpp
TEST_SRC = test.cpp

# Output files
MAIN_BIN = main
TEST_BIN = test

# Default target: build the main program
all: $(MAIN_BIN)

# Rule to build the main program
$(MAIN_BIN): $(MAIN_SRC) $(BIRTH_SRC)
	$(CXX) $(CXXFLAGS) $(MAIN_SRC) $(BIRTH_SRC) -o $(MAIN_BIN)

# Rule to build the test program
$(TEST_BIN): $(TEST_SRC) $(BIRTH_SRC)
	$(CXX) $(CXXFLAGS) $(TEST_SRC) $(BIRTH_SRC) -o $(TEST_BIN)

# Target to run the test
run_test: $(TEST_BIN)
	@echo "Running test with 100 people..."
	./$(TEST_BIN)

# Target to run the main program
run_main: $(MAIN_BIN)
	@echo "Running main with 10000 people..."
	./$(MAIN_BIN)

# Clean up
clean:
	rm -f $(MAIN_BIN) $(TEST_BIN)
