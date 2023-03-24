import time, datetime, config, talib, pandas
from binance.client import Client
from mongodb import (get_placeholder_buy, store_profit_history, store_buyval_history, 
store_datab_walletbal, get_datab_walletbal)

client = Client(config.api_key, config.api_secret, testnet=True)
print("\nSuccessfully logged in", end="\n\n")

SYMBOL     = 'ETHUSDT'
ASSET      = 'USDT'
TIMEFRAME  = '1m'
QTY_TRADE  =  1
tempvalue  =  0
Minor0     =  0
Minor1_4   =  0
Minor1_5   =  0
buyid      = ''
m0stat     = False
sell1stat  = False
buystatus  = set()

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

# Function that prints the current price, mark price, position, and other data on the display
def print_data():
    print(f"Current: {get_last_price()}  /  Place: {get_placeholder_buy()}  /  Position: {position}  /  Buystatus: {buystatus}  /  tempval: {tempvalue}  /  m0stat: {m0stat}  /  sell1stat: {sell1stat}")
    print(f"Major: {bars.Major.iloc[-1]}  /  Minor0[-2]: {Minor0}  /  Minor1: {bars.Minor1.iloc[-1]}  /  RSI: {bars.RSI.iloc[-1]}")
    print(f"Minor1[-2]: {bars.Minor1.iloc[-2]} / Minor1[-4]: {bars.Minor1.iloc[-4]} / Minor1[-5]: {bars.Minor1.iloc[-5]}")
    print(f"reqminorval(3): {round(reqminorval(3),4)} / reqminorval(4): {round(reqminorval(4),4)} / reqval(0.4): {round(reqval(0.4),4)} / reqval(0.8): {round(reqval(0.8),4)} / reqval(1.2): {round(reqval(1.2),4)} / reqval(1.6): {round(reqval(1.6),4)}")
    print(f"reqminorval(30): {round(reqminorval(30),4)} / reqminorval(5): {round(reqminorval(5),4)} / reqminorval(60): {round(reqminorval(60),4)} / reqminorval(20): {round(reqminorval(20),4)}")
    print(f"RSI[-1]: {float(bars.RSI.iloc[-1])} / RSI[-2]: {float(bars.RSI.iloc[-2])} / ema_R[-1]: {float(bars.ema_R.iloc[-1])} / ema_R[-2]: {float(bars.ema_R.iloc[-2])}")
    return 

# Used to determine the minimum requred value for a close price that needs to be met before executing
def reqval(x):
    n = 360
    return (sum(abs(float(x)-float(y)) for (x,y) in 
            zip(bars.close.iloc[-(n+1):-1].tolist(), bars.close.iloc[-(n+2):-2].tolist()))/n)*x

# Used to determine the minimum requred value for a Minor trend that needs to be met before executing
def reqminorval(x):
    n = 360
    return (sum(abs(float(x)-float(y)) for (x,y) in 
            zip(bars.Minor1.iloc[-(n+1):-1].tolist(), bars.Minor1.iloc[-(n+2):-2].tolist()))/n)*x

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
    bars["Minor0"] = talib.LINEARREG_ANGLE(bars.ema_B, 4)
    bars["Minor1"] = talib.LINEARREG_ANGLE(bars.ema_C, 4)
    bars["Minor2"] = talib.LINEARREG_ANGLE(bars.ema_D, 4)
    return bars

