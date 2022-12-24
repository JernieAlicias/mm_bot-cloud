import time, datetime, config, talib, pandas
from binance.client import Client
from mongodb import get_placeholder_buy, store_placeholder_buy, store_profit_history

client = Client(config.api_key, config.api_secret, testnet=True)
print("\nSuccessfully logged in", end="\n\n")

SYMBOL        = 'ETHUSDT'
ASSET         = 'USDT'
TIMEFRAME     = '5m'
QTY_TRADE     =  1

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
    print(f"Ema_B: {bars.ema_B.iloc[-1]}  /  Ema_C: {bars.ema_C.iloc[-1]}  /  LNRANG: {bars.LNRANG.iloc[-1]}")
    return 

# Gets the bars/klines in 5 minutes data timeframe from Binance Futures then adds the indicators
def get_bars():
    datenow = datetime.datetime.now() - datetime.timedelta(days=2) # Used to indicate the date start of the bars
    bars = client.futures_historical_klines(SYMBOL, interval=TIMEFRAME, 
    start_str=datenow.strftime("%Y-%m-%d %H:%M:%S"))
    bars = pandas.DataFrame(bars, columns=['time','open','high',
    'low','close','vol','closetime','qav','trades','tbb','tbq','Nan'])
    bars = bars.set_index(bars.columns[0])
    bars["ema_A"]  = talib.EMA(bars.close, 3)
    bars["ema_B"]  = talib.EMA(bars.close, 9)
    bars["ema_C"]  = talib.EMA(bars.close, 18)
    bars["ema_D"]  = talib.EMA(bars.close, 39)
    bars["ema_E"]  = talib.EMA(bars.close, 63)
    bars["ema_F"]  = talib.EMA(bars.close, 100)
    bars["SMA"]    = talib.SMA(bars.close, 300)
    bars["LNRANG"] = talib.LINEARREG_ANGLE(bars.SMA, 3)
    return bars

# Function that initiates the Buy order in Binance Futures market
def order_buy(): 
    m, x, y, z = get_mark_price(), bars.ema_C.iloc[-1], bars.ema_C.iloc[-2], bars.ema_B.iloc[-2]
    client.futures_create_order(symbol=SYMBOL, side='BUY', type='MARKET', quantity=QTY_TRADE)   
    store_placeholder_buy(datetime.datetime.now().strftime("%x"), datetime.datetime.now().strftime("%X"), m, x, y, z)      
    print("Buying at Mark Price: ", m)
    print(f'Symbol: {SYMBOL} / Side: BUY / Quantity: {QTY_TRADE} / Current Position: {get_position()}')
    print_datetime()

# Function that initiates the Sell order in Binance Futures market
def order_sell():
    m, x, y, z = get_mark_price(), bars.ema_C.iloc[-1], bars.ema_C.iloc[-2], bars.ema_B.iloc[-2]
    client.futures_create_order(symbol=SYMBOL, side='SELL', type='MARKET', quantity=QTY_TRADE)     
    profit = get_wallet_balance() - wallet_balance
    store_profit_history(profit, datetime.datetime.now().strftime("%x"), datetime.datetime.now().strftime("%X"), m, x, y, z) 
    print("Profit gain: ", profit)
    print(f'Symbol: {SYMBOL} / Side: SELL / Quantity: {QTY_TRADE} / Current Position: {get_position()}')
    print_datetime()

