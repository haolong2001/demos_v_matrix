
#include <Eigen/Dense>
#include <vector>
#include <map>
#include <set>
#include <iostream>
#include <fstream>

using namespace Eigen;
using namespace std;

// find first 0 and set the rest of the row 0 
int findFirstZero(const ArrayXi& arr) {
    if (arr.sum() == arr.size()) return -1; // Quick exit if no '0's are present

    Eigen::Index blockSize = 10;
    for (Eigen::Index i = 0; i < arr.size(); i += blockSize) {
        Eigen::Index blockEnd = std::min(i + blockSize, arr.size());
        int blockSum = arr.segment(i, blockEnd - i).sum();
        if (blockSum != blockEnd) {
            for (Eigen::Index j = i; j < blockEnd; ++j) {
                if (arr[j] == 0) return static_cast<int>(j);
            }
        }
    }
    return -1;
}

void ZeroRest(ArrayXXi& largeArray) {
    int numRows = largeArray.rows();
    int numCols = largeArray.cols();

    // Vectors for storing first '1' indices and mapping of columns to rows
    vector<int> firstOneIndices(numRows, -1); // Initialize with -1 to signify "no '1' found"
    map<int, set<int>> columnToRowMap;

    // Populate firstOneIndices and columnToRowMap
    int idx0; 

    for (int i = 0; i < numRows; ++i) {
        idx0 = findFirstZero(largeArray.row(i));
        if (idx0 != -1){
            //columnToRowMap[idx0].insert(i);
            largeArray.row(i).segment(idx0, numCols - idx0).setZero();
        }
        
        }
    // Apply zeroing logic for columns where multiple rows share the first '1'
    // for (auto& entry : columnToRowMap) {
    //     // in c++, entry.second is the value
    //     if (entry.second.size() > 1) { // Handle only if more than one row has the first '1' at the same column
    //         for (int row : entry.second) {
    //             largeArray.row(row).segment(entry.first + 1, numCols - entry.first - 1).setZero();
    //         }
    //     }
    // }


}

int main() {
    // Example usage
    ofstream logFile("timing_log.txt");
    ArrayXXi largeArray(5, 10);
    largeArray << 0, 0, 1, 1, 1, 1, 1, 0, 0, 0,
                  0, 1, 1, 1, 0, 1, 1, 0, 0, 0,
                  1, 0, 0, 1, 1, 1, 1, 0, 0, 0,
                  1, 0, 1, 1, 0, 1, 0, 0, 0, 1,
                  1, 1, 0, 0, 1, 1, 0, 0, 0, 0;

    ZeroRest(largeArray);

    // Output the modified matrix
    logFile << "Modified largeArray:\n" << largeArray << endl;
    logFile.close();
    return 0;
}


// int main() {
//     // Example matrix
//     Eigen::MatrixXi mat(3, 10);
//     mat << 1, 1, 1, 1, 1, 1, 0, 1, 1, 0,
//            0, 1, 1, 1, 1, 1, 1, 1, 1, 1,
//            1, 1, 1, 1, 0, 0, 1, 1, 1, 0;

//     // Vector to store the indices of the first zero in each row
//     Eigen::VectorXi firstZeroIndices(mat.rows());

//     int segmentSize = 5; // Define segment size; adjust based on matrix size

//     for (int i = 0; i < mat.rows(); ++i) {
//         firstZeroIndices(i) = -1; // Initialize with -1 indicating no zero found
//         for (int j = 0; j < mat.cols(); j += segmentSize) {
//             // Calculate the sum of the current segment
//             int sum = 0;
//             for (int k = j; k < j + segmentSize && k < mat.cols(); ++k) {
//                 sum += mat(i, k);
//             }

//             // If sum is less than segmentSize, there must be at least one zero in this segment
//             if (sum < segmentSize) {
//                 // Linear search in this segment to find the first zero
//                 for (int k = j; k < j + segmentSize && k < mat.cols(); ++k) {
//                     if (mat(i, k) == 0) {
//                         firstZeroIndices(i) = k;
//                         break;
//                     }
//                 }
//                 if (firstZeroIndices(i) != -1) break; // Stop if zero is found
//             }
//         }
//     }

//     std::cout << "Indices of the first zero in each row:\n" << firstZeroIndices << std::endl;

//     return 0;
// }
