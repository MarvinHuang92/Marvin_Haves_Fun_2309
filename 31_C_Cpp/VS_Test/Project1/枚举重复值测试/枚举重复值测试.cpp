#include <stdio.h>

int main()
{
	enum MONTH {Jan = 1, Feb, Mar, Apr, May = 1} month;  //��һ��MONTH�ǡ�����ġ��������֣������month���Ǳ�������

	month = Jan;
	printf("%d\n", month);

	month = May;
	printf("%d\n", month);
	
	getchar();
	return 0;
}