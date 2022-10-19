import baostock as bs
import pandas as pd
import mplfinance as mpf
#### 登陆系统 ####
lg = bs.login()
# 显示登陆返回信息
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

stk_code = 'sh.600809'
#### 获取历史K线数据 ####
# 详细指标参数，参见“历史行情指标参数”章节
rs = bs.query_history_k_data_plus(stk_code,
    "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST",
    start_date='2021-06-01', end_date='2022-06-17',
    frequency="d", adjustflag="1") #frequency="d"取日k线，adjustflag="3"默认不复权；1：后复权；2：前复权。已支持分钟线、日线、周线、月线前后复权。
print('query_history_k_data_plus respond error_code:'+rs.error_code)
print('query_history_k_data_plus respond  error_msg:'+rs.error_msg)

#### 打印结果集 ####
data_list = []
while (rs.error_code == '0') & rs.next():
    # 获取一条记录，将记录合并在一起
    data_list.append(rs.get_row_data())
result = pd.DataFrame(data_list, columns=rs.fields)
#### 结果集输出到csv文件 ####
result.to_csv("Data/history_k_data-%s.csv" % stk_code, index=False)
# print(result)

#### 登出系统 ####
bs.logout()

# 绘制图形

result['date'] = pd.to_datetime(result['date'])  # 转换日期列的格式，便于作图
result['open'] = result['open'].apply(lambda x: float(x))  # 转换格式-str2float
result.high = result['high'].apply(lambda x: float(x))  # 转换格式
result['low'] = result['low'].apply(lambda x: float(x))  # 转换格式
result['close'] = result['close'].apply(lambda x: float(x))  # 转换格式
result.volume = result.volume.apply(lambda x: float(x))  # 转换格式

result.set_index(['date'], inplace=True)  # 将日期列作为行索引
# result = result.sort_index()  # 倒序
print(result)
mpf.plot(result, type='candle', mav=(5, 10, 20), volume=True, style='blueskies', title='\nstk_code='+stk_code)
"""
参数含义：

code：股票代码，sh或sz.+6位数字代码，或者指数代码，如：sh.601398。sh：上海；sz：深圳。此参数不可为空；
fields：指示简称，支持多指标输入，以半角逗号分隔，填写内容作为返回类型的列。详细指标列表见历史行情指标参数章节，日线与分钟线参数不同。此参数不可为空；
start：开始日期（包含），格式“YYYY-MM-DD”，为空时取2015-01-01；
end：结束日期（包含），格式“YYYY-MM-DD”，为空时取最近一个交易日；
frequency：数据类型，默认为d，日k线；d=日k线、w=周、m=月、5=5分钟、15=15分钟、30=30分钟、60=60分钟k线数据，不区分大小写；指数没有分钟线数据；周线每周最后一个交易日才可以获取，月线每月最后一个交易日才可以获取。
adjustflag：复权类型，默认不复权：3；1：后复权；2：前复权。已支持分钟线、日线、周线、月线前后复权。 BaoStock提供的是涨跌幅复权算法复权因子，具体介绍见：复权因子简介或者BaoStock复权因子简介。
注意：

股票停牌时，对于日线，开、高、低、收价都相同，且都为前一交易日的收盘价，成交量、成交额为0，换手率为空。
如果需要将换手率转为float类型，可使用如下方法转换：result["turn"] = [0 if x == "" else float(x) for x in result["turn"]]

关于复权数据的说明：

BaoStock使用“涨跌幅复权法”进行复权，详细说明参考上文“复权因子简介”。不同系统间采用复权方式可能不一致，导致数据不一致。

“涨跌幅复权法的”优点：可以计算出资金收益率，确保初始投入的资金运用率为100%，既不会因为分红而导致投资减少，也不会因为配股导致投资增加。

返回数据说明
参数名称	参数描述	算法说明
date	交易所行情日期	
code	证券代码	
open	开盘价	
high	最高价	
low	最低价	
close	收盘价	
preclose	前收盘价	见表格下方详细说明
volume	成交量（累计 单位：股）	
amount	成交额（单位：人民币元）	
adjustflag	复权状态(1：后复权， 2：前复权，3：不复权）	
turn	换手率	[指定交易日的成交量(股)/指定交易日的股票的流通股总股数(股)]*100%
tradestatus	交易状态(1：正常交易 0：停牌）	
pctChg	涨跌幅（百分比）	日涨跌幅=[(指定交易日的收盘价-指定交易日前收盘价)/指定交易日前收盘价]*100%
peTTM	滚动市盈率	(指定交易日的股票收盘价/指定交易日的每股盈余TTM)=(指定交易日的股票收盘价*截至当日公司总股本)/归属母公司股东净利润TTM
pbMRQ	市净率	(指定交易日的股票收盘价/指定交易日的每股净资产)=总市值/(最近披露的归属母公司股东的权益-其他权益工具)
psTTM	滚动市销率	(指定交易日的股票收盘价/指定交易日的每股销售额)=(指定交易日的股票收盘价*截至当日公司总股本)/营业总收入TTM
pcfNcfTTM	滚动市现率	(指定交易日的股票收盘价/指定交易日的每股现金流TTM)=(指定交易日的股票收盘价*截至当日公司总股本)/现金以及现金等价物净增加额TTM
isST	是否ST股，1是，0否	
注意“前收盘价”说明：

证券在指定交易日行情数据的前收盘价，当日发生除权除息时，“前收盘价”不是前一天的实际收盘价，而是根据股权登记日收盘价与分红现金的数量、配送股的数里和配股价的高低等结合起来算出来的价格。

具体计算方法如下:

1、计算除息价:

除息价=股息登记日的收盘价-每股所分红利现金额

2、计算除权价:

送红股后的除权价=股权登记日的收盘价/(1+每股送红股数)

配股后的除权价=(股权登记日的收盘价+配股价*每股配股数)/(1+每股配股数)

3、计算除权除息价

除权除息价=(股权登记日的收盘价-每股所分红利现金额+配股价*每股配股数)/(1+每股送红股数+每股配股数)

“前收盘价”由交易所计算并公布。首发日的“前收盘价”等于“首发价格”。
"""