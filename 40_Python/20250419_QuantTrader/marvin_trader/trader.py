import os
import pandas as pd
# import yfinance as yf
import baostock as bs
import matplotlib.pyplot as plt
from strategies import *


def baostock_get_data(symbol, start_date, end_date):

    #### 登陆系统 ####
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:'+lg.error_code)
    print('login respond error_msg:'+lg.error_msg)

    #### 获取历史K线数据 ####
    # 详细指标参数，参见“历史行情指标参数”章节
    # 如添加更多指标参数，需注意数据类型转换(默认都是str)
    attributes = "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST"
    # frequency="d"取日k线，adjustflag="3"默认不复权
    rs = bs.query_history_k_data_plus(symbol, attributes, start_date, end_date, frequency="d", adjustflag="3")
    print('query_history_k_data_plus respond error_code:'+rs.error_code)
    print('query_history_k_data_plus respond error_msg:'+rs.error_msg)

    #### 获取结果集 ####
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)

    #### 登出系统 ####
    bs.logout()

    # 数据类型转换：将str转为数值（暂只对常用指标转换，如需要可添加更多）
    result["Open"] = pd.to_numeric(result["open"])  # 为了适配yfinance脚本风格，首字母大写
    result["High"] = pd.to_numeric(result["high"])  # 为了适配yfinance脚本风格，首字母大写
    result["Low"] = pd.to_numeric(result["low"])    # 为了适配yfinance脚本风格，首字母大写
    result["Close"] = pd.to_numeric(result["close"])# 为了适配yfinance脚本风格，首字母大写
    result["preclose"] = pd.to_numeric(result["preclose"])
    result["volume"] = pd.to_numeric(result["volume"])
    result["amount"] = pd.to_numeric(result["amount"])
    result["turn"] = pd.to_numeric(result["turn"])

    return result

def create_output_dir():
    if not os.path.isdir("output"):
        os.mkdir("output")
    if not os.path.isdir("output/svg_plot"):
        os.mkdir("output/svg_plot")
    if not os.path.isdir("output/csv"):
        os.mkdir("output/csv")

def get_stock_list(input_csv):
    # 忽略csv注释中的中文编码错误
    data = pd.read_csv(input_csv, encoding="utf_8", encoding_errors="ignore")

    data = data.iloc[1:]  # 丢弃第一行（中文注释）
    data = data.drop(["comment", "Unnamed: 6"], axis=1)  # 丢弃指定的列

    # 修改日期格式
    data['start_date'] = data.apply(lambda data: data['start_date'].replace("/", "-"), axis=1)
    data['end_date'] = data.apply(lambda data: data['end_date'].replace("/", "-"), axis=1)
    # 将yfinance的股票代码格式适配为baostock的格式
    def symbol_adaptation(symbol_str):
        if ".SS" in symbol_str:
            symbol_str = "sh." + symbol_str.strip(".SS")
        elif ".SZ" in symbol_str:
            symbol_str = "sz." + symbol_str.strip(".SZ")
        return symbol_str
    data['symbol'] = data.apply(lambda data: symbol_adaptation(data['symbol']), axis=1)

    # records是内置参数，将dataframe转换为字典列表 [{}, {}, ...] 的格式
    dict_from_df = data.to_dict("records")
    # print(dict_from_df)

    return dict_from_df

