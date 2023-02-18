import datetime, talib, pandas, math
from binance.client import Client

liveapi_key    = "XKsaY99DDM52Iu7jh4KOg2hpzhjpZe8Ot4zRQn123H8FpPKG3HdpduhBcAun41Ku"
liveapi_secret = "XzCTtkAg4OOAGrveJ8ZuE54le10B3Dcr8lAsV3EkWyynaySfD5EqVPxM4IDjAbc8"

client = Client(liveapi_key, liveapi_secret, testnet=False)
print("\nSuccessfully logged in", end="\n\n")

SYMBOL    = 'ETHUSDT'
ASSET     = 'USDT'
TIMEFRAME = '1m'
QTY_TRADE =  1

position  = 0
buyvalue  = 0
openvalue = 0
buyid     = ''
bstatus   = []
sstatus   = []
p1  = 0
b1  = 0
o1  = 0
bi1 = ''
bst = []
sst = []

def BuySellLogic(x):
    global position, buyvalue, openvalue, buyid, bstatus, sstatus

    if position == 0: 

        sstatus = []
        if x['Major'] <= -1.5: 
        
            if bstatus.count('dontbuy') == 0 and x['Minor1[-2]'] < -20 and x['Minor1'] < -20: bstatus = ['dontbuy']

            if (bstatus.count('dontbuy') > 0 and x['Minor1'] - x['Minor1[-3]'] > 2 or 
                x['Minor1'] - x['Minor1[-2]'] > 1.5): bstatus = []

            if float(x['close']) < x['ema_C'] < x['ema_D']:

                if bstatus.count('buy-1b') > 0:

                    if (x['ema_A[-3]'] > x['ema_B[-3]'] and x['ema_A[-2]'] < x['ema_B[-2]']): bstatus = []

                elif x['Minor1'] <= -2:

                    if (bstatus.count('buy-1b') == 0 and x['Minor1'] - x['Minor1[-2]'] >= 
                        math.log(-x['Minor1'],2)): bstatus.append('buy-1b')

        elif -1.5 < x['Major'] < 1.5:

            if bstatus.count('dontbuy') == 0 and x['Minor1[-2]'] < -20 and x['Minor1'] < -20: bstatus = ['dontbuy']

            if (bstatus.count('dontbuy') > 0 and x['Minor1'] - x['Minor1[-3]'] > 2 or 
                x['Minor1'] - x['Minor1[-2]'] > 1.5): bstatus = []

            if (bstatus.count('buy1ai') == 0 and x['Minor1[-6]'] <= -2 and x['Minor1[-7]'] <= -2 and
                x['Minor1[-5]'] - x['Minor1[-8]'] > 0 and x['Minor1'] > 0 and
                float(x['close']) > float(x['close[-2]']) > float(x['close[-3]']) > float(x['close[-4]'])): 
                bstatus.append('buy1ai')

    elif position == 1:

        bstatus = []
        if -1.5 < x['Major'] < 1.5: pass

    if position == 0:

        if bstatus.count('dontbuy') > 0: return None

        elif -1.5 < x['Major'] < 1.5:

            if float(x['close']) < x['ema_C'] < x['ema_D']:

                if -2 < x['Minor1'] < -1.5:

                    if x['RSI[-2]'] - x['RSI[-3]'] < 0 and x['RSI'] - x['RSI[-2]'] > 0 and x['RSI[-2]'] < 30:
                        position = 1
                        buyvalue = float(x['close'])
                        return 'BuyRSI'              

                    elif (x['ema_A[-3]'] < x['ema_B[-3]'] and x['ema_A'] >= x['ema_B'] and  
                          x['Minor2'] < -0.5 and float(x['close']) - float(x['open']) > -0.25):
                          position = 1
                          buyvalue = float(x['close'])
                          buyid = 'Buy1Aii'
                          return 'Buy1Aii'

                    else: return None

                elif x['Minor1'] <= -3:

                    if (x['Minor1'] - x['Minor1[-2]'] >= math.log(-x['Minor1'],2) and
                        float(x['close']) - float(x['open']) >= 1):
                        position = 1
                        buyvalue = float(x['close'])
                        openvalue = float(x['open[-3]'])
                        buyid = 'Buy1B'
                        return 'Buy1B'        

