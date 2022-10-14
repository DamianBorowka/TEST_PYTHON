from ast import Not
from asyncio.windows_events import NULL
from calendar import calendar
from concurrent.futures import thread
from ctypes.wintypes import PINT
#from curses.ascii import NUL
from distutils.command.clean import clean
from http import client
from pickle import TRUE
import tzlocal
import websocket, json, pprint, talib, numpy, sys
import config
import signal
from binance.client import Client
from binance.enums import *
import time
import copy
import pandas as pd
import os
from datetime import datetime
import math
#import dateutil.tz

import logging
import datetime

ILE_DANYCH_Z_GIELDY = 200  #ILE KLINE MA POBRAĆ ŻEBY LICZYĆ RSI NP

RSI_PERIOD_00 = 13
RSI_PERIOD_01 = 14
RSI_PERIOD_02 = 100
RSI_PERIOD_03 = 10
RSI_PERIOD_04 = 10

RSI_OVERBOUGHT_00 = 73 #5m
RSI_OVERBOUGHT_01 = 73 #15m
RSI_OVERBOUGHT_02 = 51 #15m - 100
RSI_OVERBOUGHT_03 = 70 #1h
RSI_OVERBOUGHT_04 = 70 #4h

RSI_OVERSOLD_00 = 27
RSI_OVERSOLD_01 = 27
RSI_OVERSOLD_02 = 49
RSI_OVERSOLD_03 = 27
RSI_OVERSOLD_04 = 30

WIELKOSC_STANDARDOWEGO_ZAKUPU = 10.5 #USDT
BLOKADA_ZAKUPU_W_MS = 1800000
BLOKADA_ZAKUPU_PO_SELL_W_MS = 86400000
LOAD_COIN_FORM_BINANCE = False

COIN_LIST = ['BATUSDT']
LISTA_COINOW_DOSTEPNYCH_NA_BIANCE = []
LISTA_COINOW_STAN_GT_ZERO = []

timestamp_last_buy = {}
timestamp_last_sell = {}
blokada_handlu = {}
step_size_buy = {}
min_quantity = {}
new_data_5m = {}
new_data_15m = {}
new_data_1h = {}
new_data_4h = {}
closes_5m = {}
closes_15m = {}
closes_1h = {}
closes_4h = {}
first_run_5m = {}
first_run_15m = {}
first_run_1h = {}
first_run_4h = {}
RSI_5m_PERIOD_00 = {}
RSI_15m_PERIOD_01 = {}
RSI_15m_PERIOD_02 = {}
RSI_1h_PERIOD_03 = {}
RSI_1h_PERIOD_03_CONT_5m = {} #LICZONE KONTYNUACYJNIE TZN JEŚLI JEST NIEPEŁNA GODZINA TO OSTATNI ELEMENT TO ZAMKNIĘĘCIE ŚWIECY 5m
RSI_4h_PERIOD_04 = {}
RSI_4h_PERIOD_04_CONT_5m = {} #LICZONE KONTYNUACYJNIE TZN JEŚLI JEST NIEPEŁNA GODZINA TO OSTATNI ELEMENT TO ZAMKNIĘĘCIE ŚWIECY 5m
COIN_IN_GAME_AVERAGE_PRICE = {}
COIN_IN_GAME_AVERAGE_PRICE_CHECK = {}
SOCKED_ADDRESS_5M = {}
SOCKED_ADDRESS_15M = {}
SOCKED_ADDRESS_1H = {}
SOCKED_ADDRESS_4H = {}

def WEBSOCKET_COINUSDT(socket):
    ws = websocket.WebSocketApp(socket, on_open=on_open, on_close=on_close, on_message=on_message)
    ws.run_forever()

def on_open(ws):
    print('opened connection for: ', ws.url)

def on_close(ws):
    print('closed connection for: ', ws.url)

