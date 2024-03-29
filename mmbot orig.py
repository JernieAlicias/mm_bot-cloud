import time, datetime, config, talib, pandas, math
from binance.client import Client
from mongodb import (get_placeholder_buy, store_profit_history, store_buyval_history, 
store_datab_walletbal, get_datab_walletbal, get_openvalue, store_openvalue)

client = Client(config.api_key, config.api_secret, testnet=True)
print("\nSuccessfully logged in", end="\n\n")

SYMBOL     = 'ETHUSDT'
ASSET      = 'USDT'
TIMEFRAME  = '1m'
QTY_TRADE  =  1
tempvalue  =  0
buyid      = ''
buystatus  = set()
sellstatus = set()

# Prints the current date and time at the end of the display
def print_datetime():
    datetime1 = datetime.datetime.now()
    now = str(datetime1.replace(microsecond=0))
    print(f"Date & Time: {now}", end="\n\n")
    return 

# Gets our current position (number of crypto coins that we have)
def get_position():
    positions = Client.futures_account(self=client)['positions']
    for p in positions:
        if p['symbol'] == SYMBOL:
           return float(p['positionAmt'])
    return 0

# Gets our current wallet balance for the computation of profit
def get_wallet_balance():
    balances = Client.futures_account(self=client)['assets']
    for b in balances:
        if b['asset'] == ASSET:
           return float(b['walletBalance'])
    return 0

# Gets the latest (current) price of a Symbol based on the latest trade
def get_last_price():
    return float(Client.futures_recent_trades(self=client, symbol=SYMBOL)[-1]['price'])

# Gets the mark price of a Symbol to be used for placeholder, calculation of profit, etc.
def get_mark_price():
    return float(Client.futures_mark_price(self=client, symbol=SYMBOL)['markPrice'])

# Function that prints the current price, mark price, position, and other data on the display
def print_data():
    print(f"Current: {get_last_price()}  /  Mark Price: {get_mark_price()}  /  Place: {get_placeholder_buy()}  /  Position: {position}")
    print(f"Major: {bars.Major.iloc[-1]}  /  Minor1: {bars.Minor1.iloc[-1]}  /  RSI: {bars.RSI.iloc[-1]}  /  Buystatus: {buystatus}")
    return 

# Gets the bars/klines in 5 minutes data timeframe from Binance Futures then adds the indicators
def get_bars():
    datestart = datetime.datetime.now() - datetime.timedelta(days=2) # Used to indicate the date start of the bars
    bars = client.futures_historical_klines(SYMBOL, interval=TIMEFRAME, 
    start_str=datestart.strftime("%Y-%m-%d %H:%M:%S"))
    bars = pandas.DataFrame(bars, columns=['time','open','high',
    'low','close','vol','closetime','qav','trades','tbb','tbq','Nan'])
    bars = bars.set_index(bars.columns[0])
    bars["RSI"]    = talib.RSI(bars.close, 14) 
    bars["ema_A"]  = talib.EMA(bars.close, 3)
    bars["ema_B"]  = talib.EMA(bars.close, 6)
    bars["ema_C"]  = talib.EMA(bars.close, 80)
    bars["ema_D"]  = talib.EMA(bars.close, 500)
    bars["ema_R"]  = talib.EMA(bars.RSI,   6)
    bars["SMA"]    = talib.SMA(bars.close, 1500)
    bars["Major"]  = talib.LINEARREG_ANGLE(bars.SMA,   4)
    bars["Minor1"] = talib.LINEARREG_ANGLE(bars.ema_C, 4)
    bars["Minor2"] = talib.LINEARREG_ANGLE(bars.ema_D, 4)
    return bars

# Function that initiates the Buy order in Binance Futures market
def order_buy(buyid): 
    m, x, y, z = get_mark_price(), bars.Major.iloc[-1], bars.Minor1.iloc[-1], bars.Minor2.iloc[-1]
    client.futures_create_order(symbol=SYMBOL, side='BUY', type='MARKET', quantity=QTY_TRADE)      
    store_buyval_history(buyid, datetime.datetime.now().strftime("%x"), datetime.datetime.now().strftime("%X"), m, x, y, z)
    print("Buying at Mark Price: ", m)
    print(f'Symbol: {SYMBOL} / Side: BUY / Quantity: {QTY_TRADE} / Current Position: {get_position()}')
    print_datetime()

# Function that initiates the Sell order in Binance Futures market
def order_sell(sellid):
    m, x, y, z = get_mark_price(), bars.Major.iloc[-1], bars.Minor1.iloc[-1], bars.Minor2.iloc[-1]
    client.futures_create_order(symbol=SYMBOL, side='SELL', type='MARKET', quantity=QTY_TRADE)     
    profit = get_wallet_balance() - get_datab_walletbal()
    store_profit_history(sellid, profit, datetime.datetime.now().strftime("%x"), datetime.datetime.now().strftime("%X"), m, x, y, z)
    store_datab_walletbal(get_wallet_balance())
    print("Profit gain: ", profit)
    print(f'Symbol: {SYMBOL} / Side: SELL / Quantity: {QTY_TRADE} / Current Position: {get_position()}')
    print_datetime()