#                    elif (x['ema_A[-3]'] < x['ema_B[-3]'] and x['ema_A'] >= x['ema_B'] and  
#                          float(x['close']) - float(x['open']) > -0.25):
#                          position = 1
#                          buyvalue = float(x['close'])
#                          buyid = 'Buy1Aii2'
#                          return 'Buy1Aii2'  

                    else: return None

                else: return None

            elif float(x['close']) < x['ema_C']:

                if x['Minor1[-3]'] <= -2:

                    if (x['Minor1[-3]'] - x['Minor1[-4]'] >= math.log(-x['Minor1[-3]'],2) and
                       float(x['close']) + float(x['close[-2]']) - 
                       float(x['open'])  - float(x['open[-2]'])  > -0.25):
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

            elif (bstatus.count('buy1ai') > 0 and 
                  float(x['close[-2]']) < float(x['open[-2]']) and float(x['close']) > float(x['open'])):
                    position = 1
                    buyvalue = float(x['open'])
                    bstatus = []
                    buyid = 'Buy1Ai'
                    return 'Buy1Ai'
            
            else: return None

        elif x['Major'] <= -1.5 or x['Major[-2]'] <= -1.5:

            if float(x['close']) < x['ema_C'] < x['ema_D']:

                if x['Minor1'] <= -2:

                    if (bstatus.count('dontbuy') == 0 and x['RSI[-3]'] - x['RSI[-4]'] < 0  and x['RSI[-3]'] < 30 and 
                      ((x['RSI[-2]'] - x['RSI[-3]'] > 1  and x['RSI[-2]'] < 30) or 
                        x['RSI[-2]'] - x['RSI[-3]'] > 5) and float(x['close']) > float(x['open[-2]'])):
                        position = 1
                        buyvalue = float(x['open'])
                        buyid = 'Buy-RSI'
                        return 'Buy-RSI'              

                    elif (bstatus.count('buy-1b') > 0 and 
                        float(x['close[-2]']) < x['ema_A[-2]'] and float(x['close']) > x['ema_A']):
                        position = 1
                        bstatus  = []
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

        elif -1.5 < x['Major']  <  1.5:

            if (buyid == 'go to Buy1Bi' and            
                x['Minor1'] - x['Minor1[-2]'] <= -0.75 and float(x['close']) < buyvalue - 1):           
                    position = 0
                    buyid = ''
                    return 'Sell1Bi' 

            elif (buyid == 'Buy1B' and                
                  float(x['close']) < openvalue):
                    position = 0
                    openvalue = 0
                    buyid = ''
                    return 'Sellfor1B' 

            elif (buyid == 'Buy1Ai' and                
                  float(x['close']) < buyvalue - 1):
                    position = 0
                    openvalue = 0
                    buyid = ''
                    return 'Sellfor1Ai' 
            
            elif (buyid == 'Buy-RSI' and
                  x['RSI'] < 30 and float(x['close']) < float(x['open'])):
                        #Sell immediately
                        position = 0
                        buyid = ''
                        return 'Sell-RSIi'

            elif (buyid == 'Buy-RSI' and
                  x['ema_R[-2]']  - x['ema_R[-3]'] > 0  and  x['ema_R[-2]'] > 30    and 
                 (x['ema_R']      - x['ema_R[-2]'] < 5  or   x['RSI'] < x['ema_R']) and 
                  float(x['close']) > buyvalue and x['Minor1'] < 15):
                        position = 0
                        buyid = ''
                        return 'Sell-RSI'         

#            elif (float(x['close']) <= buyvalue - 7 and buyid == 'Buy1Aii'):
#                position = 0
#                buyid = ''
#                return 'Sell1Aii'

