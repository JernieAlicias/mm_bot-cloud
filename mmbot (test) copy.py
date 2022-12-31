import time, datetime, config, talib, pandas
from binance.client import Client
from mongodb import get_placeholder_buy, store_placeholder_buy, store_profit_history

client = Client(config.api_key, config.api_secret, testnet=True)
print("\nSuccessfully logged in", end="\n\n")

SYMBOL        = 'ETHUSDT'
ASSET         = 'USDT'
TIMEFRAME     = '1m'
QTY_TRADE     =  1

# Gets the bars/klines in 5 minutes data timeframe from Binance Futures then adds the indicators
def get_bars():
    datenow = datetime.datetime.now() - datetime.timedelta(days=30) # Used to indicate the date start of the bars
    bars = client.futures_historical_klines(SYMBOL, interval=TIMEFRAME, 
    start_str=datenow.strftime("%Y-%m-%d %H:%M:%S"))
    bars = pandas.DataFrame(bars, columns=['time','open','high',
    'low','close','vol','closetime','qav','trades','tbb','tbq','Nan'])
    bars = bars.set_index(bars.columns[0])
    bars["ema_C"]  = talib.EMA(bars.close, 80)
    bars["ema_F"]  = talib.EMA(bars.close, 500)
    bars["SMA"]    = talib.SMA(bars.close, 1500)
    bars["Major"]  = talib.LINEARREG_ANGLE(bars.SMA,   4)
    bars["Minor1"] = talib.LINEARREG_ANGLE(bars.ema_C, 4)
    bars["Minor2"] = talib.LINEARREG_ANGLE(bars.ema_F, 4)
    return bars

bars = get_bars()
print(bars)
print("done")

bars.to_excel(r'C:\Users\Personal Computer\Desktop\newer.xlsx')
print("done")

