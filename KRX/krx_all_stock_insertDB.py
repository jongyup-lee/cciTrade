import FinanceDataReader as fdr
import pymysql
from datetime import datetime, timedelta

class CCIMonitor():
    def __init__(self):
        self.conn = pymysql.connect(host='stocktrade.c14kwm840um7.us-east-1.rds.amazonaws.com', 
                               user='root', 
                               password='stocktraderootpwd', 
                               db='stocktrade', 
                               charset='utf8', 
                               port=3306)
        self.cur = self.conn.cursor()

        # 유니크 인덱스 생성 (이미 존재하지 않는 경우에만)
        self.cur.execute('''
        CREATE UNIQUE INDEX IF NOT EXISTS idx_stock_code_date 
        ON stock_price_data (stock_code, date)
        ''')
        self.conn.commit()

        # 종목 코드 리스트
        krx = fdr.StockListing('KRX')
        self.stock_codes = krx['Code'].tolist()
        #self.stock_codes = ['000020', '000320', '000720', '000880', '001120', '001390', '001430', '001500', '001540', '001680', '001940', '002100', '002390', '002790', '003090', '003540', '003850', '004000', '004020', '004310', '005010', '007210', '008930', '009070', '009290', '010780', '011280', '011560', '012630', '013030', '013580', '013890', '014530', '016580', '017810', '018250', '018290', '023160', '024720', '024880', '025950', '026150', '026890', '028100', '029960', '030190', '030200', '032300', '033270', '035510', '035600', '035610', '035890', '036530', '038500', '039340', '039570', '041190', '041440', '041920', '042670', '044490', '046440', '049520', '051500', '052260', '053050', '053080', '058850', '060150', '064820', '065510', '066700', '067310', '078520', '078930', '081660', '082920', '083420', '084110', '084690', '086670', '086960', '089600', '090350', '091700', '092460', '092730', '094820', '095660', '099190', '100090', '100840', '108380', '108670', '111770', '114810', '114840', '122990', '123890', '126600', '126730', '131370', '137950', '138490', '144510', '183190', '190510', '195940', '200130', '200670', '210980', '211270', '214370', '216080', '226320', '228670', '234300', '237880', '241560', '241590', '251120', '251970', '267290', '267850', '271980', '282720', '285130', '290550', '293490', '294870', '300720', '317400', '322000', '330350', '344820', '357230', '368770', '375500', '377450', '382480', '383800', '439090', '443670', '453860', '460850', '460860', '472850', '950130', '950140']

    def insertEachData(self):
        print('insertEachData')
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)

        for code in self.stock_codes:
            df = fdr.DataReader(code, start_date, end_date)
            
            for i, (index, row) in enumerate(df.iterrows(), 1):
                try:
                    self.cur.execute('''
                    INSERT IGNORE INTO stock_price_data 
                    (stock_code, date, open, high, low, close, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ''', (code, index.date(), float(row['Open']), float(row['High']), 
                          float(row['Low']), float(row['Close']), float(row['Volume'])))
                    
                    if self.cur.rowcount > 0:
                        print(f'[{code}] 새로운 데이터 삽입: {index.date()}')
                    else:
                        print(f'[{code}] 기존 데이터 존재: {index.date()}')
                    
                    print(f'[{code}] 진행 상황: {i} / {len(df)}')
                    
                except Exception as e:
                    print(f"오류 발생: {e}")
                    continue

            self.conn.commit()

        self.cur.close()
        self.conn.close()
        print("데이터 저장이 완료되었습니다.")

if __name__ == "__main__":
    cm = CCIMonitor()
    cm.insertEachData()



