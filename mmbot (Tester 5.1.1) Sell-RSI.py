import datetime, talib, pandas, math
from binance.client import Client

liveapi_key    = "XKsaY99DDM52Iu7jh4KOg2hpzhjpZe8Ot4zRQn123H8FpPKG3HdpduhBcAun41Ku"
liveapi_secret = "XzCTtkAg4OOAGrveJ8ZuE54le10B3Dcr8lAsV3EkWyynaySfD5EqVPxM4IDjAbc8"

client = Client(liveapi_key, liveapi_secret, testnet=False)
print("\nSuccessfully logged in", end="\n\n")

SYMBOL        = 'ETHUSDT'
ASSET         = 'USDT'
TIMEFRAME     = '1m'
QTY_TRADE     =  1

position = 0
buyvalue = 0
buyid = 'others'
bstatus = 'buy'
p1 = 0
b1 = 0
bi1 = 'others'
bst = 'buy'

def BuySellLogic(x):
    global position, buyvalue, buyid, bstatus

    if (x['Major[-2]'] < -1.5 and x['Major[-3]'] >= -1.5) or bstatus == 'dontbuy': 
        
        if x['Major'] < -1.5 and x['Minor1'] < -20: bstatus = 'dontbuy'

        elif x['Minor1[-3]'] < -20 and x['Minor1[-2]'] > -20 and x['Minor1'] > -20: bstatus = 'buy'

    if position == 0:

        if bstatus == 'dontbuy': return None

        elif -1.5 < x['Major']  <  1.5:

            if float(x['close']) < x['ema_C'] < x['ema_D']:

                if -2 < x['Minor1'] < -1.5:

                    if x['RSI[-2]'] - x['RSI[-3]'] < 0 and x['RSI'] - x['RSI[-2]'] > 0 and x['RSI[-2]'] < 30:
                        position = 1
                        buyvalue = float(x['close'])
                        return 'BuyRSI'              

                    elif (x['ema_A[-3]'] < x['ema_B[-3]'] and x['ema_A'] >= x['ema_B'] and  
                          x['Minor2'] < -0.5):
                          position = 1
                          buyvalue = float(x['close'])
                          return 'Buy1Aii'

                    else: return None

                elif x['Minor1'] <= -2:

                    if x['Minor1'] - x['Minor1[-2]'] >= math.log(-x['Minor1'],2):
                        position = 1
                        buyvalue = float(x['close'])
                        return 'Buy1B'          

                    else: return None

                else: return None

            elif x['ema_D'] < float(x['close']) < x['ema_C']:

                if x['Minor1'] <= -2:

                    if x['Minor1'] - x['Minor1[-2]'] >= math.log(-x['Minor1'],2):
                        position = 1
                        buyvalue = float(x['close'])
                        buyid = 'Buy1Bi'
                        #Then sleep for 2 mins
                        return 'Buy1Bi'

                    else: return None

                else: return None

            elif x['Minor1[-2]'] - x['Minor1[-5]'] >= 3:

                if (x['Minor1[-2]'] > -3 and float(x['close']) > float(x['open[-2]']) and 
                    -2 < x['Minor2[-3]'] and x['Minor1'] - x['Minor1[-2]'] > 1 and 
                    (x['Minor2'] > 0.5 or float(x['close']) < x['ema_D'])):
                    position = 1
                    buyvalue = float(x['close'])
                    buyid = 'Buy2'
                    return 'Buy2'

                else: return None

            elif (x['Minor1[-6]'] <= -2 and x['Minor1[-7]'] <= -2 and  
                  x['Minor1[-5]'] - x['Minor1[-8]'] > 0 and x['Minor1'] > 0):
                    position = 1
                    buyvalue = float(x['close'])
                    buyid = 'Buy1Ai'
                    return 'Buy1Ai'
            
            else: return None

        elif x['Major'] <= -1.5:

            if float(x['close']) < x['ema_C'] < x['ema_D']:

                if x['Minor1'] <= -2:

                    if (x['RSI[-2]'] - x['RSI[-3]'] < 0 and x['RSI[-2]'] < 30 and
                      ((x['RSI'] - x['RSI[-2]'] > 1 and x['RSI'] < 30) or x['RSI'] - x['RSI[-2]'] > 5)):
                        position = 1
                        buyvalue = float(x['close'])
                        buyid = 'Buy-RSI'
                        return 'Buy-RSI'              

                    elif x['Minor1'] - x['Minor1[-2]'] >= math.log(-x['Minor1'],2):
                        position = 1
                        buyvalue = float(x['close'])
                        buyid = 'Buy-1B'
                        return 'Buy-1B'

                    else: return None

                else: return None

        elif 1.5 <= x['Major']:

            if x['Minor1[-2]'] - x['Minor1[-5]'] >= 3:

                if (x['Minor1[-2]'] > -3 and float(x['close']) > float(x['close[-2]']) and 
                    -2 < x['Minor2[-3]'] and x['Major[-2]'] < 1.5):

                    position = 1
                    buyvalue = float(x['close'])
                    buyid = 'Buy+2'
                    return 'Buy+2'

                else: return None

            else: return None

        else: return None

    else: # if position == 1:

        if  buyid == 'Buy-1B': 
            buyid = 'go to Buy-1Bi'
            return None

        elif buyid == 'Buy1Bi':
             buyid = 'go to Buy1Bi'
             return None

        elif buyid == 'Buy-RSI':
             buyid = 'go to Buy-RSI'
             return None

        elif -1.5 < x['Major']  <  1.5:

            if float(x['close']) <= float(x['open[-3]']) and buyid == 'go to Buy1Bi':

                position = 0
                buyid = 'others'
                return 'Sell1Bi'

