#include <iostream>
using namespace std;

int main()
{
    float a;
    float b;
    float c;

    // 分别独立赋值
    a = 1.0f;
    b = 1.0f;
    
    cout << "a = " << a << endl;
    cout << "b = " << b << endl;

    if (a == b) {
        cout << "Equal." << endl;
    } else {
        cout << "Not Equal." << endl;
    }


    // 令二者相等赋值
    a = b;

    cout << "a = " << a << endl;
    cout << "b = " << b << endl;

    if (a == b) {
        cout << "Equal." << endl;
    } else {
        cout << "Not Equal." << endl;
    }


    // 借助参数赋值
    c = 1.0f;
    a = c;
    b = c;

    cout << "a = " << a << endl;
    cout << "b = " << b << endl;

    if (a == b) {
        cout << "Equal." << endl;
    } else {
        cout << "Not Equal." << endl;
    }


    return 0;
}
