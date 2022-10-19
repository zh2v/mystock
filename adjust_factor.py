import baostock as bs
import pandas as pd

# 登陆系统
lg = bs.login()
# 显示登陆返回信息
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

stk_code = 'sz.002415'
# 查询2018至2022年复权因子
rs_list = []
rs_factor = bs.query_adjust_factor(code=stk_code, start_date="2018-01-01", end_date="2022-12-31")
while (rs_factor.error_code == '0') & rs_factor.next():
    rs_list.append(rs_factor.get_row_data())
result_factor = pd.DataFrame(rs_list, columns=rs_factor.fields)
# 打印输出
print(result_factor)

# 结果集输出到csv文件
result_factor.to_csv("Data/adjust_factor_data-%s.csv" % stk_code, encoding="gbk", index=False)

# 登出系统
bs.logout()

"""
参数含义：

code：股票代码，sh或sz.+6位数字代码，或者指数代码，如：sh.601398。sh：上海；sz：深圳。此参数不可为空；
start_date：开始日期，为空时默认为2015-01-01，包含此日期；
end_date：结束日期，为空时默认当前日期，包含此日期。
返回示例数据
code	dividOperateDate	foreAdjustFactor	backAdjustFactor	adjustFactor
sh.600000	2015-06-23	0.663792	6.295967	6.295967
sh.600000	2016-06-23	0.751598	7.128788	7.128788
sh.600000	2017-05-25	0.989551	9.385732	9.385732
返回数据说明
参数名称	参数描述	算法说明
code	证券代码	
dividOperateDate	除权除息日期	
foreAdjustFactor	向前复权因子	除权除息日前一个交易日的收盘价/除权除息日最近的一个交易日的前收盘价
backAdjustFactor	向后复权因子	除权除息日最近的一个交易日的前收盘价/除权除息日前一个交易日的收盘价
adjustFactor	本次复权因子	
"""