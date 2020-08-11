# Pivots
import pandas as pd
import yfinance as yf
import datetime as dt
from pandas_datareader import data as pdr
import matplotlib.pyplot as plt

yf.pdr_override() # activate yahoo finance workaroound
start =dt.datetime(2019,1,1) # sets starat point of datetime
now = dt.datetime.now() #  sets end point of dataframe

stock=input("Enter a stock ticker symbol: ")

while stock !="quit": #  Runs this loop until user enters quit

	df = pdr.get_data_yahoo(stock, start, now) # Fetches stock price into dataframe

	df['High'].plot(label='high') # plots high values of stock

	pivots=[] # stores pivot values
	dates=[]  # stores dates corresponding to those pivot values
	counter=0 # will keep track of whether a certain value is a pivot 
	lastPivont=0 # will store the last Pivot value

	Range=[0,0,0,0,0,0,0,0,0,0] #  Array used to iterate through stock prices
	dateRange=[0,0,0,0,0,0,0,0,0,0] #  Array used to iterate through corresponding dataes
	
	for i in df.index: #  Iterates through price history
		currentMax=max(Range, default=0) #  Determines the maximum value of a 10 item array, ,
		value=round(df["High"][i],2) #  Receives next high value from the dataframe
		
		Range=Range[1:9]
		Range.append(value)
		dateRange=dateRange[1:9]
		dateRange.append(i)

		if currentMax==max(Range, default=0):
			counter+=1
		else:
			counter=0
		if counter ==5:
			lastPivot=currentMax
			dateloc=Range.index(lastPivot)
			lastDate=dateRange[dateloc]

			pivots.append(lastPivot)
			dates.append(lastDate)
		
	#print(str(pivots))
	#print(str(dates))
	timeD=dt.timedelta(days=30)

	for index in range(len(pivots)):
		print(str(pivots[index])+": "+str(dates[index]))
		plt.plot_date([dates[index],dates[index]+timeD],
			[pivots[index],pivots[index]], linestyle="-", linewidth=2, marker=",")

	plt.show()	
	stock=input("Enter a stock ticker symbol: ")







