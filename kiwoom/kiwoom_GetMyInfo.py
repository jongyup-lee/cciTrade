
from PyQt5.QtTest import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *

class GetMyInfo():
    def __init__(self, kiwoomMain) -> None:
        print('[GetMyInfo] __init__')
        self.kiwoomMain = kiwoomMain

        # 스크린 번호
        #self.kiwoomMain.screen_my_info = "2000"
        #self.kiwoomMain.detail_account_info_event_loop = QEventLoop() # 이벤트 루프 : 예수금 상세 정보 요청
    
    # 내 정보 가져오기
    def get_account_info(self):
        account_list = self.kiwoomMain.dynamicCall("GetLoginInfo(String)", "ACCNO")
        self.kiwoomMain.account_num = account_list.split(';')[1]

    # 예수금 정보 가져오기
    def detail_account_info(self):
        # SetInputValue 서버 전송전 필요 데이터 입력
        # CommRqData 데이터 요청 실행
        self.kiwoomMain.dynamicCall("SetInputValue(String, String)", "계좌번호", self.kiwoomMain.account_num)
        self.kiwoomMain.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")
        self.kiwoomMain.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00")
        self.kiwoomMain.dynamicCall("SetInputValue(String, String)", "조회구분", "2")
        self.kiwoomMain.dynamicCall("CommRqData(String, String, int, String)", "예수금상세현황요청", "OPW00001", "0", self.kiwoomMain.screen_my_info)

        self.kiwoomMain.detail_account_info_event_loop.exec_()

    # 계좌 평가 잔고 내역 요청
    def detail_account_mystock(self, sPrevNext="0"): 
        self.kiwoomMain.dynamicCall("SetInputValue(String, String)", "계좌번호", self.kiwoomMain.account_num)
        self.kiwoomMain.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")
        self.kiwoomMain.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00")
        self.kiwoomMain.dynamicCall("SetInputValue(String, String)", "조회구분", "2")
        self.kiwoomMain.dynamicCall("CommRqData(String, String, int, String)", "계좌평가잔고내역요청", "OPW00018", sPrevNext, self.kiwoomMain.screen_my_info)

        if sPrevNext == "0" or sPrevNext == "":
            self.kiwoomMain.detail_account_info_event_loop.exec_()

    # 미체결 종목 요청
    def not_concluded_account(self, sPrevNext="0"): 
        self.kiwoomMain.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.kiwoomMain.account_num)
        self.kiwoomMain.dynamicCall("SetInputValue(QString, QString)", "체결구분", "1")
        self.kiwoomMain.dynamicCall("SetInputValue(QString, QString)", "매매구분", "0")
        self.kiwoomMain.dynamicCall("CommRqData(String, String, int, String)", "실시간미체결종목요청", "opt10075", sPrevNext, self.kiwoomMain.screen_my_info)

        self.kiwoomMain.detail_account_info_event_loop.exec_()