def on_message(ws, message):
    global closes_5m
    global closes_15m
    global new_data_5m
    global new_data_15m
    global RSI_5m_PERIOD_00
    global RSI_15m_PERIOD_01
    global RSI_15m_PERIOD_02
    global RSI_1h_PERIOD_03
    global RSI_1h_PERIOD_03_CONT_5m
    global RSI_4h_PERIOD_04
    global RSI_4h_PERIOD_04_CONT_5m
    global ILE_DANYCH_Z_GIELDY

    cont_closes_1h = {}
    cont_closes_4h = {}

    json_message = json.loads(message) 
    candle = json_message['k']
    start_time = candle['t']
    stop_time = candle['T']
    is_candle_close = candle['x']
    close = candle['c']
    symbol = candle['s']
    interval = candle['i']
    #print(symbol,'   ',close)
    if len(closes_5m[symbol]) == 0:
        empty_list = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_5MINUTE, limit=(ILE_DANYCH_Z_GIELDY+1))
        df_empty_list = pd.DataFrame(empty_list[:-1], columns=['TIME_OPEN','OPEN','HIGH','LOW','CLOSE','VOLUME','TIME_CLOSE','QUOTE','TRADERS','TBB','TBQ','WTF'])
        closes_5m[symbol] = df_empty_list['CLOSE'].tolist()
        closes_5m[symbol] = list(map(float, closes_5m[symbol]))
    
    if len(closes_15m[symbol]) == 0:
        empty_list = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_15MINUTE, limit=(ILE_DANYCH_Z_GIELDY+1))
        df_empty_list = pd.DataFrame(empty_list[:-1], columns=['TIME_OPEN','OPEN','HIGH','LOW','CLOSE','VOLUME','TIME_CLOSE','QUOTE','TRADERS','TBB','TBQ','WTF'])
        closes_15m[symbol] = df_empty_list['CLOSE'].tolist()
        closes_15m[symbol] = list(map(float, closes_15m[symbol]))
        first_run_15m[symbol] = True

    if len(closes_1h[symbol]) == 0:
        empty_list = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1HOUR, limit=(ILE_DANYCH_Z_GIELDY+1))
        df_empty_list = pd.DataFrame(empty_list[:-1], columns=['TIME_OPEN','OPEN','HIGH','LOW','CLOSE','VOLUME','TIME_CLOSE','QUOTE','TRADERS','TBB','TBQ','WTF'])
        closes_1h[symbol] = df_empty_list['CLOSE'].tolist()
        closes_1h[symbol] = list(map(float, closes_1h[symbol]))
        first_run_1h[symbol] = True

    if len(closes_4h[symbol]) == 0:
        empty_list = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_4HOUR, limit=(ILE_DANYCH_Z_GIELDY+1))
        df_empty_list = pd.DataFrame(empty_list[:-1], columns=['TIME_OPEN','OPEN','HIGH','LOW','CLOSE','VOLUME','TIME_CLOSE','QUOTE','TRADERS','TBB','TBQ','WTF'])
        closes_4h[symbol] = df_empty_list['CLOSE'].tolist()
        closes_4h[symbol] = list(map(float, closes_4h[symbol]))
        first_run_4h[symbol] = True

    if len(closes_4h[symbol]) > 0 and len(closes_1h[symbol]) > 0 and len(closes_15m[symbol]) > 0 and len(closes_5m[symbol]) > 0:
        if is_candle_close and interval == '5m':
            closes_5m[symbol].append(float(close))
            if len(closes_5m[symbol]) >= ILE_DANYCH_Z_GIELDY:
                closes_5m[symbol] = closes_5m[symbol][(len(closes_5m[symbol]) - ILE_DANYCH_Z_GIELDY):]
                np_closes = numpy.array(closes_5m[symbol])
                RSI_5m_PERIOD_00[symbol] = talib.RSI(np_closes, RSI_PERIOD_00)
                RSI_5m_PERIOD_00[symbol] = [round(num, 4) for num in RSI_5m_PERIOD_00[symbol]]
                new_data_5m[symbol] = True     
                   

        if (is_candle_close or first_run_15m[symbol]) and interval == '15m':
            if not first_run_15m[symbol]:
                closes_15m[symbol].append(float(close))
            if len(closes_15m[symbol]) >= ILE_DANYCH_Z_GIELDY:
                closes_15m[symbol] = closes_15m[symbol][(len(closes_5m[symbol])-ILE_DANYCH_Z_GIELDY):]
                np_closes = numpy.array(closes_15m[symbol])
                RSI_15m_PERIOD_01[symbol] = talib.RSI(np_closes, RSI_PERIOD_01)
                RSI_15m_PERIOD_02[symbol] = talib.RSI(np_closes, RSI_PERIOD_02)
                RSI_15m_PERIOD_01[symbol] = [round(num, 4) for num in RSI_15m_PERIOD_01[symbol]]        
                RSI_15m_PERIOD_02[symbol] = [round(num, 4) for num in RSI_15m_PERIOD_02[symbol]]
                new_data_15m[symbol] = True
            first_run_15m[symbol] = False

        if (is_candle_close or first_run_1h[symbol]) and interval == '1h':
            if not first_run_1h[symbol]:
                closes_1h[symbol].append(float(close))
            if len(closes_1h[symbol]) >= ILE_DANYCH_Z_GIELDY:
                #print('bez first run k-line: ', closes_1h[symbol])
                closes_1h[symbol] = closes_1h[symbol][(len(closes_1h[symbol]) - ILE_DANYCH_Z_GIELDY):]
                np_closes = numpy.array(closes_1h[symbol])
                RSI_1h_PERIOD_03[symbol] = talib.RSI(np_closes, RSI_PERIOD_03)
                RSI_1h_PERIOD_03[symbol] = [round(num, 4) for num in RSI_1h_PERIOD_03[symbol]]
                new_data_1h[symbol] = True
            first_run_1h[symbol] = False

        if (is_candle_close or first_run_4h[symbol]) and interval == '4h':
            if not first_run_4h[symbol]:
                closes_4h[symbol].append(float(close))
            if len(closes_4h[symbol]) >= ILE_DANYCH_Z_GIELDY:
                closes_4h[symbol] = closes_4h[symbol][(len(closes_4h[symbol]) - ILE_DANYCH_Z_GIELDY):]
                np_closes = numpy.array(closes_4h[symbol])
                RSI_4h_PERIOD_04[symbol] = talib.RSI(np_closes, RSI_PERIOD_04)
                RSI_4h_PERIOD_04[symbol] = [round(num, 4) for num in RSI_4h_PERIOD_04[symbol]]
                new_data_4h[symbol] = True
            first_run_4h[symbol] = False

        if interval =='5m':
            #wyliczenie kontynuacyjnego RSI        
            if (len(closes_1h[symbol]) >= ILE_DANYCH_Z_GIELDY) and new_data_5m[symbol]:
                #cont_closes_1h = copy.deepcopy(closes_1h)
                #cont_closes_1h[symbol].append(closes_5m[symbol][-1])
                cont_closes_1h[symbol] = closes_1h[symbol][:]
                cont_closes_1h[symbol].append(closes_5m[symbol][-1])
                cont_np_closes = numpy.array(cont_closes_1h[symbol])        
                RSI_1h_PERIOD_03_CONT_5m[symbol] = talib.RSI(cont_np_closes, RSI_PERIOD_03)
                RSI_1h_PERIOD_03_CONT_5m[symbol] = [round(num, 4) for num in RSI_1h_PERIOD_03_CONT_5m[symbol]]

            if (len(closes_4h[symbol]) >= ILE_DANYCH_Z_GIELDY) and new_data_5m[symbol]:
                #cont_closes_4h = copy.deepcopy(closes_4h)
                #cont_closes_4h[symbol].append(closes_5m[symbol][-1])
                cont_closes_4h[symbol] = closes_4h[symbol][:]
                cont_closes_4h[symbol].append(closes_5m[symbol][-1])
                cont_np_closes = numpy.array(cont_closes_4h[symbol])        
                RSI_4h_PERIOD_04_CONT_5m[symbol] = talib.RSI(cont_np_closes, RSI_PERIOD_04)
                RSI_4h_PERIOD_04_CONT_5m[symbol] = [round(num, 4) for num in RSI_4h_PERIOD_04_CONT_5m[symbol]]
        #delta = numpy.trunc(abs(current_timestamp()-stop_time)/1000)
        #if delta >= 31:
        #    delta = numpy.trunc(abs(current_timestamp()-stop_time)/1000)
        #    print('sleep for: ',symbol, ' interval: ', interval, 'time:', delta)
        #    time.sleep(delta-30)
        #    print('wake up for:', symbol, ' interval: ', interval)

