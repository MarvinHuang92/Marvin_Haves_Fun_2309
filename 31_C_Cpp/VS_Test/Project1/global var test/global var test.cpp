#include <iostream>
using namespace std;

// ȫ�ֱ�������
int g = 20;

int func()
{
	g = 5;
	return 0;
}

int main()
{
	// �ֲ���������
	int g; //= 10;

	cout << g;

	return 0;
}