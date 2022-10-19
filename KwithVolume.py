import baostock as bs
import pandas as pd
import mplfinance as mpf
import re


def code_is(code_name):
    code_list = pd.read_csv("Data/stock_basic.csv")  # 获取所有证券代码信息 , encoding="gbk"
    code_list = code_list['code'].tolist()

    pattern = re.compile('(?<=\d{2}\.)[\u4e00-\u9fa5]+\.\w{3}')
    match1 = pattern.search(code_name)
    if len(code_name) == 9:
        d=1



def get_k_data(stk_code, start_date, end_date):
    rs = bs.query_history_k_data_plus(stk_code,
                                      "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST",
                                      start_date=start_date, end_date=end_date, frequency="d",
                                      adjustflag="2")  # frequency="d"取日k线，adjustflag="3"默认不复权；1：后复权；2：前复权。已支持分钟线、日线、周线、月线前后复权。
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    #### 结果集输出到csv文件 ####
    result.to_csv("Data/history_k_data-%s.csv" % stk_code, index=False)
    return result


def draw_k_vol(stk_code, stk_name):
    data = pd.read_csv("Data/history_k_data-%s.csv" % stk_code, index_col=0, parse_dates=True)
    kwargs = dict(type='candle', mav=(5, 10, 20), volume=True, figratio=(11, 8), figscale=0.85)
    mpf.plot(data, **kwargs, style=my_style,
             title='\n{}, {} K线图'.format(stk_name, stk_code), ylabel="价格(RMB)", ylabel_lower="成交量(shares)")
    # 下面输出同样的图形，上面的更好，多个图形可以共同使用**kwargs
    # mpf.plot(data, type='candle', mav=(5, 10, 20), volume=True, style=my_style,
    #          title='\n恒立液压', ylabel_lower="volume(shares)")

my_color = mpf.make_marketcolors(
    up='red',  # 上涨K线的颜色
    down="green",  # 下跌K线的颜色
    edge="inh",  # 蜡烛图箱体的颜色，inh 表示继承up and down
    volume="inherit",  # 成交量柱子的颜色，inherit 表示继承up and down
    wick="blue",   # 蜡烛图影线的颜色
    alpha=0.8  # candlestick face，取值在0.1-1之间。K线蜡烛颜色的深浅
)

my_style = mpf.make_mpf_style(
    base_mpf_style='blueskies',  # 继承内置的风格，不想继承的话就不需要设置。
    marketcolors=my_color,  # K线的颜色方面的信息
    gridaxis='both',  # 设置网格线方向,both双向 'horizontal’水平, 'vertical’垂直
    gridstyle='-.',  # 设置网格线线型,例如‘-’/‘solid’, ‘–’/‘dashed’, ‘-.’/‘dashdot’, ‘:’/‘dotted’, None/’ ‘/’’
    y_on_right=True,  # 设置y轴位置是否在右
    rc={'font.family': 'SimHei', 'axes.unicode_minus': 'False'},  # 用来解决 mplfinance库生成的图象 中文乱码和不显示负数的问题
    edgecolor='black',  # 设置框线样式
    # figcolor='r',  # 设置图像外周边填充色
    # facecolor='black',  # 设置前景色（坐标系颜色）
    # gridcolor='b'  # 设置网格线颜色
)


#  style参数常用的内置样式有：‘binance’, ‘blueskies’, ‘brasil’, ‘charles’, ‘checkers’,
# ‘classic’, ‘default’, ‘mike’, ‘nightclouds’, ‘sas’, ‘starsandstripes’, ‘yahoo’
# 可使用 mpf.available_styles() 查询


if __name__ == '__main__':
    # 登陆系统
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:' + lg.error_code)
    print('login respond error_msg:' + lg.error_msg)

    start_date = '2021-06-18'
    end_date = '2022-08-17'
    stk_code = 'sh.601100'
    stk_name = '我的股票'
    get_k_data(stk_code, start_date, end_date)
    draw_k_vol(stk_code, stk_name)

    # 登出系统
    bs.logout()