#            elif (float(x['close[-2]']) > x['ema_C[-2]'] and float(x['close']) <= x['ema_C'] and 
#                  buyid == 'Buy2'):
#                  position = 0
#                  buyid = ''
#                  return 'SellB2'        

            elif float(x['close']) > x['ema_C'] > x['ema_D']:

                if 1.5 < x['Minor1'] < 2:

                    if x['ema_A[-3]'] > x['ema_B[-3]'] and x['ema_A'] <= x['ema_B'] and x['Minor2'] > 0.5:
                        position = 0
                        buyid = ''
                        return 'Sell1A'

                    else: return None

                elif 2 <= x['Minor1']:

                    if x['Minor1'] - x['Minor1[-3]'] <= -math.log(x['Minor1'],2):
                        position = 0
                        buyid = ''
                        return 'Sell1B'

                    else: return None

                else: return None

            elif x['ema_C'] >= float(x['close']) > x['ema_D']:

                if (float(x['close[-2]']) >= x['ema_C[-2]'] and float(x['close[-3]']) >= x['ema_C[-3]'] and 
                    float(x['close']) >= buyvalue + 1):
                    position = 0
                    buyid = ''
                    return 'Sell2A'

                else: return None

            elif x['ema_D'] > float(x['close']) > x['ema_C'] or float(x['close']) > x['ema_D'] > x['ema_C']:

                if 2 <= x['Minor1']:

                    if x['Minor1'] - x['Minor1[-3]'] <= -math.log(x['Minor1'],2):
                        position = 0
                        buyid = ''
                        return 'Sell3A'

 #                   elif (x['ema_A[-3]'] > x['ema_B[-3]'] and x['ema_A[-2]'] < x['ema_B[-2]'] and
 #                       x['ema_A'] < x['ema_B'] and float(x['close']) >= buyvalue + 1.25):
 #                       position = 0
 #                       buyid = ''
 #                       return 'Sell3B'

                    else: return 
                    
                else: return None    

            else: return None

        elif x['Major'] <= -1.5:

            if buyid == 'Buy-RSI':

                if (x['RSI'] < 30 and float(x['close']) < float(x['open'])):
                        #Sell immediately
                        position = 0
                        buyid = ''
                        return 'Sell-RSIi'

                elif (x['ema_R[-2]']  - x['ema_R[-3]'] > 0  and  x['ema_R[-2]'] > 30    and 
                     (x['ema_R']      - x['ema_R[-2]'] < 5  or   x['RSI'] < x['ema_R']) and 
                      float(x['close']) > buyvalue and x['Minor1'] < 15):
                        position = 0
                        buyid = ''
                        return 'Sell-RSI'

                else: return None

            elif buyid == 'go to Buy-1Bi': #from Buy-1B

                if x['Minor1'] <= -2 and float(x['close']) <= buyvalue: 
                        position = 0
                        buyid = ''
                        return 'Sell-1Bi'

                elif 2 <= x['Minor1'] and x['Minor1'] - x['Minor1[-3]'] <= -math.log(x['Minor1'],2): 
                        position = 0
                        buyid = ''
                        return 'Sell-1B'

                else: return None

            else: return None

        elif 1.5 < x['Major']:

                if 10 <= x['Minor2']:

                    if x['Minor1'] - x['Minor1[-2]'] <= 0:
                        position = 0
                        buyid = ''
                        return 'Sell+1A'

                    else: return None

                else: return None

#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

