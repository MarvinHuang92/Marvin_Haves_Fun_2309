import pandas as pd

# 基类
class Strategy():
    def __init__(self, avg_near, avg_far):
        self.AvgDays_Near = avg_near
        self.AvgDays_Far = avg_far
    
    def calcCommonInfo(self, data, periods=1):
        # 计算相较昨日的涨跌幅
        data['Daily_Return'] = data['Close'].pct_change()  # for yfinance
        # data['Daily_Return'] = data['pctChg'] / 100.0  # for baostock (百分比，需要除以100)
        # 计算过去N个交易日平均涨跌幅
        # data['Sum_Return'] = (data['Close'] - data['Close'].shift(periods)) / data['Close'].shift(periods)
        # data['Avg_Return'] = data['Sum_Return'] / periods
        data['Avg_Return'] = data['Close'].pct_change(periods)
        # 计算短期和长期移动平均
        data['MA_Near'] = data['Close'].rolling(window=self.AvgDays_Near).mean()
        data['MA_Far'] = data['Close'].rolling(window=self.AvgDays_Far).mean()
        # 初始化Signal值(表示买卖动作，也表示仓位：0卖出至空仓，1买入至满仓)
        data['Signal'] = 0
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
        data = self.calcCommonInfo(data)
        # 生成买卖信号
        # 昨天涨了，则今天开盘时全仓买入
        # 昨天跌了，今天空仓
        data.loc[data['Daily_Return'] > 0, 'Signal'] = 1  # 以昨日涨幅为信号，涨幅为正则满仓，否则空仓
        return data
    

# 自定义策略
class StrategyCustomize(Strategy):
    def __init__(self, avg_near=5, avg_far=30):
        super().__init__(avg_near, avg_far)
        self.name = "Customize"  # dummy

    # 计算仓位
    def calcPosition(self, data):

        N = 4  # 平均涨跌幅计算天数
        R_up = 0.01  # 平均涨幅阈值
        X_up = 0.005  # 当日止损线 （正值：稳健，负值：激进，设为-1表示没有止损）
        R_down = -0.005  # 平均跌幅阈值
        data = self.calcCommonInfo(data, periods=N)
        
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
    

# 多股轮动策略
class StrategyMultiTargetRotation(Strategy):
    def __init__(self, avg_near=5, avg_far=30):
        super().__init__(avg_near, avg_far)
        self.name = "MultiTargetRotation"

    # 第一轮调用：仅计算单只股票涨幅信息 Daily_Return and Avg_Return
    def calcSingleStockReturn(self, data):
        N = 4  # 平均涨跌幅计算天数，越大越稳健
        data = self.calcCommonInfo(data, periods=N)
        return data

    # 第二轮调用：计算选择哪只股票
    def calcChoice(self, data, num=1):
        X_up = 0.015  # 当日止损线 （正值：稳健，负值：激进，设为-1表示没有止损）
        
        # 比较所有个股的平均涨幅，选取最大值所在列
        # AR = Avg_Return, DR = Daily_Return
        compare_range = []
        for i in range(num):
            compare_range.append('Avg_Return_%s' % str(i+1))
        data['Avg_Return_Max'] = data[compare_range].max(axis=1)
        data['ARMax_index'] = data[compare_range].idxmax(axis=1) #, skipna=True)
        data['ARMax_index'] = data.apply(lambda data: str(data['ARMax_index']).strip("nan").strip("Avg_Return_"), axis=1)
        
        # 计算平均涨幅最大的个股，对应的当天涨幅
        def get_value_by_index(col_index, data):
            if col_index.strip('Daily_Return_') == '':
                return '0'
            elif col_index.strip('Daily_Return_') == '0':
                return '0'
            else:
                return data[col_index]
        data['DR_on_ARMax_index'] = data.apply(lambda data: get_value_by_index(
            "Daily_Return_" + str(data['ARMax_index']), data), axis=1)
        
        # 转换格式str -> float
        data['ARMax_index'] = pd.to_numeric(data['ARMax_index'])
        data['DR_on_ARMax_index'] = pd.to_numeric(data['DR_on_ARMax_index'])
        
        # 生成选股信号：若平均涨幅最大的个股，对应的当天涨幅超过止损线，输出其序号到Choice，否则输出0（默认值）
        data.loc[data['DR_on_ARMax_index'] >= X_up, 'Choice'] = data['ARMax_index']
        # 输出昨日选择目标股票的今日涨幅：【注意shift(1)下移一行，表示时间差】，空仓输出0
        data['Choice_Shifted'] = data['Choice'].shift(1)
        data['Strategy_Return'] = data.apply(lambda data: get_value_by_index(
            "Daily_Return_" + str(data['Choice_Shifted']).strip('.0'), data), axis=1)
        
         # 转换格式str -> float
        data['Strategy_Return'] = pd.to_numeric(data['Strategy_Return'])

        return data