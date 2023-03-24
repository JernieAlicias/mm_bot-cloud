'''
In order for mmbot to work, you need a Binance Futures Testnet Account and a MongoDB account.
To do this, first go to https://testnet.binancefuture.com/en/futures/BTCUSDT then register to create your free account.
After creating your account, go to API Key and copy your personal API key and API secret then paste it in the
config.py file inside the quotation marks.

Second, go to https://www.mongodb.com/ then register to create your free account. After creating your account, you'll
be brought to the Security Quickstart page to set your username and password for your cluster (Make a simple username
such as 'admin' and password like '1234'). Set your cluster to Local Environment then add your current IP address.
After creating your cluster, click on 'Connect', then 'Connect your application', then set the driver to 'python'
and choose your current python version. After doing so, you should be able to see your personal connection string
which will be used to connect mmbot to mongodb. Replace <password> in the string with your password for your user.
Copy it and paste it inside the config.py file inside quotation marks.

example mongodb connection string:
"mongodb+srv://admin:<password>@cluster0.abcdefgh.mongodb.net/?retryWrites=true&w=majority"

'''