import sys
from PyQt5.QtTest import *

class RealDataSlot():
    def __init__(self, kiwoomMain) -> None:
        print('[RealDataSlot] __init__')
        self.kiwoomMain = kiwoomMain

    def realdata_slot(self, sCode, sRealType, sRealData):
        print("[RealDataSlot] realdata_slot() => 장시작/종료, 실시간 데이터 요청에 대한 응답 - %s " % sRealType)
        if sRealType == "장시작시간":
            fid = self.realType.REALTYPE[sRealType]['장운영구분']
            value = self.kiwoomMain.dynamicCall("GetCommRealData(QString, int)", sCode, fid)
            print("sRealType :: 장시작시간 - value : %s " % value)

            if value == '0':
                print("[info] 장시작 전")
            elif value == '3':
                print("[info] 장시작")
            elif value == '2':
                print("[info] 장 종료, 동시호가로 넘어감")
            elif value == '4':
                print("[info] 15시 30분 장종료")

                for code in self.portfolio_stock_dict.key():
                    self.kiwoomMain.dynamicCall("SetRealRemove(QString, QString)", self.portfolio_stock_dict[code]['스크린번호'], code)

                QTest.qWait(5000)

                print("[info] 장종료 - 기존 데이터 삭제 및 신규 종목 등록 시작")
                self.file_delete()
                self.calculator_fnc()

                sys.exit()

        elif sRealType == "주식체결":  ##################

            print("sRealType :: 주식체결")
            # 체결시간 => HHMMSS
            a = self.kiwoomMain.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['체결시간'])
            b = self.kiwoomMain.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['현재가'])
            b = abs(int(b))  # abs : 절대값
            c = self.kiwoomMain.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['전일대비'])
            c = abs(int(c))  # abs : 절대값
            d = self.kiwoomMain.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['등락율'])
            d = float(d)
            e = self.kiwoomMain.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['(최우선)매도호가'])
            e = abs(int(e))
            f = self.kiwoomMain.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['(최우선)매수호가'])
            f = abs(int(f))
            g = self.kiwoomMain.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['거래량'])
            g = abs(int(g))
            h = self.kiwoomMain.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['누적거래량'])
            h = abs(int(h))
            i = self.kiwoomMain.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['고가'])
            i = abs(int(i))
            j = self.kiwoomMain.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['시가'])
            j = abs(int(j))
            k = self.kiwoomMain.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['저가'])
            k = abs(int(k))

            if sCode not in self.portfolio_stock_dict:  # 체결된 종목이 나의 관심 종목에 저장되어 있지 않다면
                self.portfolio_stock_dict.update({sCode: {}})  # 추가한다.

            self.portfolio_stock_dict[sCode].update({'체결시간': a})
            self.portfolio_stock_dict[sCode].update({'현재가': b})
            self.portfolio_stock_dict[sCode].update({'전일대비': c})
            self.portfolio_stock_dict[sCode].update({'등락율': d})
            self.portfolio_stock_dict[sCode].update({'(최우선)매도호가': e})
            self.portfolio_stock_dict[sCode].update({'(최우선)매수호가': f})
            self.portfolio_stock_dict[sCode].update({'거래량': g})
            self.portfolio_stock_dict[sCode].update({'누적거래량': h})
            self.portfolio_stock_dict[sCode].update({'고가': i})
            self.portfolio_stock_dict[sCode].update({'시가': j})
            self.portfolio_stock_dict[sCode].update({'저가': k})

            ############################################################################################################
            ### 매매를 위한 조건
            ############################################################################################################
            # 1. 계좌 잔고 평가 내역에 있고 당일 실시간 잔고에 없어야 함  - 61강 2분 15초 이후
            if sCode in self.account_stock_dict.keys() and sCode not in self.jango_dict.keys():
                print("%s %s" % ("[계좌 잔고 평가 내역에 있고 당일 실시간 잔고에 없음] 신규매도를 한다", sCode))

                asd = self.account_stock_dict[sCode]  # #계좌 평가 잔고 내역 리스트

                # 등락률
                meme_rate = (b - asd['매입가']) / asd['매입가'] * 100

                if asd['매매가능수량'] > 0 and (meme_rate > 5 or meme_rate < -5):
                    order_success = self.kiwoomMain.dynamicCall(
                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString",
                        ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                         sCode, asd['매매가능수량'], 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])

                    if order_success == 0:
                        print("[info] 매도 주문 전달 성공")
                        del self.account_stock_dict[sCode]
                    else:
                        print("[info] 매도주문 전달 실패")

            elif sCode in self.jango_dict.keys():
                print("%s %s" % ("[당일 실시간 잔고 계좌에 존재] 신규매도를 한다", sCode))
                jd = self.jango_dict[sCode]
                meme_rate = (b - jd['매입단가']) / jd['매입단가'] * 100

                if jd['주문가능수량'] > 0 and (meme_rate > 5 or meme_rate < -5):
                    order_success = self.kiwoomMain.dynamicCall(
                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString",
                        ['신규매도', self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2, sCode, jd['주문가능수량'],
                         0, self.realType.SENDTYPE['거래구분']['시장가'], ""])

                    if order_success == 0:
                        self.logging.logger.debug("[info] 매도주문 전달 성공")
                    else:
                        self.logging.logger.debug("[info] 매도주문 전달 실패")

            elif d > 2.0 and sCode not in self.jango_dict.keys():
                print("%s %s" % ("[등락율이 2% 상회/실시간 잔고 계좌에 미존재] 신규매수를한다", sCode))
                result = (self.use_money * 0.1) / e
                quantity = int(result)

                order_success = self.kiwoomMain.dynamicCall(
                    "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString",
                    ["신규매수", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1, sCode, quantity,
                     e, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                if order_success == 0:
                    print("[info] 매수주문 전달 성공")
                else:
                    print("[info] 매수주문 전달 실패")

            # 미체결 종목
            # 루프 도중 미체결 리스트의 수량이 변경되어 오류가 발생하는 현상을 방지하기 위해 임의의 변수에 할당하여 루프 실행
            not_meme_list = list(self.not_account_stock_dick)
            for order_num in not_meme_list:
                code = self.not_account_stock_dick[order_num]["종목코드"]
                meme_price = self.not_account_stock_dick[order_num]["주문가격"]
                not_quantity = self.not_account_stock_dick[order_num]["미체결수량"]
                order_gubun = self.not_account_stock_dick[order_num]['주문구분']

                # 매수 취소
                if order_gubun == "신규매수" and not_quantity > 0 and e > meme_price:
                    print("%s %s", ("매수취소한다.", sCode))
                    order_success = self.kiwoomMain.dynamicCall(
                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString",
                        ["매수취소", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 3, code, 0, 0,
                         self.realType.SENDTYPE['거래구분']['지정가'], order_num])

                    if order_success == 0:
                        print("[info] 매수 취소 전달 성공")
                    else:
                        print("[info] 매수 취소 전달 실패")


                elif not_quantity == 0:
                    del self.not_account_stock_dick[order_num]