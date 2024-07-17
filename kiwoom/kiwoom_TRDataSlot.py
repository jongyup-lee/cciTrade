class TrDataSlot():
    def __init__(self, kiwoomMain) -> None:
        print('[TrDataSlot] __init__')
        self.kiwoomMain = kiwoomMain

    ################################################################################################################
    # ToDo :
    # get_account_info(self): 내 정보 가져오기
    # detail_account_info(self): 예수금 정보 획득
    # detail_account_mystock(self, sPrevNext="0"): # 계좌 평가 잔고 내역 요청
    # not_concluded_account(self, sPrevNext="0"): # 미체결 종목 요청
    # self.gmi
    ################################################################################################################

    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext): #
        '''
        TR 요청에 대한 응답 처리
        sScrNo : 스크린번호
        sRQName : 요청명 - 개발자 마음대로
        sTrCode : 요청 ID TR코드
        sRecordName :  사용안함
        sPrevNext : 다음 페이지가 있는지
        return :
        '''

        if sRQName == "예수금상세현황요청":
            deposit = self.kiwoomMain.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "예수금")
            ok_deposit = self.kiwoomMain.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "출금가능금액")

            ##############################################################
            # 매수 가능 금액 조절 - 몰빵하는 것을 시스템 적으로 조정하는 기능 (차후 조정하면서 매매할 수 있음)
            ##############################################################
            self.kiwoomMain.use_money = int(deposit) * self.kiwoomMain.use_money_persent
            self.kiwoomMain.use_money = self.kiwoomMain.use_money / 4
            ##############################################################

            self.kiwoomMain.detail_account_info_event_loop.exit() # 예수금 상세 현황 요청 이벤트 루트 종료

        elif sRQName == "계좌평가잔고내역요청":
            # 총 매입 금액 / 총 수익률
            total_buy_money = self.kiwoomMain.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "총매입금액")
            total_buy_money_result = int(total_buy_money)

            total_progit_loss_rate = self.kiwoomMain.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "총수익률(%)")
            total_progit_loss_rate_result = float(total_progit_loss_rate)

            # 보유 종목 개수
            rows = self.kiwoomMain.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            cnt = 0
            for i in range(rows):
                code = self.kiwoomMain.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"종목번호")
                code = code.strip()[1:]

                code_nm = self.kiwoomMain.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"종목명")
                stock_quantity = self.kiwoomMain.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"보유수량")
                buy_price = self.kiwoomMain.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"매입가")
                learn_rate = self.kiwoomMain.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"수익률(%)")
                current_price = self.kiwoomMain.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"현재가")
                total_chegual_price = self.kiwoomMain.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"매입금액")
                possible_quantity = self.kiwoomMain.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"매매가능수량")

                if code in self.kiwoomMain.account_stock_dict:
                    pass
                else:
                    self.kiwoomMain.account_stock_dict.update({code:{}})

                code_nm = code_nm.strip()
                stock_quantity = int(stock_quantity.strip())
                buy_price = int(buy_price.strip())
                learn_rate = float(learn_rate.strip())
                current_price = int(current_price.strip())
                total_chegual_price = int(total_chegual_price.strip())
                possible_quantity = int(possible_quantity.strip())

                self.kiwoomMain.account_stock_dict[code].update({"종목명": code_nm})
                self.kiwoomMain.account_stock_dict[code].update({"보유수량": stock_quantity})
                self.kiwoomMain.account_stock_dict[code].update({"매입가": buy_price})
                self.kiwoomMain.account_stock_dict[code].update({"수익률(%)": learn_rate})
                self.kiwoomMain.account_stock_dict[code].update({"현재가": current_price})
                self.kiwoomMain.account_stock_dict[code].update({"매입금액": total_chegual_price})
                self.kiwoomMain.account_stock_dict[code].update({"매매가능수량": possible_quantity})

                cnt += 1
            if sPrevNext == "":
                sPrevNext = "0"

            if sPrevNext == "2":
                self.kiwoomMain.gmi.detail_account_mystock(sPrevNext="2")
            else:
                self.kiwoomMain.detail_account_info_event_loop.exit()


            #self.detail_account_mystock_event_loop.eixt() # 계좌 평가 잔고 내역 요청 이벤트 루트 종료

        elif sRQName == "실시간미체결종목요청":
            rows = self.kiwoomMain.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            for i in range(rows):
                code = self.kiwoomMain.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"종목코드")
                code_nm = self.kiwoomMain.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"종목명")
                order_no = self.kiwoomMain.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"주문번호")
                order_status = self.kiwoomMain.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"주문상태")
                order_quantity = self.kiwoomMain.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"주문수량")
                order_price = self.kiwoomMain.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"주문가격")
                order_gubun = self.kiwoomMain.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"주문구분")
                not_quantity = self.kiwoomMain.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"미체결수량")
                ok_quantity = self.kiwoomMain.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"체결량")

                code = code.strip()
                code_nm = code_nm.strip()
                order_no = int(order_no.strip())
                order_status = order_status.strip()
                order_quantity = int(order_quantity.strip())
                order_price = int(order_price.strip())
                order_gubun = order_gubun.strip().lstrip("+").lstrip("-")
                not_quantity = int(not_quantity.strip())
                ok_quantity = int(ok_quantity.strip())

                if order_no in self.kiwoomMain.not_account_stock_dick:
                    pass
                else:
                    self.kiwoomMain.not_account_stock_dick[order_no] = {}

                nasd = self.kiwoomMain.not_account_stock_dick[order_no]

                nasd.update({"종목코드": code})
                nasd.update({"종목명": code_nm})
                nasd.update({"주문번호": order_no})
                nasd.update({"주문상태": order_status})
                nasd.update({"주문수량": order_quantity})
                nasd.update({"주문가격": order_price})
                nasd.update({"주문구분": order_gubun})
                nasd.update({"미체결수량": not_quantity})
                nasd.update({"체결량": ok_quantity})

                print("[info] 미체결 종목 : %s " % self.kiwoomMain.not_account_stock_dick[order_no])

            self.kiwoomMain.detail_account_info_event_loop.exit()

        elif sRQName == "주식일봉차트조회":
            code = self.kiwoomMain.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0,"종목코드")
            code = code.strip()

            # 해당 종목의 거래일 수 조회
            cnt = self.kiwoomMain.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)

            # 새로운 조건식을 구성하기 위한 요소들
            # 봉수 : cnt

            ########################################################################################################
            # 해당 종목의 모든 거래일 데이터를 받아와서 self.calcul_data에 저장
            ########################################################################################################
            for i in range(cnt):
                data = []
                current_price = self.kiwoomMain.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"현재가")
                value = self.kiwoomMain.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"거래량")
                trading_value = self.kiwoomMain.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"거래대금")
                date = self.kiwoomMain.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"일자")
                start_price = self.kiwoomMain.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"시가")
                high_price = self.kiwoomMain.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"고가")
                low_price = self.kiwoomMain.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"저가")

                data.append("")
                data.append(current_price.strip())
                data.append(value.strip())
                data.append(trading_value.strip())
                data.append(date.strip())
                data.append(start_price.strip())
                data.append(high_price.strip())
                data.append(low_price.strip())
                data.append("")

                self.kiwoomMain.calcul_data.append(data.copy())
                # print("조회한 종목 %s일의 일 데이터(data) 리스트 내용 : %s" % (i, self.calcul_data))
                # ['', '316', '376190', '119', '20190326', '310', '323', '310', '']
                #     현재가 ,  거래량  ,거래대금,    일자   ,  시가,   고가,   저가
                # 0일부터 총 조회 일수까지 루프
            ########################################################################################################
            # 해당 종목의 모든 거래일 데이터를 받아와서 self.calcul_data에 저장 끝
            ########################################################################################################

            if sPrevNext == "2":
                self.kiwoomMain.day_kiwoom_db(code=code, sPrevNext=sPrevNext)
            else: # sPrevNext가 0 또는 Null일 경우 - 조회된 거래일 데이터 수가 600개 미만일 경우
                pass_success = False #120일 이평선을 그릴만큼의 데이터가 있는지 체크

                ########################################################################################################
                # 120일 기준 검색식 - 관심종목/매매대상/본인스타일의 종목 선별 식
                ########################################################################################################
                if self.kiwoomMain.calcul_data == None or len(self.calcul_data) < 120:
                    pass_success = False
                else:
                    #120일 이상 될 경우
                    total_price = 0
                    for value in self.calcul_data[:120]: # 리스트의 첫 번째 요소부터 120번째 요소까지를 포함하는 부분 리스트를 반환
                        total_price += int(value[1])

                    moving_average_price = total_price / 120 # 조회한 당일 기준 120일간의 평균가격 (기준일을 변경하지 않는 한 루프가 끝나는 순간까지 변하지 않음)


                    #오조회 기준일 저가 120일 평균 가격보다 높거나 같고 120일 평균 가격이 당일 고가보다 낮거나 같은지의 여부
                    bottom_price = False
                    check_price = None

                    # 조회 기준일 저가 120일 평균 가격보다 낮거나 같고 120일 평균 가격이 당일 고가보다 낮거나 같음
                    if int(self.kiwoomMain.calcul_data[0][7]) <= moving_average_price and moving_average_price <= int(self.kiwoomMain.calcul_data[0][6]):
                        bottom_price = True
                        check_price = int(self.kiwoomMain.calcul_data[0][6])


                    # 조회한 종목의 모든 거래일에 대한 데이터를 data에 담은 후 해당 종목의
                    # 조회일의 현재가가 120일 이평선보다 밑에 있는지 확인.
                    # 그렇게 확인을 하다가 일봉이 120-일 이평선보다 위에 있으면 계산 진행

                    prev_price = None # 조회한 종목 해당일의 저가
                    if bottom_price == True: # 조회 기준일 저가가 120일 평균 가격보다 낮거나 같고 120일 평균 가격이 당일 고가보다 낮거나 같음
                        print("======================================================================================================")
                        moving_average_price_prev = 0 # 조회한 종목의 조회일 기준 120일 평균 가격 (조회한 당일 이전의 날짜 기준 120일 평균 가격 - 2일전 기준 120평균, 3일전 기준 120 평균, 4일전 120 평균..... )
                        # 루프를 도는 동아 120일 평균 가격은 계속 변함
                        price_top_moving = False # 일 고가가 120일 평균 가격보다 낮거나 같고 조회일 수가 20일 보다 작은지 여부

                        idx = 1
                        while True: # 해당 종목의 당일부터 이전 나날의 120일 평균을 구하고 기준 가격과의 높낮이를 구하여
                            if len(self.kiwoomMain.calcul_data[idx:]) < 120: # 120일치가 있는지 계속 확인
                                break
                            total_price = 0
                            for value in self.kiwoomMain.calcul_data[idx:120+idx]:
                                total_price += int(value[1])
                            moving_average_price_prev = total_price / 120

                            # 조회 당일 고가가 120일 평균 가격보다 작거나 같고 조회일수가 20일 보다 작으면
                            if moving_average_price_prev <= int(self.calcul_data[idx][6]) and idx <= 20:
                                price_top_moving = False
                                break
                            # 조회 당일 저가가 120일 평균 가격 보다 높고 조회일 수가 20일 보다 크면
                            elif int(self.kiwoomMain.calcul_data[idx][7]) > moving_average_price_prev and idx > 20:
                                price_top_moving = True
                                prev_price = int(self.kiwoomMain.calcul_data[idx][7]) # 해당일의 저가
                                break
                            idx += 1

                        # 해당 부분 이평선이 가장 최근 일자의 이평선 가격보다 낮은지 확인
                        if price_top_moving == True:
                            # 120일 평균선이 조회일 기준 120일 평균보다 크고
                            if moving_average_price > moving_average_price_prev and check_price > prev_price:
                                pass_success = True

                #--------------------------------------------------------------------------------------------------------
                # 120일 기준 검색 조건에 부합하는 종목을 텍스트 파일로 저장함
                # 이후 결과물 어떤 방식으로 출력하고 사용할지 고민해야 함
                #--------------------------------------------------------------------------------------------------------
                if pass_success == True:
                    code_nm = self.kiwoomMain.dynamicCall("GetMasterCodeName(QString)", code) # 종목코드 1개의 종목 한글명을 반환한다.

                    f = open("D:/works/AutoTradePJT/python/progrmaGarden/pythonProject/files/condition_stock.txt", "a", encoding="utf8")
                    f.write("%s\t%s\t%s\n" % (code, code_nm, str(self.calcul_data[0][1])))
                    f.close()

                elif pass_success == False:
                    print("조건부 통과 못함")

                self.kiwoomMain.calcul_data.clear()
                self.kiwoomMain.calculator_event_loop.exit()
                ########################################################################################################
                # 120일 기준 검색식 끝
                ########################################################################################################
