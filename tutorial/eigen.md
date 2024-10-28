three mandatory template parameters of Matrix are:
```cpp
Matrix<typename Scalar, int RowsAtCompileTime, int ColsAtCompileTime>

// for convenience
typedef Matrix<float, 4, 4> Matrix4f;

// 


```

## cpp matrix file types 


```cpp
double arr[3][4]; // 
```

C-style arrays (stack-allocated); memory contiguously 

```cpp
std::array<std::array<double, 4>, 3> arr;

```
C-style array but comes with some additional features, such as bounds checking in debug mode and compatibility with STL algorithms.

a wrapper around a C-style array

```cpp
double* arr = new double[3 * 4];
#include <iostream>

int main() {
    int x = 3, y = 4, z = 5;

    // Dynamically allocate a 3D array using a single 1D array
    double* array = new double[x * y * z];

    // Accessing an element at position (i, j, k)
    int i = 1, j = 2, k = 3;
    array[i * (y * z) + j * z + k] = 1.0;

    // Print the value at (i, j, k)
    std::cout << "Value at (" << i << ", " << j << ", " << k << "): " << array[i * (y * z) + j * z + k] << std::endl;

    // Don't forget to free the allocated memory
    delete[] array;

    return 0;
}

```
dynamically allocate an array with 

non resizeable; no boundary checking


## c++ reference 
In C++, const string& is a reference to a std::string object that is constant, meaning the string it refers to cannot be modified through this reference. Here's a breakdown:

```cpp
void printString(const std::string& str) {
    std::cout << str << std::endl;
}

```

## cpp file read / write 



## print 

```cpp
nline 
```



## Eigen Matrix Slicing in C++

In Eigen, slicing or selecting parts of a matrix is not as straightforward as in some other libraries like NumPy. However, Eigen provides methods to extract columns, rows, or blocks of a matrix. You cannot directly use syntax like `mock_popu_mat[i].slice(0)` or `mock_popu_mat[i][:, 0]`, but you can achieve similar functionality using the provided Eigen methods.


### 1. Extracting a Specific Column:
If you want to extract the first column of `mock_popu_mat[i]` (i.e., the `0`-th column), you can use the `.col()` method:

```cpp
Eigen::VectorXd first_column = mock_popu_mat[i].col(0);
```

This will extract the first column of the matrix `mock_popu_mat[i]` into a vector.

### 2. Extracting a Specific Row:
Similarly, if you want to extract the first row, you can use the `.row()` method:

```cpp
Eigen::RowVectorXd first_row = mock_popu_mat[i].row(0);
```

This extracts the first row as a row vector.

### 3. Extracting a Block (Submatrix):
If you want to extract a block (submatrix), you can use the `.block()` method. For example, to extract a block that starts at row 0, column 0 and has a size of 10 rows and 5 columns:

```cpp
Eigen::MatrixXd submatrix = mock_popu_mat[i].block(0, 0, 10, 5);
```

### 4. Extracting Multiple Columns:
If you want to extract multiple columns (say columns 0 through 2), you can use the `.block()` method as well:

```cpp
Eigen::MatrixXd first_three_columns = mock_popu_mat[i].block(0, 0, mock_popu_mat[i].rows(), 3);
```

This extracts all rows and the first three columns.

### Conclusion:
To summarize, in Eigen, you can extract columns, rows, or blocks using methods like `.col()`, `.row()`, and `.block()`, Eigen's functionality allows for flexible matrix manipulation.


```cpp
#include <Eigen/Dense>
#include <iostream>

double mock_popu_mat[8][86][35];  // Your 3D array

int i = 0;  // Index for the first dimension
// Map the 2D slice of the 3D array as an Eigen Matrix
Eigen::Map<Eigen::Matrix<double, 86, 35>> slice(mock_popu_mat[i]);

// Now you can work with 'slice' as a standard Eigen matrix
std::cout << slice.col(0);  // Example: accessing the first column (age group)
```

above code serves as an example for mock_popu_mat

## float vs double 

float 32 digits; double 64 digits 



When you multiply an integer array by a floating-point value, the result will conceptually be **floating-point**, but `Eigen` cannot automatically determine that conversion from `int` to `float` during the element-wise multiplication operation.

In C++, there is no implicit type promotion in this case, and attempting to multiply an integer matrix (`immi_mat`) with a float (`mock_scale`) without explicit casting **will lead to a compilation error**.



##  size / sizeof

size gives the vector size, while sizeof returns the bites



## const / static



```cpp
const int x = 10;  // x cannot be modified after this point
x = 20;            // Error: cannot modify a constant variable

```



### static 

The `static` keyword is used to indicate that **memory is allocated once** and **persists** across the lifetime of the program (or the containing function). The behavior of `static` depends on the context in which it is used.

#### Static Variables

- **Static Local Variable**:
  - A `static` local variable inside a function **retains its value** between function calls. It has **function scope** but **static storage duration**.

```cpp
void increment() {
    static int count = 0;  // Initialized only once, retains value between calls
    count++;
    std::cout << count << std::endl;
}

int main() {
    increment();  // Output: 1
    increment();  // Output: 2
    increment();  // Output: 3
    return 0;
}

```

**Static Global Variable**:

- If a global variable is declared as `static`, its visibility is **limited to the file** it is declared in. This is used to restrict access to variables to a single translation unit.

  ```cpp
  static int globalVar = 10;  // This variable is only accessible within this file.
  
  ```

  ```cpp
  In summary, const is used to define immutability, while static is used to control the storage duration or visibility of a variable or function.
  ```

  
