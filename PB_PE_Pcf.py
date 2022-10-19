import pandas as pd
import baostock as bs


def all_stock_list(date):  # 获取某一天的全市场的证券和指数代码
    stc_list = bs.query_all_stock(date)
    print('query_all_stock respond error_code:' + stc_list.error_code)
    print('query_all_stock respond error_msg:' + stc_list.error_msg)
    # 打印结果集
    code_list = []
    while (stc_list.error_code == '0') & stc_list.next():
        # 获取一条记录，将记录合并在一起
        code_list.append(stc_list.get_row_data()[0])
    print(code_list[0:10])
    return code_list


def rd_stock_basic(type='1'):  # 默认 1为股票
    code_list = pd.read_csv("Data/stock_basic.csv")  # 获取所有证券代码信息  encoding="gbk"
    code_list = code_list[code_list['type'].astype(str) == type]
    code_list = code_list['code'].tolist()
    return code_list


def PB_PE_Pcf(code_list, date):
    # 市净率（Price to book ratio 即 PB），指的是每股股价与每股净资产的比率，即 每股股价/每股净资产
    # 市盈率（P/E ratio）也称“股价收益比率”或“市价盈利比率（简称市盈率）”
    # 市现率（PCF），指的是股票价格与每股现金流量的比率，即：每股股价/每股现金流量

    df_PTTM = pd.DataFrame()
    # 获取沪深A股历史K线数据
    for code in code_list:
        # 详细指标参数，参见“历史行情指标参数”章节
        rs = bs.query_history_k_data_plus(code, "date,code,pbMRQ,peTTM,pcfNcfTTM", start_date=date, end_date=date,
                                          frequency="d", adjustflag="3")
        if rs.error_code == '0':
            result = rs.get_data()
            n = result.shape[0]
            if n <= 0:  # 跳过空数据
                continue
            # 删除pbMRQ为0的证券或指数
            if float(result.iloc[0, 3]) != 0:  # 保存市盈率peTTM 不为0的数据
                if df_PTTM.empty:
                    df_PTTM = result
                else:
                    df_PTTM = pd.concat([df_PTTM, result])
    df_PTTM.index = df_PTTM['code']
    stock_info = pd.read_csv("Data/stock_basic.csv", index_col='code')  # 获取所有证券代码信息, encoding="gbk"
    df_PTTM = df_PTTM.join(stock_info)  # 添加证券基本信息
    df_PTTM['peTTM'] = df_PTTM['peTTM'].astype(float)
    df_PTTM = df_PTTM.sort_values(by='peTTM')  # 市盈率排序
    df_PTTM.to_csv("Data\\history_A_stock_k_data_PbPePcf.csv", index=False)  # 结果集输出到csv文件
    # print(df)
    return df_PTTM





if __name__ == '__main__':
    # 登陆系统
    lg = bs.login()

    # 显示登陆返回信息
    print('login respond error_code:' + lg.error_code)
    print('login respond error_msg:' + lg.error_msg)
    code_list = ['sz.300032', 'sz.300033', 'sz.300034', 'sz.300035', 'sz.300036', 'sz.300037']
    start_date = '2019-06-18'
    end_date = '2022-08-17'
    df = PB_PE_Pcf(code_list, end_date)
    df['pbMRQ'] = df['pbMRQ'].astype(float)
    df['peTTM'] = df['peTTM'].astype(float)
    df['pcfNcfTTM'] = df['pcfNcfTTM'].astype(float)

    # 以pbMRQ进行升序排序
    df_sortby = df.sort_values(by='pbMRQ')  # 市净率（Price to book ratio 即 PB），指的是每股股价与每股净资产的比率，即 每股股价/每股净资产
    print("当天A股市场pb最低的证券：" + df_sortby.iloc[0][1])
    # 以peTTM进行升序排序
    df_sortby = df.sort_values(by='peTTM')  # 市盈率（P/E ratio）也称“股价收益比率”或“市价盈利比率（简称市盈率）”
    print("当天A股市场peTTM最低的证券：" + df_sortby.iloc[0][1])
    # 以pbMRQ进行升序排序
    df_sortby = df.sort_values(by='pcfNcfTTM')  # 市现率（PCF），指的是股票价格与每股现金流量的比率，即：每股股价/每股现金流量
    print("当天A股市场pcfNcfTTM最低的证券：" + df_sortby.iloc[0][1])
    # 登出系统
    bs.logout()
    df_PTTM = df
    peTTM_rank = df_PTTM['code_name'].tolist()[:5]
    print(type(peTTM_rank))
    peTTM_rank = '市盈率排名前20\n' + str(peTTM_rank)
    print(peTTM_rank)