#include <stdio.h>
/* ��ʮ������ת��Ϊ���Ӧ����������������ǰ׺0x��0X�� �������0-9��a-f��A-F */

#define MAX 100

int htoi(char s[])
{
	int i, n, a, c;

	if (s[1] == 'x' || s[1] == 'X')
		a = 2;							//�����ǰ׺������ǰ��λ��
	else a = 0;

	n = 0;
	for (i = a; s[i] >= '0' && s[i] <= '9' || s[i] >= 'A' && s[i] <= 'F' || s[i] >= 'a' && s[i] <= 'f'; ++i) {
		if (s[i] >= '0' && s[i] <= '9')
			c = s[i] - '0';				//c��ʾ��ǰλת��Ϊʮ���ƵĽ��
		else if (s[i] >= 'A' && s[i] <= 'F')
			c = s[i] - 'A' + 10;
		else
			c = s[i] - 'a' + 10;
		n = 16 * n + c;
	}
	return n;
}

int main()
{
	int i, c;
	char s[MAX];

	printf("������һ��ʮ������������С����(.)��β\n\n");

	while (true) {
		for (i = 0; (c = getchar()) != '.'; ++i)
			s[i] = c;
		s[i] = '\0';

		printf("%s��Ӧ��ʮ������Ϊ��%d\n\n",s, htoi(s));  //��ǰ�����⣺���С��������б��������һ�λ�����ӵڶ��ο�ʼ�������0
	}
}