def srednia_cena_zakupu(symbol):
    global LISTA_COINOW_DOSTEPNYCH_NA_BIANCE
    global LISTA_COINOW_STAN_GT_ZERO

    lista_wydatkow = []
    lista_zakupow = []
    tabela = []
    #print('ŚREDNIA CENA ZAKUPU')
    for index in range(50):
        try:
            tabela_01 = client.get_all_orders(symbol=symbol, limit = 2000)
            tabela = pd.DataFrame(tabela_01)
            break
        except Exception as e:
            time.sleep(0.3)
            continue        
    
    print(tabela)
    current_balance_coin = 3
    #print('ILOŚĆ COINÓW ',symbol,' NA GIEŁDZIE: ', LISTA_COINOW_STAN_GT_ZERO[symbol])
    ilosc_kupionych = 0
    koszt_kupionych = 0
    t_buy = False
    t_sell = False
    #print('REV ORDER')
    wymiar_tablicy_y = tabela.shape[0]
    #print(wymiar_tablicy_y)
    if wymiar_tablicy_y > 0:
        for licznik in range(wymiar_tablicy_y-1,-1,-1):
            vol_from_tabela = float(tabela.at[licznik,'executedQty'])
            #print(vol_from_tabela)
            side_from_tabela = tabela.at[licznik,'side']
            status = tabela.at[licznik,'status']
            cost_from_tabela = float(tabela.at[licznik,'cummulativeQuoteQty'])
            time_from_list = int(tabela.at[licznik,'time'])
            #print(side_from_tabela, ' ', vol_from_tabela, ' ', cost_from_tabela)
            if status == 'FILLED':
                if side_from_tabela == 'BUY':
                    print('BUY', vol_from_tabela)                
                    ilosc_kupionych = round(ilosc_kupionych + vol_from_tabela,6)     
                    lista_zakupow.append(vol_from_tabela)
                    lista_wydatkow.append(cost_from_tabela)
                    if not t_buy:
                        timestamp_last_buy[symbol] = time_from_list
                        t_buy = True
                elif side_from_tabela == 'SELL':
                    print('SELL', vol_from_tabela) 
                    ilosc_kupionych = ilosc_kupionych - vol_from_tabela
                    lista_zakupow.append(-vol_from_tabela)
                    lista_wydatkow.append(-cost_from_tabela)
                    if not t_sell:
                        timestamp_last_sell[symbol] = time_from_list
                        t_sell = True
                #ilosc_kupionych = sum(lista_zakupow[:])
                #print(LISTA_COINOW_STAN_GT_ZERO[symbol])
                #print(lista_zakupow)
                #print(lista_wydatkow)
                if LISTA_COINOW_STAN_GT_ZERO[symbol] == ilosc_kupionych:#sum(lista_wydatkow[:])) <= 0:
                    #print('Lista wydatkow: ', lista_wydatkow)
                    #print('Lista zakupow: ',lista_zakupow)  
                    #print('Średnia cena zakupu  SUM:', sum(lista_wydatkow[:])/sum(lista_zakupow[:]))
                    #print('Średnia cena zakupu MATH:', ilosc_kupionych/LISTA_COINOW_STAN_GT_ZERO[symbol])
                    return float(sum(lista_wydatkow[:])/sum(lista_zakupow[:]))
                    break      
                #print('2Lista wydatkow: ', lista_wydatkow)
                #print('2Lista zakupow: ',lista_zakupow)   
    else:
        return float(0)

