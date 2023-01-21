import pymongo

mongodb_user_url = "mongodb+srv://admin:1234@mmbot.w7z57gn.mongodb.net/?retryWrites=true&w=majority"
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
    place = {"_id": "USDT_Wallet", "balance" : 0} 
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
def store_profit_history(sellid, profit, date, time, markprice, major, minor1, minor2):
    new_profit = {"_id" : profits_history.count_documents({}) + 1, "date" : date, "time": time, 
    "sell id": sellid, "profit": profit, "price": markprice, "major": major, "minor1": minor1, "minor2": minor2} 
    profits_history.insert_one(new_profit) 
    totalp = datab.find_one({"_id":"Profit"})["total profit"]
    datab.update_one( {"_id":"Profit"}, {"$set":{ "total profit": totalp + profit }})

# Used to record the date, time, buy order id, and buy value into the database for analyzation purposes
def store_buyval_history(buyid, date, time, buyvalue, major, minor1, minor2):
    new_buyval = {"_id" : buyvalue_history.count_documents({}) + 1, "date" : date, "time": time,
    "buy id": buyid,  "bought at": buyvalue, "major": major, "minor1": minor1, "minor2": minor2}
    buyvalue_history.insert_one(new_buyval)
    datab.update_one({"_id":"Buy_placeh"}, {"$set":{ "date" : date, "time" : time, 
    "buy id" : buyid, "bought at": buyvalue, "major": major, "minor1": minor1, "minor2": minor2}})    

# Used to add up all of the profits from the database history
def get_sum_profits():
    sum_profit = 0
    for x in profits_history.find({},{ "_id": 0, "profit": 1 }):
        sum_profit += float(x["profit"])
    return sum_profit

