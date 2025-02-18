cmake_minimum_required(VERSION 3.1)
# include(cmake/internal.cmake)
SET(CMAKE_C_COMPILER "gcc")
SET(CMAKE_CXX_COMPILER "g++")
#以上，指定编译器路径

PROJECT (20250218_Textinfo_Arbitration)
SET(SRC_LIST textinfo_arbitration.cpp)
MESSAGE(STATUS "This is BINARY dir " ${HELLO_BINARY_DIR})
MESSAGE(STATUS "This is SOURCE dir "${HELLO_SOURCE_DIR})
ADD_EXECUTABLE(textinfo_arbitration ${SRC_LIST})