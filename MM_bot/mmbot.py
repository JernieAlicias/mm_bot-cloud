import time, datetime, config, talib, pandas
from binance.client import Client
from mongodb import get_placeholder_buy, store_placeholder_buy, store_profit_history

client = Client(config.api_key, config.api_secret, testnet=True)
print("\nSuccessfully logged in", end="\n\n")

SYMBOL        = 'ETHUSDT'
ASSET         = 'USDT'
TIMEFRAME     = '1m'
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

# Gets our current wallet balance for the compution of profit
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
def print_data(id):
    print(f"Current: {get_last_price()}  /  Mark Price: {get_mark_price()}  /  {id}: {get_placeholder_buy(id)}  /  Position: {position}")
    print(f"Ema_3: {bars.ema_3.iloc[-1]}  /  Ema_6: {bars.ema_6.iloc[-1]}  /  LNRANG: {bars.LNRANG.iloc[-1]}")
    return 

# Gets the bars/klines in 1 minute data timeframe from Binance Futures then add the EMAs
def get_bars():
    datenow = datetime.datetime.now() - datetime.timedelta(days=1) # Used to indicate the date start of the bars
    bars = client.futures_historical_klines(SYMBOL, interval=TIMEFRAME, 
    start_str=datenow.strftime("%Y-%m-%d %H:%M:%S"))
    bars = pandas.DataFrame(bars, columns=['time','open','high',
    'low','close','vol','closetime','qav','trades','tbb','tbq','Nan'])
    bars = bars.set_index(bars.columns[0])
    bars["ema_3"]   = talib.EMA(bars.close, 3)
    bars["ema_6"]   = talib.EMA(bars.close, 6)
    bars["ema_13"]  = talib.EMA(bars.close, 13)
    bars["ema_21"]  = talib.EMA(bars.close, 21)
    bars["ema_35"]  = talib.EMA(bars.close, 35)
    bars["SMA"]     = talib.SMA(bars.close, 480)
    bars["SD"]      = talib.STDDEV(bars.close, 959, 1)
    bars["LNRANG"]  = talib.LINEARREG_ANGLE(bars.close, 15)
    return bars

# Function that initiates the order to Buy in Binance Futures market
def order_buy(id): 
    m, x, y, z = get_mark_price(), bars.ema_6.iloc[-1], bars.ema_6.iloc[-2], bars.ema_3.iloc[-2]
    client.futures_create_order(symbol=SYMBOL, side='BUY', type='MARKET', quantity=QTY_TRADE)   
    store_placeholder_buy(id, datetime.datetime.now().strftime("%x"), datetime.datetime.now().strftime("%X"), m, x, y, z)      
    print("Buying at Mark Price: ", m)
    print(f'Symbol: {SYMBOL} / Side: BUY / Quantity: {QTY_TRADE} / Current Position: {get_position()}')
    print(f"Sleeping for 5 seconds")
    print_datetime()
    time.sleep(5)

# Function that initiates the order to Sell in Binance Futures market
def order_sell():
    m, x, y, z = get_mark_price(), bars.ema_6.iloc[-1], bars.ema_6.iloc[-2], bars.ema_3.iloc[-2]
    client.futures_create_order(symbol=SYMBOL, side='SELL', type='MARKET', quantity=QTY_TRADE)     
    profit = get_wallet_balance() - wallet_balance
    store_profit_history(profit, datetime.datetime.now().strftime("%x"), datetime.datetime.now().strftime("%X"), m, x, y, z) 
    print("Profit gain: ", profit)
    print(f'Symbol: {SYMBOL} / Side: SELL / Quantity: {QTY_TRADE} / Current Position: {get_position()}')
    print(f"Sleeping for 5 seconds")
    print_datetime()
    time.sleep(5)