def Profit(x):
    global p1, b1, o1, bi1, bst, sst

    if p1 == 0:

        sst = []
        if x['Major'] <= -1.5: 
        
            if bst.count('dontbuy') == 0 and x['Minor1[-2]'] < -20 and x['Minor1'] < -20: bst = ['dontbuy']

            if (bst.count('dontbuy') > 0 and x['Minor1'] - x['Minor1[-3]'] > 2 or 
                x['Minor1'] - x['Minor1[-2]'] > 1.5): bst = []

            if float(x['close']) < x['ema_C'] < x['ema_D']:

                if bst.count('buy-1b'):

                    if (x['ema_A[-3]'] > x['ema_B[-3]'] and x['ema_A[-2]'] < x['ema_B[-2]']): bst = []

                elif x['Minor1'] <= -2:

                    if (bst.count('buy-1b') == 0 and x['Minor1'] - x['Minor1[-2]'] >= 
                        math.log(-x['Minor1'],2)): bst.append('buy-1b')

        elif -1.5 < x['Major'] < 1.5:

            if bst.count('dontbuy') == 0 and x['Minor1[-2]'] < -20 and x['Minor1'] < -20: bst = ['dontbuy']

            if (bst.count('dontbuy') > 0 and x['Minor1'] - x['Minor1[-3]'] > 2 or 
                x['Minor1'] - x['Minor1[-2]'] > 1.5): bst = []

            if (bst.count('buy1ai') == 0 and x['Minor1[-6]'] <= -2 and x['Minor1[-7]'] <= -2 and
                x['Minor1[-5]'] - x['Minor1[-8]'] > 0 and x['Minor1'] > 0 and
                float(x['close']) > float(x['close[-2]']) > float(x['close[-3]']) > float(x['close[-4]'])): 
                bst.append('buy1ai')

    elif p1 == 1:
        
        bst = []
        if -1.5 < x['Major'] < 1.5: pass

    if p1 == 0:

        if bst.count('dontbuy') > 0: return None

        if -1.5 < x['Major']  <  1.5:

            if float(x['close']) < x['ema_C'] < x['ema_D']:

                if -2 < x['Minor1'] < -1.5:

                    if x['RSI[-2]'] - x['RSI[-3]'] < 0 and x['RSI'] - x['RSI[-2]'] > 0 and x['RSI[-2]'] < 30:
                        p1 = 1
                        b1 = float(x['close'])
                        #BuyRSI
                        return None

                    elif (x['ema_A[-3]'] < x['ema_B[-3]'] and x['ema_A'] >= x['ema_B'] and  
                          x['Minor2'] < -0.5 and float(x['close']) - float(x['open']) > -0.25):
                          p1 = 1
                          b1 = float(x['close'])
                          bi1 = 'Buy1Aii'
                          #Buy1Aii
                          return None

                    else: return None

                elif x['Minor1'] <= -3:

                    if (x['Minor1'] - x['Minor1[-2]'] >= math.log(-x['Minor1'],2) and
                        float(x['close']) - float(x['open']) >= 1):
                        p1 = 1
                        b1 = float(x['close'])
                        o1 = float(x['open[-3]'])
                        bi1 = 'Buy1B'
                        #Buy1B
                        return None