# Function for the buy and sell logic of mm_bot
def buy_sell_logic(place, openv):
    print_data()
    global tempvalue, buyid, buystatus, sellstatus

    if position == 0:

        sellstatus = set()
        if float(bars.Major.iloc[-1]) <= -1.5:

            if (('dontbuy' not in buystatus) and ((float(bars.Minor1.iloc[-2]) < -20 and 
                float(bars.Minor1.iloc[-1]) < -20) or float(bars.Minor1.iloc[-1]) - float(bars.Minor1.iloc[-3]) < -2 or
                float(bars.Minor1.iloc[-1]) - float(bars.Minor1.iloc[-2]) < -1.5)): 
                buystatus.add('dontbuy')

            if ('dontbuy' in buystatus) and float(bars.Minor1.iloc[-1]) - float(bars.Minor1.iloc[-2]) > -2.5: 
                buystatus.discard('dontbuy')

            if (float(bars.close.iloc[-1]) < float(bars.ema_C.iloc[-1]) and float(bars.Minor1.iloc[-1]) <= -2):

                if (('buy-rsi' not in buystatus) and float(bars.RSI.iloc[-3]) - float(bars.RSI.iloc[-4]) < 1.5 and float(bars.RSI.iloc[-4]) < 30 and 
                   ((float(bars.RSI.iloc[-2]) - float(bars.RSI.iloc[-3]) > 0.75 and float(bars.RSI.iloc[-3]) < 30) or 
                     float(bars.RSI.iloc[-2]) - float(bars.RSI.iloc[-3]) > 5)):
                     buystatus.add('buy-rsi')
                     tempvalue = float(bars.close.iloc[-2])
                     time.sleep(50) 
                     #Conditions for Buy-RSI are adjusted by -1 to compensate for Live Bars

                if (('buy-1b' not in buystatus) and float(bars.Minor1.iloc[-1]) - float(bars.Minor1.iloc[-2]) >=
                      math.log(-float(bars.Minor1.iloc[-1]),2)):
                  
                    n = 0
                    for _ in  range(10):
                        if (('buy-1b' not in buystatus) and float(bars.Minor1.iloc[-1]) - float(bars.Minor1.iloc[-2]) >=
                              math.log(-float(bars.Minor1.iloc[-1]),2)): n += 1
                        time.sleep(3)                      
                    if  n == 10: 
                        buystatus.add('buy-1b')

            if ('buy-rsi' in buystatus) or ('buy-1b' in buystatus) or ('buy1ai' in buystatus):    

                if (float(bars.ema_A.iloc[-3]) > float(bars.ema_B.iloc[-3]) and 
                    float(bars.ema_A.iloc[-2]) < float(bars.ema_B.iloc[-2])):
                    buystatus.discard('buy-rsi')
                    buystatus.discard('buy-1b')
                    buystatus.discard('buy1ai')                     

        elif -1.5 < float(bars.Major.iloc[-1]) < 1.5: 

            if (('dontbuy' not in buystatus) and (float(bars.Minor1.iloc[-2]) < -20 and 
                float(bars.Minor1.iloc[-1]) < -20)): 
                buystatus.add('dontbuy')

            if (('dontbuy' in buystatus) and float(bars.Minor1.iloc[-1]) - float(bars.Minor1.iloc[-3]) > 2 or
                float(bars.Minor1.iloc[-1]) - float(bars.Minor1.iloc[-2]) > 1.5): buystatus.discard('dontbuy')

            #Buystatus for Buy1Ai
            if (('buy1ai' not in buystatus) and float(bars.Minor1.iloc[-6]) <= -2 and float(bars.Minor1.iloc[-7]) <= -2 and
                float(bars.Minor1.iloc[-5]) -  float(bars.Minor1.iloc[-8]) > 0 and 
                float(bars.Minor1.iloc[-1]) >  0 and float(bars.close.iloc[-1]) >
                float(bars.close.iloc[-2])  >  float(bars.close.iloc[-3]) > float(bars.close.iloc[-4])):

                n = 0
                for _ in  range(10):
                    if (('buy1ai' not in buystatus) and float(bars.Minor1.iloc[-6]) <= -2 and float(bars.Minor1.iloc[-7]) <= -2 and
                        float(bars.Minor1.iloc[-5]) -  float(bars.Minor1.iloc[-8]) > 0 and 
                        float(bars.Minor1.iloc[-1]) >  0 and float(bars.close.iloc[-1]) >
                        float(bars.close.iloc[-2])  >  float(bars.close.iloc[-3]) > 
                        float(bars.close.iloc[-4])): n += 1
                    time.sleep(3)                      
                if  n == 10: 
                    buystatus.add('buy1ai')

            if (float(bars.close.iloc[-1])  < float(bars.ema_C.iloc[-1]) and float(bars.Minor1.iloc[-1]) <= -2):

                if (('buy-rsi' not in buystatus) and float(bars.RSI.iloc[-3]) - float(bars.RSI.iloc[-4]) < 1.5 and float(bars.RSI.iloc[-4]) < 30 and 
                   ((float(bars.RSI.iloc[-2]) - float(bars.RSI.iloc[-3]) > 0.75 and float(bars.RSI.iloc[-3]) < 30) or 
                     float(bars.RSI.iloc[-2]) - float(bars.RSI.iloc[-3]) > 5)):
                     buystatus.add('buy-rsi')
                     tempvalue = float(bars.close.iloc[-2])
                     time.sleep(50) 
                     #Conditions for Buy-RSI are adjusted by -1 to compensate for Live Bars

            if ('buy-rsi' in buystatus) or ('buy-1b' in buystatus) or ('buy1ai' in buystatus):    

                if (float(bars.ema_A.iloc[-3]) > float(bars.ema_B.iloc[-3]) and 
                    float(bars.ema_A.iloc[-2]) < float(bars.ema_B.iloc[-2])):
                    buystatus.discard('buy-rsi')
                    buystatus.discard('buy-1b')
                    buystatus.discard('buy1ai')   

    elif position == 1:

        buystatus = set()
        if -1.5 < float(bars.Major.iloc[-1]) < 1.5: 

            if (buyid == 'Buy-RSI' and float(bars.ema_R.iloc[-2]) - float(bars.ema_R.iloc[-3]) > 0 and
                float(bars.ema_R.iloc[-2]) > 30): sellstatus.add('sell-rsi')

        elif float(bars.Major.iloc[-1]) <= -1.5:

            if (buyid == 'Buy-RSI' and float(bars.ema_R.iloc[-2]) - float(bars.ema_R.iloc[-3]) > 0 and
                float(bars.ema_R.iloc[-2]) > 30): sellstatus.add('sell-rsi')

    if position < QTY_TRADE: # BUYING PHASE

        if ('dontbuy' in buystatus): 
            
            if float(bars.close.iloc[-1]) < tempvalue - 1:
                buystatus.discard('buy-rsi')
                print("You're in Buying phase, waiting to buy [0a] / ", end="") 

            else: print("You're in Buying phase, waiting to buy [0b] / ", end="") 
        
        # If the major trend starts to go bullish, then the bot buys immediately
        elif 1.5 <= float(bars.Major.iloc[-1]):

            # 
            if float(bars.Minor1.iloc[-2]) - float(bars.Minor1.iloc[-5]) >= 3:

                #
                if (float(bars.Minor1.iloc[-2]) > -3 and float(bars.close.iloc[-1]) > float(bars.close.iloc[-2]) and
                    -2 < float(bars.Minor2.iloc[-3]) and float(bars.Major.iloc[-2]) < 1.5):

                    n = 0
                    for _ in  range(10):
                        if (float(bars.Minor1.iloc[-2]) > -3 and float(bars.close.iloc[-1]) > 
                            float(bars.close.iloc[-2])  and -2 < float(bars.Minor2.iloc[-3]) and 
                            float(bars.Major.iloc[-2])  < 1.5): n += 1
                        time.sleep(3)                      
                    if  n == 10: 
                        buyid = 'Buy+2'
                        order_buy(buyid)
                        print("Order Buy id:Buy+2 - Sleeping for 1 minute")  
                        time.sleep(60)  

                    else: print("You're in Buying phase, waiting to buy [1a] / ", end="")       

                else: print("You're in Buying phase, waiting to buy [1b] / ", end="")   

            else: print("You're in Buying phase, waiting to buy [1c] / ", end="")     

        # If the major trend goes sideways, then the bot has the following buy condition:
        elif -1.5 < float(bars.Major.iloc[-1]) < 1.5: 

            #
            if ('buy-rsi' in buystatus):

                if float(bars.close.iloc[-1]) >= tempvalue + 1:
                    buyid = 'Buy-RSI'
                    order_buy(buyid)
                    buystatus = set()
                    tempvalue = 0
                    print("Order Buy id:Buy-RSI - Sleeping for 1 minute")  
                    time.sleep(60)  

                elif tempvalue + 1 > float(bars.close.iloc[-1]) > tempvalue - 1:
                    print("You're in Buying phase, waiting to buy [2-0a] / ", end="")

                else: 
                    n = 0
                    for _ in  range(20):
                        if float(bars.close.iloc[-1]) <= tempvalue - 1: n += 1
                        else: break
                        time.sleep(3)                      
                    if  n == 20: 
                        buystatus.discard('buy-rsi')

                    else: print("You're in Buying phase, waiting to buy [2-0b] / ", end="")
            
            # If close < ema_C < ema_D. then the buy conditions are:
            elif float(bars.close.iloc[-1]) < float(bars.ema_C.iloc[-1]) < float(bars.ema_D.iloc[-1]):
                
                # If the value of Minor1 is in between -2 and -1.5, then the buy conditions are:
                if -2 < float(bars.Minor1.iloc[-1]) < -1.5:
                    
                    #
                    if (float(bars.RSI.iloc[-2]) - float(bars.RSI.iloc[-3]) < 0 and 
                        float(bars.RSI.iloc[-1]) - float(bars.RSI.iloc[-2]) > 0 and 
                        float(bars.RSI.iloc[-2]) < 30):

                        n = 0
                        for _ in  range(10):
                            if (float(bars.RSI.iloc[-2]) - float(bars.RSI.iloc[-3]) < 0 and 
                                float(bars.RSI.iloc[-1]) - float(bars.RSI.iloc[-2]) > 0 and 
                                float(bars.RSI.iloc[-2]) < 30): n += 1
                            time.sleep(3)                      
                        if  n == 10: 
                            buyid = 'BuyRSI'
                            order_buy(buyid)
                            print("Order Buy id:BuyRSI - Sleeping for 1 minute")  
                            time.sleep(60)  

                        else: print("You're in Buying phase, waiting to buy [2-1a] / ", end="")

                    # If ema_A crosses over ema_B from below, then the buy condition is:
                    elif (float(bars.ema_A.iloc[-3])  <  float(bars.ema_B.iloc[-3]) and
                          float(bars.ema_A.iloc[-1])  >= float(bars.ema_B.iloc[-1]) and 
                          float(bars.close.iloc[-1])  -  float(bars.open.iloc[-1]) > -0.25 and
                          float(bars.Minor2.iloc[-1]) <  -0.5 ):

                        n = 0
                        for _ in  range(10):
                            if (float(bars.ema_A.iloc[-3])  <  float(bars.ema_B.iloc[-3]) and
                                float(bars.ema_A.iloc[-1])  >= float(bars.ema_B.iloc[-1]) and 
                                float(bars.close.iloc[-1])  -  float(bars.open.iloc[-1]) > -0.25 and
                                float(bars.Minor2.iloc[-1]) <  -0.5 ): n += 1
                            time.sleep(3)                      
                        if  n == 10: 
                            buyid = 'Buy1Aii'
                            order_buy(buyid)
                            print("Order Buy id:Buy1Aii - Sleeping for 1 minute")  
                            time.sleep(60)  

                        else: print("You're in Buying phase, waiting to buy [2-1b] / ", end="")

                    else: print("You're in Buying phase, waiting to buy [2-1c] / ", end="")

                # If the value of Minor1 is less than or equal to -2, then the buy condition is:
                elif float(bars.Minor1.iloc[-1]) <= -3:
                    
                    # If the price suddenly spikes up, then the buy condition is:
                    if (float(bars.Minor1.iloc[-1]) - float(bars.Minor1.iloc[-2]) >= 
                        math.log(-float(bars.Minor1.iloc[-1]),2) and
                        float(bars.close.iloc[-1])  - float(bars.open.iloc[-1]) >= 1):

                        n = 0
                        Minor1_iloc_2 = float(bars.Minor1.iloc[-2])
                        for _ in  range(10):
                            if (float(bars.Minor1.iloc[-1]) - Minor1_iloc_2 >= 
                                math.log(-float(bars.Minor1.iloc[-1]),2) and
                                float(bars.close.iloc[-1])  - float(bars.open.iloc[-1]) >= 1): n += 1
                            time.sleep(3)                      
                        if  n == 10: 
                            buyid = 'Buy1B'
                            order_buy(buyid)
                            store_openvalue(float(bars.open.iloc[-3]))
                            print("Order Buy id:Buy1B - Sleeping for 1 minute")  
                            time.sleep(60)  

                        else: print("You're in Buying phase, waiting to buy [2-2a] / ", end="")

                    else: print("You're in Buying phase, waiting to buy [2-2b] / ", end="")

                else: print("You're in Buying phase, waiting to buy [2-2c] / ", end="")

            #
            elif float(bars.close.iloc[-1]) < float(bars.ema_C.iloc[-1]):

                # 
                if float(bars.Minor1.iloc[-3]) <= -2:

                    # 
                    if (float(bars.Minor1.iloc[-3]) - float(bars.Minor1.iloc[-4]) >= 
                        math.log(-float(bars.Minor1.iloc[-3]),2) and
                        float(bars.close.iloc[-1]) + float(bars.close.iloc[-2]) -
                        float(bars.open.iloc[-1])  - float(bars.open.iloc[-2])  > -0.25):

                        n = 0
                        for _ in  range(10):
                            if (float(bars.Minor1.iloc[-3]) - float(bars.Minor1.iloc[-4]) >= 
                                math.log(-float(bars.Minor1.iloc[-3]),2) and
                                float(bars.close.iloc[-1]) + float(bars.close.iloc[-2]) -
                                float(bars.open.iloc[-1])  - float(bars.open.iloc[-2])  > -0.25): n += 1
                            time.sleep(3)                      
                        if  n == 10: 
                            buyid = 'Buy1Bi'
                            order_buy(buyid)
                            print("Order Buy id:Buy1Bi - Sleeping for 2 minutes")  
                            time.sleep(120)  

                        else: print("You're in Buying phase, waiting to buy [2-3a] / ", end="")

                    else: print("You're in Buying phase, waiting to buy [2-3b] / ", end="")         

                else: print("You're in Buying phase, waiting to buy [2-3c] / ", end="")       

            # If the price suddenly spikes up greatly, then the buy condition is:
 #           elif float(bars.Minor1.iloc[-1]) - float(bars.Minor1.iloc[-4]) >= 3:
 #
 #               #
 #               if (float(bars.Minor1.iloc[-1]) <= -3 or float(bars.close.iloc[-1])  <= float(bars.open.iloc[-2]) or
 #                   float(bars.Minor2.iloc[-1]) <= -2 or float(bars.Minor2.iloc[-1]) >= 1.75):
 #                   print("You're in Buying phase, waiting to buy [2g] / ", end="")
 #
 #               else: 
 #                   n = 0
 #                   Minor1_iloc_4 = float(bars.Minor1.iloc[-4])
 #                   for _ in  range(5):
 #                       if float(bars.Minor1.iloc[-1]) - Minor1_iloc_4 >= 3: n += 1
 #                       time.sleep(3)                      
 #                   if  n == 5: 
 #                       buyid = 'Buy2'
 #                       order_buy(buyid)
 #                       print("Order Buy id:Buy2 - Sleeping for 1 minute")  
 #                       time.sleep(60)  
 #
 #                   else: print("You're in Buying phase, waiting to buy [2-4a] / ", end="")

            # 
            elif (('buy1ai' in buystatus) and 
                  float(bars.close.iloc[-2]) < float(bars.open.iloc[-2]) and
                  float(bars.close.iloc[-1]) > float(bars.open.iloc[-1])):

                n = 0
                for _ in  range(10):
                    if (('buy1ai' in buystatus) and 
                        float(bars.close.iloc[-2]) < float(bars.open.iloc[-2]) and
                        float(bars.close.iloc[-1]) > float(bars.open.iloc[-1])): n += 1
                    time.sleep(3)                      
                if  n == 10: 
                    buyid = 'Buy1Ai'
                    buystatus = set()
                    order_buy(buyid)
                    print("Order Buy id:Buy1Ai - Sleeping for 1 minute")  
                    time.sleep(60)  

                else: print("You're in Buying phase, waiting to buy [2-5a] / ", end="") 

            else: print("You're in Buying phase, waiting to buy [2-5b] / ", end="")

        # If the major trend starts to go bearish, the bot has the following buy conditions:
        elif float(bars.Major.iloc[-1]) <= -1.5 or float(bars.Major.iloc[-2]) <= -1.5:

            #
            if ('buy-rsi' in buystatus):

                if float(bars.close.iloc[-1]) >= tempvalue + 1:
                    buyid = 'Buy-RSI'
                    order_buy(buyid)
                    buystatus = set()
                    tempvalue = 0
                    print("Order Buy id:Buy-RSI - Sleeping for 1 minute")  
                    time.sleep(60)  

                elif tempvalue + 1 > float(bars.close.iloc[-1]) > tempvalue - 1:
                    print("You're in Buying phase, waiting to buy [3-1a] / ", end="")

                else: 
                    n = 0
                    for _ in  range(20):
                        if float(bars.close.iloc[-1]) <= tempvalue - 1: n += 1
                        else: break
                        time.sleep(3)                      
                    if  n == 20: 
                        buystatus.discard('buy-rsi')

                    else: print("You're in Buying phase, waiting to buy [3-2b] / ", end="")

            # If the price suddenly spikes up, then the buy condition is:
            elif (('buy-1b' in buystatus) and float(bars.close.iloc[-2]) < float(bars.ema_A.iloc[-2]) and
                  float(bars.close.iloc[-1]) > float(bars.ema_A.iloc[-1])):

                n = 0
                for _ in  range(10):
                    if (('buy-1b' in buystatus) and float(bars.close.iloc[-2]) < float(bars.ema_A.iloc[-2]) and
                         float(bars.close.iloc[-1]) > float(bars.ema_A.iloc[-1])): n += 1
                    time.sleep(3)                      
                if  n == 10: 
                    buyid = 'Buy-1B'
                    buystatus  = set()
                    order_buy(buyid)
                    print("Order Buy id:Buy-1B - Sleeping for 1 minute")  
                    time.sleep(60)  

                else: print("You're in Buying phase, waiting to buy [3a] / ", end="")

            else: print("You're in Buying phase, waiting to buy [3b] / ", end="")                    

        else: print("You're in Buying phase, waiting to buy [3c] / ", end="")         

    else: # position = QTY_TRADE: # SELLING PHASE
        
        # If the major trend starts to go bullish, then the bot has the following sell conditions:
        if 1.5 <= float(bars.Major.iloc[-1]):
            
            #
            if 10 <= float(bars.Minor2.iloc[-1]):

                #
                if float(bars.Minor1.iloc[-1]) - float(bars.Minor1.iloc[-2]) <= 0:

                    n = 0
                    Minor1_iloc_2 = float(bars.Minor1.iloc[-2])
                    for _ in  range(5):
                        if float(bars.Minor1.iloc[-1]) - Minor1_iloc_2 <= 0: n += 1
                        time.sleep(3)                      
                    if  n == 5: 
                        order_sell("Sell+1A")
                        buyid = ''
                        print("Order Sell id:Sell+1A - Sleeping for 1 minute")  
                        time.sleep(60)  

                    else: print("You're in Selling phase, waiting to sell [1-1a] / ", end="")  

                else: print("You're in Selling phase, waiting to sell [1-1b] / ", end="") 

            else: print("You're in Selling phase, waiting to sell [1-1c] / ", end="")               

        # If the major trend goes sideways, then the bot has the following sell condition:
        elif -1.5 < float(bars.Major.iloc[-1]) < 1.5: 

            #
            if (buyid == 'Buy1Bi' and
                float(bars.Minor1.iloc[-1]) - float(bars.Minor1.iloc[-2]) <= -0.75 and
                float(bars.close.iloc[-1])  - place < -1):

                n = 0
                Minor1_iloc_2 = float(bars.Minor1.iloc[-2])
                for _ in  range(5):
                    if (buyid == 'Buy1Bi' and float(bars.Minor1.iloc[-1]) - Minor1_iloc_2 <= -0.75 and
                        float(bars.close.iloc[-1]) - place < -1): n += 1
                    time.sleep(3)                      
                if  n == 5: 
                    order_sell("Sell1Bi")
                    buyid = ''
                    print("Order Sell id:Sell1Bi - Sleeping for 1 minute")  
                    time.sleep(60)  

                else: print("You're in Selling phase, waiting to sell [2-1a] / ", end="")

            #
            elif (buyid == 'Buy1B' and
                  float(bars.close.iloc[-1]) < openv):

                n = 0
                for _ in  range(3):
                    if (buyid == 'Buy1B' and
                        float(bars.close.iloc[-1]) < openv): n += 1
                    time.sleep(3)                      
                if  n == 3: 
                    order_sell("Sellfor1B")
                    buyid = ''
                    print("Order Sell id:Sellfor1B - Sleeping for 1 minute")  
                    time.sleep(60)  

                else: print("You're in Selling phase, waiting to sell [2-2a] / ", end="")

            #
            elif (buyid == 'Buy1Ai' and
                  float(bars.close.iloc[-1]) < place - 1):

                n = 0
                for _ in  range(3):
                    if (buyid == 'Buy1Ai' and
                        float(bars.close.iloc[-1]) < place - 1): n += 1
                    time.sleep(3)                      
                if  n == 3: 
                    order_sell("Sellfor1Ai")
                    buyid = ''
                    print("Order Sell id:Sellfor1Ai - Sleeping for 1 minute")  
                    time.sleep(60)  

                else: print("You're in Selling phase, waiting to sell [2-2b] / ", end="")

            #
            elif (buyid == 'Buy-RSI' and
                  float(bars.close.iloc[-1]) < place - 1):

                  n = 0
                  for _ in  range(5):
                      if buyid == 'Buy-RSI' and float(bars.close.iloc[-1]) < place - 1: n += 1
                      time.sleep(3)                      
                  if  n == 5: 
                      order_sell("Sell-RSIi")
                      buyid = ''
                      print("Order Sell id:Sell-RSIi - Sleeping for 1 minute")  
                      time.sleep(60)  

                  else: print("You're in Selling phase, waiting to sell [2-3a1] / ", end="")

            #
            elif (('sell-rsi' in sellstatus) and
                 ((float(bars.ema_A.iloc[-2]) >  float(bars.ema_B.iloc[-2])  and 
                   float(bars.ema_A.iloc[-1]) <= float(bars.ema_B.iloc[-1])) or
                   float(bars.RSI.iloc[-1])   <  float(bars.ema_R.iloc[-1])) and
                   float(bars.close.iloc[-1]) >  place - 0.75 and float(bars.Minor1.iloc[-1]) < 15):

                  n = 0
                  for _ in  range(3):
                      if (('sell-rsi' in sellstatus) and
                         ((float(bars.ema_A.iloc[-2]) >  float(bars.ema_B.iloc[-2])  and 
                           float(bars.ema_A.iloc[-1]) <= float(bars.ema_B.iloc[-1])) or
                           float(bars.RSI.iloc[-1])   <  float(bars.ema_R.iloc[-1])) and
                           float(bars.close.iloc[-1]) >  place - 0.75 and float(bars.Minor1.iloc[-1]) < 15): n += 1
                      time.sleep(3)                      
                  if  n == 3: 
                      order_sell("Sell-RSI")
                      buyid = ''
                      sellstatus = set()
                      print("Order Sell id:Sell-RSI - Sleeping for 1 minute")  
                      time.sleep(60)  

                  else: print("You're in Selling phase, waiting to sell [2-3a2] / ", end="")

            # If close > ema_C > ema_D. then the sell conditions are:
            elif float(bars.close.iloc[-1]) > float(bars.ema_C.iloc[-1]) > float(bars.ema_D.iloc[-1]):
            
                # If the value of Minor1 is less than or equal to 1.5, then the sell condition is:
                if float(bars.Minor1.iloc[-1]) <= 1.5: 

                    pass




                # If the value of Minor1 is in between 2 and 1.5, then the sell condition is:
                elif 1.5 < float(bars.Minor1.iloc[-1]) < 2:
                    
                    # If ema_A crosses over ema_B from above, then the sell condition is:
                    if (float(bars.ema_A.iloc[-3])  >  float(bars.ema_B.iloc[-3]) and
                        float(bars.ema_A.iloc[-1])  <= float(bars.ema_B.iloc[-1]) and  
                        float(bars.Minor2.iloc[-1]) > 0.5):

                        n = 0
                        for _ in  range(5):
                            if (float(bars.ema_A.iloc[-3])  >  float(bars.ema_B.iloc[-3]) and
                                float(bars.ema_A.iloc[-1])  <= float(bars.ema_B.iloc[-1]) and  
                                float(bars.Minor2.iloc[-1]) > 0.5): n += 1
                            time.sleep(3)                      
                        if  n == 5: 
                            order_sell("Sell1A")
                            buyid = ''
                            print("Order Sell id:Sell1A - Sleeping for 1 minute")  
                            time.sleep(60)  

                        else: print("You're in Selling phase, waiting to sell [2-4a] / ", end="")

                    else: print("You're in Selling phase, waiting to sell [2-4b] / ", end="")

                # If the value of Minor1 is greater than or equal to 2, then the sell condition is:
                elif 2 <= float(bars.Minor1.iloc[-1]):

                    # If the price suddenly goes down, then the sell condition is:
                    if ((float(bars.Minor1.iloc[-1]) - float(bars.Minor1.iloc[-3])) <= 
                        -math.log(float(bars.Minor1.iloc[-1]),2)):

                        n = 0
                        Minor1_iloc_3 = float(bars.Minor1.iloc[-3])
                        for _ in  range(3):
                            if ((float(bars.Minor1.iloc[-1]) - Minor1_iloc_3) <= 
                                -math.log(float(bars.Minor1.iloc[-1]),2)): n += 1
                            time.sleep(3)                      
                        if  n == 3: 
                            order_sell("Sell1B")
                            buyid = ''
                            print("Order Sell id:Sell1B - Sleeping for 1 minute")  
                            time.sleep(60)  

                        else: print("You're in Selling phase, waiting to sell [2-5a] / ", end="")

                    else: print("You're in Selling phase, waiting to sell [2-5b] / ", end="")

            #
            elif float(bars.ema_C.iloc[-1]) >= float(bars.close.iloc[-1]) > float(bars.ema_D.iloc[-1]):
                    
                #
                if (float(bars.ema_C.iloc[-1]) >= float(bars.close.iloc[-1]) and
                    float(bars.close.iloc[-2]) >= float(bars.ema_C.iloc[-2]) and 
                    float(bars.close.iloc[-3]) >= float(bars.ema_C.iloc[-3]) and 
                    float(bars.close.iloc[-1]) >= place + 1):

                    n = 0
                    for _ in  range(3):
                        if (float(bars.ema_C.iloc[-1]) >= float(bars.close.iloc[-1]) and
                            float(bars.close.iloc[-2]) >= float(bars.ema_C.iloc[-2]) and 
                            float(bars.close.iloc[-3]) >= float(bars.ema_C.iloc[-3]) and 
                            float(bars.close.iloc[-1]) >= place + 1): n += 1
                        time.sleep(3)                      
                    if  n == 3: 
                        order_sell("Sell2A")
                        buyid = ''
                        print("Order Sell id:Sell2A - Sleeping for 1 minute")  
                        time.sleep(60)  

                    else: print("You're in Selling phase, waiting to sell [2-6a] / ", end="")

                else: print("You're in Selling phase, waiting to sell [2-6b] / ", end="")

            #
            elif (float(bars.ema_D.iloc[-1]) > float(bars.close.iloc[-1]) > float(bars.ema_C.iloc[-1]) or
                  float(bars.close.iloc[-1]) > float(bars.ema_D.iloc[-1]) > float(bars.ema_C.iloc[-1]) ):

                # If the value of Minor1 is greater than or equal to 2, then the sell condition is:
                if 2 <= float(bars.Minor1.iloc[-1]):

                    # If the price suddenly goes down, then the sell condition is:
                    if ((float(bars.Minor1.iloc[-1]) - float(bars.Minor1.iloc[-3])) <= 
                        -math.log(float(bars.Minor1.iloc[-1]),2)):

                        n = 0
                        Minor1_iloc_3 = float(bars.Minor1.iloc[-3])
                        for _ in  range(3):
                            if ((float(bars.Minor1.iloc[-1]) - Minor1_iloc_3) <= 
                                -math.log(float(bars.Minor1.iloc[-1]),2)): n += 1
                            time.sleep(3)                      
                        if  n == 3: 
                            order_sell("Sell3A")
                            buyid = ''
                            print("Order Sell id:Sell3A - Sleeping for 1 minute")  
                            time.sleep(60)  

                        else: print("You're in Selling phase, waiting to sell [2-7a] / ", end="")

                    else: print("You're in Selling phase, waiting to sell [2-7b] / ", end="")

                else: print("You're in Selling phase, waiting to sell [2-7c] / ", end="")

            else: print("You're in Selling phase, waiting to sell [2-7d] / ", end="")

        # If the major trend starts to go bearish, then the bot sells immediately:
        elif float(bars.Major.iloc[-1]) <= -1.5:
            
            if buyid == 'Buy-RSI':

                #
                if float(bars.close.iloc[-1]) < place - 1:

                    n = 0
                    for _ in  range(5):
                        if buyid == 'Buy-RSI' and float(bars.close.iloc[-1]) < place - 1: n += 1
                        time.sleep(3)                      
                    if  n == 5: 
                        order_sell("Sell-RSIi")
                        buyid = ''
                        print("Order Sell id:Sell-RSIi - Sleeping for 1 minute")  
                        time.sleep(60)  

                    else: print("You're in Selling phase, waiting to sell [2-3a1] / ", end="")

                #
                elif (('sell-rsi' in sellstatus) and
                     ((float(bars.ema_A.iloc[-2]) >  float(bars.ema_B.iloc[-2])  and 
                       float(bars.ema_A.iloc[-1]) <= float(bars.ema_B.iloc[-1])) or
                       float(bars.RSI.iloc[-1])   <  float(bars.ema_R.iloc[-1])) and
                       float(bars.close.iloc[-1]) >  place - 0.75 and float(bars.Minor1.iloc[-1]) < 15):

                    n = 0
                    for _ in  range(3):
                        if (('sell-rsi' in sellstatus) and
                           ((float(bars.ema_A.iloc[-2]) >  float(bars.ema_B.iloc[-2])  and 
                             float(bars.ema_A.iloc[-1]) <= float(bars.ema_B.iloc[-1])) or
                             float(bars.RSI.iloc[-1])   <  float(bars.ema_R.iloc[-1])) and
                             float(bars.close.iloc[-1]) >  place - 0.75 and float(bars.Minor1.iloc[-1]) < 15): n += 1
                        time.sleep(3)                      
                    if  n == 3: 
                        order_sell("Sell-RSI")
                        buyid = ''
                        sellstatus = set()
                        print("Order Sell id:Sell-RSI - Sleeping for 1 minute")  
                        time.sleep(60)  

                    else: print("You're in Selling phase, waiting to sell [3-1a] / ", end="")

                else: print("You're in Selling phase, waiting to sell [3-1b] / ", end="")

            elif buyid == 'Buy-1B':

                # If the value of Minor1 is less than or equal to 1.5, then the sell condition is:
                if float(bars.Minor1.iloc[-1]) <= -2 and float(bars.close.iloc[-1]) <= place: 

                    n = 0
                    for _ in  range(3):
                        if float(bars.Minor1.iloc[-1]) <= -2 and float(bars.close.iloc[-1]) <= place: n += 1
                        time.sleep(3)                      
                    if  n == 3: 
                        order_sell("Sell-1Bi")
                        buyid = ''
                        print("Order Sell id:Sell-1Bi - Sleeping for 1 minute")  
                        time.sleep(60)  

                    else: print("You're in Selling phase, waiting to sell [3-2a] / ", end="")

                # If the price suddenly goes down, then the sell condition is:
                elif (2 <= float(bars.Minor1.iloc[-1]) and 
                     (float(bars.Minor1.iloc[-1]) - float(bars.Minor1.iloc[-3])) <= 
                     -math.log(float(bars.Minor1.iloc[-1]),2)):

                    n = 0
                    Minor1_iloc_3 = float(bars.Minor1.iloc[-3])
                    for _ in  range(3):
                        if (2 <= float(bars.Minor1.iloc[-1]) and 
                           (float(bars.Minor1.iloc[-1]) - Minor1_iloc_3) <= 
                           -math.log(float(bars.Minor1.iloc[-1]),2)): n += 1
                        time.sleep(3)                      
                    if  n == 3: 
                        order_sell("Sell-1B")
                        buyid = ''
                        print("Order Sell id:Sell-1B - Sleeping for 1 minute")  
                        time.sleep(60)  

                    else: print("You're in Selling phase, waiting to sell [3-2b] / ", end="")

                else: print("You're in Selling phase, waiting to sell [3-2c] / ", end="")  

            else: print("You're in Selling phase, waiting to sell [3-2d] / ", end="")           

    print_datetime()

# Function that contains the main codes/functions to run mm_bot 
def run_mmbot():
    global bars, position
    bars = get_bars() 
    position = get_position()               
    buy_sell_logic(get_placeholder_buy(), get_openvalue())

while True: # Loops the run_mmbot() function and automatically reruns it if there is an exception
    
    try: run_mmbot()
    except Exception as error: 
         print(error)
         continue
