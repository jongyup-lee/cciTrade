from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *

class GetConditionStockList():
    def __init__(self, kiwoomMain):
        print('[GetConditionStockList] __init__')
        self.kiwoomMain = kiwoomMain

        self.kiwoomMain.condition_event_loop = QEventLoop() # EventLoop 설정
    
    def getConditionStocks(self):
        print('[GetConditionStockList] getConditionStocks()')
        self.kiwoomMain.dynamicCall("GetConditionLoad()")
        self.kiwoomMain.condition_event_loop.exec_() # EventLoop 시작

    def condition_slot(self, scrno, codelist, conditionName, nindex, nnext):
        print('[GetConditionStockList] condition_slot()')
        self.codelist = []
        self.codelist.append(codelist)
        '''
        Date : 2024-07-14        
        ToDo : 
        1. self.kiwoomMain.portfolio_stock_dict.update({order_number: {}})
        포트폴리오에 update해줘야 함
        '''
        for code in self.codelist:
            self.kiwoomMain.portfolio_stock_dict.update({code: {}})

        self.kiwoomMain.condition_event_loop.exit() # EventLoop 끝

    def conditionVer_slot(self, iRet):
        print('[GetConditionStockList] conditionVer_slot() iRet : %s' % iRet)
        condition_list = {'index':[], 'name':[]}
        temprary_condition_list = self.kiwoomMain.dynamicCall("GetConditionNameList()")
        
        # ";"를 기준으로 조건들을 분리합니다.
        condition_list = temprary_condition_list.split(';')
        # 마지막 빈 문자열 제거
        condition_list = [c for c in condition_list if c]
        # 각 조건을 "^"를 기준으로 분리하여 2차원 배열로 만듭니다.
        parsed_conditions = [condition.split('^') for condition in condition_list]        
        # 예를 들어, 첫 번째 조건의 첫 번째와 두 번째 요소를 각각 추출합니다.
        nindex = parsed_conditions[0][0]
        conditionName = parsed_conditions[0][1]

        a = self.kiwoomMain.dynamicCall("SendCondition(QString, QString, int, int)", '0101', str(conditionName), nindex, 0)

        if a == 1:
            print("조건검색 조회 요청 성공")
        elif a != 1:
            print('조건검색 조회 요청 실패')
