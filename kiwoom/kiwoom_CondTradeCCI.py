import mysql.connector
import pymysql
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import create_engine

class CCIMonitor:
    def __init__(self, kiwoomMain):
        print('[CCIMonitor] __init__')
        self.kiwoomMain = kiwoomMain

        # SQLAlchemy 엔진 생성
        self.engine = create_engine('mysql+pymysql://root:stocktraderootpwd@stocktrade.c14kwm840um7.us-east-1.rds.amazonaws.com:3306/stocktrade')

    def __del__(self):
        if hasattr(self, 'engine'):
            self.engine.dispose()

    # calculate_cci 메서드는 변경 없음

    def get_stock_data(self, stock_code, days=200):
        print('[CCIMonitor] 3rd : get_stock_data => (%s)' % stock_code)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        query = f"""
        SELECT date, open, high, low, close, volume
        FROM stock_price_data
        WHERE stock_code = '{stock_code}'
          AND date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY date
        """
        df = pd.read_sql(query, self.engine)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df

    def monitor_stock(self, stock_code):
        print('[CCIMonitor] 2nd : monitor_cciSignal_stocks => (%s)' % stock_code)
        df = self.get_stock_data(stock_code, days=200)
        
        if df.empty:
            print(f"No data available for stock code: {stock_code}")
            return False, None, None, None
        else:
            print(df)

        df = df.sort_index()  # 날짜순으로 정렬
        
        # 마지막 거래일 찾기
        last_trading_day = df.index[-1]
        
        # 20일 이동평균 계산
        df['ma_20'] = df['close'].rolling(window=20).mean()
        
        # CCI(50) 계산
        df['cci_50'] = self.calculate_cci(df, period=50)
        
        # 마지막 거래일의 종가, MA20, CCI50 가져오기
        last_close = df.loc[last_trading_day, 'close']
        last_ma_20 = df.loc[last_trading_day, 'ma_20']
        last_cci_50 = df.loc[last_trading_day, 'cci_50']
        
        # nan 체크
        if np.isnan(last_ma_20) or np.isnan(last_cci_50):
            print(f"Warning: Insufficient data for calculations. MA20: {last_ma_20}, CCI50: {last_cci_50}")
            return False, last_close, last_ma_20, last_cci_50

        # CCI(50) 0 상향돌파 확인 (당일에 발생한 경우만)
        cci_crossup = (last_cci_50 > 0) and (df['cci_50'].iloc[-2] <= 0) and (last_trading_day.date() == datetime.now().date())
        # cci_crossup = (last_cci_50 > 0) and (df['cci_50'].iloc[-2] <= 0)
        
        # 조건 확인
        condition_met = (cci_crossup and  # CCI(50) 0 상향돌파 (당일)
                        (last_close > last_ma_20))  # 마지막 종가가 20일 이동평균보다 위에 있음
        
        return condition_met, last_close, last_ma_20, last_cci_50

    def monitor_cciSignal_stocks(self, sCode):
        print(f"Monitoring at {datetime.now()}")
        print('[CCIMonitor] 1st : monitor_cciSignal_stocks => (%s)' % sCode)
        stock_codes = self.kiwoomMain.portfolio_stock_dict
        #stock_codes = stock_codes
        # stock_codes = list(self.kiwoomMain.portfolio_stock_dict.keys())
        
        condition_met, last_close, ma_20, cci_50 = self.monitor_stock(sCode)
        
        if condition_met:
            # print("SIGNAL: CCI(50) crossed above 0 and last close is above 20-day MA")
            return True

        #for code in stock_codes:
        #    print(f"Stock Code: {code}")
        #    #print(f"Last Close: {last_close:.2f}")
        #    #print(f"20-day MA: {ma_20:.2f}")
        #    #print(f"CCI(50): {cci_50:.2f}")
        #    if condition_met:
        #        # print("SIGNAL: CCI(50) crossed above 0 and last close is above 20-day MA")
        #        return True, code
        #    #print("----------------------------------------------------------------------------------------------------")
        #print("\n")