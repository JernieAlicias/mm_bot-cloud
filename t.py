import talib, pandas

t = [1217.91, 1217.85, 1217.81]
t = pandas.DataFrame(t, columns=["num"])
t["test"] = talib.LINEARREG_ANGLE(t.num, 3)

print(t, end="\n\n")
print(t.test.iloc[-1], end="\n\n")

