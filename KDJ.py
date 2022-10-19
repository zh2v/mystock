import baostock as bs
import pandas as pd
import matplotlib.pyplot as plt


def computeKDJ(code, startdate, enddate):
    login_result = bs.login(user_id='anonymous', password='123456')
    print(login_result.error_msg)
    # 获取股票日K线数据
    rs = bs.query_history_k_data(code, "date,code,high,close,low,tradeStatus", start_date=startdate, end_date=enddate,
                                 frequency="d", adjustflag="3")
    # 打印结果集
    result_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        result_list.append(rs.get_row_data())
    df_init = pd.DataFrame(result_list, columns=rs.fields)
    # 剔除停盘数据
    df_status = df_init[df_init['tradeStatus'] == '1']
    low = df_status['low'].astype(float)
    del df_status['low']
    df_status.insert(0, 'low', low)
    high = df_status['high'].astype(float)
    del df_status['high']
    df_status.insert(0, 'high', high)
    close = df_status['close'].astype(float)
    del df_status['close']
    df_status.insert(0, 'close', close)
    # 计算KDJ指标,前9个数据为空
    low_list = df_status['low'].rolling(window=9).min()
    high_list = df_status['high'].rolling(window=9).max()
    rsv = (df_status['close'] - low_list) / (high_list - low_list) * 100
    df_data = pd.DataFrame()
    df_data['K'] = rsv.ewm(com=2).mean()
    df_data['D'] = df_data['K'].ewm(com=2).mean()
    df_data['J'] = 3 * df_data['K'] - 2 * df_data['D']
    df_data.index = df_status['date'].values
    df_data.index.name = 'date'
    # 删除空数据
    df_data = df_data.dropna()
    # 计算KDJ指标金叉、死叉情况
    df_data['KDJ_金叉死叉'] = ''
    kdj_position = df_data['K'] > df_data['D']
    df_data.loc[kdj_position[(kdj_position == True) & (kdj_position.shift() == False)].index, 'KDJ_金叉死叉'] = '金叉'
    df_data.loc[kdj_position[(kdj_position == False) & (kdj_position.shift() == True)].index, 'KDJ_金叉死叉'] = '死叉'
    df_data.plot(title='KDJ')
    plt.show()
    bs.logout()
    return (df_data)


if __name__ == '__main__':
 code = 'sh.601100'
 startdate = '2021-06-24'
 enddate = '2022-06-24'
 df = computeKDJ(code, startdate, enddate)
 # 保存到文件中
 df.to_csv("Data/KDJ-%s.csv" % code, encoding='gbk')


'''KDJ 的计算比较复杂，首先要计算周期（n 日、n 周等）的 RSV 值，即未成熟随机指标
值，然后再计算 K 值、D 值、J 值等。以 n 日 KDJ 数值的计算为例：
（1）n 日 RSV=（Cn－Ln）/（Hn－Ln）×100
公式中，Cn 为第 n 日收盘价；Ln 为 n 日内的最低价；Hn 为 n 日内的最高价。
（2）其次，计算 K 值与 D 值：
当日 K 值=2/3×前一日 K 值+1/3×当日 RSV
当日 D 值=2/3×前一日 D 值+1/3×当日 K 值
若无前一日 K 值与 D 值，则可分别用 50 来代替。
（3）J 值=3*当日 K 值-2*当日 D 值
KDJ 的基本使用方法：
K 线是快速确认线——数值在 90 以上为超买，数值在 10 以下为超卖；
D 线是慢速主干线——数值在 80 以上为超买，数值在 20 以下为超卖；
J 线为方向敏感线，当 J 值大于 100，特别是连续 5 天以上，股价至少会形成短期头部，
反之 J 值小于 0 时，特别是连续数天以上，股价至少会形成短期底部。
'''