# Function that initiates the Buy order in Binance Futures market
def order_buy(buyid): 
    m, x, y, z, w = get_last_price(), bars.Minor0.iloc[-1], bars.Minor1.iloc[-1], bars.RSI.iloc[-1], bars.ema_R.iloc[-1]
    a, b, c, d, e, f = reqval(0.4), reqval(0.8), reqval(1.2), reqval(1.6), reqminorval(40), reqminorval(6)
    g, h = reqminorval(40), reqminorval(20)
    client.futures_create_order(symbol=SYMBOL, side='BUY', type='MARKET', quantity=QTY_TRADE)      
    store_buyval_history(buyid, (datetime.datetime.now()+datetime.timedelta(hours=8)).strftime("%x"), (datetime.datetime.now()+datetime.timedelta(hours=8)).strftime("%X"), 
                         m, x, bars.Minor0.iloc[-2], bars.Minor0.iloc[-3], y, bars.Minor1.iloc[-2], bars.Minor1.iloc[-3],
                         bars.Minor1.iloc[-4], bars.Minor1.iloc[-5], a, b, c, d, e, f, g, h, z, bars.RSI.iloc[-2], w, bars.ema_R.iloc[-2], tempvalue)
    print("Buying at Mark Price: ", m)
    print(f'Symbol: {SYMBOL} / Side: BUY / Quantity: {QTY_TRADE} / Current Position: {get_position()}')
    print_datetime()

# Function that initiates the Sell order in Binance Futures market
def order_sell(sellid):
    m, x, y, z, w = get_last_price(), reqval(0.4), reqval(0.8), reqval(1.2), reqval(1.6)
    client.futures_create_order(symbol=SYMBOL, side='SELL', type='MARKET', quantity=QTY_TRADE)     
    profit = get_wallet_balance() - get_datab_walletbal()
    store_profit_history(sellid, profit, (datetime.datetime.now()+datetime.timedelta(hours=8)).strftime("%x"), (datetime.datetime.now()+datetime.timedelta(hours=8)).strftime("%X"), m, x, y, z, w)
    store_datab_walletbal(get_wallet_balance())
    print("Profit gain: ", profit)
    print(f'Symbol: {SYMBOL} / Side: SELL / Quantity: {QTY_TRADE} / Current Position: {get_position()}')
    print_datetime()