def zaladuj_coiny_z_binance():
    global LISTA_COINOW_DOSTEPNYCH_NA_BIANCE
    global LISTA_COINOW_STAN_GT_ZERO
    
    for index in range(5):
        try:
            info = client.get_account()
            #print('załaduj coiny z binance')
            #print(info)
            LISTA_COINOW_DOSTEPNYCH_NA_BIANCE = pd.DataFrame(info['balances'])
            LISTA_COINOW_DOSTEPNYCH_NA_BIANCE['asset'] = LISTA_COINOW_DOSTEPNYCH_NA_BIANCE['asset'].astype(str) + 'USDT'
            LISTA_COINOW_DOSTEPNYCH_NA_BIANCE = pd.DataFrame({'asset':LISTA_COINOW_DOSTEPNYCH_NA_BIANCE['asset'], 'free':LISTA_COINOW_DOSTEPNYCH_NA_BIANCE['free']})
            dictt = LISTA_COINOW_DOSTEPNYCH_NA_BIANCE
            #with open('plik_01_python.txt', 'w') as f:
            #    f.write(LISTA_COINOW_DOSTEPNYCH_NA_BIANCE.to_string())
            for index, row in dictt.iterrows():
                if float(row['free']) < 0.00000001:
                    dictt.drop(index, inplace=True)
            LISTA_COINOW_STAN_GT_ZERO = dict(zip(dictt['asset'],dictt['free']))
            for index, vol in LISTA_COINOW_STAN_GT_ZERO.items():
                LISTA_COINOW_STAN_GT_ZERO[index] = float(vol)
            #print(LISTA_COINOW_DOSTEPNYCH_NA_BIANCE)
            for index in COIN_LIST:
                info = client.get_symbol_info(index)
                min_quantity[index] = float(info['filters'][2]['minQty'])
                step_size_buy[index] = float(info['filters'][2]['stepSize'])
            break
        except Exception as e:
            time.sleep(0.3)
            continue
    #print('min:', min_quantity)
    #print('step:',step_size_buy)

def order(side, quantity, symbol):    
    zwrotka = False
    for liczba in range(5):
        try:
            order_1 = client.create_order(symbol=symbol, side=side, type=ORDER_TYPE_MARKET, quantity=quantity)
            if order_1:
                print('Wysłano zlecenie ', symbol,' planowana liczba kupionych/sprzedanych tokenów to: ', quantity)
                #print(order_1)
                zwrotka = True
                break
            #else:
            #    break
        except Exception as e:
            #print("an exception occured - {}".format(e))
            time.sleep(0.3)
            continue
    if zwrotka:
        zwrotka = False
        for liczba in range(6):
            try:
                order_completed =  client.get_order(symbol, orderId= order_1['orderId'])
                if order_completed['status'] == 'FILLED':
                    zwrotka = True
                #    break
            except Exception as e:
                time.sleep(0.5)
                continue
    return zwrotka