#            elif (float(x['close[-2]']) > x['ema_C[-2]'] and float(x['close']) <= x['ema_C'] and 
#                  buyid == 'Buy2'):
#
#                position = 0
#                buyid = 'others'
#                return 'SellB2'            

            elif float(x['close']) > x['ema_C'] > x['ema_D']:

                if 1.5 < x['Minor1'] < 2:

                    if x['ema_A[-3]'] > x['ema_B[-3]'] and x['ema_A'] <= x['ema_B'] and x['Minor2'] > 0.5:
                        position = 0
                        buyid = 'others'
                        return 'Sell1A'

                    else: return None

                elif 2 <= x['Minor1']:

                    if x['Minor1'] - x['Minor1[-3]'] <= -math.log(x['Minor1'],2):
                        position = 0
                        buyid = 'others'
                        return 'Sell1B'

                    else: return None

                else: return None

            elif x['ema_C'] >= float(x['close']) > x['ema_D']:

                if (float(x['close[-2]']) >= x['ema_C[-2]'] and float(x['close[-3]']) >= x['ema_C[-3]'] and 
                    float(x['close']) >= buyvalue + 1):
                    position = 0
                    buyid = 'others'
                    return 'Sell2A'

                else: return None

            elif x['ema_D'] > float(x['close']) > x['ema_C'] or float(x['close']) > x['ema_D'] >  x['ema_C']:

                if 2 <= x['Minor1']:

                    if x['Minor1'] - x['Minor1[-3]'] <= -math.log(x['Minor1'],2):
                        position = 0
                        buyid = 'others'
                        return 'Sell3A'

                    else: return 
                    
                else: return None

            else: return None

        elif x['Major'] <= -1.5:

            if buyid == 'go to Buy-RSI':

                if (x['ema_R[-2]']  - x['ema_R[-3]'] < 1  and  x['ema_R'] - x['ema_R[-2]'] < 1 and
                    x['ema_R[-3]']  < 30):
                        position = 0
                        buyid = 'others'
                        return 'Sell-RSIi'

                elif (x['ema_R[-2]'] - x['ema_R[-3]'] > 0    and x['ema_R[-3]'] > 30 and 
                     (x['ema_R']     - x['ema_R[-2]'] < 0    or   
                     (x['RSI[-2]']   > x['ema_R[-2]'] + 1.5  and x['RSI'] < x['ema_R'] + 1.5)) and 
                      float(x['close']) > buyvalue and x['Minor1'] < 15):
                        position = 0
                        buyid = 'others'
                        return 'Sell-RSI'

                else: return None

            elif buyid == 'go to Buy-1Bi': #from Buy-1B

                if x['Minor1'] <= -2 and float(x['close']) <= buyvalue: 
                        position = 0
                        buyid = 'others'
                        return 'Sell-1Bi'

                elif 2 <= x['Minor1'] and x['Minor1'] - x['Minor1[-3]'] <= -math.log(x['Minor1'],2): 
                        position = 0
                        buyid = 'others'
                        return 'Sell-1B'

                else: return None

        elif 1.5 < x['Major']:

                if 10 <= x['Minor2']:

                    if x['Minor1'] - x['Minor1[-2]'] <= 0:
                        position = 0
                        buyid = 'others'
                        return 'Sell+1A'

                    else: return None

                else: return None

