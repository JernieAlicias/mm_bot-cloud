import config, pymongo, pandas as pd

mongodb_user_url =  config.mongodb_user_url
mongodb_client   =  pymongo.MongoClient(mongodb_user_url)

mm_bot = mongodb_client["Database"]              # Name of our overall database
datab  = mm_bot["Placeholders"]                  # Name of collection for holding "place" and "total profit"
profits_history  = mm_bot["Profits (History)"]   # Name of collection for all of the list of profits collected
buyvalue_history = mm_bot["Buy value (History)"] # Name of collection for all of the list of buy values


# Used to insert new data in a collection for the first time
def data_inserter():
    place = {"_id":"Buy_placeh","date":"t","time":"t","buy id":"buyid","bought at":0.0,"major":0.0,"minor1":0.0,"minor2":0.0} 
    datab.insert_one(place) 

# Used to insert new data in a collection for the first time
def data_inserter2():
    place = {"_id": "Open_placeh", "openvalue" : 0} 
    datab.insert_one(place) 
    

# Used to get the "bought at" value in the placeholder for buy
def get_placeholder_buy():
    x = datab.find_one({"_id":"Buy_placeh"})
    return x["bought at"]

# Used to store the wallet balance for profit calculation
def store_datab_walletbal(bal):
    datab.update_one({"_id":"USDT_Wallet"}, {"$set":{ "balance" : bal}})

# Used to get the wallet balance for profit calculation
def get_datab_walletbal():
    x = datab.find_one({"_id":"USDT_Wallet"})
    return x["balance"]

# Used to record the date, time, sell id, and profit gained into the database then adding it to the total profit
def store_profit_history(sellid, profit, date, time, markprice, reqval01, reqval02, reqval03, reqval04):

    new_profit = {"_id" : profits_history.count_documents({}) + 1, "date" : date, "time": time, 
    "sell id": sellid, "profit": profit, "price": markprice, "reqval(0.1)": reqval01, 
    "reqval(0.2)": reqval02, "reqval(0.3)": reqval03, "reqval(0.4)": reqval04,} 

    profits_history.insert_one(new_profit) 
    totalp = datab.find_one({"_id":"Profit"})["total profit"]
    datab.update_one( {"_id":"Profit"}, {"$set":{ "total profit": totalp + profit }})

# Used to record the date, time, buy order id, and buy value into the database for analyzation purposes
def store_buyval_history(buyid, date, time, buyvalue, minor0_1, minor0_2, minor0_3, 
                         minor1_1, minor1_2, minor1_3, minor1_4, minor1_5, reqval01, reqval02, reqval03, reqval04,
                         rminv80_4, rminv80_06, rminv6_4, rminv6_2, RSI1, RSI2, ema_R1, ema_R2, tempval):

    new_buyval = {"_id" : buyvalue_history.count_documents({}) + 1, "date" : date, "time": time,
    "buy id": buyid,  "bought at": buyvalue, "minor0_1": minor0_1, "minor0_2": minor0_2, "minor0_3": minor0_3, 
    "minor1_1": minor1_1, "minor1_2": minor1_2, "minor1_3": minor1_3, "minor1_4": minor1_4, "minor1_5": minor1_5, 
    "reqval(0.1)": reqval01, "reqval(0.2)": reqval02, "reqval(0.3)": reqval03, "reqval(0.4)": reqval04, 
    "rminv80_4": rminv80_4, "rminv80_06": rminv80_06, "rminv6_4": rminv6_4, "rminv6_2": rminv6_2, 
    "RSI1": RSI1, "RSI2": RSI2, "ema_R1": ema_R1, "ema_R2": ema_R2, "tempval": tempval}

    buyvalue_history.insert_one(new_buyval)
    datab.update_one({"_id":"Buy_placeh"}, {"$set":{ "date" : date, "time" : time, 
    "buy id" : buyid, "bought at": buyvalue}})    

# Used to add up all of the profits from the database history
def get_sum_profits():
    sum_profit = 0
    for x in profits_history.find({},{ "_id": 0, "profit": 1 }):
        sum_profit += float(x["profit"])
    return sum_profit

# Used to delete a number of documents in a collection
def deleter():
    for i in range(50):
        print(i)
        profits_history.delete_many({'_id':i})

# Used to print the history of buy values, profits, and other data into excel
def buyprofits_history_to_excel():
    x=pd.DataFrame(list(profits_history.find()))
    y=pd.DataFrame(list(buyvalue_history.find()))
    print(x)
    print(y)
    x.to_excel(r'C:\Users\Personal Computer\Desktop\profits_history.xlsx')
    y.to_excel(r'C:\Users\Personal Computer\Desktop\buyvalue_history.xlsx')