def buy_coin(symbol):
    global BLOKADA_ZAKUPU_W_MS
    buy_quatity = round(round((WIELKOSC_STANDARDOWEGO_ZAKUPU/closes_5m[symbol][-1])/step_size_buy[symbol])*step_size_buy[symbol],8)
    if buy_quatity < min_quantity[symbol]:
        buy_quatity = min_quantity[symbol]
    current_time = datetime.datetime.today()
    return_01 = False
    #print(abs(current_timestamp()))
    #print(timestamp_last_buy[symbol])
    #print((abs(current_timestamp() - timestamp_last_buy[symbol])))






    #PO SPRZEDAZY DAC BLOKADE ZAKUPU NA 1D!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ale tylko po całkowitej sprzedaży bo urzytkownik mógł cześciowo się pozbyć np przez ręczne sprzedanie
    #delta_time_buy = abs(current_timestamp() - timestamp_last_buy[symbol])
    delta_time_sell = abs(current_timestamp() - timestamp_last_sell[symbol])




    if ((abs(current_timestamp() - timestamp_last_buy[symbol]) >= BLOKADA_ZAKUPU_W_MS) or timestamp_last_buy[symbol] == 0) and ((delta_time_sell >= 86400000) or (timestamp_last_sell[symbol] == 0)): # and delta_time 
        if (closes_5m[symbol][-1]  <= (COIN_IN_GAME_AVERAGE_PRICE[symbol]-(COIN_IN_GAME_AVERAGE_PRICE[symbol]*0.05))):
            print(current_time,'TRY: BUY UNDER 5% BUY... BUY... BUY... : ',symbol,' CENA: ',closes_5m[symbol][-1],'RSI:',format(RSI_5m_PERIOD_00[symbol][-1], '.4f'),' ',format(RSI_15m_PERIOD_01[symbol][-1], '.4f'),' ',format(RSI_15m_PERIOD_02[symbol][-1], '.4f'),' H1',format(RSI_1h_PERIOD_03[symbol][-1], '.4f'),' ',format(RSI_1h_PERIOD_03_CONT_5m[symbol][-1], '.4f'),' H4',format(RSI_4h_PERIOD_04[symbol][-1], '.4f'),' ',format(RSI_4h_PERIOD_04_CONT_5m[symbol][-1], '.4f'), 'USDT:', format(LISTA_COINOW_STAN_GT_ZERO['USDTUSDT'], '.4f'))
            try:
                order(SIDE_BUY, buy_quatity , symbol)
            except Exception as e:
                return_01 = False
            return_01 = True
        else:
            print(current_time,' TRY: NORMAL BUY... BUY... BUY... : ',symbol,' CENA: ',closes_5m[symbol][-1],'RSI:',format(RSI_5m_PERIOD_00[symbol][-1], '.4f'),' ',format(RSI_15m_PERIOD_01[symbol][-1], '.4f'),' ',format(RSI_15m_PERIOD_02[symbol][-1], '.4f'),' H1',format(RSI_1h_PERIOD_03[symbol][-1], '.4f'),' ',format(RSI_1h_PERIOD_03_CONT_5m[symbol][-1], '.4f'),' H4',format(RSI_4h_PERIOD_04[symbol][-1], '.4f'),' ',format(RSI_4h_PERIOD_04_CONT_5m[symbol][-1], '.4f'), 'USDT:', format(LISTA_COINOW_STAN_GT_ZERO['USDTUSDT'], '.4f'))
            try:
                order(SIDE_BUY, buy_quatity, symbol)
            except Exception as e:
                return_01 = False
            return_01 = True
    #else:
        #print('else')
    return return_01


def sell_coin(symbol):
    current_time = datetime.datetime.today()
    print(current_time,'TRY SELL: ',symbol,' CENA: ',closes_5m[symbol][-1],'RSI:',format(RSI_5m_PERIOD_00[symbol][-1], '.4f'),' ',format(RSI_15m_PERIOD_01[symbol][-1], '.4f'),' ',format(RSI_15m_PERIOD_02[symbol][-1], '.4f'),' H1',format(RSI_1h_PERIOD_03[symbol][-1], '.4f'),' ',format(RSI_1h_PERIOD_03_CONT_5m[symbol][-1], '.4f'),' H4',format(RSI_4h_PERIOD_04[symbol][-1], '.4f'),' ',format(RSI_4h_PERIOD_04_CONT_5m[symbol][-1], '.4f'), 'USDT:', format(LISTA_COINOW_STAN_GT_ZERO['USDTUSDT'], '.4f'))
    try:
        order(SIDE_SELL, LISTA_COINOW_STAN_GT_ZERO[symbol] , symbol)
    except Exception as e:
        return False
    return True

def get_balance_coin(symbol):
    balance = client.get_asset_balance(asset=str(symbol[:-4]))
    return float(balance['free'])

