#include <iostream>
#include <windows.h>
#include <thread>
#include <chrono>

class KeyboardStatus {
public:
    bool key0;
    bool key1;
    bool key2;
    bool key3;
    bool key4;
    bool key5;
    bool key6;
    bool key7;
    bool key8;
    bool key9;

    KeyboardStatus() : key0(false), key1(false), key2(false), key3(false),
                       key4(false), key5(false), key6(false), key7(false),
                       key8(false), key9(false) {}
};

KeyboardStatus m_currentKBSts;
KeyboardStatus m_lastKBSts;

void GetInput() {
    // 检查数字键0-9是否被按下
    m_currentKBSts.key0 = (GetAsyncKeyState('0') & 0x8000) != 0;
    m_currentKBSts.key1 = (GetAsyncKeyState('1') & 0x8000) != 0;
    m_currentKBSts.key2 = (GetAsyncKeyState('2') & 0x8000) != 0;
    m_currentKBSts.key3 = (GetAsyncKeyState('3') & 0x8000) != 0;
    m_currentKBSts.key4 = (GetAsyncKeyState('4') & 0x8000) != 0;
    m_currentKBSts.key5 = (GetAsyncKeyState('5') & 0x8000) != 0;
    m_currentKBSts.key6 = (GetAsyncKeyState('6') & 0x8000) != 0;
    m_currentKBSts.key7 = (GetAsyncKeyState('7') & 0x8000) != 0;
    m_currentKBSts.key8 = (GetAsyncKeyState('8') & 0x8000) != 0;
    m_currentKBSts.key9 = (GetAsyncKeyState('9') & 0x8000) != 0;
}

void TextDisplay(const KeyboardStatus& current, const KeyboardStatus& last) {
    int maxKey = -1; // 用于记录满足条件的最大数字键

    // 检查每个键是否满足条件
    if (current.key0 && !last.key0) maxKey = std::max(maxKey, 0);
    if (current.key1 && !last.key1) maxKey = std::max(maxKey, 1);
    if (current.key2 && !last.key2) maxKey = std::max(maxKey, 2);
    if (current.key3 && !last.key3) maxKey = std::max(maxKey, 3);
    if (current.key4 && !last.key4) maxKey = std::max(maxKey, 4);
    if (current.key5 && !last.key5) maxKey = std::max(maxKey, 5);
    if (current.key6 && !last.key6) maxKey = std::max(maxKey, 6);
    if (current.key7 && !last.key7) maxKey = std::max(maxKey, 7);
    if (current.key8 && !last.key8) maxKey = std::max(maxKey, 8);
    if (current.key9 && !last.key9) maxKey = std::max(maxKey, 9);

    // 输出结果
    if (maxKey != -1) {
        std::cout << maxKey << std::endl;
    } else {
        std::cout << "0xFF" << std::endl;
    }
}

int main() {
    while (true) {
        GetInput();
        TextDisplay(m_currentKBSts, m_lastKBSts);

        // 将当前状态赋值给上一次状态
        m_lastKBSts = m_currentKBSts;

        // 等待0.5秒
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }

    return 0;
}