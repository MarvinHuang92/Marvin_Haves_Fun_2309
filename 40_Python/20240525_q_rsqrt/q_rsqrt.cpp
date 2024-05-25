#include <iostream>
#include <cmath>
using namespace std;

/* 快速计算平方根的倒数 y = 1/sqrt(x) */
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

/* 普通算法 */
float Normal_rsqrt(float number)
{
    float x2, y;

    x2 = sqrtf(number);
    y = 1 / x2;

    return y;
}

int main()
{
    float num = 4.0;
    float q_rsqrt = Q_rsqrt(num);
    float n_rsqrt = Normal_rsqrt(num);

    cout << q_rsqrt << endl;
    cout << n_rsqrt << endl;
	// getchar();  // 等待用户输入
    return 0;
}
