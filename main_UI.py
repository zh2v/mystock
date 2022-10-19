from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog
from PyQt5 import uic
from PyQt5.QtCore import Qt
import baostock as bs
import datetime
import BS_function as Bsf
import Avg_EarningRate as Avg_ERt
import PB_PE_Pcf as Pbecf_ttm
import KwithVolume as K_vol
import MACD
import pandas as pd
import threading


class myThread(threading.Thread):
    def __init__(self, BS_UI):
        super(myThread, self).__init__()
        self.BS_UI = BS_UI
        # self.start_date = start_date
        # self.end_date = end_date
        # self.years = years
        # self.stc_type = stc_type

    def run(self):
        print("开始线程：")
        # if self.name == 'macd':
        BS_UI.draw_macd(self.BS_UI)
        # file_info = Avg_ERt.New_Avg_EarningRate(self.start_date, self.end_date, self.years, self.stc_type)

        print("退出线程：")
        # return file_info


class BS_UI:

    def __init__(self):
        # 从文件中加载UI定义
        self.ui = uic.loadUi("UI\Bstock.ui")
        self.ui.updateBtn.clicked.connect(self.stock_update)
        self.ui.Avg_earnR.clicked.connect(self.A_EarningRate)
        self.ui.PB_PE_PcfBtn.clicked.connect(self.get_PB_PE_Pcf)
        self.ui.dirButton.clicked.connect(self.openDir)
        self.ui.end_date.setDate(datetime.date.today())
        self.ui.K_Button.clicked.connect(self.draw_K_macd)
        self.ui.macdBtn.clicked.connect(self.draw_macd)
        self.ui.kdjBtn.clicked.connect(self.draw_kdj)
        self.ui.rsiBtn.clicked.connect(self.draw_rsi)
        self.ui.cciBtn.clicked.connect(self.draw_cci)
        # self.textBrowser = self.ui.textBrowser

    def run_in_thread(self):
        thread_1 = myThread(BS_UI)
        thread_1.start()
        thread_1.join()
        # BS_UI.A_EarningRate()

    def openDir(self):
        dirPath = QFileDialog.getExistingDirectory(caption="选择一个目录", directory='/')
        self.ui.lineDir.setText(dirPath)
        return

    def printf(self, mypstr):  # 输出日志
        self.ui.textBrowser.append(mypstr)
        self.cursor = self.ui.textBrowser.textCursor()
        self.ui.textBrowser.moveCursor(self.cursor.End)
        QApplication.processEvents()

    def progress_run(self, pg_value):  # 进度显示
        pg_value = self.ui.progressBar.value() + pg_value
        if pg_value >= 100:
            pg_value = 100
        self.ui.progressBar.setValue(pg_value)

    def stock_update(self):  # 一键证券清单更新
        bs.login()
        Bsf.get_stock_basic()  # 参数可为空值，获得所有证券信息；结果集输出到csv文件:Data/stock_basic.csv
        bs.logout()
        self.printf("证券清单更新完成！")

    def trade_days(self, start_date, end_date):  # 把自然日区间起止日返回交易日区间起止日
        # bs.login()
        t_day = bs.query_trade_dates(start_date, end_date)
        if t_day.error_code == '0':
            trading_day = t_day.get_data()
        else:
            trading_day = pd.DataFrame()
            print('err: trading days not get!')
        trading_day = trading_day[trading_day['is_trading_day'] == "1"]
        start_date = trading_day.iloc[0]['calendar_date']
        end_date = trading_day.iloc[-1]['calendar_date']
        # bs.logout()
        return start_date, end_date

    def code_list_by(self):  # 根据输入类型选择，获取证券类型代码
        if self.ui.radioButton_stc.isChecked():
            stc_sel = self.ui.radioButton_stc.text()
        elif self.ui.radioButton_inx.isChecked():
            stc_sel = self.ui.radioButton_inx.text()
        elif self.ui.radioButton_ETF.isChecked():
            stc_sel = self.ui.radioButton_ETF.text()
        else:
            stc_sel = self.ui.radioButton_all.text()
        stc_type = stc_sel[0]
        return stc_type

    def A_EarningRate(self):  # 年化平均收益率
        start_date = self.ui.start_date.date().toString(Qt.ISODate)  # 将QDateEdit中date值转为ISO格式
        end_date = self.ui.end_date.date().toString(Qt.ISODate)  # 将QDateEdit中date值转为ISO格式：yyyy-mm-dd
        start_strpt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_strpt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        years = (end_strpt - start_strpt).days/365
        years = round(years, 3)
        bs.login()
        start_date, end_date = self.trade_days(start_date, end_date)
        duration = 'From ' + start_date + ' to ' + end_date
        print(duration)
        self.printf(duration)
        self.printf("时间周期为{}年！".format(years))
        self.printf("处理中......，约 5 Minutes")
        stc_type = self.code_list_by()
        # file_info = myThread('Avg_EarningRate', start_date, end_date, years, stc_type)
        # file_info.start()
        # file_info.join()
        # t2 = threading.Thread(target=Avg_ERt.New_Avg_EarningRate, args=(start_date, end_date, years, stc_type))
        # t2.start()
        file_info = Avg_ERt.New_Avg_EarningRate(start_date, end_date, years, stc_type)
        file_info = "详情信息请见表格文件-{}！".format(file_info)
        bs.logout()
        self.printf("年均收益率排名完成，图表已生成！")
        self.printf(file_info)

    def get_PB_PE_Pcf(self):  # 输出文件"Data\\history_A_stock_k_data_PbPePcf.csv"
        start_date = self.ui.start_date.date().toString(Qt.ISODate)  # 将QDateEdit中date值转为ISO格式
        end_date = self.ui.end_date.date().toString(Qt.ISODate)  # 将QDateEdit中date值转为ISO格式：yyyy-mm-dd
        bs.login()
        start_date, end_date = self.trade_days(start_date, end_date)
        type = self.code_list_by()
        code_list = Pbecf_ttm.rd_stock_basic(type)
        self.printf("处理中......，约 5 Minutes")
        df_PTTM = Pbecf_ttm.PB_PE_Pcf(code_list, end_date)
        self.printf("滚动市净率、市盈率和市现率文件已生成，按市盈率排序！")
        self.printf('文件输出到： Data\history_A_stock_k_data_PbPePcf.csv !')
        df_PTTM = df_PTTM[df_PTTM['peTTM'] > 0]
        peTTM_rank = df_PTTM['code_name'].tolist()[:20]
        pe_rank = '市盈率排名前20名的是：\n'
        for code_name in peTTM_rank:
            pe_rank += code_name
            pe_rank += ', '
        self.printf(pe_rank)
        bs.logout()


    def draw_K_macd(self):  # 输出k线数据图
        code_nm = self.ui.code_input.text()
        bs.login()
        code, name, msg = Bsf.get_code_name(code_nm)  # 获取正确的 code，name
        if msg == '':  # 输出
            start_date = self.ui.start_date.date().toString(Qt.ISODate)  # 将QDateEdit中date值转为ISO格式
            end_date = self.ui.end_date.date().toString(Qt.ISODate)  # 将QDateEdit中date值转为ISO格式：yyyy-mm-dd
            # stk_code = 'sh.601100'
            K_vol.get_k_data(code, start_date, end_date)  # 获取k线数据并保存
            K_vol.draw_k_vol(code, name)  # 绘制k据图with volume
            self.printf('K线输出成功！')
        else:  # msg不为空，说明输入的code_nm 有误
            self.printf(msg)
            QMessageBox.about(self.ui, '输入有误', msg)
        bs.logout()

    def draw_macd(self):  # 输出MACD数据图
        code_nm = self.ui.code_input.text()
        start_date = self.ui.start_date.date().toString(Qt.ISODate)  # 将QDateEdit中date值转为ISO格式
        end_date = self.ui.end_date.date().toString(Qt.ISODate)  # 将QDateEdit中date值转为ISO格式：yyyy-mm-dd
        bs.login()
        code, name, msg = Bsf.get_code_name(code_nm)  # 获取正确的 code，name
        if msg == '':  # 输出
            (msg_buy, msg_sell) = MACD.computeMACD(code, name, start_date, end_date)
            self.printf(name+msg_buy+msg_sell)
        else:  # msg不为空，说明输入的code_nm 有误
            self.printf(msg)
            QMessageBox.about(self.ui, '输入有误', msg)
        bs.logout()

    def draw_kdj(self):  # 输出
        t2 = threading.Thread(target=self.printf('我要计算KDJ in thread！'))
        t2.start()
        self.printf('我要计算KDJ数据，功能下期更新推出！')

    def draw_rsi(self):  # 输出
        self.printf('我要计算RSI数据，功能下期更新推出！')

    def draw_cci(self):  # 输出
        self.printf('我要计算CCI数据，功能下期更新推出！')

    def sample(self):  # 输出
        self.ui.progressBar.reset()
        D_value = self.ui.comboBox.currentText()
        dir = self.ui.lineDir.text()
        self.printf(dir)
        n = 0
        self.ui.progressBar.setValue(5)
        self.progress_run(n)
        self.printf("共有{}个{}{}专业新buffer文件写入成功！".format(n, dir, D_value[:4]))
        QMessageBox.about(self.ui, '提交结果', '已完成数据提取！ \n机型：{} 专业：{}\n'.format(D_value, dir))

    def run_in_thread(self, name):
        if name == 'A_EarningRate':
            self.A_EarningRate()


app = QApplication([])
window = BS_UI()
window.ui.show()
app.exec_()



# class openFile:
#     def __str__(self):
#         filePath, _ = QFileDialog.getOpenFileName(caption='选择一个文件',directory='/',filter='All Files(*.*)')
#         return filePath
#
#
# class openDir:
#     def __str__(self):
#         dirPath = QFileDialog.getExistingDirectory(caption="选择一个目录",directory='/')
#         return dirPath