def suma_obliczen():
    global new_data_5m
    global new_data_15m
    global RSI_5m_PERIOD_00
    global RSI_15m_PERIOD_01
    global RSI_15m_PERIOD_02
    global RSI_1h_PERIOD_03
    global RSI_1h_PERIOD_03_CONT_5m
    global RSI_4h_PERIOD_04
    global RSI_4h_PERIOD_04_CONT_5m
    global LOAD_COIN_FORM_BINANCE

    while True:
        first_check_usdt = True
        for num_coin in COIN_LIST: #and (COIN_IN_GAME_AVERAGE_PRICE[num_coin]) > 0
            if new_data_5m[num_coin] and len(RSI_5m_PERIOD_00[num_coin]) > 0 and len(RSI_15m_PERIOD_01[num_coin]) > 0 and len(RSI_15m_PERIOD_02[num_coin]) > 0 and len(RSI_1h_PERIOD_03[num_coin]) > 0 and len(RSI_1h_PERIOD_03_CONT_5m[num_coin]) > 0 and len(RSI_4h_PERIOD_04[num_coin]) > 0 and len(RSI_4h_PERIOD_04_CONT_5m[num_coin]) > 0:
                LOAD_COIN_FORM_BINANCE = True
                current_time = datetime.datetime.now()
                #if ((COIN_IN_GAME_AVERAGE_PRICE[num_coin] == 0) or (closes_5m[num_coin][-1] < (COIN_IN_GAME_AVERAGE_PRICE[num_coin]))) and LISTA_COINOW_STAN_GT_ZERO['USDTUSDT'] > (WIELKOSC_STANDARDOWEGO_ZAKUPU+1) and (RSI_5m_PERIOD_00[num_coin][-1] <= RSI_OVERSOLD_00) and (RSI_15m_PERIOD_01[num_coin][-1] <= RSI_OVERSOLD_01) and (RSI_15m_PERIOD_02[num_coin][-1] <= RSI_OVERSOLD_02):
                if ((COIN_IN_GAME_AVERAGE_PRICE[num_coin] == 0) or (closes_5m[num_coin][-1] < (COIN_IN_GAME_AVERAGE_PRICE[num_coin]))) and LISTA_COINOW_STAN_GT_ZERO['USDTUSDT'] >= (WIELKOSC_STANDARDOWEGO_ZAKUPU+1) and (RSI_5m_PERIOD_00[num_coin][-1] <= RSI_OVERSOLD_00) and (RSI_15m_PERIOD_01[num_coin][-1] <= RSI_OVERSOLD_01) and (RSI_1h_PERIOD_03_CONT_5m[num_coin][-1] <= RSI_OVERSOLD_03) and (RSI_4h_PERIOD_04_CONT_5m[num_coin][-1] <= RSI_OVERSOLD_04):
                    buy_order = buy_coin(num_coin)
                    if buy_order:
                        LISTA_COINOW_STAN_GT_ZERO[num_coin] = get_balance_coin(num_coin)
                        LISTA_COINOW_STAN_GT_ZERO['USDTUSDT'] = get_balance_coin('USDTUSDT')
                        COIN_IN_GAME_AVERAGE_PRICE[num_coin] = srednia_cena_zakupu(num_coin)   
                        print('ORDER COMPLETE!!!')     
                        new_data_15m[num_coin] = False
                        new_data_5m[num_coin] = False
                #elif COIN_IN_GAME_AVERAGE_PRICE[num_coin] > 0 and (closes_5m[num_coin][-1] > (1.02*COIN_IN_GAME_AVERAGE_PRICE[num_coin])) and (RSI_5m_PERIOD_00[num_coin][-1] >= RSI_OVERBOUGHT_00) and (RSI_15m_PERIOD_01[num_coin][-1] >= RSI_OVERBOUGHT_01) and (RSI_15m_PERIOD_02[num_coin][-1] >= RSI_OVERBOUGHT_02):
                elif COIN_IN_GAME_AVERAGE_PRICE[num_coin] > 0 and (closes_5m[num_coin][-1] >= (1.02*COIN_IN_GAME_AVERAGE_PRICE[num_coin])) and (RSI_15m_PERIOD_01[num_coin][-1] >= RSI_OVERBOUGHT_01) and (RSI_1h_PERIOD_03_CONT_5m[num_coin][-1] >= RSI_OVERBOUGHT_03) and (RSI_4h_PERIOD_04_CONT_5m[num_coin][-1] >= RSI_OVERBOUGHT_04):
                    sell_order = sell_coin(num_coin)
                    if sell_order:
                        LISTA_COINOW_STAN_GT_ZERO[num_coin] = get_balance_coin(num_coin)
                        LISTA_COINOW_STAN_GT_ZERO['USDTUSDT'] = get_balance_coin('USDTUSDT')
                        if LISTA_COINOW_STAN_GT_ZERO[num_coin] > 0:
                            COIN_IN_GAME_AVERAGE_PRICE[num_coin] = srednia_cena_zakupu(num_coin)
                        else:
                            COIN_IN_GAME_AVERAGE_PRICE[num_coin] = 0
                        print('ORDER COMPLETE!!!')
                        new_data_15m[num_coin] = False
                        new_data_5m[num_coin] = False 
#                else:                    
                if first_check_usdt:
                    usdt_ballance = False
                    for liczba in range(5):
                        try:
                            ballance = get_balance_coin('USDTUSDT')
                            if ballance != LISTA_COINOW_STAN_GT_ZERO['USDTUSDT']:
                                LISTA_COINOW_STAN_GT_ZERO['USDTUSDT'] = ballance
                                usdt_ballance = True
                            elif ballance == LISTA_COINOW_STAN_GT_ZERO['USDTUSDT']:
                                usdt_ballance = True
                                break
                        except Exception as e:
                            time.sleep(0.1)
                            continue
                    if not usdt_ballance and first_check_usdt:
                        print('Nie udało się pobrać nowego balansu USDT')
                    first_check_usdt = False #format(value, '.6f')
                print(current_time,' ',num_coin,' AKT PRICE: ',format(closes_5m[num_coin][-1], '.4f'), ' AVG BUY PRICE:', format(round(COIN_IN_GAME_AVERAGE_PRICE[num_coin],4), '.4f'),'RSI:',format(RSI_5m_PERIOD_00[num_coin][-1], '.4f'),' ',format(RSI_15m_PERIOD_01[num_coin][-1], '.4f'),' ',format(RSI_15m_PERIOD_02[num_coin][-1], '.4f'),' H1',format(RSI_1h_PERIOD_03[num_coin][-1], '.4f'),' ',format(RSI_1h_PERIOD_03_CONT_5m[num_coin][-1], '.4f'),' H4',format(RSI_4h_PERIOD_04[num_coin][-1], '.4f'),' ',format(RSI_4h_PERIOD_04_CONT_5m[num_coin][-1], '.4f'), 'USDT:', format(LISTA_COINOW_STAN_GT_ZERO['USDTUSDT'], '.4f'))
                new_data_15m[num_coin] = False
                new_data_5m[num_coin] = False    
                new_data_1h[num_coin] = False
                new_data_4h[num_coin] = False        
        time.sleep(0.001)

