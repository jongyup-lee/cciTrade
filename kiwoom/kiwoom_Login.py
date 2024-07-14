from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *

class Login():
    def __init__(self, kiwoomMain) -> None:
        self.kiwoomMain = kiwoomMain

    def signal_login_commConnect(self):
        self.kiwoomMain.dynamicCall("CommConnect()") # 키움 로그인을 위한 메서드 이름과 사용 방법 : dynamicCall이라는 메서드를 이용하여 호출

        self.kiwoomMain.login_event_loop = QEventLoop() # 로그인 EventLoop 설정
        self.kiwoomMain.login_event_loop.exec_() # 로그인 EventLoop 시작