#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

def Profit(x):
    global p1, b1, bi1, bst

    if (x['Major[-2]'] < -1.5 and x['Major[-3]'] >= -1.5) or bst == 'dontbuy': 
        
        if x['Major'] < -1.5 and x['Minor1'] < -20: bst = 'dontbuy'

        elif x['Minor1[-3]'] < -20 and x['Minor1[-2]'] > -20 and x['Minor1'] > -20: bst = 'buy'

    if p1 == 0:

        if bst == 'dontbuy': return None

        if -1.5 < x['Major']  <  1.5:

            if float(x['close']) < x['ema_C'] < x['ema_D']:

                if -2 < x['Minor1'] < -1.5:

                    if x['RSI[-2]'] - x['RSI[-3]'] < 0 and x['RSI'] - x['RSI[-2]'] > 0 and x['RSI[-2]'] < 30:
                        p1 = 1
                        b1 = float(x['close'])
                        #BuyRSI
                        return None

                    elif (x['ema_A[-3]'] < x['ema_B[-3]'] and x['ema_A'] >= x['ema_B'] and  
                          x['Minor2'] < -0.5):
                          p1 = 1
                          b1 = float(x['close'])
                          #Buy1Aii
                          return None

                    else: return None

                elif x['Minor1'] <= -2:

                    if x['Minor1'] - x['Minor1[-2]'] >= math.log(-x['Minor1'],2):
                        p1 = 1
                        b1 = float(x['close'])
                        #Buy1B
                        return None

                    else: return None

                else: return None

            elif x['ema_D'] < float(x['close']) < x['ema_C']:

                if x['Minor1'] <= -2:

                    if x['Minor1'] - x['Minor1[-2]'] >= math.log(-x['Minor1'],2):
                        p1 = 1
                        b1 = float(x['close'])
                        bi1 = 'Buy1Bi'
                        #Buy1Bi
                        #Then sleep for 2 mins
                        return None

                    else: return None

                else: return None

            elif x['Minor1[-2]'] - x['Minor1[-5]'] >= 3:

                if (x['Minor1[-2]'] > -3 and float(x['close']) > float(x['open[-2]']) and 
                    -2 < x['Minor2[-3]'] and x['Minor1'] - x['Minor1[-2]'] > 1 and 
                    (x['Minor2'] > 0.5 or float(x['close']) < x['ema_D'])):
                    p1 = 1
                    b1 = float(x['close'])
                    bi1 = 'Buy2'
                    #Buy2
                    return None

                else: return None

            elif (x['Minor1[-6]'] <= -2 and x['Minor1[-7]'] <= -2 and  
                  x['Minor1[-5]'] - x['Minor1[-8]'] > 0 and x['Minor1'] > 0):
                    p1 = 1
                    b1 = float(x['close'])
                    bi1 = 'Buy1Ai'
                    #Buy1Ai
                    return None
            
            else: return None

        elif x['Major'] <= -1.5:

            if float(x['close']) < x['ema_C'] < x['ema_D']:

                if x['Minor1'] <= -2:

                    if (x['RSI[-2]'] - x['RSI[-3]'] < 0 and x['RSI[-2]'] < 30 and
                      ((x['RSI'] - x['RSI[-2]'] > 1 and x['RSI'] < 30) or x['RSI'] - x['RSI[-2]'] > 5)):
                        p1 = 1
                        b1 = float(x['close'])
                        bi1 = 'Buy-RSI'
                        #Buy-RSI
                        return None

                    elif x['Minor1'] - x['Minor1[-2]'] >= math.log(-x['Minor1'],2):
                        p1 = 1
                        b1 = float(x['close'])
                        bi1 = 'Buy-1B'
                        #Buy-1B
                        return None

                    else: return None

                else: return None      

        elif 1.5 <= x['Major']:

            if x['Minor1[-2]'] - x['Minor1[-5]'] >= 3:

                if (x['Minor1[-2]'] > -3 and float(x['close']) > float(x['close[-2]']) and 
                    -2 < x['Minor2[-3]'] and x['Major[-2]'] < 1.5):

                    p1 = 1
                    b1 = float(x['close'])
                    bi1 = 'Buy+2'
                    #Buy+2
                    return None

                else: return None

            else: return None

        else: return None

    else: # if position == 1:

        if  bi1 == 'Buy-1B': 
            bi1 = 'go to Buy-1Bi'
            return None

        elif bi1 == 'Buy1Bi':
             bi1 = 'go to Buy1Bi'
             return None

        elif bi1 == 'Buy-RSI':
             bi1 = 'go to Buy-RSI'
             return None

        elif -1.5 < x['Major']  <  1.5:

            if float(x['close']) <= float(x['open[-3]']) and bi1 == 'go to Buy1Bi':
                    
                p1 = 0
                bi1 = 'others'
                proft = float(x['close']) - b1
                #Sell1Bi
                return proft

