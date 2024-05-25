#include <iostream>
using namespace std;

/* 快速计算倒数平方根 */
float Q_rsqrt(float number)
{
    long i;
    float x2, y;
    const float threehalfs = 1.5F;

    x2 = number * 0.5F;
    y = number;
    i = * (long *) &y;                      // evil floating point bit level hacking
    i = 0x5f3759df - (i >> 1);              // wtf?
    y = y * (threehalfs - (x2 * y * y));    // first iteration
    // y = y * (threehalfs - (x2 * y * y));    // second iteration, can be removed

    return y;
}


int main()
{
    float num = 4;
    float q_rsqrt = Q_rsqrt(num);

    cout << q_rsqrt << endl;
	getchar();
    return 0;
}
