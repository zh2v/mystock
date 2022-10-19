import baostock as bs
import pandas as pd
# import sys
# sys.path.append('D:/Personal/MyPython/test/func')  # 加载sys包，把新建的function model所在路径添加上

import BS_function as BSf

# print(BSf.__file__)
bs.login()

date = "2022-05-13"
all_stc = BSf.ge_all_stock()  # 参数：需要查询的交易日期，为空时默认当前日期
print(all_stc)
code = ''
stB = BSf.get_stock_basic()  # 参数可为空值，获得所有证券信息；可填代码或名称如：code = 'sh.600031'
print(stB)
print(stB[stB['type'] == '1'])
# print(stB.iloc[0, 1])
# BSf.download_data(date)

bs.logout()

