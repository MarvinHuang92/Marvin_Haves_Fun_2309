# 基类
class Strategy():
    def __init__(self, name, avg_near, avg_far):
        self.name = name
        self.AvgDays_Near = avg_near
        self.AvgDays_Far = avg_far
    
    def calcCommonInfo(self, data):
        # 计算相较昨日的涨跌幅
        data['Daily_Return'] = data['Close'].pct_change()
        # 计算短期和长期移动平均
        data['MA_Near'] = data['Close'].rolling(window=self.AvgDays_Near).mean()
        data['MA_Far'] = data['Close'].rolling(window=self.AvgDays_Far).mean()
        # 初始化Signal值(表示买卖动作，也表示仓位：0卖出至空仓，1买入至满仓)
        data['Signal'] = 0
        return data


# 子类

# 移动均线策略
class StrategyMoveAvg(Strategy):
    # 不定义__init__函数，自动调用基类__init__函数
    
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
    # 不定义__init__函数，自动调用基类__init__函数
    
    # 计算仓位
    def calcPosition(self, data):
        data = self.calcCommonInfo(data)
        # 生成买卖信号
        # 昨天涨了，则今天开盘时全仓买入
        # 昨天跌了，今天空仓
        data.loc[data['Daily_Return'] > 0, 'Signal'] = 1  # 以昨日涨幅为信号，涨幅为正则满仓，否则空仓
        return data