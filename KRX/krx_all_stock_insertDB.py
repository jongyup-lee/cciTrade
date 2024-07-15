import FinanceDataReader as fdr
import pymysql
from datetime import datetime, timedelta
import FinanceDataReader as fdr

# MariaDB 연결 설정
class CCIMonitor():
    def __init__(self):
        # db_config = {
        #     'host': 'stocktrade.c14kwm840um7.us-east-1.rds.amazonaws.com',
        #     'user': 'root',
        #     'password': 'stocktraderootpwd',
        #     'database': 'stocktrade'
        # }

        # 데이터베이스 연결
        # self.conn = mysql.connector.connect(**db_config)
        # self.cursor = self.conn.cursor()

        self.conn = pymysql.connect(host='stocktrade.c14kwm840um7.us-east-1.rds.amazonaws.com', 
                               user='root', 
                               password='stocktraderootpwd', 
                               db='stocktrade', 
                               charset='utf8', 
                               port=3306)
        self.cur = self.conn.cursor()

        # 종목 코드 리스트  # KRX에 상장된 모든 종목 코드 가져오기
        krx = fdr.StockListing('KRX')
        self.stock_codes = krx['Code'].tolist()
        
        # 종목 코드와 종목명 출력
        # for code in self.stock_codes:
        #     print("종목 코드: %s" % code)

    def insertEachData(self):
        print('insertEachData')
        # 데이터 가져올 기간 설정 (예: 최근 1년)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)

        # 각 종목에 대해 데이터 가져오기 및 저장
        for code in self.stock_codes:
            df = fdr.DataReader(code, start_date, end_date)
            
            i = 1
            for index, row in df.iterrows():
                self.cur.execute('''
                INSERT INTO stock_price_data (stock_code, date, open, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (code, index.date(), float(row['Open']), float(row['High']), float(row['Low']), float(row['Close']), float(row['Volume'])))
                print('i = %s' % i)
                i += 1

                # 변경사항 저장 및 연결 종료
                self.conn.commit()
        self.cur.close()
        self.conn.close()

        print("데이터 저장이 완료되었습니다.")

if __name__ == "__main__":
    cm = CCIMonitor()
    cm.insertEachData()
