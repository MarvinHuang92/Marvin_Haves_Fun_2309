#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""通用的状态机，可以被多个项目引用"""

__author__ = 'Marvin Huang'


# 以下State和StateMachine两个类是不变的，只改变后续的就可以

class State:  # 状态基类，空白（新的状态会成为它的子类）
    def __init__(self, name):
        self.name = name

    def do_actions(self):  # 当前动作
        pass

    def check_conditions(self):  # 状态转移关系
        pass

    def entry_actions(self):  # 进入状态的动作
        pass

    def exit_actions(self):  # 退出状态的动作
        pass


class StateMachine:  # 状态机
    def __init__(self):
        self.states = {}    # 存储状态，这是一个目录dict
        self.active_state = None    # 当前有效状态

    def add_state(self, state):
        # 增加状态
        self.states[state.name] = state

    def think(self):
        if self.active_state is None:
            return
        # 所谓think包括两个部分：1执行有效状态的动作，2随时做转移状态检查
        self.active_state.do_actions()
        new_state_name = self.active_state.check_conditions()
        if new_state_name is not None:
            self.set_state(new_state_name)

    def set_state(self, new_state_name):
        # 更改状态，执行进入/退出动作
        if self.active_state is not None:
            self.active_state.exit_actions()  # 如果有当前动作，执行它的后摇
        self.active_state = self.states[new_state_name]  # 然后将当前动作更改
        self.active_state.entry_actions()  # 执行新动作的前摇

