import sys
import os
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *
from config.errorCode import *
from config.kiwoomType import *
from kiwoom.kiwoom_ChejanSlot import ChejanSlot
from kiwoom.kiwoom_RealDataSlot import RealDataSlot
from kiwoom.kiwoom_GetMyInfo import GetMyInfo
from kiwoom.kiwoom_SetLogging import Logging
from kiwoom.kiwoom_TRDataSlot import TrDataSlot
from kiwoom.kiwoom_Login import Login
from kiwoom.kiwoom_CondStockList import GetConditionStockList

class Kiwoom(QAxWidget):

    def __init__(self):
        super().__init__()

        self.realType = RealType()
        self.lgn = Login(self)
        self.gmi = GetMyInfo(self)  # myInfo
        self.csl = GetConditionStockList(self)
        self.tds = TrDataSlot(self) # TrDataSlot
        self.rds = RealDataSlot(self)   # RealDataSlot
        self.chs = ChejanSlot(self)     # ChejanSlot
        self.slg = Logging(self)        # Logging 

        ################## 변수 모음 ##################
        self.screen_my_info = "2000"
        self.login_event_loop = None # 이벤트 루프 : 로그인
        
        self.detail_account_info_event_loop = QEventLoop() # 이벤트 루프 : 예수금 상세 정보 요청

        self.calculator_event_loop = QEventLoop()

        self.account_num = None # 보유 계좌번호
        self.use_money = 0
        self.use_money_persent = 0.5
        
        self.screen_calculation_stock = "4000"
        self.screen_real_stock = "5000" # 종목별 할당할 스크린 번호
        self.screen_meme_stock = "6000" # 종목별 할당할 주문용 스크린 번호
        self.screen_start_stop_real = "1000" # 개장, 폐장 여부에 대한 실시간 확인용 스크린 번호

        self.calcul_data = [] #종목별 일봉 데이터 저장 리스트
        self.account_stock_dict = {} # 보유하고 있는 종목 저장 딕셔너리
        self.not_account_stock_dick = {} # 미체결 주문 종목들의 집합
        self.portfolio_stock_dict = {} # 120일선 기준 필터링되어 txt파일에서 불러와 관심종목으로 저장할 딕셔너리
        self.jango_dict = {} # 당일 실시간 계좌 잔고 현황
        ################## 변수 모음 끝 ##################


        ################## 함수 실행 ##################
        self.get_ocx_instance()
        self.event_slots()
        self.real_event_slots()

        self.lgn.signal_login_commConnect() # 로그인
        self.gmi.get_account_info() # 보유 계좌 조회
        self.gmi.detail_account_info() # 계좌에 대한 상세 정보 조회
        self.gmi.detail_account_mystock() # 보유 주식 조회
        self.gmi.not_concluded_account() # 실시간 미체결 종목 조회
        self.csl.getConditionStocks()
        
        '''
        ToDo : 2024/07/14
        이번 순서에 하기 내용을 DB로 바꾸는 과정을 코딩해야 함
        # self.read_code() #  120일선 기준 필터링되어 저장된 txt파일에서 self.portfolio_stock_dict로 종목 이관하는 함수
        '''
        #print("꾸러기조건식의 종목코드들 : %s" % self.conditionStockCodes)
        
        self.screen_number_setting() # 종목별 스크린번호 관리

        # 데이터를 받아와 조건에 맞는 종목을 선정하여 txt 파일로 저장한다. => 관심종목 추가 => 필요에 따라 수행하는 역할
        # self.calculator_fnc() # 주식 시장별 정보 조회

        ################## 함수 실행 끝 ##################


        ################## 장 시작/종료 및 실시간 정보 수집 시그널 ##################

        # 실시간 등록 - SetRealReg 요청에 대한 응답은 OnReceiveRealData
        print("real_event_slots() - 장시작/종료 실시간 요청")
        self.slg.setLogging('info', '장시작/종료 실시간 요청')
        self.dynamicCall("SetRealReg(QString, QString, QString, QString", self.screen_start_stop_real, "", self.realType.REALTYPE['장시작시간']['장운영구분'],"0")

        # 종목 코드 등록
        for code in self.portfolio_stock_dict.keys():
            screen_num = self.portfolio_stock_dict[code]['스크린번호']
            fids = self.realType.REALTYPE['주식체결']['체결시간']

            self.dynamicCall("SetRealReg(QString, QString, QString, QString", screen_num, code, fids, "1")
            print("실시간 등록 코드 : %s, 스크린번호 : %s, fid 번호 : %s" % (code, screen_num, fids))

        ################## 장 시작/종료 및 실시간 정보 수집 시그널 끝 ##################
    
    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")    

    # 이벤트 집합소
    # 서버에 요청 후 리턴 받는 응답을 한 곳에서 받아 처리
    def event_slots(self):
        #로그인 이벤트 응답 / errorCode.py에 코드별 상태값 정리 참고
        self.OnEventConnect.connect(self.login_slot) # 로그인 EventLoop
        #조건 검색식 조회 응답 이벤트
        self.OnReceiveTrCondition.connect(self.csl.condition_slot)
        #로컬 사용자 조건식 저장 성공 여부 응답 이벤트
        self.OnReceiveConditionVer.connect(self.csl.conditionVer_slot)
        #TR 이벤트 응답
        self.OnReceiveTrData.connect(self.tds.trdata_slot)
        # msg 이벤트 응답
        self.OnReceiveMsg.connect(self.msg_slot)

    # 실시간 요청 컨드롤
    def real_event_slots(self):
        # 장시작/종료 실시간 응답 처리
        self.OnReceiveRealData.connect(self.rds.realdata_slot)
        # 주문에 대한 이벤트 등록
        self.OnReceiveChejanData.connect(self.chs.chejan_slot)

    def login_slot(self, errCode):
        print(errors(errCode))

        self.login_event_loop.exit() # 로그인 EventLoop 끝

    # 종목코드 가져오는 함수
    def get_code_list_by_market(self, market_code):
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market_code)
        code_list = code_list.split(";")[:-1]

        return code_list

    def calculator_fnc(self):
        code_list = self.get_code_list_by_market("10")

        for idx, code in enumerate(code_list):
            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock) # self.screen_calculation_stock : 스크린번호
            # DisconnectRealData : 해당하는 스크린 번호에 대한 실시간 데이터 받기를 해제한다.

            self.day_kiwoom_db(code=code)

    def day_kiwoom_db(self, code=None, date=None, sPrevNext="0"):
        QTest.qWait(3600) # 정보 요청을 3.6초 딜레이를 준다

        self.dynamicCall("SetInputValue(QString, QString", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString", "수정주가구분", "1")

        if date != None:
            self.dynamicCall("SetInpuValue(QString, QString)", "기준일자", date)

        self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식일봉차트조회", "opt10081", sPrevNext, self.screen_calculation_stock)
        self.calculator_event_loop.exec_()

    def read_code(self):
        if os.path.exists("files/condition_stock.txt"):
            f = open("files/condition_stock.txt", "r", encoding="utf8")

            lines = f.readlines()
            for line in lines:
                if line != "":
                    ls = line.split("\t")

                    stock_code = ls[0]
                    stock_name = ls[1]
                    stock_price = int(ls[2].split("\n")[0])
                    stock_price = abs(stock_price)

                    self.portfolio_stock_dict.update({stock_code:{"종목명":stock_name, "현재가":stock_price}})
            f.close()

    def screen_number_setting(self):
        # 각 dict에 겹치는 종목을 필터링한다.
        screen_overwrite = []

        #계좌평가잔고내역에 있는 종목들
        for code in self.account_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)

        #미체결에 있는 종목들
        for order_number in self.not_account_stock_dick.keys():
            code = self.not_account_stock_dick[order_number]['종목코드']
            if code not in screen_overwrite:
                screen_overwrite.append(code)

        #포트폴리오에 담겨있는 종목들
        for code in self.portfolio_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)

        #스크린 번호 할당
        cnt = 0
        for code in screen_overwrite:
            temp_screen = int(self.screen_real_stock)
            meme_screen = int(self.screen_meme_stock)

            if (cnt % 50) == 0:
                temp_screen += 1
                self.screen_real_stock = str(temp_screen)

            if (cnt % 50) == 0:
                meme_screen += 1
                self.screen_meme_stock = str(meme_screen)

            if code in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict[code].update({"스크린번호": str(self.screen_real_stock)})
                self.portfolio_stock_dict[code].update({"주문용스크린번호": str(self.screen_meme_stock)})

            elif code not in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict.update({code: {"스크린번호":str(self.screen_real_stock), "주문용스크린번호": str(self.screen_meme_stock)}})

            cnt += 1

    # 송수신 메시지 set
    def msg_slot(self, sScrNo, sRQName, sTrCode, msg):
        print("msg_slot() => 메시지 요청에 대한 응답 / 스크린 : %s, 요청이름 : %s, tr코드 : %s --- %s" % (sScrNo, sRQName, sTrCode, msg))

    # 파일 삭제
    def file_delete(self):
        if os.path.isfile("files/condition_stock.txt"):
            os.remove("files/condition_stock.txt")

