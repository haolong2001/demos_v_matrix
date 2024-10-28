```cpp
#include <queue>
using namespace std;

int main() {
    queue<int> q; // No need for std:: prefix now
    q.push(10);
  	q.pop();
  	
  	// first/last element
    int frontElement = q.front(); // Gets the front element
		int backElement = q.back();   // Gets the back element
    return 0;
}


```