#            elif (float(x['close[-2]']) > x['ema_C[-2]'] and float(x['close']) <= x['ema_C'] and 
#                  bi1 == 'Buy2'):
#
#                p1 = 0
#                bi1 = 'others'
#                proft = float(x['close']) - b1
#                #SellB2
#                return proft          

            elif float(x['close']) > x['ema_C'] > x['ema_D']:

                if 1.5 < x['Minor1'] < 2:

                    if x['ema_A[-3]'] > x['ema_B[-3]'] and x['ema_A'] <= x['ema_B'] and x['Minor2'] > 0.5:
                        p1 = 0
                        bi1 = 'others'
                        proft = float(x['close']) - b1
                        #Sell1A
                        return proft

                    else: return None

                elif 2 <= x['Minor1']:

                    if x['Minor1'] - x['Minor1[-3]'] <= -math.log(x['Minor1'],2):
                        p1 = 0
                        bi1 = 'others'
                        proft = float(x['close']) - b1
                        #Sell1B
                        return proft

                    else: return None

                else: return None

            elif x['ema_C'] >= float(x['close']) > x['ema_D']:

                if (float(x['close[-2]']) >= x['ema_C[-2]'] and float(x['close[-3]']) >= x['ema_C[-3]'] and 
                    float(x['close']) >= b1 + 1):
                    p1 = 0
                    bi1 = 'others'
                    proft = float(x['close']) - b1
                    #Sell2A
                    return proft

                else: return None

            elif x['ema_D'] > float(x['close']) > x['ema_C'] or float(x['close']) > x['ema_D'] >  x['ema_C']:

                if 2 <= x['Minor1']:

                    if x['Minor1'] - x['Minor1[-3]'] <= -math.log(x['Minor1'],2):
                        p1 = 0
                        bi1 = 'others'
                        proft = float(x['close']) - b1
                        #Sell3A
                        return proft

                    else: return None

                else: return None

            else: return None

        elif x['Major'] <= -1.5:

            if bi1 == 'go to Buy-RSI':

                if (x['ema_R[-2]']  - x['ema_R[-3]'] < 1  and  x['ema_R'] - x['ema_R[-2]'] < 1 and
                    x['ema_R[-3]']  < 30):
                        p1 = 0
                        bi1 = 'others'
                        proft = float(x['close']) - b1
                        #Sell-RSIi
                        return proft

                elif (x['ema_R[-2]'] - x['ema_R[-3]'] > 0    and x['ema_R[-3]'] > 30 and 
                     (x['ema_R']     - x['ema_R[-2]'] < 0    or   
                     (x['RSI[-2]']   > x['ema_R[-2]'] + 1.5  and x['RSI'] < x['ema_R'] + 1.5)) and 
                      float(x['close']) > b1 and x['Minor1'] < 15):
                        p1 = 0
                        bi1 = 'others'
                        proft = float(x['close']) - b1
                        #Sell-RSI
                        return proft

                else: return None

            if bi1 == 'go to Buy-1Bi': #from Buy-1B

                if x['Minor1'] <= -2 and float(x['close']) <= b1: 
                        p1 = 0
                        bi1 = 'others'
                        proft = float(x['close']) - b1
                        #Sell-1Bi
                        return proft

                elif 2 <= x['Minor1'] and x['Minor1'] - x['Minor1[-3]'] <= -math.log(x['Minor1'],2): 
                        p1 = 0
                        bi1 = 'others'
                        proft = float(x['close']) - b1
                        #Sell-1B
                        return proft

                else: return None

        elif 1.5 < x['Major']:

                if 10 <= x['Minor2']:

                    if x['Minor1'] - x['Minor1[-2]'] <= 0:
                        p1 = 0
                        bi1 = 'others'
                        proft = float(x['close']) - b1
                        #Sell+1A
                        return proft

                    else: return None

                else: return None


