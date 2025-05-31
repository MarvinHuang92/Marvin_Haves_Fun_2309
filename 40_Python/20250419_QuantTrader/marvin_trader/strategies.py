# import pandas as pd

"""
本文档定义所有的非轮动策略

接口定义:
策略需在data中添加如下列:
"Signal" 列: 表示下一个交易日的仓位, 0为空仓, 1为满仓
"Strategy_Return" 列: 每个交易日的收益率, 注意: 与上一个交易日的仓位相关
"Cumulative_Return" 列: 累计收益率

"""


# 基类
class Strategy():
    def __init__(self, avg_near, avg_far):
        self.AvgDays_Near = avg_near
        self.AvgDays_Far = avg_far
        self.avg_period = 1
    
    def calcCommonInfo(self, data):
        # 计算相较昨日的涨跌幅
        data['Daily_Return'] = data['Close'].pct_change(fill_method=None)  # for yfinance
        # data['Daily_Return'] = data['pctChg'] / 100.0  # for baostock (百分比，需要除以100)
        # 计算过去N个交易日平均涨跌幅
        # data['Sum_Return'] = (data['Close'] - data['Close'].shift(self.avg_period)) / data['Close'].shift(self.avg_period)
        # data['Avg_Return'] = data['Sum_Return'] / self.avg_period
        data['Avg_Return'] = data['Close'].pct_change(self.avg_period, fill_method=None)
        # 计算短期和长期移动平均
        data['MA_Near'] = data['Close'].rolling(window=self.AvgDays_Near).mean()
        data['MA_Far'] = data['Close'].rolling(window=self.AvgDays_Far).mean()
        # 初始化Signal值(表示买卖动作，也表示仓位：0卖出至空仓，1买入至满仓)
        data['Signal'] = 0
        return data
    
    def calcCumulativeReturn(self, data):
        # 计算累计收益
        # cumprod() 累计做乘法，可以体现复利
        data['Cumulative_Return'] = (1 + data['Strategy_Return']).cumprod()
        return data

    def calcStrategyReturn(self, data):
        # 计算今日收益率 = 今天涨幅*仓位（data['Signal']表示仓位）
        # 若今天跌了，收益率为负
        # 若今天空仓，收益率=0
        # shift(1)将data向下平移一行，第一行留空NaN
        data['Strategy_Return'] = data['Signal'].shift(1) * data['Daily_Return']
        # 计算累计收益
        data = self.calcCumulativeReturn(data)
        return data


# 子类

# 移动均线策略
class StrategyMoveAvg(Strategy):
    def __init__(self, avg_near=5, avg_far=30):
        super().__init__(avg_near, avg_far)
        self.name = "stategy_move_avg"
    
    # 计算仓位
    def calcPosition(self, data):
        data = self.calcCommonInfo(data)
        # 生成买卖信号
        data.loc[data['MA_Near'] > data['MA_Far'], 'Signal'] = 1  # 短期均线上穿长期均线，产生买入信号，满仓
        # data.loc[data['MA_Near'] < data['MA_Far'], 'Signal'] = 0  # 短期均线下穿长期均线，产生卖出信号，空仓（默认为0）

        # 限制条件
        # 长期均线未生成时，策略不生效，认为始终满仓，策略收益率=实际收益率
        data.loc[data['RowIndex'] < self.AvgDays_Far, 'Signal'] = 1

        return data


# 昨日收益率二值化策略
class StrategyYesterdayReturnBinarized(Strategy):
    def __init__(self, avg_near=5, avg_far=30):
        super().__init__(avg_near, avg_far)
        self.name = "stategy_yestRetBin"
    
    # 计算仓位
    def calcPosition(self, data):
        X_up = 0.015  # 当日止损线 （正值：稳健，负值：激进，设为-1表示没有止损）
        data = self.calcCommonInfo(data)
        # 生成买卖信号
        # 昨天涨了，则今天开盘时全仓买入
        # 昨天跌了，今天空仓
        data.loc[data['Daily_Return'] >= X_up, 'Signal'] = 1  # 以昨日涨幅为信号，涨幅超过止损线则满仓，否则空仓
        return data
    

# 自定义策略
class StrategyCustomize(Strategy):
    def __init__(self, avg_near=5, avg_far=30):
        super().__init__(avg_near, avg_far)
        self.name = "Customize"  # dummy

    # 计算仓位
    def calcPosition(self, data):
        self.avg_period = 4  # 平均涨跌幅计算天数
        R_up = 0.01  # 平均涨幅阈值
        X_up = 0.015  # 当日止损线 （正值：稳健，负值：激进，设为-1表示没有止损）
        R_down = -0.005  # 平均跌幅阈值
        data = self.calcCommonInfo(data)
        
        # 生成买卖信号

        # # 超跌反弹策略:
        # self.name = "OversoldRebound"
        # # 平均跌幅超过0.5%，且昨天为正收益，则买入，否则空仓
        # data.loc[(data['Avg_Return'] < R_down) & (data['Daily_Return'] >= X_up), 'Signal'] = 1

        # 连续上涨策略：
        self.name = "ContinuousUptrend"
        # 平均涨幅超过M，且昨天为正收益，则买入，否则空仓
        data.loc[(data['Avg_Return'] > R_up) & (data['Daily_Return'] >= X_up), 'Signal'] = 1

        # # 连续上涨-超跌反弹组合策略：
        # self.name = "ContinuousUptrendOrOversoldRebound"
        # data.loc[((data['Avg_Return'] > R_up) | (data['Avg_Return'] < R_down)) & (data['Daily_Return'] >= X_up), 'Signal'] = 1

        return data
    