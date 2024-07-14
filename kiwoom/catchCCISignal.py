import mysql.connector
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

'''
해야 할 일
    -. 키움에서 조건 검색을 만들어야 함
    -. stock_codes 값을 키움의 조건검색에서 검색되는 종목 코드들로 대체해야 함
    -. crossup(cci(50), 0) 신호를 구하는 수식에서 data['close']를 현재가로 수정해야함
    -. monitor_stock에서 last_close를 실시간 가격으로 수정해야 함.
'''

class CCIMonitor:
    def __init__(self):
        db_config = {
            'host': '127.0.0.1',
            'user': 'stockrich',
            'password': 'stockrich',
            'database': 'stocktrade'
        }
        self.conn = mysql.connector.connect(**db_config)

    def __del__(self):
        if self.conn.is_connected():
            self.conn.close()

    def calculate_cci(self, data, period=50):
        typical_price = (data['high'] + data['low'] + data['close']) / 3
        ma = typical_price.rolling(window=period).mean()
        mad = typical_price.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
        cci = (typical_price - ma) / (0.015 * mad)
        return cci

    def get_stock_data(self, stock_code, days=200):
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        query = f"""
        SELECT date, open, high, low, close, volume
        FROM stock_price_data
        WHERE stock_code = '{stock_code}'
          AND date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY date
        """
        df = pd.read_sql(query, self.conn)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df

    def monitor_stock(self, stock_code):
        df = self.get_stock_data(stock_code, days=200)
        
        if df.empty:
            print(f"No data available for stock code: {stock_code}")
            return False, None, None, None

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
        # cci_crossup = (last_cci_50 > 0) and (df['cci_50'].iloc[-2] <= 0) and (last_trading_day.date() == datetime.now().date())
        cci_crossup = (last_cci_50 > 0) and (df['cci_50'].iloc[-2] <= 0)
        
        # 조건 확인
        condition_met = (cci_crossup and  # CCI(50) 0 상향돌파 (당일)
                        (last_close > last_ma_20))  # 마지막 종가가 20일 이동평균보다 위에 있음
        
        return condition_met, last_close, last_ma_20, last_cci_50

    def monitor_cciSignal_stocks(self, stock_codes):
        print(f"Monitoring at {datetime.now()}")
        for code in stock_codes:
            condition_met, last_close, ma_20, cci_50 = self.monitor_stock(code)
            print(f"Stock Code: {code}")
            print(f"Last Close: {last_close:.2f}")
            print(f"20-day MA: {ma_20:.2f}")
            print(f"CCI(50): {cci_50:.2f}")
            if condition_met:
                # print("SIGNAL: CCI(50) crossed above 0 and last close is above 20-day MA")
                return (code)
            print("----------------------------------------------------------------------------------------------------")
        print("\n")

# 사용 예시
'''
if __name__ == "__main__":


    stock_codes = ['000480', '001540', '001810', '001840', '002290', '002800', '003380']

    monitor = CCIMonitor()
    monitor.monitor_stocks(stock_codes)
'''