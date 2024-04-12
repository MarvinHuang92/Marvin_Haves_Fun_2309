# 八皇后问题：求在国际象棋棋盘上摆放8个皇后，彼此不能互相攻击，有多少种摆放方式

# 显然，任意两个皇后不能处于同一行，同一列
# 用一个list表示一种摆放方法，第n个元素表示第n列的皇后处于第几行
# 第一列皇后可处于8个位置，第二列皇后可处于7个位置
# 穷举 8! = 40320 种排列方式，如不满足条件则淘汰，最终保留下的排列方式即为答案

# 允许改变棋盘大小，即皇后数量
QUEENS = 8

# 递归遍历所有棋盘排列方式
def next(chessboard, cal_index=0):
    if cal_index == QUEENS:
        return None
    if chessboard[cal_index] < QUEENS:
        chessboard[cal_index] += 1
    else:
        chessboard[cal_index] = 1
        chessboard = next(chessboard, cal_index=cal_index+1)
    return chessboard

# 检查当前棋盘是否符合规则
def check(chessboard):
    for cal_index in range(QUEENS):
        for other_cal_index in range(cal_index):
            # 任意两列不能有相同数字，否则两王后在同一行
            if chessboard[cal_index] == chessboard[other_cal_index]:
                return False
            # 任意两个皇后不能在同一斜线
            elif abs(chessboard[cal_index] - chessboard[other_cal_index]) == cal_index - other_cal_index:
                return False
    return True

if __name__ == "__main__":
    position_list = []
    chessboard = [1]*QUEENS

    while True:
        if chessboard:
            if check(chessboard):
                position_list.append(chessboard[:])
            chessboard = next(chessboard)
        else:
            break

    for pos in position_list:
        print(pos)
    
    print("Total %d solutions" % len(position_list))