# Function for the buy and sell logic of mm_bot
def buy_sell_logic(place, id, num):
    print_data(id)

    if position < num*QTY_TRADE:   # BUYING PHASE

        if (get_mark_price() > (bars.ema_480.iloc[-1] + bars.SD.iloc[-1]*50/68)) or (2 > bars.LNRANG.iloc[-1] > -2):
            print("You're in Selling phase, waiting to buy [0] / ", end="")

        # The following are the conditions to satisify to get in the buying range
        elif (float(bars.ema_3.iloc[-1])  <  float(bars.ema_13.iloc[-1]) and
              float(bars.ema_6.iloc[-1])  <  float(bars.ema_13.iloc[-1]) and
              float(bars.ema_13.iloc[-1]) <  float(bars.ema_21.iloc[-1]) and
              float(bars.ema_21.iloc[-1]) <  float(bars.ema_35.iloc[-1])):

            # This condition tells the bot to wait for the lowest possible market price before buying
            if float(bars.ema_3.iloc[-1]) < float(bars.ema_6.iloc[-1]):             
               print("You're in Selling phase, waiting to buy for lower value / ", end="")

            # Once this condition is satisfied, the bot initiates the buy order
            elif (float(bars.ema_3.iloc[-2])  <  float(bars.ema_6.iloc[-2])  and 
                  float(bars.ema_13.iloc[-2]) <  float(bars.ema_21.iloc[-2]) and 
                  float(bars.ema_13.iloc[-1]) <  float(bars.ema_21.iloc[-1]) and 
                  float(bars.ema_6.iloc[-1])  <= get_mark_price()):
                  order_buy(id)

            else: print("You're in Selling phase, waiting to buy [1] / ", end="")

        else: print("You're in Selling phase, waiting to buy [2] / ", end="")
            
    else: # position = num*QTY_TRADE:   # SELLING PHASE
        
        # The following are the conditions to satisify to get in the selling range
        if (float(bars.ema_3.iloc[-1])  >  float(bars.ema_13.iloc[-1]) and
            float(bars.ema_6.iloc[-1])  >  float(bars.ema_13.iloc[-1]) and 
            float(bars.ema_13.iloc[-1]) >  float(bars.ema_21.iloc[-1]) and
            float(bars.ema_21.iloc[-1]) >  float(bars.ema_35.iloc[-1])):

            # This code tells the bot to wait for the highest possible market price before selling
            if float(bars.ema_3.iloc[-1]) > float(bars.ema_6.iloc[-1]) and get_mark_price() > place:
               print("You're in Buying phase, waiting to sell for higher value / ", end="")

            # Once this condition is satisfied, the bot initiates the sell order
            elif (float(bars.ema_3.iloc[-2])  >  float(bars.ema_6.iloc[-2])  and
                  float(bars.ema_13.iloc[-2]) >  float(bars.ema_21.iloc[-2]) and 
                  float(bars.ema_13.iloc[-1]) >  float(bars.ema_21.iloc[-1]) and 
                  float(bars.ema_6.iloc[-1])  >= get_mark_price() > place + 1.5):
                  order_sell()

            else: print("You're in Buying phase, waiting to sell [3] / ", end="")

        else: print("You're in Buying phase, waiting to sell [4] / ", end="")

    print_datetime()


while True: # To loop the following codes as fast as possible (about 1 second)
    
    bars = get_bars() 
    position = get_position()              
    wallet_balance = get_wallet_balance()  

    # The following new conditions are used to enable the bot to have 5 place (placeholders) for the buy value.
    # The purpose of these codes is to enable the bot to continue the buy & sell logic even if the mark price 
    # goes down unexpectedly and wait for the price to go up again to sell the previous place.

    if (position == 0  or 
       (position == 1 *QTY_TRADE and get_mark_price() >= get_placeholder_buy(id="place1")-3)): 
        buy_sell_logic(get_placeholder_buy(id="place1"), id="place1", num=1)

    for i in range(3):
        if ((position == (i+1)*QTY_TRADE and get_mark_price() <  get_placeholder_buy(id="place"+str(i+1))-3) or 
            (position == (i+2)*QTY_TRADE and get_mark_price() >= get_placeholder_buy(id="place"+str(i+2))-3)):
             buy_sell_logic(get_placeholder_buy(id="place"+str(i+2)), id="place"+str(i+2), num=i+2)
             break

    if (position == 5 *QTY_TRADE): buy_sell_logic(get_placeholder_buy(id="place5"), id="place5", num=5)
