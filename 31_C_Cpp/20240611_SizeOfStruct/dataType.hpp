#include <iostream>
using namespace std;

/*-------Standard Integer Data Types--------*/
/*TRACE[SWS_Platform_00016]:This standard AUTOSAR type shall be of 8 bit signed. */
 /* Range : -128 .. +127 */
/*           0x80..0x7F */
typedef signed char     sint8;

/* TRACE[SWS_Platform_00013]: This standard AUTOSAR type shall be of 8 bit unsigned.*/
 /* Range : 0 .. 255     */
 /*         0x00 .. 0xFF */
typedef unsigned char   uint8;

/* TRACE[SWS_Platform_00017]: This standard AUTOSAR type shall be of 16 bit signed. */
/* Range : -32768 .. +32767 */
/*          0x8000..0x7FFF  */
typedef signed short    sint16;

/*TRACE[SWS_Platform_00014]: This standard AUTOSAR type shall be of 16 bit unsigned. */
/* Range : 0 .. 65535      */
/*         0x0000..0xFFFF  */
typedef unsigned short  uint16;

/*TRACE[SWS_Platform_00018]:This standard AUTOSAR type shall be 32 bit signed. */
/*Range : -2147483648 .. +2147483647   */
/*         0x80000000..0x7FFFFFFF      */
typedef signed long     sint32;

/*TRACE[SWS_Platform_00067]: This standard AUTOSAR type shall be 64 bit signed. */
/*Range: -9223372036854775808..+9223372036854775807*/
/*        0x8000000000000000..0x7FFFFFFFFFFFFFFF   */
typedef signed long long sint64;

/*TRACE[SWS_Platform_00015]:This standard AUTOSAR type shall be 32 bit unsigned. */
/* Range:  0 .. 4294967295           */
/*         0x00000000..0xFFFFFFFF    */
typedef unsigned long   uint32;

/*TRACE[SWS_Platform_00066]: This standard AUTOSAR type shall be 64 bit unsigned.*/
/* Range :   0 ..18446744073709551615              */
/*           0x0000000000000000..0xFFFFFFFFFFFFFFFF*/
typedef unsigned long long   uint64;

/* Standard Float Data Types */
/* ------------------------- */
/* TRACE[SWS_Platform_00041]: This standard AUTOSAR type shall follow the 32-bit binary interchange format
  according to IEEE 754-2008 with encoding parameters specified in chapter 3.6, table 3.5, column "binary32".*/
typedef float   float32;
/*TRACE[SWS_Platform_00042]:This standard AUTOSAR type shall follow the 64-bit binary interchange format according
            to IEEE 754-2008 with encoding parameters specified in chapter 3.6, table 3.5, column "binary64". */
typedef double  float64;

/*-------- Boolean Data Type--------- */
/* MR12 DIR 1.1 VIOLATION: the type _Bool is mapped here to the AUTOSAR type boolean to prevent the direct use of 
the type _Bool */
/* TRACE[SWS_Platform_00026]:This standard AUTOSAR type shall only be used together with the definitions TRUE and
FALSE. */

#if !defined (__cplusplus)
typedef _Bool   boolean;

#else
typedef bool boolean;

#endif
