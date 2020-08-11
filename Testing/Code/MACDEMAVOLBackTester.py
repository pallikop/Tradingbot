# Back testing
# MACD 
# https://www.whselfinvest.com/en-lu/trading-platform/free-trading-strategies/tradingsystem/41-macd-triple

# def MACD(df, slow, fast, ma):
#     df[f'EMA_{slow}'] = df.Close.ewm(span=slow, adjust=False).mean()
#     df[f'EMA_{fast}'] = df.Close.ewm(span=fast, adjust=False).mean()

#     df['MACD'] = (df[f'EMA_{fast}'] - df[f'EMA_{slow}'])
#     df['MACD_MA'] = df.MACD.ewm(span=ma, adjust=False).mean()
    
#     df['MACD_Diff'] = df['MACD'] - df['MACD_MA']
    
#     df.drop([f'EMA_{slow}', f'EMA_{fast}'], axis=1, inplace=True)
#     return df

# df = MACD(df, 26, 12, 9)

# BUY
# 	MACD : blue > red
# 	EMA : min (red) < max (blue)
# SELL
# 	MACD : blue < red
# 	EMA : : min(blue) < max (red) 


import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
from pandas_datareader import data as pdr
import os 
from pandas import ExcelWriter
import statsmodels.api as sm
import dateutil.parser

yf.pdr_override()

market=input("Choose a market NASDAQ NSE FTSE: ")


filePath=r"D:\Trading\SnakeTrader\ScreenOutput{}.xlsx".format(market)
stocklist = pd.read_excel(filePath,skipinitialspace=True)

exportList= pd.DataFrame(columns=['Stock', "Name", "Buy Date", "Buy Price", "Sell Date", "Sell Price", "No of Trades", "Total return", "Individual return"])

def MACD(df, slow, fast, ma):
    df[f'EMA_{slow}'] = df.Close.ewm(span=slow, adjust=False).mean()
    df[f'EMA_{fast}'] = df.Close.ewm(span=fast, adjust=False).mean()

    df['MACD'] = (df[f'EMA_{fast}'] - df[f'EMA_{slow}'])
    df['MACD_MA'] = df.MACD.ewm(span=ma, adjust=False).mean()
    
    df['MACD_Diff'] = df['MACD'] - df['MACD_MA']
    
    df.drop([f'EMA_{slow}', f'EMA_{fast}'], axis=1, inplace=True)
    return df

def OBV(df, n_MA):
	for i in df.Close[1:]:
		df['OBV'] = np.where(df['Close'] > df['Close'].shift(1), df['Volume'],np.where(df['Close']<df['Close'].shift(1),-df['Volume'],0)).cumsum()
	df['OBV_EMA'] = df.OBV.ewm(span=n_MA, adjust=False, min_periods=n_MA).mean()
	return df



