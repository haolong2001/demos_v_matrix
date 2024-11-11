```cpp
#include <iostream>





```









```cpp
int add(int x, int y)
{
    return x + y;
}

```



```cpp
#include <iostream>

int add(int x, int y); // forward declaration using function prototype

int main()
{
    std::cout << "The sum of 3 and 4 is " << add(3, 4) << '\n';
    return 0;
}
```



 a forward declaration so that the compiler will know what identifier *add* is when compiling *main.cpp*



```cpp
// 1) We really should have a header guard here, but will omit it for simplicity (we'll cover header guards in the next lesson)

// 2) This is the content of the .h file, which is where the declarations go
int add(int x, int y); // function prototype for add.h -- don't forget the semicolon!

```



```cpp
#include "add.h" // Insert contents of add.h at this point.  Note use of double quotes here.
#include <iostream>

int main()
{
    std::cout << "The sum of 3 and 4 is " << add(3, 4) << '\n';
    return 0;
}
```







## rules 

avoid putting function or variable definitions in header files

Doing so will generally result in a violation of the one-definition rule (ODR) in cases where the header file is included into more than one source file.





## some notes

you need to make sure the class method is defined in the .h file, 
otherwise, you cannot use the variable defined in the original function.



这个事情很头疼

比如我要写整个流程，但是我不会输出logging file，那我就要把我整个思路打断掉





clang++ -std=c++11 -Iinclude src/deathages.cpp test/test_initial_popu.cpp -o build/test_initial_popu

