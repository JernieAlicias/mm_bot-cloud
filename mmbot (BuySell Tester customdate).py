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
p1 = 0
b1 = 0
bi1 = 'others'

def BuySellLogic(x):
    global position, buyvalue, buyid
    if position == 0:

        if -1.5 < x['Major']  <  1.5:

            if float(x['close']) < x['ema_C'] < x['ema_D']:

                if -2 < x['Minor1'] < -1.5:

                    if (x['Minor1[-2]'] <= -2 and x['Minor1[-3]'] <= -2 and  
                        x['Minor1'] - x['Minor1[-4]'] > 0 and x['Minor1[-2]'] <= -0.5):
                        position = 1
                        buyvalue = float(x['close'])
                        return 'Buy1Ai'

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

            elif x['Minor1'] - x['Minor1[-4]'] >= 3:

                if (x['Minor1'] > -3 and float(x['close']) > float(x['open[-2]']) and 
                    -2 < x['Minor2[-2]']):
                    position = 1
                    buyvalue = float(x['close'])
                    return 'Buy2'

                else: return None
            
            else: return None

        elif x['Major'] <= -1.5:

            if float(x['close']) < x['ema_C'] < x['ema_D']:

                if x['Minor1'] <= -2:

                    if x['Minor1'] - x['Minor1[-2]'] >= math.log(-x['Minor1'],2):
                        position = 1
                        buyvalue = float(x['close'])
                        buyid = 'Buy-1B'
                        return 'Buy-1B'

                    else: return None

                else: return None

        else: return None

    else: # if position == 1:

        if  buyid == 'Buy-1B': 
            buyid = 'go to Buy-1Bi'
            return None

        elif -1.5 < x['Major']  <  1.5:

            if float(x['close']) > x['ema_C'] > x['ema_D']:

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

                    else: return None

                else: return None

            else: return None

        elif x['Major'] <= -1.5:

                if x['Minor1'] <= -2:

                    if float(x['close']) <= buyvalue and buyid == 'go to Buy-1Bi':
                        position = 0
                        buyid = 'others'
                        return 'Sell-1Bi'

                    else: return None

                elif 2 <= x['Minor1']:

                    if x['Minor1'] - x['Minor1[-3]'] <= -math.log(x['Minor1'],2) and buyid == 'go to Buy-1Bi':
                        position = 0
                        buyid = 'others'
                        return 'Sell-1B'

                    else: return None

                else: return None

        else: return None

#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

def Profit(x):
    global p1, b1, bi1
    if p1 == 0:

        if -1.5 < x['Major']  <  1.5:

            if float(x['close']) < x['ema_C'] < x['ema_D']:

                if -2 < x['Minor1'] < -1.5:

                    if (x['Minor1[-2]'] <= -2 and x['Minor1[-3]'] <= -2 and  
                        x['Minor1'] - x['Minor1[-4]'] > 0 and x['Minor1[-2]'] <= -0.5):
                        p1 = 1
                        b1 = float(x['close'])
                        # Buy1Ai
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

            elif x['Minor1'] - x['Minor1[-4]'] >= 3:

                if (x['Minor1'] > -3 and float(x['close']) > float(x['open[-2]']) and 
                    -2 < x['Minor2[-2]']):
                    p1 = 1
                    b1 = float(x['close'])
                    #Buy2
                    return None

                else: return None
            
            else: return None

        elif x['Major'] <= -1.5:

            if float(x['close']) < x['ema_C'] < x['ema_D']:

                if x['Minor1'] <= -2:

                    if x['Minor1'] - x['Minor1[-2]'] >= math.log(-x['Minor1'],2):
                        p1 = 1
                        b1 = float(x['close'])
                        bi1 = 'Buy-1B'
                        #Buy-1B
                        return None

                    else: return None

                else: return None        

        else: return None

    else: # if position == 1:

        if  bi1 == 'Buy-1B': 
            bi1 = 'go to Buy-1Bi'
            return None

        elif -1.5 < x['Major']  <  1.5:

            if float(x['close']) > x['ema_C'] > x['ema_D']:

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

                if x['Minor1'] <= -2:

                    if float(x['close']) <= b1 and bi1 == 'go to Buy-1Bi':
                        p1 = 0
                        bi1 = 'others'
                        proft = float(x['close']) - b1
                        #Sell-1Bi
                        return proft

                    else: return None

                elif 2 <= x['Minor1']:

                    if x['Minor1'] - x['Minor1[-3]'] <= -math.log(x['Minor1'],2) and bi1 == 'go to Buy-1Bi':
                        p1 = 0
                        bi1 = 'others'
                        proft = float(x['close']) - b1
                        #Sell-1B
                        return proft

                    else: return None

                else: return None

        else: return None


def get_bars():
    datestart = datetime.datetime.now() - datetime.timedelta(days=7) # Used to indicate the date start of the bars
    bars = client.futures_historical_klines(SYMBOL, interval=TIMEFRAME, 
    start_str=datestart.strftime("%Y-%m-%d %H:%M:%S"))
    bars = pandas.DataFrame(bars, columns=['time','open','high',
    'low','close','vol','closetime','qav','trades','tbb','tbq','Nan'])
    bars["close[-2]"]  = bars.close.shift()
    bars["close[-3]"]  = bars.close.shift(2)
    bars["open[-2]"]   = bars.open.shift()
    bars["ema_A"]      = talib.EMA(bars.close, 3)
    bars["ema_A[-3]"]  = bars.ema_A.shift(2)
    bars["ema_B"]      = talib.EMA(bars.close, 6)
    bars["ema_B[-3]"]  = bars.ema_B.shift(2)
    bars["ema_C"]      = talib.EMA(bars.close, 80)
    bars["ema_C[-2]"]  = bars.ema_C.shift()
    bars["ema_C[-3]"]  = bars.ema_C.shift(2)
    bars["ema_D"]      = talib.EMA(bars.close, 500)
    bars["SMA"]        = talib.SMA(bars.close, 1500)
    bars["Major"]      = talib.LINEARREG_ANGLE(bars.SMA,   4)
    bars["Minor1"]     = talib.LINEARREG_ANGLE(bars.ema_C, 4)
    bars["Minor1[-2]"] = bars.Minor1.shift()
    bars["Minor1[-3]"] = bars.Minor1.shift(2)
    bars["Minor1[-4]"] = bars.Minor1.shift(3)
    bars["Minor2"]     = talib.LINEARREG_ANGLE(bars.ema_D, 4)
    bars["Minor2[-2]"] = bars.Minor2.shift()
    bars["D&Time"]     = bars.apply(lambda x: datetime.datetime.fromtimestamp((x['time'])/1000), axis=1)    
    bars['BuySell']    = bars.apply(BuySellLogic, axis=1)    
    bars['Profit']     = bars.apply(Profit, axis=1)    
    return bars

bars = get_bars()
print(bars)
print("done bars")

bars.to_excel(r'C:\Users\Personal Computer\Desktop\dat1.xlsx')
print("done excel")
print(f"Profit gained: {bars['Profit'].sum()}")

