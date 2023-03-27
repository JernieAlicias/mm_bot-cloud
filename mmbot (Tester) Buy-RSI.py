import datetime, talib, pandas, math, config
from binance.client import Client

liveapi_key    = "tEbUF9Yr2Vc8Ci8fBYMROuJFYWqAUrq7qj0SX71obxA3qgJK8t1xA1g6CcU2pIRg"
liveapi_secret = "qshZq6hVedQRRDyyYKg1PO5yz382qry6vVNXZCQpJGkw5yLj5Rv5u2nNGbYAKzS5"

client = Client(liveapi_key, liveapi_secret, testnet=False)
print("\nSuccessfully logged in", end="\n\n")

SYMBOL    = 'LTCUSDT'
ASSET     = 'USDT'
TIMEFRAME = '1m'
QTY_TRADE =  1

position  = 0
buyvalue  = 0
openvalue = 0
buyid     = ''
bstatus   = set()
sstatus   = set()
p1  = 0
b1  = 0
o1  = 0
bi1 = ''
bst = set()
sst = set()

def highlow(x):

    try: return (max(float(x['close']), float(x['close[-2]']), float(x['close[-3]']), float(x['close[-4]']), 
                float(x['close[-5]']), float(x['close[-6]']), float(x['close[-7]']), float(x['close[-8]']), 
                float(x['close[-9]']), float(x['close[-10]']), float(x['close[-11]']), float(x['close[-12]']), 
                float(x['close[-13]']), float(x['close[-14]']), float(x['close[-15]']))         
          - min(float(x['close']), float(x['close[-2]']), float(x['close[-3]']), float(x['close[-4]'])))
    
    except: return None

def get_bars():
    datestart = datetime.datetime.now() - datetime.timedelta(days=15) # Used to indicate the date start of the bars
    bars = client.futures_historical_klines(SYMBOL, interval=TIMEFRAME, 
    start_str=datestart.strftime("%Y-%m-%d %H:%M:%S"))
    bars = pandas.DataFrame(bars, columns=['time','open','high',
    'low','close','vol','closetime','qav','trades','tbb','tbq','Nan'])
    bars["close[-2]"]   = bars.close.shift()
    bars["close[-3]"]   = bars.close.shift(2)
    bars["close[-4]"]   = bars.close.shift(3)
    bars["close[-5]"]   = bars.close.shift(4)
    bars["close[-6]"]   = bars.close.shift(5)
    bars["close[-7]"]   = bars.close.shift(6)
    bars["close[-8]"]   = bars.close.shift(7)
    bars["close[-9]"]   = bars.close.shift(8)
    bars["close[-10]"]   = bars.close.shift(9)
    bars["close[-11]"]   = bars.close.shift(10)
    bars["close[-12]"]   = bars.close.shift(11)
    bars["close[-13]"]   = bars.close.shift(12)
    bars["close[-14]"]   = bars.close.shift(13)
    bars["close[-15]"]   = bars.close.shift(14)
    bars["ema_C"]       = talib.EMA(bars.close, 80)
    bars["Minor1"]      = talib.LINEARREG_ANGLE(bars.ema_C, 4)
    bars["Minor1[-2]"]  = bars.Minor1.shift()
    bars["Minor1[-3]"]  = bars.Minor1.shift(2)
    bars["Minor1[-4]"]  = bars.Minor1.shift(3)
    bars["Minor1[-5]"]  = bars.Minor1.shift(4)
    bars["D&Time"]       = bars.apply(lambda x: datetime.datetime.fromtimestamp((x['time'])/1000), axis=1) 
    bars["highlow"]      = bars.apply(highlow, axis=1) 
    return bars 

bars = get_bars()
print(bars)


bars.to_excel(r'C:\Users\Personal Computer\Desktop\backtest8.1.test.xlsx')
print("done excel")


