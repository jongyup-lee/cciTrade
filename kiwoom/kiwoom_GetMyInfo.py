
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
        print('[GetMyInfo] get_account_info')
        account_list = self.kiwoomMain.kiwoomOCX.dynamicCall("GetLoginInfo(String)", "ACCNO")

        self.kiwoomMain.account_num = account_list.split(';')[1]
        print('[info] 계좌번호 : %s' % self.kiwoomMain.account_num)

    # 예수금 정보 가져오기
    def detail_account_info(self):
        # SetInputValue 서버 전송전 필요 데이터 입력
        # CommRqData 데이터 요청 실행
        print("detail_account_info() => 예수금 요청")    # 키움 예수금 정보 요청하기 위한 메서드 이름과 사용 방법 : dynamicCall이라는 메서드를 이용하여 호출
        self.kiwoomMain.kiwoomOCX.dynamicCall("SetInputValue(String, String)", "계좌번호", self.kiwoomMain.account_num)
        self.kiwoomMain.kiwoomOCX.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")
        self.kiwoomMain.kiwoomOCX.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00")
        self.kiwoomMain.kiwoomOCX.dynamicCall("SetInputValue(String, String)", "조회구분", "2")
        self.kiwoomMain.kiwoomOCX.dynamicCall("CommRqData(String, String, int, String)", "예수금상세현황요청", "OPW00001", "0", self.kiwoomMain.screen_my_info)

        self.kiwoomMain.detail_account_info_event_loop.exec_()

    # 계좌 평가 잔고 내역 요청
    def detail_account_mystock(self, sPrevNext="0"): 
        print("detail_account_mystock() = > 계좌 평가 잔고 내역 요청")
        self.kiwoomMain.kiwoomOCX.dynamicCall("SetInputValue(String, String)", "계좌번호", self.kiwoomMain.account_num)
        self.kiwoomMain.kiwoomOCX.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")
        self.kiwoomMain.kiwoomOCX.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00")
        self.kiwoomMain.kiwoomOCX.dynamicCall("SetInputValue(String, String)", "조회구분", "2")
        self.kiwoomMain.kiwoomOCX.dynamicCall("CommRqData(String, String, int, String)", "계좌평가잔고내역요청", "OPW00018", sPrevNext, self.kiwoomMain.screen_my_info)

        if sPrevNext == "0" or sPrevNext == "":
            self.kiwoomMain.detail_account_info_event_loop.exec_()

    # 미체결 종목 요청
    def not_concluded_account(self, sPrevNext="0"): 
        print("not_concluded_account() => 실시간미체결종목요청")
        self.kiwoomMain.kiwoomOCX.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.kiwoomMain.account_num)
        self.kiwoomMain.kiwoomOCX.dynamicCall("SetInputValue(QString, QString)", "체결구분", "1")
        self.kiwoomMain.kiwoomOCX.dynamicCall("SetInputValue(QString, QString)", "매매구분", "0")
        self.kiwoomMain.kiwoomOCX.dynamicCall("CommRqData(String, String, int, String)", "실시간미체결종목요청", "opt10075", sPrevNext, self.kiwoomMain.screen_my_info)

        self.kiwoomMain.detail_account_info_event_loop.exec_()