def get_bars():
    bars = client.futures_historical_klines(SYMBOL, interval=TIMEFRAME, 
    start_str="1667260800000.00", end_str="1674118800000.00")
    bars = pandas.DataFrame(bars, columns=['time','open','high',
    'low','close','vol','closetime','qav','trades','tbb','tbq','Nan'])
    bars["close[-2]"]   = bars.close.shift()
    bars["close[-3]"]   = bars.close.shift(2)
    bars["open[-2]"]    = bars.open.shift()
    bars["open[-3]"]    = bars.open.shift(2)
    bars["ema_A"]       = talib.EMA(bars.close, 3)
    bars["ema_A[-3]"]   = bars.ema_A.shift(2)
    bars["ema_B"]       = talib.EMA(bars.close, 6)
    bars["ema_B[-3]"]   = bars.ema_B.shift(2)
    bars["ema_C"]       = talib.EMA(bars.close, 80)
    bars["ema_C[-2]"]   = bars.ema_C.shift()
    bars["ema_C[-3]"]   = bars.ema_C.shift(2)
    bars["ema_D"]       = talib.EMA(bars.close, 500)
    bars["SMA"]         = talib.SMA(bars.close, 1500)
    bars["RSI"]         = talib.RSI(bars.close, 14) 
    bars["RSI[-2]"]     = bars.RSI.shift()
    bars["RSI[-3]"]     = bars.RSI.shift(2)
    bars["ema_R"]       = talib.EMA(bars.RSI, 6)
    bars['ema_R[-2]']   = bars.ema_R.shift()
    bars['ema_R[-3]']   = bars.ema_R.shift(2)
    bars["Major"]       = talib.LINEARREG_ANGLE(bars.SMA,   4)
    bars["Major[-2]"]   = bars.Major.shift()
    bars["Major[-3]"]   = bars.Major.shift(2)
    bars["Minor1"]      = talib.LINEARREG_ANGLE(bars.ema_C, 4)
    bars["Minor1[-2]"]  = bars.Minor1.shift()
    bars["Minor1[-3]"]  = bars.Minor1.shift(2)
    bars["Minor1[-4]"]  = bars.Minor1.shift(3)
    bars["Minor1[-5]"]  = bars.Minor1.shift(4)
    bars["Minor1[-6]"]  = bars.Minor1.shift(5)
    bars["Minor1[-7]"]  = bars.Minor1.shift(6)
    bars["Minor1[-8]"]  = bars.Minor1.shift(7)
    bars["Minor2"]      = talib.LINEARREG_ANGLE(bars.ema_D, 4)
    bars["Minor2[-2]"]  = bars.Minor2.shift()
    bars["Minor2[-3]"]  = bars.Minor2.shift(2)
    bars["D&Time"]      = bars.apply(lambda x: datetime.datetime.fromtimestamp((x['time'])/1000), axis=1)    
    bars['BuySell']     = bars.apply(BuySellLogic, axis=1)    
    bars['Profit']      = bars.apply(Profit, axis=1)    
    return bars 

bars = get_bars()
print(bars)
print(f"done bars. wait for excel. Profit gained: {bars['Profit'].sum()}")

bars.to_excel(r'C:\Users\Personal Computer\Desktop\datalive5.1.1.xlsx')
print("done excel")
print(f"Profit gained: {bars['Profit'].sum()}")

