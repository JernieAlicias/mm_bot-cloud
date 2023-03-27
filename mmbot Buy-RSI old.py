import time, datetime, config, talib, pandas
from binance.client import Client
from mongodb import (get_placeholder_buy, store_profit_history, store_buyval_history, 
store_datab_walletbal, get_datab_walletbal, get_openvalue)

client = Client(config.api_key, config.api_secret, testnet=True)
print("\nSuccessfully logged in", end="\n\n")

SYMBOL     = 'ETHUSDT'
ASSET      = 'USDT'
TIMEFRAME  = '1m'
QTY_TRADE  =  1
tempvalue  =  0
minor0_val =  0
Minor1_4   =  0
Minor1_5   =  0
rsi_val    =  0
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
    print(f"Current: {get_last_price()}  /  Place: {get_placeholder_buy()}  /  Position: {position}  /  Buystatus: {buystatus}  /  Sellstatus: {sellstatus}  /  tempval: {tempvalue}")
    print(f"Major: {bars.Major.iloc[-1]}  /  Minor0: {bars.Minor0.iloc[-1]}  /  Minor1: {bars.Minor1.iloc[-1]}  /  RSI: {bars.RSI.iloc[-1]}")
    print(f"Minor1[-4]: {bars.Minor1.iloc[-4]}  /  Minor1[-5]: {bars.Minor1.iloc[-5]}  /  Minor0[-3]: {bars.Minor0.iloc[-3]}")
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
    bars["Minor0"] = talib.LINEARREG_ANGLE(bars.ema_B, 4)
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
    global tempvalue, minor0_val, Minor1_4, Minor1_5, rsi_val, buyid, buystatus, sellstatus

    if position == 0:

        sellstatus = set()

        if (('dontbuy' not in buystatus) and ((float(bars.Minor1.iloc[-2]) < -20 and 
            float(bars.Minor1.iloc[-1]) < -20) or float(bars.Minor1.iloc[-1]) - float(bars.Minor1.iloc[-3]) < -2 or
            float(bars.Minor1.iloc[-1]) - float(bars.Minor1.iloc[-2]) < -1.5)): 
            buystatus.add('dontbuy')

        if ('dontbuy' in buystatus) and float(bars.Minor1.iloc[-1]) - float(bars.Minor1.iloc[-2]) > -0.75: 
            buystatus.discard('dontbuy')


        if ('buy-rsi' not in buystatus):

            if float(bars.close.iloc[-1]) <= float(bars.ema_C.iloc[-1]):  
                minor0_val =  -20
                Minor1_4   =  -float(bars.Minor1.iloc[-4])
                Minor1_5   =  -float(bars.Minor1.iloc[-5])
                rsi_val    =   45

            elif float(bars.close.iloc[-1]) > float(bars.ema_C.iloc[-1]): 
                minor0_val =  -10
                Minor1_4   =   float(bars.Minor1.iloc[-4])
                Minor1_5   =   float(bars.Minor1.iloc[-5])
                rsi_val    =   55
                

            if (float(bars.Minor0.iloc[-2]) < minor0_val and Minor1_4 >= 3 and # adjusted to (3) 03/03 3:06
                float(bars.close.iloc[-2]) < float(bars.open.iloc[-2]) and float(bars.Minor1.iloc[-1]) > -10 and
                float(bars.close.iloc[-1]) > min(float(bars.open.iloc[-1]), float(bars.close.iloc[-2])) + 1.5):

                n = 0
                minval = min(float(bars.open.iloc[-1]), float(bars.close.iloc[-2]))
                for _ in  range(20): #adjusted 03/03 10:21, 03/06 7:13
                    if float(bars.close.iloc[-1]) > minval + 1.5: n += 1
                    else: break
                    time.sleep(1)                      
                if  n == 20: 
                    buyid = 'Buy-RSI'
                    order_buy(buyid)
                    buystatus = set()
                    tempvalue = 0
                    print("Order Buy id:Buy-RSI [0a]")  

                else: print("You're in Buying phase, waiting to buy [0a] / ", end="")    
            
            elif (float(bars.RSI.iloc[-3]) - float(bars.RSI.iloc[-4]) < 1.5  and Minor1_5 >= 3 and
                  float(bars.RSI.iloc[-3]) < rsi_val and float(bars.RSI.iloc[-2]) - float(bars.RSI.iloc[-3]) > 0.5 and
                  float(bars.close.iloc[-2]) < float(bars.open.iloc[-3]) + 2 and float(bars.Minor0.iloc[-3]) < minor0_val):
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

    elif position == 1:

        buystatus = set()

        if (buyid == 'Buy-RSI' and float(bars.ema_R.iloc[-2]) - float(bars.ema_R.iloc[-3]) > 0 and
            float(bars.ema_R.iloc[-2]) > 45): 
            sellstatus.add('sell-rsi')
            print("sellstatus: 'sell-rsi' added")


    if position < QTY_TRADE: # BUYING PHASE

        if ('dontbuy' in buystatus): 
            
            if float(bars.close.iloc[-1]) < tempvalue - 1: 
                buystatus.discard('buy-rsi')
                tempvalue = 0
                print("buystatus: 'buy-rsi' removed [1]")
            
            print("You're in Buying phase, waiting to buy [-] / ", end="") 

        elif (float(bars.high.iloc[-1]) == float(bars.high.iloc[-2]) or 
              float(bars.low.iloc[-1])  == float(bars.low.iloc[-2])  or
              float(bars.high.iloc[-2]) == float(bars.high.iloc[-3]) or 
              float(bars.low.iloc[-2])  == float(bars.low.iloc[-3])):
            
            print("You're in Buying phase, waiting to buy [--] / ", end="") 
            buystatus.discard('buy-rsi')
            tempvalue = 0
            time.sleep(600)

        elif ('buy-rsi' in buystatus):

            if float(bars.close.iloc[-1]) >= tempvalue + 0.25 > float(bars.open.iloc[-1]):

                n = 0
                for _ in  range(10): # adjusted 03/06 7:14
                    if float(bars.close.iloc[-1]) >= tempvalue + 0.25 > float(bars.open.iloc[-1]): n += 1
                    else: break
                    time.sleep(1)                      
                if  n == 10: 
                    buyid = 'Buy-RSI'
                    order_buy(buyid)
                    buystatus = set()
                    tempvalue = 0
                    print("Order Buy id:Buy-RSI [1]")  
                    time.sleep(30)

                else: print("You're in Buying phase, waiting to buy [1a] / ", end="")   

            elif tempvalue + 0.25 > float(bars.close.iloc[-1]) > tempvalue - 1:

                if float(bars.close.iloc[-2]) < tempvalue: 
                    tempvalue = float(bars.close.iloc[-2])
                    time.sleep(15)
                    
                print("You're in Buying phase, waiting to buy [1b] / ", end="")

            else: 
                n = 0
                for _ in  range(30):
                    if float(bars.close.iloc[-1]) <= tempvalue - 1: n += 1
                    else: break
                    time.sleep(1)                      
                if  n == 30: 
                    buystatus.discard('buy-rsi')
                    print("buystatus: 'buy-rsi' removed")

                else: print("You're in Buying phase, waiting to buy [1c] / ", end="")             

        else: print("You're in Buying phase, waiting to buy [1d] / ", end="")      


    else: # position = QTY_TRADE: # SELLING PHASE

        if (('sell-rsi' in sellstatus) and
            float(bars.close.iloc[-1]) < ((float(bars.close.iloc[-3]) + float(bars.open.iloc[-3]))/2) and
            float(bars.close.iloc[-1]) >  place + 1):

            n = 0
            for _ in  range(20):
                if (('sell-rsi' in sellstatus) and
                    float(bars.close.iloc[-1]) < ((float(bars.close.iloc[-3]) + float(bars.open.iloc[-3]))/2) and
                    float(bars.close.iloc[-1]) >  place + 1): n += 1
                else: break
                time.sleep(1)                      
            if  n == 20: 
                order_sell("Sell-RSI")
                buyid = ''
                sellstatus = set()
                print("Order Sell id:Sell-RSI [2a] - Sleeping for 1 minute")  
                time.sleep(60)  

            else: print("You're in Selling phase, waiting to sell [2] / ", end="")

        elif (float(bars.close.iloc[-1]) < ((float(bars.close.iloc[-3]) + float(bars.open.iloc[-3]))/2) and
              place + 1 >= float(bars.close.iloc[-1]) >  place):
            
            n = 0
            for _ in  range(30):
                if (('sell-rsi' in sellstatus) and
                    float(bars.close.iloc[-1]) < ((float(bars.close.iloc[-3]) + float(bars.open.iloc[-3]))/2) and
                    float(bars.close.iloc[-1]) >  place + 1): n += 1
                else: break
                time.sleep(1)                      
            if  n == 30: 
                order_sell("Sell-RSIi")
                buyid = ''
                sellstatus = set()
                print("Order Sell id:Sell-RSIi [2a] - Sleeping for 1 minute")  
                time.sleep(60)  

            else: print("You're in Selling phase, waiting to sell [2a] / ", end="")
            
        elif float(bars.close.iloc[-1]) < place - 1.5:

            n = 0
            for _ in  range(45):
                if place - 2.5 < float(bars.close.iloc[-1]) < place - 1.5: n += 1
                else: break
                time.sleep(1)                      
            if  n == 45: 
                order_sell("Sell-RSIi")
                buyid = ''
                print("Order Sell id:Sell-RSIi [2b]- Sleeping for 1 minute")  
                time.sleep(60)  

            elif float(bars.close.iloc[-1]) < place - 2:

                n = 0
                for _ in  range(5):
                    if float(bars.close.iloc[-1]) < place - 2: n += 1
                    else: break
                    time.sleep(1)                      
                if  n == 5: 
                    order_sell("Sell-RSIi")
                    buyid = ''
                    print("Order Sell id:Sell-RSIi [2c]- Sleeping for 1 minute")  
                    time.sleep(60)  

                else: print("You're in Selling phase, waiting to sell [2b] / ", end="")

            else: print("You're in Selling phase, waiting to sell [2c] / ", end="")

        else: print("You're in Selling phase, waiting to sell [2d] / ", end="")

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