# Function for the buy and sell logic of mm_bot
def buy_sell_logic(place):
    print_data()

    if position < QTY_TRADE: # BUYING PHASE
        
        # If the main trend starts to go bullish, then the bot buys immediately
        if float(bars.LNRANG.iloc[-1]) >= 1.5:

            if float(bars.LNRANG.iloc[-3]) >= 1.5 and float(bars.LNRANG.iloc[-1]) >= 1.5: 
               print("You're in Buying phase, waiting to buy [1] / ", end="")

            else: 
                n = 0
                for _ in  range(3):
                      if (float(bars.LNRANG.iloc[-5]) < 1.5 and float(bars.LNRANG.iloc[-4]) <  1.5 and 
                          float(bars.LNRANG.iloc[-3]) < 1.5 and float(bars.LNRANG.iloc[-1]) >= 1.5 and
                          float(bars.ema_A.iloc[-1])  > float(bars.ema_B.iloc[-1])): n += 1
                      time.sleep(3)
                if n == 3: 
                      order_buy()
                      print("Order Buy # 1 - Sleeping for 5 minutes")  
                      time.sleep(300)  
                else: print("You're in Buying phase, waiting to buy [2] / ", end="")

        # If the main trend goes sideways, then the bot has the following buy condition:
        elif 1.5 > float(bars.LNRANG.iloc[-1]) > -1.5: 
            
            # If ema_A crosses ema_B from below, then the bot buys immediately
            if (float(bars.ema_A.iloc[-3]) <  float(bars.ema_B.iloc[-3]) < float(bars.ema_C.iloc[-3]) < 
                float(bars.ema_D.iloc[-3]) <  float(bars.ema_E.iloc[-3]) < float(bars.ema_F.iloc[-3]) and 
                float(bars.ema_A.iloc[-2]) >= float(bars.ema_B.iloc[-2])): 
                order_buy()
                print("Order Buy # 2")

            else: print("You're in Buying phase, waiting to buy [3] / ", end="")

        # If the main trend starts to go bearish, the bot has the following buy conditions:
        elif float(bars.LNRANG.iloc[-1]) <= -1.5:
            
            # If the latest close price crosses the SMA from below, then the bot buys immediately
            if (float(bars.SMA.iloc[-3]) >  float(bars.close.iloc[-3]) and 
                float(bars.SMA.iloc[-2]) <= float(bars.close.iloc[-2])): 
                order_buy()
                print("Order Buy # 3")
            
            # If ema_D crosses ema_E from below, then the bot buys immediately
            elif (float(bars.ema_D.iloc[-3]) <  float(bars.ema_E.iloc[-3]) and
                  float(bars.ema_D.iloc[-2]) >= float(bars.ema_E.iloc[-2])):
                  order_buy()
                  print("Order Buy # 4")

            else: print("You're in Buying phase, waiting to buy [4] / ", end="")

    else: # position = QTY_TRADE: # SELLING PHASE
        
        # If the main trend starts to go bearish, then the bot sells immediately
        if float(bars.LNRANG.iloc[-1]) <= -1.5:
            
            if float(bars.LNRANG.iloc[-3]) <= -1.5 and float(bars.LNRANG.iloc[-1]) <= -1.5: 
               print("You're in Selling phase, waiting to sell [5] / ", end="")

            else: 
                n = 0
                for _ in  range(3):
                      if (float(bars.LNRANG.iloc[-5]) > -1.5 and float(bars.LNRANG.iloc[-4]) >  -1.5 and 
                          float(bars.LNRANG.iloc[-3]) > -1.5 and float(bars.LNRANG.iloc[-1]) <= -1.5 and
                          float(bars.ema_A.iloc[-1])  < float(bars.ema_B.iloc[-1])): n += 1
                      time.sleep(3)
                if n == 3: 
                      order_sell()
                      print("Order Sell # 1")    
                else: print("You're in Selling phase, waiting to sell [6] / ", end="")

        # If the main trend goes sideways, then the bot has the following sell condition:
        elif 1.5 > float(bars.LNRANG.iloc[-1]) > -1.5: 
            
            # If ema_A crosses ema_B from above, then the bot sells immediately
            if (float(bars.ema_A.iloc[-3]) >  float(bars.ema_B.iloc[-3]) > float(bars.ema_C.iloc[-3]) > 
                float(bars.ema_D.iloc[-3]) >  float(bars.ema_E.iloc[-3]) > float(bars.ema_F.iloc[-3]) and 
                float(bars.ema_A.iloc[-2]) <= float(bars.ema_B.iloc[-2])): 
                order_sell()
                print("Order Sell # 2")

            else: print("You're in Selling phase, waiting to sell [7] / ", end="")

        # If the main trend starts to go bullish, then the bot has the following sell conditions:
        elif float(bars.LNRANG.iloc[-1]) >= 1.5:
            
            # If the latest mark price crosses the SMA from above, then the bot sells immediately
            if   ((float(bars.SMA.iloc[-2])   <  float(bars.close.iloc[-2])  and 
                   float(bars.SMA.iloc[-1])   >= get_mark_price() > place + 1.5)): 
                   order_sell() 
                   print("Order Sell # 3")

            # If ema_A crosses ema_B from above, then the bot sells immediately
            elif ((float(bars.ema_A.iloc[-3]) >  float(bars.ema_B.iloc[-3]) and
                   float(bars.ema_A.iloc[-2]) <= float(bars.ema_B.iloc[-2]) and 
                   float(bars.close.iloc[-1]) >  place + 1.5)): 
                   order_sell()  
                   print("Order Sell # 4")

            # If the price goes down below the placeholder value, then the bot sells immediately
            elif  (float(bars.close.iloc[-2]) <  place - 1): 
                   order_sell()    
                   print("Order Sell # 5")     

            else:  print("You're in Selling phase, waiting to sell [8] / ", end="")              

    print_datetime()

# Function that contains the main codes/functions to run mm_bot 
def run_mmbot():
    global bars, position, wallet_balance
    bars = get_bars() 
    position = get_position()              
    wallet_balance = get_wallet_balance()  
    buy_sell_logic(get_placeholder_buy())

while True: # Loops the run_mmbot() function and automatically reruns it if there is an exception
    
    try: run_mmbot()
    except Exception as error: 
         print(error)
         continue
