import pymysql
import pandas as pd
import time
from pykiwoom.kiwoom import *
from datetime import datetime, timedelta

class StockDataManager:
    def __init__(self, host, user, password, db):
        print("__init__")
        #self.conn = pymysql.connect(host=host, user=user, password=password, db=db, charset='utf8')
        
        self.conn = pymysql.connect(host='stocktrade.c14kwm840um7.us-east-1.rds.amazonaws.com', 
                               user='root', 
                               password='stocktraderootpwd', 
                               db='stocktrade', 
                               charset='utf8', 
                               port=3306)
        self.cursor = self.conn.cursor()

        #self.cursor = self.conn.cursor()
        self.kiwoom = Kiwoom()
        self.kiwoom.CommConnect(block=True)
        self.sector_cache = {}  # 여기에 sector_cache 속성을 추가합니다
        self.codes = ['000020', '000320', '000720', '000880', '001120', '001390', '001430', '001500', '001540', '001680', '001940', '002100', '002390', '002790', '003090', '003540', '003850', '004000', '004020', '004310', '005010', '007210', '008930', '009070', '009290', '010780', '011280', '011560', '012630', '013030', '013580', '013890', '014530', '016580', '017810', '018250', '018290', '023160', '024720', '024880', '025950', '026150', '026890', '028100', '029960', '030190', '030200', '032300', '033270', '035510', '035600', '035610', '035890', '036530', '038500', '039340', '039570', '041190', '041440', '041920', '042670', '044490', '046440', '049520', '051500', '052260', '053050', '053080', '058850', '060150', '064820', '065510', '066700', '067310', '078520', '078930', '081660', '082920', '083420', '084110', '084690', '086670', '086960', '089600', '090350', '091700', '092460', '092730', '094820', '095660', '099190', '100090', '100840', '108380', '108670', '111770', '114810', '114840', '122990', '123890', '126600', '126730', '131370', '137950', '138490', '144510', '183190', '190510', '195940', '200130', '200670', '210980', '211270', '214370', '216080', '226320', '228670', '234300', '237880', '241560', '241590', '251120', '251970', '267290', '267850', '271980', '282720', '285130', '290550', '293490', '294870', '300720', '317400', '322000', '330350', '344820', '357230', '368770', '375500', '377450', '382480', '383800', '439090', '443670', '453860', '460850', '460860', '472850', '950130', '950140']


    def insert_stock_info(self):
        print("insert_stock_info")
        kospi = self.kiwoom.GetCodeListByMarket('0')
        time.sleep(6)  # API 호출 후 대기
        kosdaq = self.kiwoom.GetCodeListByMarket('10')
        time.sleep(6)  # API 호출 후 대기
        
        for market, codes in [('KOSPI', kospi), ('KOSDAQ', kosdaq)]:
            for code in self.codes:
                name = self.kiwoom.GetMasterCodeName(code)
                # sector 정보를 얻는 다른 방법을 사용
                sector = self.get_sector(code)  # 이 메서드는 아래에 정의됩니다
                listing_date = self.kiwoom.GetMasterListedStockDate(code)
                
                sql = """INSERT INTO stock_info (stock_code, stock_name, market, sector, listing_date) 
                        VALUES (%s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE 
                        stock_name = VALUES(stock_name), 
                        market = VALUES(market), 
                        sector = VALUES(sector), 
                        listing_date = VALUES(listing_date)"""
                self.cursor.execute(sql, (code, name, market, sector, listing_date))
        
        self.conn.commit()

    def get_sector(self, code):
        print("get_sector")
        # OPT10001 (주식기본정보요청)을 사용하여 업종 정보를 얻습니다
        df = self.kiwoom.block_request("opt10001",
                                    종목코드=code,
                                    output="주식기본정보",
                                    next=0)
        if not df.empty and '업종' in df.columns:
            sector = df['업종'].iloc[0]
        else:
            sector = "Unknown"
            
        self.sector_cache[code] = sector
        time.sleep(6)  # API 호출 제한 방지를 위한 대기
        return sector

    def insert_daily_price(self, days=30):
        print("insert_daily_price")
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
        
        codes = self.kiwoom.GetCodeListByMarket('0') + self.kiwoom.GetCodeListByMarket('10')
        time.sleep(6)
        
        for code in self.codes:
            df = self.kiwoom.block_request("opt10081", 
                                           종목코드=code,
                                           기준일자=end_date,
                                           수정주가구분=1,
                                           output="주식일봉차트조회",
                                           next=0)
            time.sleep(6)

            print('[%s] 전일종가 -------------------- %s' %  (code, df['전일종가']))
            '''
            for _, row in df.iterrows():
                sql = """INSERT INTO daily_price (stock_code, date, open, high, low, close, volume)
                         VALUES (%s, %s, %s, %s, %s, %s, %s)
                         ON DUPLICATE KEY UPDATE
                         open = VALUES(open), high = VALUES(high), low = VALUES(low),
                         close = VALUES(close), volume = VALUES(volume)"""
                self.cursor.execute(sql, (code, row['일자'], row['시가'], row['고가'], row['저가'], row['전일종가'], row['거래량']))
            
            self.conn.commit()
            time.sleep(6)
            '''
    def insert_financial_info(self):
        print("insert_financial_info")
        codes = self.kiwoom.GetCodeListByMarket('0') + self.kiwoom.GetCodeListByMarket('10')
        
        for code in self.codes:
            df = self.kiwoom.block_request("opt10001", 종목코드=code, output="주식기본정보", next=0)
            
            if not df.empty:
                row = df.iloc[0]
                sql = """INSERT INTO financial_info 
                         (stock_code, fiscal_year, fiscal_quarter, revenue, operating_profit, net_income, eps, per, pbr, roe)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                         ON DUPLICATE KEY UPDATE
                         revenue = VALUES(revenue), operating_profit = VALUES(operating_profit),
                         net_income = VALUES(net_income), eps = VALUES(eps), per = VALUES(per),
                         pbr = VALUES(pbr), roe = VALUES(roe)"""
                self.cursor.execute(sql, (code, datetime.now().year, (datetime.now().month-1)//3 + 1,
                                          row['매출액'], row['영업이익'], row['당기순이익'],
                                          row['EPS'], row['PER'], row['PBR'], row['ROE']))
            
            self.conn.commit()

    def insert_index_info(self):
        print("insert_index_info")
        indices = [('1001', 'KOSPI'), ('1028', 'KOSPI200'), ('2001', 'KOSDAQ'), ('2203', 'KOSDAQ150')]
        
        for code, name in indices:
            sql = """INSERT INTO index_info (index_code, index_name) 
                     VALUES (%s, %s)
                     ON DUPLICATE KEY UPDATE index_name = VALUES(index_name)"""
            self.cursor.execute(sql, (code, name))
        
        self.conn.commit()

    def insert_index_composition(self):
        print("insert_index_composition")
        indices = [('1001', 'KOSPI'), ('1028', 'KOSPI200'), ('2001', 'KOSDAQ'), ('2203', 'KOSDAQ150')]
        
        for index_code, _ in indices:
            df = self.kiwoom.block_request("opt20011", 시장구분=index_code, output="업종별주가지수", next=0)
            
            for _, row in df.iterrows():
                sql = """INSERT INTO index_composition (index_code, stock_code, weight)
                         VALUES (%s, %s, %s)
                         ON DUPLICATE KEY UPDATE weight = VALUES(weight)"""
                self.cursor.execute(sql, (index_code, row['종목코드'], row['비중']))
            
            self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()

def main():
    manager = StockDataManager(host='127.0.0.1', user='stockrich', password='stockrich', db='stocktrade')
    
    try:
        #manager.insert_stock_info()
        manager.insert_daily_price()
        #manager.insert_financial_info()
        #manager.insert_index_info()
        #manager.insert_index_composition()
    finally:
        manager.close()

if __name__ == "__main__":
    main()