#                    elif (x['ema_A[-3]'] < x['ema_B[-3]'] and x['ema_A'] >= x['ema_B'] and  
#                          float(x['close']) - float(x['open']) > -0.25):
#                          p1 = 1
#                          b1 = float(x['close'])
#                          bi1 = 'Buy1Aii2'
#                          #Buy1Aii2
#                          return None

                    else: return None

                else: return None

            elif float(x['close']) < x['ema_C']:

                if x['Minor1[-3]'] <= -2:

                    if (x['Minor1[-3]'] - x['Minor1[-4]'] >= math.log(-x['Minor1[-3]'],2) and
                       float(x['close']) + float(x['close[-2]']) - 
                       float(x['open'])  - float(x['open[-2]'])  > -0.25):
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

            elif (bst.count('buy1ai') > 0 and 
                  float(x['close[-2]']) < float(x['open[-2]']) and float(x['close']) > float(x['open'])):
                    p1 = 1
                    b1 = float(x['open'])
                    bst = []
                    bi1 = 'Buy1Ai'
                    #Buy1Ai
                    return None
            
            else: return None

        elif x['Major'] <= -1.5 or x['Major[-2]'] <= -1.5:

            if float(x['close']) < x['ema_C'] < x['ema_D']:

                if x['Minor1'] <= -2:

                    if (bst.count('dontbuy') == 0 and x['RSI[-3]'] - x['RSI[-4]'] < 0  and x['RSI[-3]'] < 30 and 
                      ((x['RSI[-2]'] - x['RSI[-3]'] > 1  and x['RSI[-2]'] < 30) or 
                        x['RSI[-2]'] - x['RSI[-3]'] > 5) and float(x['close']) > float(x['open[-2]'])):
                        p1 = 1
                        b1 = float(x['open'])
                        bi1 = 'Buy-RSI'
                        #Buy-RSI
                        return None

                    elif (bst.count('buy-1b') > 0 and 
                        float(x['close[-2]']) < x['ema_A[-2]'] and float(x['close']) > x['ema_A']):
                        p1 = 1
                        bst = []
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

        elif -1.5 < x['Major']  <  1.5:         

            if (bi1 == 'go to Buy1Bi' and            
                x['Minor1'] - x['Minor1[-2]'] <= -0.75 and float(x['close']) < b1 - 1):                   
                    p1 = 0
                    bi1 = ''
                    proft = float(x['close']) - b1
                    #Sell1Bi
                    return proft

            elif (bi1 == 'Buy1B' and            
                  float(x['close']) < o1):
                    p1 = 0
                    o1 = 0
                    bi1 = ''
                    proft = float(x['close']) - b1
                    #Sellfor1B
                    return proft

            elif (bi1 == 'Buy1Ai' and            
                  float(x['close']) < b1 - 1):
                    p1 = 0
                    o1 = 0
                    bi1 = ''
                    proft = float(x['close']) - b1
                    #Sellfor1Ai
                    return proft

            elif (bi1 == 'Buy-RSI' and
                  x['RSI'] < 30 and float(x['close']) < float(x['open'])):
                        #Sell immediately
                        p1 = 0
                        bi1 = ''
                        proft = float(x['close']) - b1
                        #Sell-RSIi
                        return proft

            elif (bi1 == 'Buy-RSI' and
                  x['ema_R[-2]']  - x['ema_R[-3]'] > 0  and  x['ema_R[-2]'] > 30    and 
                 (x['ema_R']      - x['ema_R[-2]'] < 5  or   x['RSI'] < x['ema_R']) and 
                  float(x['close']) > b1 and x['Minor1'] < 15):
                        p1 = 0
                        bi1 = ''
                        proft = float(x['close']) - b1
                        #Sell-RSI
                        return proft

#            elif (float(x['close']) <= b1 - 7 and bi1 == 'Buy1Aii'):
#                p1 = 0
#                bi1 = ''
#                proft = float(x['close']) - b1
#                #Sell1Aii
#                return proft

#            elif (float(x['close[-2]']) > x['ema_C[-2]'] and float(x['close']) <= x['ema_C'] and 
#                  bi1 == 'Buy2'):#
#                  p1 = 0
#                  bi1 = ''
#                  proft = float(x['close']) - b1
#                  #SellB2
#                  return proft          

            elif float(x['close']) > x['ema_C'] > x['ema_D']:

                if 1.5 < x['Minor1'] < 2:

                    if x['ema_A[-3]'] > x['ema_B[-3]'] and x['ema_A'] <= x['ema_B'] and x['Minor2'] > 0.5:
                        p1 = 0
                        bi1 = ''
                        proft = float(x['close']) - b1
                        #Sell1A
                        return proft

                    else: return None

                elif 2 <= x['Minor1']:

                    if x['Minor1'] - x['Minor1[-3]'] <= -math.log(x['Minor1'],2):
                        p1 = 0
                        bi1 = ''
                        proft = float(x['close']) - b1
                        #Sell1B
                        return proft

                    else: return None

                else: return None

            elif x['ema_C'] >= float(x['close']) > x['ema_D']:

                if (float(x['close[-2]']) >= x['ema_C[-2]'] and float(x['close[-3]']) >= x['ema_C[-3]'] and 
                    float(x['close']) >= b1 + 1):
                    p1 = 0
                    bi1 = ''
                    proft = float(x['close']) - b1
                    #Sell2A
                    return proft

                else: return None

            elif x['ema_D'] > float(x['close']) > x['ema_C'] or float(x['close']) > x['ema_D'] > x['ema_C']:

                if 2 <= x['Minor1']:

                    if x['Minor1'] - x['Minor1[-3]'] <= -math.log(x['Minor1'],2):
                        p1 = 0
                        bi1 = ''
                        proft = float(x['close']) - b1
                        #Sell3A
                        return proft

