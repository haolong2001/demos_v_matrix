
#include <fstream>
#include <iostream>
#include <Eigen/Dense>
#include <Eigen/LU>

// #include "stdafx.h"  standard 

using Eigen::MatrixXd;
using namespace std;

int binRW(MatrixXd& matrixIO, const string& fileName, const bool isWrite) {
	if (isWrite) {
		ofstream outputData;
		outputData.open(fileName);
		if (outputData) {
			int i, r = matrixIO.rows(), c = matrixIO.cols();
			outputData.write(reinterpret_cast<const char *>(&r), sizeof(int));
			outputData.write(reinterpret_cast<const char *>(&c), sizeof(int));
			double *array = new double[r * c];
			for (i = 0; i < (r * c); i++)
				array[i] = matrixIO(i / c, i % c);
			outputData.write(reinterpret_cast<const char *>(array), sizeof(double) * r * c);
			outputData.close();
			return 0;
		}
	}
	else {
		ifstream inputData;
		inputData.open(fileName);
		if (inputData) {
			int i, r, c;
			inputData.read(reinterpret_cast<char *>(&r), sizeof(int));
			inputData.read(reinterpret_cast<char *>(&c), sizeof(int));
			matrixIO.resize(r, c);
			for (i = 0; i < (r * c); i++)
				inputData.read(reinterpret_cast<char *>(&matrixIO(i / c, i % c)), sizeof(double));
			inputData.close();
			return 0;
		}
	}
	return -1;
}

int main()
{
	MatrixXd m1 = MatrixXd::Random(2, 3), m2 = MatrixXd::Random(1, 2);
	binRW(m1, "myFile.bin", 1);
	cout << "m1 = " << endl << m1 << endl;
	cout << "m2 = " << endl << m2 << endl;
	binRW(m2, "myFile.bin", 0);
	cout << "m1 = " << endl << m1 << endl;
	cout << "m2 = " << endl << m2 << endl;
	getchar();
	MatrixXd lm = MatrixXd::Random(10000, 10000);
	binRW(lm, "largeFile.bin", 1);
    return 0;
}

