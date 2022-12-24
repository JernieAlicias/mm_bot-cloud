import pymongo

mongodb_user_url = "mongodb+srv://admin:1234@mycluster.dyybuan.mongodb.net/?retryWrites=true&w=majority"
mongodb_client = pymongo.MongoClient(mongodb_user_url)

mm_bot = mongodb_client["Database"]            # Name of our overall database
datab  = mm_bot["Collection"]                  # Name of collection for holding "place" and "total profit"
profits_history = mm_bot["Profits (History)"]  # Name of collection for all of the list of profits collected
profits_daily   = mm_bot["Profits (Daily)"]    # Name of collection for the list of daily profits collected


# Used to insert new data in a collection for the first time
def data_inserter():
    place = { "_id": "place5", "date" : "", "time": "", "bought at": 0, "ema6[-1]":0, "ema6[-2]":0, "ema3[-2]":0} 
    datab.insert_one(place) 

# Used to insert new data in a collection for the first time
def data_inserter2():
    place = { "_id": "Buy", "Buy again" : True} 
    datab.insert_one(place) 

# Used to store the date, time, and "bought at" value in the placeholder for buy
def store_placeholder_buy(date, time, place, ema6_1, ema6_2, ema3_2):    
    datab.update_one( {"_id":"place1"}, {"$set":{ "date" : date, "time" : time, 
    "bought at": place, "ema6[-1]": ema6_1, "ema6[-2]": ema6_2, "ema3[-2]": ema3_2}})

# Used to get the "bought at" value in the placeholder for buy
def get_placeholder_buy():
    x = datab.find_one({"_id":"place1"})
    return x["bought at"]

# Used to record the date, time, and profit gained into the database then adding it to the total profit
def store_profit_history(profit, date, time, markprice, ema6_1, ema6_2, ema3_2):
    new_profit = {"_id" : profits_history.count_documents({}) + 1, "date" : date, "time": time, 
    "profit": profit, "price": markprice, "ema6[-1]": ema6_1, "ema6[-2]": ema6_2, "ema3[-2]": ema3_2} 
    profits_history.insert_one(new_profit) 
    totalp = datab.find_one({"_id":"Profit"})["total profit"]
    datab.update_one( {"_id":"Profit"}, {"$set":{ "total profit": totalp + profit }})

# Used to add up all of the profits from the database history
def get_sum_profits():
    sum_profit = 0
    for x in profits_history.find({},{ "_id": 0, "profit": 1 }):
        sum_profit += float(x["profit"])
    return sum_profit
