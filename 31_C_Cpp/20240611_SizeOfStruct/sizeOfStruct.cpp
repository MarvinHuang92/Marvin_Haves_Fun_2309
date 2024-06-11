#include <iostream>
using namespace std;

#include "dataType.hpp"

// #pragma pack(4)

// 默认按结构体中最长的成员对齐
// 最长是float64，则对齐长度为8

typedef struct
{
   uint16   foo_1;
   uint32   foo_2;
   uint8    foo_3;
   float32  foo_4;
   sint16   foo_5;
   boolean  foo_6;
   float64  foo_7;
}STRUCT_1;

typedef struct
{
   boolean  foo_1;
   uint8    foo_2;
   uint16   foo_3;
   sint16   foo_4;
   uint32   foo_5;
   float32  foo_6;
   float64  foo_7;
}STRUCT_2;

// 全是bool值，对齐长度为1
typedef struct
{
   uint8    foo_1;
   uint8    foo_2;
   uint8    foo_3;
   boolean  foo_4;
   boolean  foo_5;
   boolean  foo_6;
   boolean  foo_7;
}STRUCT_3;

int main()
{
    int size_1 = sizeof(STRUCT_1);
    int size_2 = sizeof(STRUCT_2);
    int size_3 = sizeof(STRUCT_3);

    cout << "Size_1 = " << size_1 << endl;
    cout << "Size_2 = " << size_2 << endl;
    cout << "Size_3 = " << size_3 << endl;

    return 0;
}