def main(stock_info, strategy):
    # # 获取股票数据，后缀上海=SS，深圳=SZ
    # # 多只股票可定义为列表
    # # symbol = "000300.SS"  # 沪深300指数
    # symbol = "159919.SZ"  # 沪深300ETF
    # start_date = "2018-01-01"
    # end_date = "2025-04-18"

    symbol = stock_info["symbol"]
    start_date = stock_info["start_date"]
    end_date = stock_info["end_date"]

    # 获取股票的历史交易信息（当前：每次仅处理一只股票）
    # data = yf.download(symbol, start=start_date, end=end_date, auto_adjust=False)
    csv_path = "output/csv/history_k_data.csv_%s_%s_%s.csv" % (symbol, start_date, end_date)
    # 尝试读取已有的csv
    if os.path.exists(csv_path):
        data = pd.read_csv(csv_path)
    # 若不存在，从baostock搜索，并将结果集输出到csv
    else:  
        data = baostock_get_data(symbol, start_date, end_date)
        data['RowIndex'] = range(len(data))  # 给每一行添加索引，方便后面调用
        data.to_csv(csv_path, encoding="gbk", index=False)
    print(data.head())  # 不加参数，默认显示5行

    ########## 执行交易策略 ##########
    # 计算每日交易仓位
    data = strategy.calcPosition(data)


    ########## 回测 ##########
    # 计算策略收益
    # 收益率 = 今天涨幅*仓位（data['Signal']表示仓位）
    # 若今天跌了，收益率为负
    # 若今天空仓，收益率=0
    # shift(1)将data向下平移一行，第一行留空NaN
    data['Strategy_Return'] = data['Signal'].shift(1) * data['Daily_Return']
    
    # 计算累计收益
    # cumprod() 累计做乘法，可以体现复利
    data['Cumulative_Return'] = (1 + data['Strategy_Return']).cumprod()


    ########## 绘图 ##########
    plt.figure(figsize=(10, 6))
    # # 拆分为2行1列，fig表示总图，ax1, ax2表示两个子图，共享x轴
    # fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

    # plot 1:绘制股价和移动平均线
    plt.subplot(2, 1, 1)
    plt.plot(data['Close'], label='Close Price')
    plt.plot(data['MA_Near'], label='%d-day Moving Average' % strategy.AvgDays_Near)
    plt.plot(data['MA_Far'], label='%d-day Moving Average' % strategy.AvgDays_Far)

    # 标记买卖信号
    plt.scatter(data[data['Signal'] == 1].index, data[data['Signal'] == 1]['MA_Near'], marker='^', color='g', label='Buy Signal')
    plt.scatter(data[data['Signal'] == 0].index, data[data['Signal'] == 0]['MA_Near'], marker='v', color='r', label='Sell Signal')

    plt.title("Stock Price with Moving Averages")
    # 不显示第一张图的x轴刻度和label
    # plt.xlabel("Date")
    ax = plt.gca()
    ax.axes.xaxis.set_visible(False)
    plt.ylabel("Price (CNY)")
    plt.legend()

    # plot 2:绘制累计收益曲线
    plt.subplot(2, 1, 2)
    plt.plot(data['Cumulative_Return'], label='Strategy Cumulative Return', color='b')
    plt.plot(data['Close'] / data['Close'].iloc[0], label='Stock Cumulative Return', color='g')
    plt.title("Cumulative Return of Strategy vs. Stock")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Return")
    plt.legend()

    plt.suptitle("%s Stock Return from %s to %s" % (symbol, start_date, end_date)) # 总图标题
    # plt.supxlabel("Date") # 总图共享x轴标签

    fig_fname = "Stock_Return_%s_%s_%s_%s_Avg_%d_%d" % (strategy.name, symbol, start_date, end_date, 
                                                        strategy.AvgDays_Near, strategy.AvgDays_Far)
    plt.savefig("output/svg_plot/%s.svg" % fig_fname, dpi=None, format="svg")  # 文件名包含格式，可省略 format="svg" 参数
    plt.show()  # 要在保存图片之后再 show() ，否则show()会重新生成一个新的图片，保存的是空图片


if __name__ == "__main__":
    create_output_dir()

    # ########## 选择交易策略 ##########
    # 移动平均线策略
    # strategy = StrategyMoveAvg("stategy_move_avg", avg_near=1, avg_far=60)
    # 昨日收益率二值化策略
    strategy = StrategyYesterdayReturnBinarized("stategy_yestRetBin", avg_near=1, avg_far=60)

    # 编译输入列表的每只股票，计算策略收益
    for stock_info in get_stock_list("input/Stock_list.csv"):
        if not (stock_info['baostock_available'] == 'N'):
            main(stock_info, strategy)