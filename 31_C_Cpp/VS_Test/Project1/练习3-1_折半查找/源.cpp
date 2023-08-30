#include <stdio.h>
/* binsearch: find x in v[0] <= v[1] <= ... <= v[n-1] */
// ����������v[]�в����ض�����ֵx���������������±�


int elow, ehigh; //�����ⲿ���������ڴ洢low��high�Ľ��


int binsearch(int x, int v[], int n) //ԭʼ����
{
	int low, high, mid;

	low = 0;
	high = n - 1;

	while (low <= high) {
		mid = (low + high) / 2;  //�Զ�����ȡ��
		if (x < v[mid])
			high = mid - 1;
		else if (x > v[mid])
			low = mid + 1;
		else {/* �ҵ���ƥ��ֵ������v[mid] */
			elow = low;
			ehigh = high;
			return mid;
		}
	}
	// ���������whileѭ����һ����low = high + 1�����ߴ�С�������ˣ�
	elow = low;
	ehigh = high;
	return -1;
	/* û��ƥ��ֵ */
}

int binsearch2(int x, int v[], int n) //�Լ�д���º�������while��ֻ����һ��if�ж�
{
	int low, high, mid;

	low = 0;
	high = n - 1;

	while (low < high) {  //����ȥ�����ڵ����������������ѭ��
		mid = (low + high) / 2;  //�Զ�����ȡ��
		if (x > v[mid])  //����ʹ�ô�����������������С����������Ϊmid��������ȡ���ģ����������ܵ�������ѭ��
			low = mid + 1;
		else
			high = mid;
	}
	// ���������whileѭ����һ����low = high������������low = high + 1
	elow = low;
	ehigh = high;
	if (x == v[low])
		return low;  //�����low����high�����ԣ�����������ȵ�
	else
		return -1;
	/* û��ƥ��ֵ */
}

int binsearch3(int x, int v[], int n) //��2�е��ж������ߵ������Կ��ܵ���ѭ��
{
	int low, high, mid;

	low = 0;
	high = n - 1;

	while (low < high) {
		mid = (low + high) / 2;
		if (x < v[mid])  //�����������2�෴
			high = mid - 1;
		else             //���������һ�������������ѭ��
			low = mid;
	}

	elow = low;
	ehigh = high;
	if (x == v[low])
		return low;
	else
		return -1;
	/* û��ƥ��ֵ */
}

int main()
{
	int x = 8;
	int v[12];
	int i;

	for (i = 0; i < 12; ++i)
		v[i] = i * 2;  //��ʼ������Ϊ0,2,4...22

	int pos = binsearch2(x, v, 12);

	printf("position = %d\nlow = %d\nhigh = %d\n", pos, elow, ehigh);

}