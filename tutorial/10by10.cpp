#include <iostream>
#include <Eigen/Dense>
#include <chrono>
#include <fstream>
#include <algorithm>  // Ensure this is included for std::min


using namespace std;

// Function to find the first '1' in an Eigen ArrayXi using a sum check followed by segmented detailed checks
int findFirstOne(const Eigen::ArrayXi& arr) {
    if (arr.sum() == 0) return -1;  // Quick exit if no '1's are present
    int k = min(3,4);
    int blockSize = 10;
    for (int i = 0; i < arr.size(); i += blockSize) {
        // Calculate sum for the current block to check for any '1's
        // static_cast<int>(arr.size())
        int blockEnd = min(i + blockSize, static_cast<int>(arr.size()));
        int blockSum = arr.segment(i, blockEnd - i).sum();
        if (blockSum > 0) {
            // If sum is not zero, iterate through this block to find the first '1'
            for (int j = i; j < i + blockSize && j < arr.size(); ++j) {
                if (arr[j] == 1) return j;
            }
        }
    }
    return -1;  // Should not reach here if sum check is correct, but added for safety
}



int main() {
    // 0.356542 ms
    // Generate a large array of size 100x60 filled randomly with 0s and 1s
    Eigen::ArrayXXi largeArray = Eigen::ArrayXXi::Random(100, 60).unaryExpr([](int x) { return (x < 0) ? 0 : 1; });

    // Open a log file to record the timing data
    // this will generate below current folder 
    ofstream logFile("timing_log.txt");

    // Measure the total processing time
    auto totalStart = chrono::high_resolution_clock::now();

    // Process each row of the array, logging the time taken for the bit comparison
    for (int i = 0; i < largeArray.rows(); ++i) {
        //auto start = chrono::high_resolution_clock::now();
        int index = findFirstOne(largeArray.row(i));
        //auto end = chrono::high_resolution_clock::now();

        //chrono::duration<double, milli> elapsed = end - start;
        //logFile << "Row " << i << ": Index of first '1' is " << index << ", Time taken: " << elapsed.count() << " ms\n";
    }

    auto totalEnd = chrono::high_resolution_clock::now();
    chrono::duration<double, milli> totalElapsed = totalEnd - totalStart;

    logFile << "Total time taken to process the entire array: " << totalElapsed.count() << " ms" << endl;

    logFile.close();
    cout << "Total time taken to process the entire array: " << totalElapsed.count() << " ms" << endl;

    return 0;
}

// int main() {
//     // Test the function with a sample array
//     Eigen::ArrayXi arr(60);
//     arr << Eigen::ArrayXi::Zero(59), 1;  // Mostly zeros, one '1' at the end

//     int index = findFirstOne(arr);
//     cout << "Index of the first '1': " << index << endl;

//     return 0;
// }
