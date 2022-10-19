import baostock as bs
import pandas as pd

#### 登陆系统 ####
lg = bs.login()
# 显示登陆返回信息
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

#### 查询除权除息信息####
# 查询2015年除权除息信息
stk_code = 'sz.002415'
rs_list = []
rs_dividend_2015 = bs.query_dividend_data(code=stk_code, year="2020", yearType="report")
while (rs_dividend_2015.error_code == '0') & rs_dividend_2015.next():
    rs_list.append(rs_dividend_2015.get_row_data())

# 查询2016年除权除息信息
rs_dividend_2016 = bs.query_dividend_data(code=stk_code, year="2021", yearType="report")
while (rs_dividend_2016.error_code == '0') & rs_dividend_2016.next():
    rs_list.append(rs_dividend_2016.get_row_data())

# 查询2017年除权除息信息
rs_dividend_2017 = bs.query_dividend_data(code=stk_code, year="2022", yearType="report")
while (rs_dividend_2017.error_code == '0') & rs_dividend_2017.next():
    rs_list.append(rs_dividend_2017.get_row_data())

result_dividend = pd.DataFrame(rs_list, columns=rs_dividend_2017.fields)
# 打印输出
print(result_dividend)

#### 结果集输出到csv文件 ####
result_dividend.to_csv("Data/history_Dividend_data-%s.csv" % stk_code, encoding="gbk",index=False)

#### 登出系统 ####
bs.logout()

""""
参数含义：
code：股票代码，sh或sz.+6位数字代码，或者指数代码，如：sh.601398。sh：上海；sz：深圳。此参数不可为空；
year：年份，如：2017。此参数不可为空；
yearType：年份类别，默认为"report":预案公告年份，可选项"operate":除权除息年份。此参数不可为空。

返回数据说明
参数名称	参数描述	算法说明
code	证券代码	
dividPreNoticeDate	预批露公告日	
dividAgmPumDate	股东大会公告日期	
dividPlanAnnounceDate	预案公告日	
dividPlanDate	分红实施公告日	
dividRegistDate	股权登记告日	
dividOperateDate	除权除息日期	
dividPayDate	派息日	
dividStockMarketDate	红股上市交易日	
dividCashPsBeforeTax	每股股利税前	派息比例分子(税前)/派息比例分母
dividCashPsAfterTax	每股股利税后	派息比例分子(税后)/派息比例分母
dividStocksPs	每股红股	
dividCashStock	分红送转	每股派息数(税前)+每股送股数+每股转增股本数
dividReserveToStockPs	每股转增资本	
"""