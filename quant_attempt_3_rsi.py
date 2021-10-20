import pandas_datareader as pdr
import datetime
import matplotlib.pyplot as plt
import numpy as np

df = pdr.get_data_yahoo('TCS.NS', 
                          start=datetime.datetime(2016, 6, 1), 
                          end=datetime.datetime(2021, 6, 1))

close_data = df['Close']
print(close_data)
close_delta = close_data.diff()
benchmark_sell_value = pdr.get_data_yahoo('TCS.NS', start=datetime.datetime(2019, 6, 1), end=datetime.datetime(2021, 6, 1))['Close'][0]
print(benchmark_sell_value)
benchmark_return = ( 100000*(benchmark_sell_value/close_data[0]) - 100000 )
benchmark_return_percent = benchmark_return/1000
print("benchmark return =", benchmark_return)
print("benchmark return percent = ",benchmark_return_percent, "%")


# Making two series, one for lower closes and one for higher closes
up = close_delta.clip(lower=0)
down = -1 * close_delta.clip(upper=0)

# Using exponential moving average
periods = 14
ma_up = up.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
ma_down = down.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()

rs = ma_up / ma_down
rsi = 100 - (100/(1 + rs))
df['RSI'] = rsi


df['sell_signal'] = 0
df['buy_signal'] = 0
df['sell_signal'] = np.where((rsi>70)&(rsi.shift(1)<=70), 1, 0)
df['buy_signal'] = np.where((rsi<30)&(rsi.shift(1)>=30), 1, 0)

df['Current Position']=0  # 1 = long position , 0 = not holding   
current_position = 0     
for i in range(len(close_data)-1):  
  if (df['buy_signal'][i]==1 and current_position==0):
    current_position = 1
  elif (df['sell_signal'][i]==1 and current_position==1):
    current_position = 0
  df['Current Position'][i+1] = current_position


df['Current Stock Holding'] = 0
df['Current Capital'] = 100000
for i in range(1, len(close_data)):
  if (df['Current Position'][i-1] == 0 and df['Current Position'][i] == 1 ):
    df['Current Capital'][i] = 0
    df['Current Stock Holding'][i] = ((99/100)*df['Current Capital'][i-1])/(df['Close'][i-1])
  
  elif (df['Current Position'][i-1] == 1 and df['Current Position'][i] == 0 ):
    df['Current Capital'][i] = (99/100)*(df['Current Stock Holding'][i-1])*(df['Close'][i-1])
    df['Current Stock Holding'][i] = 0  
  
  else:
    df['Current Capital'][i] = df['Current Capital'][i-1]
    df['Current Stock Holding'][i] = df['Current Stock Holding'][i-1]

final_capital = df['Current Capital'][-1] + (99/100)*(df['Current Stock Holding'][-1])*(df['Close'][-1])
final_return = ( final_capital - 100000 )
final_return_percent = final_return/1000
print( "final return =", final_return)
print("final return percent = ",final_return_percent, "%")


plt.plot(df['Close'])
plt.plot(rsi)
for i in range(1,len(close_data)):
  if(df['buy_signal'][i] == 1):
    plt.plot(df.index[i],df['RSI'][i],'^', markersize=5, color='g')
  if(df['sell_signal'][i] == 1):
    plt.plot(df.index[i],df['RSI'][i],'v', markersize=5, color='r')

for i in range(1,len(close_data)):
  if(df['Current Position'][i-1]==0 and df['Current Position'][i]==1):
    plt.plot(df.index[i],df['Close'][i],'^', markersize=10, color='g')
  if(df['Current Position'][i-1]==1 and df['Current Position'][i]==0):
    plt.plot(df.index[i],df['Close'][i],'v', markersize=10, color='r')
plt.show()         

print(df)
df.to_csv('file.csv', sep='\t', float_format='%.2f')

