
import datetime as dt
import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os
from pandas import ExcelWriter

yf.pdr_override() 
start =dt.datetime(2019,1,1)
now = dt.datetime.now()

# endyear=2019
# endmonth=1
# endday=1
# end=dt.datetime(endyear,endmonth,endday)
# root = Tk()
ftypes = [(".xlsm","*.xlsx",".xls")]
#ttl  = "Title"
#dir1 = 'C:\\'
#filePath = askopenfilename(filetypes = ftypes, initialdir = dir1, title = ttl)

market=input("Choose a market NASDAQ NSE FTSE: ")

#filePath=r"D:\Trading\SnakeTrader\FTSE.xlsx"
#filePath=r"D:\Trading\SnakeTrader\NSE.xlsx"
filePath=r"D:\Trading\SnakeTrader\{}.xlsx".format(market)
#filePath=r"D:\Trading\SnakeTrader\NSE_SAMPLE.xlsx"

stocklist = pd.read_excel(filePath)
#stocklist=stocklist.head()

exportList= pd.DataFrame(columns=['Stock', "Name", "50 Day MA", "150 Day Ma", "200 Day MA", "52 Week Low", "52 week High"])

for i in stocklist.index:
	stock=str(stocklist["Stock"][i])
	print(stock)
	stockName=stocklist["Name"][i]
	
	try:
		#print(0)
		df = pdr.get_data_yahoo(stock, start, now)
		# df = pdr.get_data_yahoo(stock, start, end)
		#print(1)	
		smaUsed=[50,150,200]
		#print(2)
		for x in smaUsed:
			#print(3)
			sma=x
			#print(4)
			df["SMA_"+str(sma)]=round(df.iloc[:,4].rolling(window=sma).mean(),2)
			#print(5)
		#print(df)
		currentClose=df["Adj Close"][-1]
		moving_average_50=df["SMA_50"][-1]
		moving_average_150=df["SMA_150"][-1]
		moving_average_200=df["SMA_200"][-1]
		low_of_52week=min(df["Adj Close"][-260:])
		high_of_52week=max(df["Adj Close"][-260:])
		try:
			#print(6)
			moving_average_200_20 = df["SMA_200"][-20]
			#print(7)
		except Exception:
			#print(8)
			moving_average_200_20=0
		#print(9)
		#Condition 1: Current Price > 150 SMA and > 200 SMA
		if(currentClose>moving_average_150>moving_average_200):
			cond_1=True
			#print(9.1)
		else:
			cond_1=False
			#print(9.2)
		#Condition 2: 150 SMA and > 200 SMA
		if(moving_average_150>moving_average_200):
			cond_2=True
			#print(9.3)
		else:
			cond_2=False
			#print(9.4)
		#Condition 3: 200 SMA trending up for at least 1 month (ideally 4-5 months)
		if(moving_average_200>moving_average_200_20):
			cond_3=True
			#print(9.5)
		else:
			cond_3=False
			#print(9.6)
		#Condition 4: 50 SMA> 150 SMA and 50 SMA> 200 SMA
		if(moving_average_50>moving_average_150>moving_average_200):
			#print("Condition 4 met")
			cond_4=True
			#print(9.7)
		else:
			#print("Condition 4 not met")
			cond_4=False
			#print(9.8)
		#Condition 5: Current Price > 50 SMA
		if(currentClose>moving_average_50):
			cond_5=True
			#print(9.9)
		else:
			cond_5=False
			#print(9.10)
		#Condition 6: Current Price is at least 30% above 52 week low (Many of the best are up 100-300% before coming out of consolidation)
		if(currentClose>=(1.3*low_of_52week)):
			cond_6=True
			#print(9.11)
		else:
			cond_6=False
			#print(9.12)
		#Condition 7: Current Price is within 25% of 52 week high
		if(currentClose>=(.75*high_of_52week)):
			cond_7=True
			#print(9.13)
		else:
			cond_7=False
			#print(9.14)
		#Condition 8: IBD RS rating >70 and the higher the better
		#if(RS_Rating>70):
			#cond_8=True
			#print(9.15)
		#else:
			#cond_8=False
		#print(10)
		if(cond_1 and cond_2 and cond_3 and cond_4 and cond_5 and cond_6 and cond_7):
			exportList = exportList.append({'Stock': stock, "Name":stockName, "50 Day MA": moving_average_50, "150 Day Ma": moving_average_150, "200 Day MA": moving_average_200, "52 Week Low": low_of_52week, "52 week High": high_of_52week}, ignore_index=True)
			print("YES")
		else:
			print("NO")
	except Exception:
		print("No data on "+stock)

print(exportList)

newFile=os.path.dirname(filePath)+"/ScreenOutput{}.xlsx".format(market)
writer= ExcelWriter(newFile)
exportList.to_excel(writer,"Sheet1")
writer.save()