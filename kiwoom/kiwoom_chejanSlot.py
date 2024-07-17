

class ChejanSlot():
    def __init__(self, kiwoomMain) -> None:
        print('[ChejanSlot] __init__')
        self.kiwoomMain = kiwoomMain

    def chejan_slot(self, sGubun, nItemCnt, sFidLit):
            print("chejan_slot() => 나의 매매 주문 요청에 대한 응답")
            intGubun = int(sGubun)
            if intGubun == 0:
                print("[info] 주문체결")
                account_num = self.kiwoomMain.dynamicCall("GetChejanData(int)", self.kiwoomMain.realType.REALTYPE['주문체결']['계좌번호'])
                sCode = self.kiwoomMain.dynamicCall("GetChejanData(int)", self.kiwoomMain.realType.REALTYPE['주문체결']['종목코드'])[1:]
                stock_name = self.kiwoomMain.dynamicCall("GetChejanData(int)", self.kiwoomMain.realType.REALTYPE['주문체결']['종목명'])
                stock_name = stock_name.strip()
                origin_number = self.kiwoomMain.dynamicCall("GetChejanData(int)", self.kiwoomMain.realType.REALTYPE['주문체결']['원주문번호'])
                order_number = self.kiwoomMain.dynamicCall("GetChejanData(int)", self.kiwoomMain.realType.REALTYPE['주문체결']['주문번호'])
                order_status = self.kiwoomMain.dynamicCall("GetChejanData(int)", self.kiwoomMain.realType.REALTYPE['주문체결']['주문상태'])
                order_quan = self.kiwoomMain.dynamicCall("GetChejanData(int)", self.kiwoomMain.realType.REALTYPE['주문체결']['주문수량'])
                order_quan = int(order_quan)
                order_price = self.kiwoomMain.dynamicCall("GetChejanData(int)", self.kiwoomMain.realType.REALTYPE['주문체결']['주문가격'])
                order_price = int(order_price)
                not_chegual_qaun = self.kiwoomMain.dynamicCall("GetChejanData(int)", self.kiwoomMain.realType.REALTYPE['주문체결']['미체결수량'])
                not_chegual_qaun = int(not_chegual_qaun)
                order_gubun = self.kiwoomMain.dynamicCall("GetChejanData(int)", self.kiwoomMain.realType.REALTYPE['주문체결']['주문구분'])
                order_gubun = order_gubun.strip().lstrip('+').lstrip('-')
                chegual_time_str = self.kiwoomMain.dynamicCall("GetChejanData(int)", self.kiwoomMain.realType.REALTYPE['주문체결']['주문/체결시간'])
                chegual_price = self.kiwoomMain.dynamicCall("GetChejanData(int)", self.kiwoomMain.realType.REALTYPE['주문체결']['체결가'])
                if chegual_price == '':
                    chegual_price = 0
                else:
                    chegual_price = int(chegual_price)

                chegual_quantity = self.kiwoomMain.dynamicCall("GetChejanData(int)", self.kiwoomMain.realType.REALTYPE['주문체결']['체결량'])
                if chegual_quantity == '':
                    chegual_quantity = 0
                else:
                    chegual_quantity = int(chegual_quantity)

                current_price = self.kiwoomMain.dynamicCall("GetChejanData(int)", self.kiwoomMain.realType.REALTYPE['주문체결']['현재가'])
                current_price = abs(int(current_price))

                first_sell_price = self.kiwoomMain.dynamicCall("GetChejanData(int)", self.kiwoomMain.realType.REALTYPE['주문체결']['(최우선)매도호가'])
                first_sell_price = abs(int(first_sell_price))

                first_buy_price = self.kiwoomMain.dynamicCall("GetChejanData(int)", self.kiwoomMain.realType.REALTYPE['주문체결']['(최우선)매수호가'])
                first_buy_price = abs(int(first_buy_price))

                # 새로 들어온  주문이면 주문번호 할당
                if order_number not in self.kiwoomMain.not_account_stock_dick.keys():
                    self.kiwoomMain.not_account_stock_dick.update({order_number: {}})

                self.kiwoomMain.not_account_stock_dick[order_number].update({"종목코드": sCode})
                self.kiwoomMain.not_account_stock_dick[order_number].update({"주문번호": order_number})
                self.kiwoomMain.not_account_stock_dick[order_number].update({"종목명": stock_name})
                self.kiwoomMain.not_account_stock_dick[order_number].update({"주문상태": order_status})
                self.kiwoomMain.not_account_stock_dick[order_number].update({"주문수량": order_quan})
                self.kiwoomMain.not_account_stock_dick[order_number].update({"주문가격": order_price})
                self.kiwoomMain.not_account_stock_dick[order_number].update({"미체결수량": not_chegual_qaun})
                self.kiwoomMain.not_account_stock_dick[order_number].update({"원주문번호": origin_number})
                self.kiwoomMain.not_account_stock_dick[order_number].update({"주문구분": order_gubun})
                self.kiwoomMain.not_account_stock_dick[order_number].update({"주문/체결시간": chegual_time_str})
                self.kiwoomMain.not_account_stock_dick[order_number].update({"체결가": chegual_price})
                self.kiwoomMain.not_account_stock_dick[order_number].update({"체결량": chegual_quantity})
                self.kiwoomMain.not_account_stock_dick[order_number].update({"현재가": current_price})
                self.kiwoomMain.not_account_stock_dick[order_number].update({"(최우선)매도호가": first_sell_price})
                self.kiwoomMain.not_account_stock_dick[order_number].update({"(최우선)매수호가": first_buy_price})

            elif intGubun == 1:
                print("[info] 잔고")
                account_num = self.kiwoomMain.dynamicCall("GetChejanData(int)", self.kiwoomMain.realType.REALTYPE['잔고']['계좌번호'])
                sCode = self.kiwoomMain.dynamicCall("GetChejanData(int)", self.kiwoomMain.realType.REALTYPE['잔고']['종목코드'])[1:]
                stock_name = self.kiwoomMain.dynamicCall("GetChejanData(int)", self.kiwoomMain.realType.REALTYPE['잔고']['종목명'])
                stock_name = stock_name.strip()
                current_price = self.kiwoomMain.dynamicCall("GetChejanData(int)", self.kiwoomMain.realType.REALTYPE['잔고']['현재가'])
                current_price = abs(int(current_price))
                stock_quan = self.kiwoomMain.dynamicCall("GetChejanData(int)", self.kiwoomMain.realType.REALTYPE['잔고']['보유수량'])
                stock_quan = int(stock_quan)
                like_quan = self.kiwoomMain.dynamicCall("GetChejanData(int)", self.kiwoomMain.realType.REALTYPE['잔고']['주문가능수량'])
                like_quan = int(like_quan)
                buy_price = self.kiwoomMain.dynamicCall("GetChejanData(int)", self.kiwoomMain.realType.REALTYPE['잔고']['매입단가'])
                buy_price = abs(int(buy_price))
                total_buy_price = self.kiwoomMain.dynamicCall("GetChejanData(int)", self.kiwoomMain.realType.REALTYPE['잔고']['총매입가'])
                total_buy_price = int(total_buy_price)
                meme_gubun = self.kiwoomMain.dynamicCall("GetChejanData(int)", self.kiwoomMain.realType.REALTYPE['잔고']['매도매수구분'])
                meme_gubun = self.kiwoomMain.realType.REALTYPE['매도수구분'][meme_gubun]
                first_sell_price = self.kiwoomMain.dynamicCall("GetChejanData(int)", self.kiwoomMain.realType.REALTYPE['잔고']['(최우선)매도호가'])
                first_sell_price = abs(int(first_sell_price))
                first_buy_price = self.kiwoomMain.dynamicCall("GetChejanData(int)", self.kiwoomMain.realType.REALTYPE['잔고']['(최우선)매수호가'])
                first_buy_price = abs(int(first_buy_price))

                if sCode not in self.kiwoomMain.jango_dict.keys():
                    self.kiwoomMain.jango_dict.update({sCode: {}})

                self.kiwoomMain.jango_dict[sCode].update({"현재가": current_price})
                self.kiwoomMain.jango_dict[sCode].update({"종목코드": sCode})
                self.kiwoomMain.jango_dict[sCode].update({"종목명": stock_name})
                self.kiwoomMain.jango_dict[sCode].update({"보유수량": stock_quan})
                self.kiwoomMain.jango_dict[sCode].update({"주문가능수량": like_quan})
                self.kiwoomMain.jango_dict[sCode].update({"매입단가": buy_price})
                self.kiwoomMain.jango_dict[sCode].update({"총매입가": total_buy_price})
                self.kiwoomMain.jango_dict[sCode].update({"매도매수구분": meme_gubun})
                self.kiwoomMain.jango_dict[sCode].update({"(최우선)매도호가": first_sell_price})
                self.kiwoomMain.jango_dict[sCode].update({"(최우선)매수호가": first_buy_price})

                if stock_quan == 0:
                    del self.kiwoomMain.jango_dict[sCode]
                    # 해당 종목에 대해 실시간 데이터 수신 대기 상태 해제
                    self.kiwoomMain.dynamicCall("SetRealRemove(QString, QString)", self.kiwoomMain.portfolio_stock_dict[sCode]['스크린번호'], sCode)