def current_timestamp():
    now = datetime.datetime.today()
    return int(time.mktime(now.timetuple())*1000)

def sprawdz_coiny_binance(): #wywala błąd bo w momencie jak zaczytuje zmienne to inny wątek z nich korzysta
    global LOAD_COIN_FORM_BINANCE
    while True:
        if LOAD_COIN_FORM_BINANCE:
            time.sleep(240)
            zaladuj_coiny_z_binance()
            for coin_index in COIN_LIST:
                if coin_index in LISTA_COINOW_STAN_GT_ZERO:
                    if LISTA_COINOW_STAN_GT_ZERO[coin_index]:
                        COIN_IN_GAME_AVERAGE_PRICE[coin_index] = srednia_cena_zakupu(coin_index)
                    else:
                        COIN_IN_GAME_AVERAGE_PRICE[coin_index] = float(0)
                else:
                    COIN_IN_GAME_AVERAGE_PRICE[coin_index] = float(0)
            LOAD_COIN_FORM_BINANCE = False
        time.sleep(1)


if __name__ == '__main__':
    import threading
    #os.system('cls')    

    COIN_IN_GAME_AVERAGE_PRICE_CHECK['BNBUSDT'] = 0
    for add_coin in COIN_LIST:
        timestamp_last_buy[add_coin] = 0
        timestamp_last_sell[add_coin] = 0
        blokada_handlu[add_coin] = 0
        step_size_buy[add_coin] = 0
        min_quantity[add_coin] = 0
        new_data_5m[add_coin] = False
        new_data_15m[add_coin] = False
        new_data_1h[add_coin] = False
        new_data_4h[add_coin] = False
        closes_5m[add_coin] = []
        closes_15m[add_coin] = []
        closes_1h[add_coin] = []
        closes_4h[add_coin] = []
        first_run_5m[add_coin] = False
        first_run_15m[add_coin] = False
        first_run_1h[add_coin] = False
        first_run_4h[add_coin] = False
        RSI_5m_PERIOD_00[add_coin] = []
        RSI_15m_PERIOD_01[add_coin] = []
        RSI_15m_PERIOD_02[add_coin] = []
        RSI_1h_PERIOD_03[add_coin] = []
        RSI_1h_PERIOD_03_CONT_5m[add_coin] = []
        RSI_4h_PERIOD_04[add_coin] = []
        RSI_4h_PERIOD_04_CONT_5m[add_coin] = []
        COIN_IN_GAME_AVERAGE_PRICE[add_coin] = 0
        COIN_IN_GAME_AVERAGE_PRICE_CHECK[add_coin] = 0
        SOCKED_ADDRESS_5M[add_coin] = "wss://stream.binance.com:9443/ws/"+ add_coin.lower() +"@kline_5m"
        SOCKED_ADDRESS_15M[add_coin] = "wss://stream.binance.com:9443/ws/"+ add_coin.lower() +"@kline_15m"
        SOCKED_ADDRESS_1H[add_coin] = "wss://stream.binance.com:9443/ws/"+ add_coin.lower() +"@kline_1h"
        SOCKED_ADDRESS_4H[add_coin] = "wss://stream.binance.com:9443/ws/"+ add_coin.lower() +"@kline_4h"

    polaczono = False
    while not polaczono:
        try:
            print('Proba polaczenia')
            client = Client(config.API_KEY, config.API_SECRET)
            polaczono = True
        except Exception as e:
            time.sleep(1)
            polaczono = False
    print('Polaczono :)')
    zaladuj_coiny_z_binance()
  
    for coin_index in COIN_LIST:
        COIN_IN_GAME_AVERAGE_PRICE[coin_index] = float(0)

    for coin_index in COIN_LIST:
        if coin_index in LISTA_COINOW_STAN_GT_ZERO:
            if LISTA_COINOW_STAN_GT_ZERO[coin_index]:
                COIN_IN_GAME_AVERAGE_PRICE[coin_index] = srednia_cena_zakupu(coin_index)
                
            else:
                COIN_IN_GAME_AVERAGE_PRICE[coin_index] = float(0)

    print(LISTA_COINOW_STAN_GT_ZERO)
    print(COIN_IN_GAME_AVERAGE_PRICE)

    for thread_index in COIN_LIST:
        for liczba in range(5):
            try:
                empty_list = client.get_klines(symbol=thread_index, interval=Client.KLINE_INTERVAL_5MINUTE, limit=(ILE_DANYCH_Z_GIELDY+1))
                if empty_list:
                    df_empty_list = pd.DataFrame(empty_list[:-1], columns=['TIME_OPEN','OPEN','HIGH','LOW','CLOSE','VOLUME','TIME_CLOSE','QUOTE','TRADERS','TBB','TBQ','WTF'])
                    closes_5m[thread_index] = df_empty_list['CLOSE'].tolist()
                    closes_5m[thread_index] = list(map(float, closes_5m[thread_index]))
                    first_run_5m[thread_index] = True
                    break
            except Exception as e:
                time.sleep(0.3)
                continue
        for liczba in range(5):
            try:
                empty_list = client.get_klines(symbol=thread_index, interval=Client.KLINE_INTERVAL_15MINUTE, limit=(ILE_DANYCH_Z_GIELDY+1))
                if empty_list:
                    df_empty_list = pd.DataFrame(empty_list[:-1], columns=['TIME_OPEN','OPEN','HIGH','LOW','CLOSE','VOLUME','TIME_CLOSE','QUOTE','TRADERS','TBB','TBQ','WTF'])
                    closes_15m[thread_index] = df_empty_list['CLOSE'].tolist()
                    closes_15m[thread_index] = list(map(float, closes_15m[thread_index]))
                    first_run_15m[thread_index] = True
                    break
            except Exception as e:
                time.sleep(0.3)
                continue        
        for liczba in range(5):
            try:
                empty_list = client.get_klines(symbol=thread_index, interval=Client.KLINE_INTERVAL_1HOUR, limit=(ILE_DANYCH_Z_GIELDY+1))
                if empty_list:
                    df_empty_list = pd.DataFrame(empty_list[:-1], columns=['TIME_OPEN','OPEN','HIGH','LOW','CLOSE','VOLUME','TIME_CLOSE','QUOTE','TRADERS','TBB','TBQ','WTF'])
                    closes_1h[thread_index] = df_empty_list['CLOSE'].tolist()
                    closes_1h[thread_index] = list(map(float, closes_1h[thread_index]))
                    first_run_1h[thread_index] = True
                    break
            except Exception as e:
                time.sleep(0.3)
                continue              
        for liczba in range(5):
            try:
                empty_list = client.get_klines(symbol=thread_index, interval=Client.KLINE_INTERVAL_4HOUR, limit=(ILE_DANYCH_Z_GIELDY+1))
                if empty_list:
                    df_empty_list = pd.DataFrame(empty_list[:-1], columns=['TIME_OPEN','OPEN','HIGH','LOW','CLOSE','VOLUME','TIME_CLOSE','QUOTE','TRADERS','TBB','TBQ','WTF'])
                    closes_4h[thread_index] = df_empty_list['CLOSE'].tolist()
                    closes_4h[thread_index] = list(map(float, closes_4h[thread_index])) 
                    first_run_4h[thread_index] = True
                    break
            except Exception as e:
                time.sleep(0.3)
                continue         
        if  len(closes_4h[thread_index]) == ILE_DANYCH_Z_GIELDY and len(closes_1h[thread_index]) == ILE_DANYCH_Z_GIELDY and len(closes_15m[thread_index]) == ILE_DANYCH_Z_GIELDY and len(closes_5m[thread_index]) == ILE_DANYCH_Z_GIELDY:
            #print(len(closes_4h[thread_index]),' ',len(closes_1h[thread_index]),' ',len(closes_15m[thread_index]),' ',len(closes_5m[thread_index]))
            print('Pobrano dane historyczne dla ', thread_index)

        THREAD = threading.Thread(target=WEBSOCKET_COINUSDT, args=(SOCKED_ADDRESS_5M[thread_index],))
        #THREAD_LIST.append(THREAD)
        THREAD.start()
        time.sleep(0.5)
        THREAD = threading.Thread(target=WEBSOCKET_COINUSDT, args=(SOCKED_ADDRESS_15M[thread_index],))
        #THREAD_LIST.append(THREAD)
        THREAD.start()       
        time.sleep(0.5)
        THREAD = threading.Thread(target=WEBSOCKET_COINUSDT, args=(SOCKED_ADDRESS_1H[thread_index],))
        #THREAD_LIST.append(THREAD)
        THREAD.start()
        time.sleep(0.5)
        THREAD = threading.Thread(target=WEBSOCKET_COINUSDT, args=(SOCKED_ADDRESS_4H[thread_index],))
        #THREAD_LIST.append(THREAD)
        THREAD.start()       
        time.sleep(0.5)

    t998 = threading.Thread(target=sprawdz_coiny_binance)
    t999 = threading.Thread(target=suma_obliczen)
    
    #WEBSOCKET_COINUSDT("wss://stream.binance.com:9443/ws/bnbusdt@kline_5m")
    #print('bla')
    #WEBSOCKET_COINUSDT("wss://stream.binance.com:9443/ws/btcusdt@kline_5m")
    #print('bla bla')
    t998.start()
    t999.start()