# Function for the buy and sell logic of mm_bot
def buy_sell_logic(place):
    print_data()
    global tempvalue, Minor1_4, Minor1_5, buyid, buystatus, Minor0, m0stat, sell1stat

    if position == 0:
            
        if (('dontbuy' not in buystatus) and ((float(bars.Minor1.iloc[-2]) < -reqminorval(40) and 
            float(bars.Minor1.iloc[-1]) < -reqminorval(40)) or float(bars.Minor1.iloc[-1]) - float(bars.Minor1.iloc[-3]) < -reqminorval(4) or
            float(bars.Minor1.iloc[-1]) - float(bars.Minor1.iloc[-2]) < -reqminorval(3))): 
            buystatus.add('dontbuy')

        if (('dontbuy' in buystatus) and (float(bars.Minor1.iloc[-1]) - float(bars.Minor1.iloc[-2]) > -reqminorval(1.5) or
            (float(bars.close.iloc[-1]) > float(bars.open.iloc[-1]) and float(bars.close.iloc[-2]) > float(bars.open.iloc[-2])) or
                float(bars.close.iloc[-1]) > min(float(bars.open.iloc[-1]), float(bars.close.iloc[-2])) + reqval(1.2))): 
            buystatus.discard('dontbuy')


        if ('buy-rsi' not in buystatus):
        
            if float(bars.close.iloc[-1]) <= float(bars.ema_C.iloc[-1]):  
                Minor1_4   =  -float(bars.Minor1.iloc[-4])
                Minor1_5   =  -float(bars.Minor1.iloc[-5])

            elif float(bars.close.iloc[-1]) > float(bars.ema_C.iloc[-1]): 
                Minor1_4   =   float(bars.Minor1.iloc[-4])
                Minor1_5   =   float(bars.Minor1.iloc[-5])


            if  m0stat == False: Minor0 = float(bars.Minor0.iloc[-2])

            if  float(bars.Minor0.iloc[-2]) <= -reqminorval(30): 
                Minor0 =  float(bars.Minor0.iloc[-2])
                m0stat =  True

            if  m0stat == True and float(bars.Minor0.iloc[-2]) > reqminorval(30): 
                Minor0 =  float(bars.Minor0.iloc[-2])
                m0stat =  False
                

            if (('dontbuy' not in buystatus) and (Minor0 < -reqminorval(30) or float(bars.RSI.iloc[-2]) < 30) and 
                Minor1_4 >= reqminorval(5) and float(bars.RSI.iloc[-2]) < 45 and float(bars.Minor1.iloc[-1]) > -reqminorval(20) and
                float(bars.close.iloc[-1]) > min(float(bars.open.iloc[-1]), float(bars.close.iloc[-2])) + reqval(1.2) and
                float(bars.close.iloc[-1]) > float(bars.open.iloc[-1])):

                n, m = 0, 0
                minval = min(float(bars.open.iloc[-1]), float(bars.close.iloc[-2]))
                for _ in  range(30): #adjusted 03/03 10:21, 03/06 7:13, 03/14 9:30 (20 to 30)
                    if  float(bars.close.iloc[-1]) > minval + reqval(1.6): m += 10
                    if (float(bars.close.iloc[-1]) > minval + reqval(1.2) and 
                        float(bars.close.iloc[-1]) > float(bars.open.iloc[-1])): n += 1
                    else: break
                    if  m == 30: break
                    time.sleep(1)                      
                if  n == 30 or m == 30: 
                    buyid = 'Buy-RSI'
                    order_buy('Buy-RSI [0a]')
                    buystatus = set()
                    tempvalue = 0
                    print("Order Buy id:Buy-RSI [0a]") 
                    time.sleep(30)  

                else: print("You're in Buying phase, waiting to buy [0a] / ", end="")    
            
            elif (float(bars.RSI.iloc[-3]) < 30 or (float(bars.RSI.iloc[-3]) - float(bars.RSI.iloc[-4]) < 1.5 and Minor1_5 >= reqminorval(5) and
                    float(bars.RSI.iloc[-3]) < 45 and float(bars.RSI.iloc[-2]) - float(bars.RSI.iloc[-3]) > 0.5 and Minor0 < -reqminorval(30))):
                    buystatus.add('buy-rsi')
                    tempvalue = float(bars.close.iloc[-2])
                    print("buystatus: 'buy-rsi' added [0]")
                    time.sleep(15) 

        if ('buy-rsi' in buystatus):    

            if (float(bars.ema_A.iloc[-3]) > float(bars.ema_B.iloc[-3]) and 
                float(bars.ema_A.iloc[-2]) < float(bars.ema_B.iloc[-2])):
                buystatus.discard('buy-rsi')   
                tempvalue = 0
                print("buystatus: 'buy-rsi' removed [0]")             

    elif position == 1: buystatus = set()


    if position < QTY_TRADE: # BUYING PHASE

        if ('dontbuy' in buystatus): 
            
            if ('buy-rsi' in buystatus) and float(bars.close.iloc[-1]) < tempvalue - reqval(0.8): 

                if float(bars.close.iloc[-2]) < tempvalue: 
                    tempvalue = float(bars.close.iloc[-2])
            
            print("You're in Buying phase, waiting to buy [-] / ", end="") 

        elif ('buy-rsi' in buystatus):

            if (float(bars.close.iloc[-2]) >= (tempvalue + reqval(0.4)) and
                float(bars.close.iloc[-3]) > float(bars.close.iloc[-4]) and
                float(bars.RSI.iloc[-2])   > float(bars.ema_R.iloc[-2])):
                buyid = 'Buy-RSI'
                order_buy('Buy-RSI [1]')
                buystatus = set()
                tempvalue = 0
                print("Order Buy id:Buy-RSI [1]")  
                time.sleep(30) 

            elif tempvalue + reqval(0.4) > float(bars.close.iloc[-1]) > tempvalue - reqval(0.8):

                if float(bars.close.iloc[-2]) < tempvalue: 
                    tempvalue = float(bars.close.iloc[-2])
                    time.sleep(15)
                    
                print("You're in Buying phase, waiting to buy [1b] / ", end="")

            else: 
                n = 0
                for _ in  range(30):
                    if float(bars.close.iloc[-1]) <= tempvalue - reqval(0.8): n += 1
                    else: break
                    time.sleep(1)                      
                if  n == 30: 
                    buystatus.discard('buy-rsi')
                    tempvalue = 0
                    print("buystatus: 'buy-rsi' removed / ", end="")
                    print("You're in Buying phase, waiting to buy [1b~] / ", end="")

                else: 
                    if float(bars.close.iloc[-2]) < tempvalue: 
                        tempvalue = float(bars.close.iloc[-2])
                    print("You're in Buying phase, waiting to buy [1c] / ", end="")             

        else: print("You're in Buying phase, waiting to buy [1d] / ", end="")      


    else: # position = QTY_TRADE: # SELLING PHASE

        if  float(bars.close.iloc[-2]) >  place + reqval(0.4): sell1stat = True

        if (float(bars.close.iloc[-1]) < ((float(bars.close.iloc[-3]) + float(bars.open.iloc[-3]))/2) and
           (float(bars.close.iloc[-1]) >   place + reqval(0.4) or sell1stat) and 
            float(bars.close.iloc[-1]) <   float(bars.open.iloc[-1])):

            n, m = 0, 0
            for _ in  range(30):
                if    float(bars.close.iloc[-1]) <    float(bars.open.iloc[-3]): n += 5 
                elif (float(bars.close.iloc[-1]) <  ((float(bars.close.iloc[-3]) + float(bars.open.iloc[-3]))/2) and
                     (float(bars.close.iloc[-1]) >    place + reqval(0.4) or sell1stat) and 
                      float(bars.close.iloc[-1]) <    float(bars.open.iloc[-1])): n += 1
                elif  float(bars.close.iloc[-1]) >= ((float(bars.close.iloc[-3]) + float(bars.open.iloc[-3]))/2): m += 1
                else: break
                if m == 3 or n >= 30: break
                time.sleep(1)                      
            if  n >= 27: 
                order_sell("Sell-RSI [2]")
                sell1stat = False
                buyid = ''
                print("Order Sell id:Sell-RSI [2] - Sleeping for 1 minute")  
                time.sleep(30)  

            else: print("You're in Selling phase, waiting to sell [2] / ", end="")
            
        elif (float(bars.close.iloc[-1]) < place - reqval(0.8) and
              float(bars.close.iloc[-1]) < float(bars.open.iloc[-1])):

            n = 0
            for _ in  range(60):
                if (place - reqval(1.6) < float(bars.close.iloc[-1]) < place - reqval(0.8) and
                    float(bars.close.iloc[-1]) < float(bars.open.iloc[-1])): n += 1
                else: break
                time.sleep(1)                      
            if  n == 60: 
                order_sell("Sell-RSIi [2b]")
                sell1stat = False
                buyid = ''
                print("Order Sell id:Sell-RSIi [2b]")  

            elif (float(bars.close.iloc[-1]) < place - reqval(1.6) and
                  float(bars.close.iloc[-1]) < float(bars.open.iloc[-1])):

                n = 0
                for _ in  range(2):
                    if (float(bars.close.iloc[-1]) < place - reqval(1.6) and
                        float(bars.close.iloc[-1]) < float(bars.open.iloc[-1])): n += 1
                    else: break
                    time.sleep(1)                      
                if  n == 2: 
                    order_sell("Sell-RSIi [2c]")
                    sell1stat = False
                    buyid = ''
                    print("Order Sell id:Sell-RSIi [2c]")  

                else: print("You're in Selling phase, waiting to sell [2b] / ", end="")

            else: print("You're in Selling phase, waiting to sell [2c] / ", end="")

        else: print("You're in Selling phase, waiting to sell [2d] / ", end="")

    print_datetime()

# Function that contains the main codes/functions to run mm_bot 
def run_mmbot():
    global bars, position
    bars = get_bars() 
    position = get_position()               
    buy_sell_logic(get_placeholder_buy())

while True: # Loops the run_mmbot() function and automatically reruns it if there is an exception
    
    try: run_mmbot()
    except Exception as error: 
         print(error)
         continue

