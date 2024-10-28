#include <iostream>
#include <fstream>
#include <string>

using namespace std;

int main() {
    // Create and open a logging file
    ofstream logFile("logfile.txt");

    // Check if the file is open successfully
    if (!logFile.is_open()) {
        cerr << "Error: Could not open the log file!" << endl;
        return 1;
    }

    // Log some information
    logFile << "Logging started." << endl;
    logFile << "This is a log message." << endl;
    logFile << "Another log message." << endl;

    // You can log variables as well
    int someVariable = 42;
    logFile << "Value of someVariable: " << someVariable << endl;

    // Log an error message
    logFile << "An error occurred: Invalid input." << endl;

    // Close the log file
    logFile.close();

    cout << "Logging complete. Check logfile.txt for the output." << endl;

    return 0;
}