def eachStock(stock,exportList):
	print(stock)
	buyDate="None"
	sellDate="None"
	# startyear=2020
	# startmonth=1
	# startday=1

	startyear=2020
	startmonth=1
	startday=1
	# endyear=2020
	# endmonth=1
	# endday=1

	start=dt.datetime(startyear,startmonth,startday)
	# end=dt.datetime(endyear,endmonth,endday)
	now=dt.datetime.now()
	df=pdr.get_data_yahoo(stock,start,now)
	# df=pdr.get_data_yahoo(stock,start,end)
	df.dropna(subset=['Open'], how='all', inplace=True)
	df.dropna(subset=['High'], how='all', inplace=True)
	df.dropna(subset=['Low'], how='all', inplace=True)
	df.dropna(subset=['Close'], how='all', inplace=True)
	df.dropna(subset=['Adj Close'], how='all', inplace=True)
	df.dropna(subset=['Volume'], how='all', inplace=True)

	if(market=="FTSE"):
		# for i in df.index:
		# 	if(str(i)=="2020-06-30 00:00:00" or str(i)=="2020-07-02 00:00:00"):
		df["Open"]["2020-06-30 00:00:00"]=df["Open"]["2020-07-03 00:00:00"]
		df["High"]["2020-06-30 00:00:00"]=df["High"]["2020-07-03 00:00:00"]
		df["Low"]["2020-06-30 00:00:00"]=df["Low"]["2020-07-03 00:00:00"]
		df["Close"]["2020-06-30 00:00:00"]=df["Close"]["2020-07-03 00:00:00"]
		df["Adj Close"]["2020-06-30 00:00:00"]=df["Adj Close"]["2020-07-03 00:00:00"]
		df["Volume"]["2020-06-30 00:00:00"]=df["Volume"]["2020-07-03 00:00:00"]

		df["Open"]["2020-07-02 00:00:00"]=df["Open"]["2020-07-03 00:00:00"]
		df["High"]["2020-07-02 00:00:00"]=df["High"]["2020-07-03 00:00:00"]
		df["Low"]["2020-07-02 00:00:00"]=df["Low"]["2020-07-03 00:00:00"]
		df["Close"]["2020-07-02 00:00:00"]=df["Close"]["2020-07-03 00:00:00"]
		df["Adj Close"]["2020-07-02 00:00:00"]=df["Adj Close"]["2020-07-03 00:00:00"]
		df["Volume"]["2020-07-02 00:00:00"]=df["Volume"]["2020-07-03 00:00:00"]
		#print("value on 2020 June 30 is {}".format(df["Adj Close"][i]))
		#df=pdr.get_data_yahoo(stock,start,end)
	df=MACD(df, 26, 12, 9)  # Now df has three additional columns MACD, MACD_MA, MACD_Diff
	df=OBV(df, 13)
	df.dropna(subset=['OBV_EMA'], how='all', inplace=True)
	# print(df)
	emasUsed=[3,5,8,12,10,15,30,35,40,45,50,60]
	for x in emasUsed:
		ema=x
		df["Ema_"+str(ema)]=round(df.iloc[:,4].ewm(span=ema, adjust=False).mean(),2)
		# df["Vol_"+str(ema)]=round(df.iloc[:,5].ewm(span=ema, adjust=False).mean(),2)
	df=df.iloc[60:]
	

	# print(df)
	pos=0
	num=0
	bp=0
	sp=0

	percentchange=[]
	bullishDivergence=False
	bearishDivergence=False
	for i in df.index:
		buy_cond_1=False
		buy_cond_2=False
		buy_cond_3=False
		sell_cond_1=False
		sell_cond_2=False
		# print(df["Ema_3"][i])
		# print(df["Ema_5"][i])
		# print(df["Ema_8"][i])
		# print(df["Ema_10"][i])
		# print(df["Ema_12"][i])
		# print(df["Ema_15"][i])
		blueMin=min(df["Ema_3"][i],df["Ema_5"][i],df["Ema_8"][i],df["Ema_10"][i],df["Ema_12"][i],df["Ema_15"][i],)
		blueMax=max(df["Ema_3"][i],df["Ema_5"][i],df["Ema_8"][i],df["Ema_10"][i],df["Ema_12"][i],df["Ema_15"][i],)
		redMin=min(df["Ema_30"][i],df["Ema_35"][i],df["Ema_40"][i],df["Ema_45"][i],df["Ema_50"][i],df["Ema_60"][i],)
		redMax=max(df["Ema_30"][i],df["Ema_35"][i],df["Ema_40"][i],df["Ema_45"][i],df["Ema_50"][i],df["Ema_60"][i],)
		close=df["Adj Close"][i]
		# MACD : blue > red
		# EMA : min (red) < max (blue)
		if(pos==0):
			if(df["MACD"][i]>df["MACD_MA"][i]):
				buy_cond_1=True
			if(redMin<blueMax):
				buy_cond_2=True
			if(df["OBV"][i]>df["OBV_EMA"][i]):
				buy_cond_3=True
			if(buy_cond_1 and buy_cond_2 and buy_cond_3):
				pos=1
				bp=close
				buyDate=i
				sp=""
				sellDate=""
				print(f'{buyDate} Buying now at {str(bp)}')
		# MACD : blue < red
		# EMA : : min(blue) < max (red) 
		elif(pos==1):
			if(df["MACD"][i]<df["MACD_MA"][i]):
				sell_cond_1=True
			if(blueMin<redMax):
				sell_cond_2=True
			if(sell_cond_1 and sell_cond_2):
				pos=0
				sp=close
				sellDate=i
				print(f'{sellDate} Selling now at {str(sp)}')
				pc=(close/bp-1)*100
				percentchange.append(pc)
		if(num==df["Adj Close"].count()-1 and pos==1):
			print(f' {i} Selling now at {str(close)} End of dataframe. Hence virtual selling')
			sp=close
			pc=(close/bp-1)*100
			percentchange.append(pc)
		num+=1
	print(percentchange)
	gains=0
	ng=0
	losses=0
	nl=0
	totalR=1
	for i in percentchange:
		if(i>0):
			gains+=i
			ng+=1
		else:
			losses+=i
			nl+=1
		totalR=totalR*((i/100)+1)
	totalR=round((totalR-1)*100,2)
	print(f' TotalReturns are {str(totalR)}')
	if(ng>0):
		avgGain=gains/ng
		maxR=str(max(percentchange))
	else:
		avgGain=0
		maxR="undefined"
	if(nl>0):
		avgLoss=losses/nl
		maxL=str(min(percentchange))
		#ratio=str(-avgGain/avgLoss)
	else:
		avgLoss=0
		maxL="undefined"
		#ratio="inf"
	if(ng>0 or nl>0):
		battingAvg=ng/(ng+nl)
	else:
		battingAvg=0

	print()
	#print("Results for "+ stock +" going back to "+str(df.index[0])+", Sample size: "+str(ng+nl)+" trades")
	#print("EMAs used: "+str(emasUsed))
	#print("Batting Avg: "+ str(battingAvg))
	#print("Gain/loss ratio: "+ ratio)
	#print("Average Gain: "+ str(avgGain))
	#print("Average Loss: "+ str(avgLoss))
	#print("Max Return: "+ maxR)
	#print("Max Loss: "+ maxL)
	#print("Total return over "+str(ng+nl)+ " trades: "+ str(totalR)+"%" )
	#print("Example return Simulating "+str(n)+ " trades: "+ str(nReturn)+"%" )

	stockDict={}
	stockDict={'Stock': stock, "Buy Date": buyDate, "Buy Price": str(bp), "Sell Date": sellDate, "Sell Price": str(sp), "No of Trades": str(ng+nl), "Total return": str(totalR), "Individual return": percentchange}
	return stockDict
	
for i in stocklist.index:
	try:
		stock=str(stocklist["Stock"][i])
		name=stocklist["Name"][i]
		stockDict=eachStock(stock,exportList)	
		exportList = exportList.append({'Stock': stockDict['Stock'], "Name" : name, "Buy Date":stockDict['Buy Date'], "Buy Price":stockDict['Buy Price'], "Sell Date":stockDict['Sell Date'], "Sell Price":stockDict['Sell Price'], "No of Trades": stockDict['No of Trades'], "Total return": stockDict['Total return'], "Individual return": stockDict['Individual return']},ignore_index=True)		
	except Exception:
		print("Some unknown Exception occurred")

newFile=os.path.dirname(filePath)+"/ReturnsOutput{}.xlsx".format(market)
writer= ExcelWriter(newFile)
exportList.to_excel(writer,"Sheet1")
writer.save()
