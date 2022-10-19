import baostock as bs
import pandas as pd

# 登陆系统
lg = bs.login()
# 显示登陆返回信息
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

stk_code = 'sz.002415'
# 成长能力
growth_list = []
rs_growth = bs.query_growth_data(code=stk_code, year=2022, quarter=1)
while (rs_growth.error_code == '0') & rs_growth.next():
    growth_list.append(rs_growth.get_row_data())
result_growth = pd.DataFrame(growth_list, columns=rs_growth.fields)
# 打印输出
print(result_growth)
# 结果集输出到csv文件
result_growth.to_csv("Data\\growth_data-%s.csv" % stk_code, encoding="gbk", index=False)

# 登出系统
bs.logout()

"""
参数含义：

code：股票代码，sh或sz.+6位数字代码，或者指数代码，如：sh.601398。sh：上海；sz：深圳。此参数不可为空；
year：统计年份，为空时默认当前年；
quarter：统计季度，为空时默认当前季度。不为空时只有4个取值：1，2，3，4。

返回数据说明
参数名称	参数描述	算法说明
code	证券代码	
pubDate	公司发布财报的日期	
statDate	财报统计的季度的最后一天, 比如2017-03-31, 2017-06-30	
YOYEquity	净资产同比增长率	(本期净资产-上年同期净资产)/上年同期净资产的绝对值*100%
YOYAsset	总资产同比增长率	(本期总资产-上年同期总资产)/上年同期总资产的绝对值*100%
YOYNI	净利润同比增长率	(本期净利润-上年同期净利润)/上年同期净利润的绝对值*100%
YOYEPSBasic	基本每股收益同比增长率	(本期基本每股收益-上年同期基本每股收益)/上年同期基本每股收益的绝对值*100%
YOYPNI	归属母公司股东净利润同比增长率	(本期归属母公司股东净利润-上年同期归属母公司股东净利润)/上年同期归属母公司股东净利润的绝对值*100%

"""