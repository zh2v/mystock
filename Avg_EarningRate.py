import baostock as bs
import pandas as pd
import matplotlib.pyplot as plt
import math


def Nget_OCprice(code, start_date, end_date):  # 获取周期开盘价 和 收盘价，高效新函数2022-9-4
    rs_open = bs.query_history_k_data(code, "open", start_date=start_date, end_date=start_date, frequency="d",
                                      adjustflag="1")  # 获取证券当日开盘价，后复权1，前复权2，默认不复权3
    if rs_open.error_code == '0':
        result_open = rs_open.get_data()
        result_open.index = [code]
    else:
        result_open = pd.DataFrame()
    rs_close = bs.query_history_k_data(code, "close", start_date=end_date, end_date=end_date, frequency="d",
                                       adjustflag="1")  # 获取证券当日收盘价，后复权1，前复权2，默认不复权3
    if rs_close.error_code == '0':
        result_close = rs_close.get_data()
        result_close.index = [code]
    else:
        result_close = pd.DataFrame()
    result = result_open.join(result_close)
    return result

def get_closeprice(code, start_date, end_date):  # 优先使用 Nget_OCprice
    ###  获取沪深 A 股历史 K 线数据  ###
    # 详细指标参数，参见“历史行情指标参数”章节
    rs_open = bs.query_history_k_data(code, "open", start_date=start_date, end_date=start_date, frequency="d",
                                      adjustflag="1")  # 获取证券当日开盘价，后复权1，前复权2，默认不复权3

    data_list = []
    while (rs_open.error_code == '0') & rs_open.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs_open.get_row_data())
    result_open = pd.DataFrame(data_list, columns=rs_open.fields, index=[code])

    rs_close = bs.query_history_k_data(code, "close", start_date=end_date, end_date=end_date, frequency="d",
                                       adjustflag="1")  # 获取证券当日收盘价，后复权1，前复权2，默认不复权3

    data_list = []
    while (rs_close.error_code == '0') & rs_close.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs_close.get_row_data())
    result_close = pd.DataFrame(data_list, columns=rs_close.fields, index=[code])

    result = result_open.join(result_close)
    return result


def New_Avg_EarningRate(start_date, end_date, Nyears, stc_type):  # 高效计算平均年收益率 2022-9-4
    # t_day = bs.query_trade_dates(start_date, end_date)
    # if t_day.error_code == '0':
    #     trading_day = t_day.get_data()
    # else:
    #     trading_day = pd.DataFrame()
    #     print('err: trading days not get!')
    # trading_day = trading_day[trading_day['is_trading_day'] == "1"]
    # start_date = trading_day.iloc[0]['calendar_date']
    # end_date = trading_day.iloc[-1]['calendar_date']
    # 获取全部证券代码列表
    stock_info = pd.read_csv("Data/stock_basic.csv", index_col='code')  # 获取所有证券代码信息 , encoding="gbk"
    if stc_type != "A":
        stock_info = stock_info[stock_info['type'] == int(stc_type)]  # 根据radioButton获取相应类型的证券代码信息，股票，指数，ETF...
    code_list = stock_info.index.tolist()

    result = pd.DataFrame()  # 空数据
    for code in code_list:
        # 获取一条记录，将记录合并在一起
        df = Nget_OCprice(code, start_date, end_date)
        if result.empty:
            result = df  # 第一个非空数据
        else:
            result = result.append(df)  # 添加第二 - N行数据
    result = result.join(stock_info)  # 添加证券基本信息
    result = result[result['open'] != '']  # 筛选open 非空的数据
    result['open'] = result['open'].astype(float)  # 转换为浮点数
    result['close'] = result['close'].astype(float)
    result['avgEarningRate'] = (result['close'] / result['open']).apply(lambda x: math.pow(x, 1 / Nyears) - 1)  # 添加新列
    result = result.sort_values(by=['avgEarningRate'], ascending=False)  # 平均收益率降序排列
    file_nm = "Data/{}years Avg_Earning_Rate_data.csv".format(round(Nyears))
    result.to_csv(file_nm, index=True)  # 输出文件
    result.index = result['code_name']
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    plt_title = '{}years Avg Earning Rate'.format(Nyears)
    result[:20]['avgEarningRate'].plot(title=plt_title, kind='bar')  # 取部分数据画图
    plt.show()
    return file_nm


def compute_Avg_EarningRate(start_date, end_date):  # 优先使用 New_Avg_EarningRate


    # 获取全部证券基本资料
    # rs = bs.query_stock_basic()
    # rs = bs.query_all_stock(end_date)  # 获取所有证券代码信息
    code_list = pd.read_csv("Data/stock_basic.csv")  # 获取所有证券代码信息 , encoding="gbk"
    code_list = code_list[code_list['type'] == 1]
    code_list = code_list['code'].tolist()

    result = pd.DataFrame()  # 空数据
    for code in code_list:
        # 获取一条记录，将记录合并在一起
        # code = rs.get_row_data()[0]  # 获取1个证券代码
        df = get_closeprice(code, start_date, end_date)
        if result.empty:
            result = df  # 第一个非空数据
        else:
            result = result.append(df)  # 添加第二 - N行数据
    result = result[result['open'] != '']  # 筛选open 非空的数据
    result['open'] = result['open'].astype(float)  # 转换为浮点数
    result['close'] = result['close'].astype(float)
    result['avgEarningRate'] = (result['close'] / result['open']).apply(lambda x: math.pow(x, 1 / 3) - 1)  # 添加新列
    result = result.sort_values(by=['avgEarningRate'], ascending=False)  # 平均收益率降序排列
    result.to_csv("Data/Avg_Earning_Rate_data.csv", encoding="gbk", index=True)  # 输出文件
    result[:10]['avgEarningRate'].plot(title='Avg Earning Rate', kind='bar')  # 取部分数据画图
    plt.show()


if __name__ == '__main__':
    # 登陆系统
    lg = bs.login()

    # 显示登陆返回信息
    print('login respond error_code:' + lg.error_code)
    print('login respond error_msg:' + lg.error_msg)

    start_date = '2019-06-18'
    end_date = '2022-08-17'
    New_Avg_EarningRate(start_date, end_date, 3.012, 1)
    # compute_Avg_EarningRate(start_date, end_date)
    # 登出系统
    bs.logout()
