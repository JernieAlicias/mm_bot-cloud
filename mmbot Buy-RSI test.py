import time, datetime, config, talib, pandas
from binance.client import Client
from mongodb import (get_placeholder_buy, store_profit_history, store_buyval_history, 
store_datab_walletbal, get_datab_walletbal, get_openvalue)

liveapi_key    = "tEbUF9Yr2Vc8Ci8fBYMROuJFYWqAUrq7qj0SX71obxA3qgJK8t1xA1g6CcU2pIRg"
liveapi_secret = "qshZq6hVedQRRDyyYKg1PO5yz382qry6vVNXZCQpJGkw5yLj5Rv5u2nNGbYAKzS5"

client = Client(liveapi_key, liveapi_secret, testnet=False)
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

    n=360
    x=[abs(float(x)-float(y)) for (x,y) in zip(bars.Minor1.iloc[-(n+1):-1].tolist(), bars.Minor1.iloc[-(n+2):-2].tolist())]
    print(len(bars))
    print(len(x))
    print(sum(x)/n)


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