#                    elif (x['ema_A[-3]'] > x['ema_B[-3]'] and x['ema_A[-2]'] < x['ema_B[-2]'] and
#                        x['ema_A'] < x['ema_B'] and float(x['close']) >= b1 + 1.25):
#                        p1 = 0
#                        bi1 = ''
 #                       proft = float(x['close']) - b1
#                        #Sell3B
#                        return proft

                    else: return None

                else: return None

            else: return None

        elif x['Major'] <= -1.5:

            if bi1 == 'Buy-RSI':

                if (x['RSI'] < 30 and float(x['close']) < float(x['open'])):
                        #Sell immediately
                        p1 = 0
                        bi1 = ''
                        proft = float(x['close']) - b1
                        #Sell-RSIi
                        return proft

                elif (x['ema_R[-2]']  - x['ema_R[-3]'] > 0  and  x['ema_R[-2]'] > 30    and 
                     (x['ema_R']      - x['ema_R[-2]'] < 5  or   x['RSI'] < x['ema_R']) and 
                      float(x['close']) > b1 and x['Minor1'] < 15):
                        p1 = 0
                        bi1 = ''
                        proft = float(x['close']) - b1
                        #Sell-RSI
                        return proft

                else: return None

            if bi1 == 'go to Buy-1Bi': #from Buy-1B

                if x['Minor1'] <= -2 and float(x['close']) <= b1: 
                        p1 = 0
                        bi1 = ''
                        proft = float(x['close']) - b1
                        #Sell-1Bi
                        return proft

                elif 2 <= x['Minor1'] and x['Minor1'] - x['Minor1[-3]'] <= -math.log(x['Minor1'],2): 
                        p1 = 0
                        bi1 = ''
                        proft = float(x['close']) - b1
                        #Sell-1B
                        return proft

                else: return None

        elif 1.5 < x['Major']:

                if 10 <= x['Minor2']:

                    if x['Minor1'] - x['Minor1[-2]'] <= 0:
                        p1 = 0
                        bi1 = ''
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
    bars["close[-4]"]   = bars.close.shift(3)
    bars["open[-2]"]    = bars.open.shift()
    bars["open[-3]"]    = bars.open.shift(2)
    bars["ema_A"]       = talib.EMA(bars.close, 3)
    bars["ema_A[-2]"]   = bars.ema_A.shift()
    bars["ema_A[-3]"]   = bars.ema_A.shift(2)
    bars["ema_B"]       = talib.EMA(bars.close, 6)
    bars["ema_B[-2]"]   = bars.ema_B.shift()
    bars["ema_B[-3]"]   = bars.ema_B.shift(2)
    bars["ema_C"]       = talib.EMA(bars.close, 80)
    bars["ema_C[-2]"]   = bars.ema_C.shift()
    bars["ema_C[-3]"]   = bars.ema_C.shift(2)
    bars["ema_D"]       = talib.EMA(bars.close, 500)
    bars["SMA"]         = talib.SMA(bars.close, 1500)
    bars["RSI"]         = talib.RSI(bars.close, 14) 
    bars["RSI[-2]"]     = bars.RSI.shift()
    bars["RSI[-3]"]     = bars.RSI.shift(2)
    bars["RSI[-4]"]     = bars.RSI.shift(3)
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

bars.to_excel(r'C:\Users\Personal Computer\Desktop\backtest6.1.5.xlsx')
print("done excel")
print(f"Profit gained: {bars['Profit'].sum()}")

