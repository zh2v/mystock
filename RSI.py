import baostock as bs
import pandas as pd
import talib as ta
import matplotlib.pyplot as plt


def computeRSI(code, startdate, enddate):
    """计算证券在起止时间内的 RSI 指标。
    :param code:证券代码
    :param startdate:起始日期
    :param enddate:截止日期
    :return:
    """
    login_result = bs.login(user_id='anonymous', password='123456')
    print(login_result.error_msg)
    # 获取股票日 K 线数据,adjustflag 复权状态(1：后复权， 2：前复权，3：不复权）
    rs = bs.query_history_k_data(code, "date,code,close,tradeStatus", start_date=startdate, end_date=enddate,
                                 frequency="d", adjustflag="3")
    # 打印结果集
    result_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        result_list.append(rs.get_row_data())
    df_init = pd.DataFrame(result_list, columns=rs.fields)
    # 剔除停盘数据
    df_status = df_init[df_init['tradeStatus'] == '1']
    df_status['close'] = df_status['close'].astype(float)
    rsi_12days = ta.RSI(df_status['close'], timeperiod=12)
    rsi_6days = ta.RSI(df_status['close'], timeperiod=6)
    rsi_24days = ta.RSI(df_status['close'], timeperiod=24)
    df_status['rsi_6days'] = rsi_6days
    df_status['rsi_12days'] = rsi_12days
    df_status['rsi_24days'] = rsi_24days
    # RSI 超卖和超买
    rsi_buy_position = df_status['rsi_6days'] > 80
    rsi_sell_position = df_status['rsi_6days'] < 20
    df_status.loc[rsi_buy_position[(rsi_buy_position == True) & (rsi_buy_position.shift() == False)].index, '超买'] = '超买'
    df_status.loc[
     rsi_sell_position[(rsi_sell_position == True) & (rsi_sell_position.shift() == False)].index, '超卖'] = '超卖'
    return df_status


if __name__ == '__main__':
    code = "sh.601100"
    startdate = "2021-01-01"
    enddate = "2022-07-05"
    df = computeRSI(code, startdate, enddate)
    df2 = df[['date', 'rsi_6days', 'rsi_12days', 'rsi_24days']]
    df2.index = df['date']
    df2.plot(title='RSI')
    plt.show()
    df.to_csv("Data/RSI-%s.csv" % code, encoding='gbk')

'''
计算公式：
N 日 RSI =N 日内收盘涨幅的平均值/(N 日内收盘涨幅均值+N 日内收盘跌幅均值) ×100
由上面算式可知 RSI 指标的技术含义，即以向上的力量与向下的力量进行比较，若向上
的力量较大，则计算出来的指标上升；若向下的力量较大，则指标下降，由此测算出市场走
势的强弱。
市场上一般的规则：（快速 RSI 指 6 日的 RSI，慢速 RSI 指 14 日的 RSI）
1. RSI 金叉：快速 RSI 从下往上突破慢速 RSI 时,认为是买进机会。
2. RSI 死叉：快速 RSI 从上往下跌破慢速 RSI 时,认为是卖出机会
3. 慢速 RSI<20 为超卖状态,为买进机会。
4. 慢速 RSI>80 为超买状态,为卖出机会。'''