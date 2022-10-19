import baostock as bs
import pandas as pd
import re


def ge_all_stock(day=''):  # day：需要查询的交易日期，为空时默认当前日期。
    stock_A = bs.query_all_stock(day)
    # print(stock_A, "Hello BS")
    stock_alldata = stock_A.get_data()
    stock_alldata.to_csv("Data/All_stock_data.csv", index=False)
    print(stock_alldata.shape, 'Data saved successfully!')
    return stock_alldata
'''
返回示例数据
code	tradeStatus	code_name
sh.000001	1	上证综合指数
sh.000002	1	上证A股指数
sh.000003	1	上证B股指数
返回数据说明
参数名称	参数描述
code	证券代码
tradeStatus	交易状态(1：正常交易 0：停牌）
code_name	证券名称
'''

def get_stock_basic(code=''):  # 获取证券基本资料
    # 参数含义：
    # code：A股股票代码，sh或sz. + 6位数字代码，或者指数代码，如：sh.601398。sh：上海；sz：深圳。可以为空；
    # code_name：股票名称，支持模糊查询，可以为空。
    st_bs = bs.query_stock_basic(code)
    result = st_bs.get_data()
    # 结果集输出到csv文件
    if code == '':
        result.to_csv("Data/stock_basic.csv", index=False)
    else:
        result.to_csv("Data/stock_basic-%s.csv" % code, index=False)
    print('stock_basic', result.shape, code,'Data saved successfully!')
    return result
'''
返回示例数据
code	code_name	ipoDate	outDate	type	status
sh.600000	浦发银行	1999-11-10		1	1
返回数据说明
参数名称	参数描述
code	证券代码
code_name	证券名称
ipoDate	上市日期
outDate	退市日期
type	证券类型，其中1：股票，2：指数，3：其它，4：可转债，5：ETF
status	上市状态，其中1：上市，0：退市
'''


def get_code_name(code_name):  # 获取证券基本资料
    pattern1 = re.compile(r'\b(of|sh|sz|bj).\d{6}$')  # 匹配完整证券代码 如：sh.600001
    pattern2 = re.compile(r'\b([0-9]{6})$')  # 匹配仅数字部分证券代码 如：600001
    match1 = pattern1.search(code_name)
    match2 = pattern2.search(code_name)
    code = ''
    name = ''
    msg = ''
    if code_name == '':
        msg = '股票代码/名称不能为空！'

    code_list = pd.read_csv("Data/stock_basic.csv")  # 获取所有证券代码信息从本地文件中
    # code_list = code_list[code_list['type']==1]
    code_list = code_list[['code', 'code_name']]

    if match1:  # 匹配完整证券代码 如：sh.600001
        print(match1)
        st_bs = bs.query_stock_basic(code_name)
        result = st_bs.get_data()
        code = result.loc[0, 'code']
        name = result.loc[0]['code_name']
    elif match2:  # 匹配仅数字部分证券代码 如：600001
        print(match2)
        code_lst = []
        for code_b in code_list['code']:  # 匹配仅数字部分证券代码， 将匹配的所有代码加入清单
            if code_b[-6:] == code_name:
                code_lst.append(code_b)
        if len(code_lst) == 1:  # 清单如果是唯一值，直接获取code，name
            code_name = code_lst[0]
            st_bs = bs.query_stock_basic(code_name)
            result = st_bs.get_data()
            code = result.loc[0, 'code']
            name = result.loc[0]['code_name']
            # msg = '输入正确！'
        elif len(code_lst) > 1:  # 清单如果是多个值，提示重新输入
            msg = '输入的代码不唯一' + str(code_lst) + '，请加上前缀sh./sz./...'
            print(msg)
        else:  # 清单如果是空值，提示重新输入
            msg = '请重新输入正确的代码, eg: sh.600001'
            print(msg)
    elif code_name != '':  # 没有匹配上述两种证券代码，作为证券名称(code_name=code_name)获取code，name
        print('Not match code!!')
        st_bs = bs.query_stock_basic(code_name=code_name)
        result = st_bs.get_data()
        if result.shape[0] == 1:  # 结果如果是唯一值，直接获取code，name
            code = result.loc[0, 'code']
            name = result.loc[0]['code_name']
        elif result.shape[0] > 1:  # 清单如果是多个值，提示重新输入
            msg = '输入的名称不唯一' + str(result['code_name'].to_list()) + '，请加上前缀sh./sz./...'
            print(msg)
        else:  # 清单如果是空值，提示重新输入
            msg = '输入的证券名称没找到，请重新输入'
            print(msg)
    if (code == '' or name == '') and msg == '':
        msg = '请重新输入正确的代码, eg: sh.600001'
    return code, name, msg

def download_data(date):
    # 获取指定日期的指数、股票数据
    stock_df = ge_all_stock(date)
    data_df = pd.DataFrame()
    # print(type(stock_df["code"]))
    for code in stock_df["code"]:
        print("Downloading :" + code)
        k_rs = bs.query_history_k_data_plus(code, "date,code,open,high,low,close", date, date)
        data_df = data_df.append(k_rs.get_data())
    data_df.to_csv("Data/AssignDayData.csv", index=False)
    print(data_df)


if __name__ == '__main__':
    # 获取指定日期全部股票的日K线数据
    bs.login()
    date = "2022-05-13"
    # getAllStock(date)
    code = ''  # code = 'sh.600031'
    code_nm= '三一重工'
    get_stock_basic(code_nm)  # 参数可为空值，获得所有证券信息；可填代码或名称如：code = 'sh.600031'
    # download_data(date)
    bs.logout()

