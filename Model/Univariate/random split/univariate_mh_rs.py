# -*- coding: utf-8 -*-
"""Univariate_MH_RS

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YmO6GQRo5E6QpcZE0wMk5-QX7mc22S38
"""

from math import sqrt
import numpy as np
import sklearn
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import RandomForestRegressor
import pandas as pd
import matplotlib.pyplot as plt
from numpy import concatenate
from matplotlib import pyplot
from pandas import read_csv
from pandas import DataFrame
from pandas import concat
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from pandas import read_csv
from datetime import datetime
from keras.layers import Bidirectional
from tensorflow import keras
import datetime
from keras.layers import RepeatVector
from keras.layers import TimeDistributed
from numpy import array
import time

from google.colab import drive
drive.mount('/content/drive')

from sklearn.externals import joblib
scaler_filename = "/content/drive/My Drive/covid project/Data/scalars/Maharashtra_moving"
scaler = joblib.load(scaler_filename) 
def rmse(pred, actual):
    # print(pred.shape)
    # print(actual)
    pred_flat = np.ndarray.flatten(pred)
    pred_un = scaler.inverse_transform(np.reshape(pred_flat,(pred_flat.shape[0],1)))
    actual_flat = np.ndarray.flatten(actual)
    actual_un = scaler.inverse_transform(np.reshape(actual_flat,(actual_flat.shape[0],1)))
    actual_flaten = []
    pred_flaten = []
    for lis in actual_un:
      actual_flaten.append(lis[0])
    for lis in pred_un:
      pred_flaten.append(lis[0])
    error = np.subtract(pred_flaten, actual_flaten)
    # print(error)
    try:
      error = np.reshape(error,(actual.shape[0],actual.shape[1]))
    except:
      pass
    sqerror= np.sum(np.square(error))/actual.shape[0]
    return np.sqrt(sqerror)

# actual_un = [[3],[4],[5]] -> [3,4,5]

# Commented out IPython magic to ensure Python compatibility.
# %load_ext tensorboard
import tensorflow as tf
import datetime, os
logdir = os.path.join("logs", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
tensorboard_callback = tf.keras.callbacks.TensorBoard(logdir, histogram_freq=1)

early_stopping_callback = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=3)

future_predict_df = pd.read_csv('/content/drive/My Drive/covid project/Data/Processed_Data/moving_avg/test_Maharashtra.csv',index_col = 0)
from sklearn.externals import joblib
scaler_filename = "/content/drive/My Drive/covid project/Data/scalars/Maharashtra_moving"
scaler = joblib.load(scaler_filename)

def MODEL_LSTM(name,x_train,x_test,y_train,y_test,Num_Exp,n_steps_in,n_steps_out,Epochs,Hidden):
    n_features = 1
    x_train = x_train.reshape((x_train.shape[0], x_train.shape[1], n_features))
    print(x_train.shape)
    x_test = x_test.reshape((x_test.shape[0], x_test.shape[1], n_features))
    print(x_test.shape)
    
    train_acc=np.zeros(Num_Exp)
    test_acc=np.zeros(Num_Exp)
    Step_RMSE=np.zeros([Num_Exp,n_steps_out])
    
    model = Sequential()
    model.add(LSTM(Hidden, activation='relu', input_shape=(n_steps_in,n_features), dropout=0.2))
    model.add(Dense(32))
    model.add(Dense(n_steps_out))
    model.compile(optimizer='adam', loss='mse')
    model.summary()
    future_prediction = np.zeros([Num_Exp,60])
    
    Best_RMSE=10000000000   #Assigning a large number 
    
    start_time=time.time()
    for run in range(Num_Exp):
        print("Experiment",run+1,"in progress")
        # fit model
        model.fit(x_train, y_train, epochs=Epochs,batch_size=10, verbose=0, shuffle=False)
        
        y_predicttrain = model.predict(x_train)
        y_predicttest = model.predict(x_test)
        train_acc[run] = rmse( y_predicttrain,y_train)
        # print("ooooooooooook") 
        test_acc[run] = rmse( y_predicttest, y_test) 
        # print("yyyyyyyyyyyeeeessssss") 
        if test_acc[run]<Best_RMSE:
            Best_RMSE=test_acc[run]
            Best_Predict_Test=y_predicttest
        for j in range(n_steps_out):
            Step_RMSE[run][j]=rmse(y_predicttest[:,j], y_test[:,j])
          
        chain_inp = []
        chain_out = []
        chain_inp.append(list(future_predict_df.tail(1).iloc[0,0:6]))
        chain_out.append(list(future_predict_df.tail(1).iloc[0,6:10]))
        chain_inp = np.asarray(chain_inp, dtype=np.float32)
        chain_out = np.asarray(chain_out, dtype=np.float32)
        results = []
        for step in range (1,16):
          chain_inp = np.concatenate([chain_inp.reshape(chain_inp.shape[0],chain_inp.shape[1],n_features)[:,-2:,:],chain_out.reshape(chain_out.shape[0],chain_out.shape[1],n_features)],axis=1)
          chain_out = model.predict(chain_inp)
          # print(chain_out.shape)
          for pred in chain_out[0]:
            results.append(pred)
        future_prediction[run][:] = np.ndarray.flatten(scaler.inverse_transform(np.reshape(results,(len(results),1))))
        # print(future_prediction)
    print("Total time for",Num_Exp,"experiments",time.time()-start_time)
    return future_prediction,train_acc,test_acc,Step_RMSE,Best_Predict_Test


def MODEL_Bi_LSTM(name, x_train,x_test,y_train,y_test,Num_Exp,n_steps_in,n_steps_out,Epochs,Hidden):
    n_features = 1
    x_train = x_train.reshape((x_train.shape[0], x_train.shape[1], n_features))
    print(x_train.shape)
    x_test = x_test.reshape((x_test.shape[0], x_test.shape[1], n_features))
    print(x_test.shape)
    
    train_acc=np.zeros(Num_Exp)
    test_acc=np.zeros(Num_Exp)
    Step_RMSE=np.zeros([Num_Exp,n_steps_out])
    
    model = Sequential()
    model.add(Bidirectional(LSTM(Hidden, activation='relu', dropout=0.2), input_shape=(n_steps_in,n_features)))
    model.add(Dense(16))
    model.add(Dense(n_steps_out))
    model.compile(optimizer='adam', loss='mse')
    model.summary()
  
    future_prediction = np.zeros([Num_Exp,60])
    Best_RMSE=10000000000   #Assigning a large number 
    start_time=time.time()
    for run in range(Num_Exp):
        print("Experiment",run+1,"in progress")
        # fit model
        model.fit(x_train, y_train, epochs=Epochs,batch_size=10, verbose=0, shuffle=False)
        y_predicttrain = model.predict(x_train)
        y_predicttest = model.predict(x_test)
        train_acc[run] = rmse( y_predicttrain,y_train) 
        test_acc[run] = rmse( y_predicttest, y_test) 
        if test_acc[run]<Best_RMSE:
            Best_RMSE=test_acc[run]
            Best_Predict_Test=y_predicttest
        for j in range(n_steps_out):
            Step_RMSE[run][j]=rmse(y_predicttest[:,j], y_test[:,j])
        
        chain_inp = []
        chain_out = []
        chain_inp.append(list(future_predict_df.tail(1).iloc[0,0:6]))
        chain_out.append(list(future_predict_df.tail(1).iloc[0,6:10]))
        chain_inp = np.asarray(chain_inp, dtype=np.float32)
        chain_out = np.asarray(chain_out, dtype=np.float32)
        results = []
        for step in range (1,16):
          chain_inp = np.concatenate([chain_inp.reshape(chain_inp.shape[0],chain_inp.shape[1],n_features)[:,-2:,:],chain_out.reshape(chain_out.shape[0],chain_out.shape[1],n_features)],axis=1)
          chain_out = model.predict(chain_inp)
          # print(chain_out.shape)
          for pred in chain_out[0]:
            results.append(pred)
        future_prediction[run][:] = np.ndarray.flatten(scaler.inverse_transform(np.reshape(results,(len(results),1))))

    print("Total time for",Num_Exp,"experiments",time.time()-start_time)
    return future_prediction,train_acc,test_acc,Step_RMSE,Best_Predict_Test


def MODEL_EN_DC(name, x_train,x_test,y_train,y_test,Num_Exp,n_steps_in,n_steps_out,Epochs,Hidden):
    n_features = 1
    x_train = x_train.reshape((x_train.shape[0], x_train.shape[1], n_features))
    print(x_train.shape)
    x_test = x_test.reshape((x_test.shape[0], x_test.shape[1], n_features))
    print(x_test.shape)
    y_train = y_train.reshape((y_train.shape[0], y_train.shape[1], n_features))
    print(y_train.shape)
    y_test = y_test.reshape((y_test.shape[0], y_test.shape[1], n_features))
    print(y_test.shape)
    
    train_acc=np.zeros(Num_Exp)
    test_acc=np.zeros(Num_Exp)
    Step_RMSE=np.zeros([Num_Exp,n_steps_out])
    
    model = Sequential()
    model.add(LSTM(Hidden, activation='relu',input_shape=(n_steps_in,n_features)))
    model.add(RepeatVector(n_steps_out))
    model.add(LSTM(Hidden, activation='relu', return_sequences=True))
    model.add(TimeDistributed(Dense(1,activation='relu')))
    # model.add(TimeDistributed(Dense(1,activation='relu')))
    model.compile(optimizer='adam', loss='mse')
    model.summary()
    Best_RMSE=10000000000
    future_prediction = np.zeros([Num_Exp,60])
    start_time=time.time()
    for run in range(Num_Exp):
        print("Experiment",run+1,"in progress")
        # fit model
        model.fit(x_train, y_train, epochs=Epochs,batch_size=10, verbose=0, shuffle=False, callbacks = [early_stopping_callback])
        y_predicttrain = model.predict(x_train)
        y_predicttest = model.predict(x_test)
        train_acc[run] = rmse( y_predicttrain,y_train) 
        test_acc[run] = rmse( y_predicttest, y_test) 
        if test_acc[run]<Best_RMSE:
            Best_RMSE=test_acc[run]
            Best_Predict_Test=y_predicttest
        for j in range(n_steps_out):
            Step_RMSE[run][j]=rmse(y_predicttest[:,j,0], y_test[:,j,0])

        chain_inp = []
        chain_out = []
        chain_inp.append(list(future_predict_df.tail(1).iloc[0,0:6]))
        chain_out.append(list(future_predict_df.tail(1).iloc[0,6:10]))
        chain_inp = np.asarray(chain_inp, dtype=np.float32)
        chain_out = np.asarray(chain_out, dtype=np.float32)
        results = []
        for step in range (1,16):
          chain_inp = np.concatenate([chain_inp.reshape(chain_inp.shape[0],chain_inp.shape[1],n_features)[:,-2:,:],chain_out.reshape(chain_out.shape[0],chain_out.shape[1],n_features)],axis=1)
          chain_out = model.predict(chain_inp)
          # print(chain_out.shape)
          for pred in chain_out[0]:
            results.append(pred)
        results = np.asarray(results)
        future_prediction[run][:] = np.ndarray.flatten(scaler.inverse_transform(np.reshape(results,(len(results),1))))

    print("Total time for",Num_Exp,"experiments",time.time()-start_time)
    return future_prediction,train_acc,test_acc,Step_RMSE,Best_Predict_Test.reshape(y_test.shape[0], y_test.shape[1])

def Plot_Mean(name,Overall_Analysis,n_steps_out):
  labels = ['Train','Test']
  LSTM=[Overall_Analysis[0][0],Overall_Analysis[0][5]]
  Bi_LSTM=[Overall_Analysis[1][0],Overall_Analysis[1][5]]
  EN_DC=[Overall_Analysis[2][0],Overall_Analysis[2][5]]
  
  yer1=np.array([Overall_Analysis[0][3]-Overall_Analysis[0][0],Overall_Analysis[0][8]-Overall_Analysis[0][5]])
  yer2=np.array([Overall_Analysis[1][3]-Overall_Analysis[1][0],Overall_Analysis[1][8]-Overall_Analysis[1][5]])
  yer3=np.array([Overall_Analysis[2][3]-Overall_Analysis[2][0],Overall_Analysis[2][8]-Overall_Analysis[2][5]])
 
  width = 0.25  # the width of the bars
  Plot(name,labels,width,LSTM,Bi_LSTM,EN_DC,yer1,yer2,yer3,"","RMSE","Train&Test_RMSE_Mean_Comparison",4)

def Plot_Step_RMSE_Mean(name,Overall_Analysis,n_steps_out):
    
    LSTM=Overall_Analysis[0,10:n_steps_out*5+10:5]
    Bi_LSTM=Overall_Analysis[1,10:n_steps_out*5+10:5]
    EN_DC=Overall_Analysis[2,10:n_steps_out*5+10:5]
    
    yer1=np.subtract(Overall_Analysis[0,13:n_steps_out*5+10:5],LSTM)
    print(yer1)
    yer2=np.subtract(Overall_Analysis[1,13:n_steps_out*5+10:5],Bi_LSTM)
    yer3=np.subtract(Overall_Analysis[2,13:n_steps_out*5+10:5],EN_DC)
    
    labels = []
    for j in range(n_steps_out):
        labels=np.concatenate((labels,[str(j+1)]))
    width = 0.3  # the width of the bars
    Plot(name,labels,width,LSTM,Bi_LSTM,EN_DC,yer1,yer2,yer3,"Steps","RMSE","Step_RMSE_Comparison",2)
    

def Plot(name,labels,width,LSTM,Bi_LSTM,EN_DC,yer1,yer2,yer3,xlabel,ylabel,Gname,cap):
    r1 = np.arange(len(labels))
    r2 = [x + width for x in r1]
    r3 = [x + width for x in r2]

    fig = plt.figure(figsize=(4,4))
    ax = plt.subplot()
    # fig, ax = plt.subplots()
  
    rects1 = ax.bar(r1, LSTM, width,edgecolor = 'black', yerr=yer1,capsize=cap,  label='LSTM')
    rects2 = ax.bar(r2, Bi_LSTM, width,edgecolor = 'black', yerr=yer2,capsize=cap,  label='BD-LSTM')
    rects3 = ax.bar(r3, EN_DC, width,edgecolor = 'black', yerr=yer3,capsize=cap,  label='ED-LSTM')    
    plt.xlabel(xlabel, fontsize = 18)
    plt.ylabel(ylabel, fontsize = 18)
    plt.xticks([r + width for r in range(len(LSTM))], labels)
    
    plt.setp(ax.get_xticklabels(), fontsize=14)
    plt.setp(ax.get_yticklabels(), fontsize=14)
    
    
    ax.legend()
    fig.tight_layout()
    plt.savefig("/content/drive/My Drive/covid project/Model/Results/MH/"+name+"_"+Gname+".png",dpi=300)
    plt.show()

from google.colab import drive
drive.mount('/content/drive')

from datetime import timedelta, date

def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)

start_dt = date(2020, 12, 2)
end_dt = start_dt + timedelta(days=59)
time_axis = []
for dt in daterange(start_dt, end_dt):
    time_axis.append(dt)
print(len(time_axis))

# def main():
    
n_steps_in, n_steps_out = 6,4
Overall_Analysis=np.zeros([3,10+n_steps_out*5])
for i in range(1,2):
    problem=i
    if problem ==1:
        TrainData = pd.read_csv('/content/drive/My Drive/covid project/Data/Processed_Data/random_shuffle/train_Maharashtra.csv',index_col = 0)
        TrainData = TrainData.values
        TestData = pd.read_csv('/content/drive/My Drive/covid project/Data/Processed_Data/random_shuffle/test_Maharashtra.csv',index_col = 0)
        TestData = TestData.values
        name= "MH" 

    x_train = TrainData[:,0:n_steps_in]
    y_train = TrainData[:,n_steps_in : n_steps_in+n_steps_out ]
    x_test = TestData[:,0:n_steps_in]
    y_test = TestData[:,n_steps_in : n_steps_in+n_steps_out]
    
    print(name)
    Num_Exp=30    #No. of experiments
    Epochs= 1000
    Hidden= 32
    TrainRMSE_mean=np.zeros(4)
    TestRMSE_mean=np.zeros(4)
    TrainRMSE_Std=np.zeros(4)
    TestRMSE_Std=np.zeros(4)
    Step_RMSE_mean=np.zeros([4,n_steps_out])
    train_acc=np.zeros(Num_Exp)
    test_acc=np.zeros(Num_Exp)
    Step_RMSE=np.zeros([Num_Exp,n_steps_out])


    for k in range(1,4):

        method=k
        if method ==1:
            future_prediction,train_acc,test_acc,Step_RMSE,Best_Predict_Test=MODEL_LSTM(name + '_' + str(Epochs) + '_' + str(Hidden),x_train,x_test,y_train,y_test,Num_Exp,n_steps_in,n_steps_out,Epochs,Hidden)
            Mname="MODEL_LSTM"
        if method ==2:
            future_prediction,train_acc,test_acc,Step_RMSE,Best_Predict_Test=MODEL_Bi_LSTM(name + '_' + str(Epochs) + '_' + str(Hidden),x_train,x_test,y_train,y_test,Num_Exp,n_steps_in,n_steps_out,Epochs,Hidden)
            Mname="MODEL_Bi_LSTM"
        if method ==3:
            future_prediction,train_acc,test_acc,Step_RMSE,Best_Predict_Test=MODEL_EN_DC(name + '_' + str(Epochs) + '_' + str(Hidden),x_train,x_test,y_train,y_test,Num_Exp,n_steps_in,n_steps_out,Epochs,Hidden)
            Mname="MODEL_EN_DC"
            

        print(Mname)
        pred_values = future_prediction.mean(axis=0)
        per_05 = np.percentile(future_prediction, 5, axis=0)
        per_95 = np.percentile(future_prediction, 95, axis=0)
        plt.figure()
        plt.plot(time_axis, pred_values, color='blue')
        plt.plot(time_axis, per_05, color='green', alpha=0.4)
        plt.plot(time_axis, per_95, color='green', alpha=0.4)
        plt.fill_between(time_axis, per_05, per_95, facecolor='g', alpha=0.4)
        plt.ylabel('Daily New cases') 
        plt.xlabel('Time') 
        plt.xticks(rotation = 45)
        # plt.title('Predicted')
        plt.legend()
        plt.savefig("/content/drive/My Drive/covid project/Model/Results/"+name+"/"+Mname+'/future_pred.png',dpi=300) 
        plt.show()
        plt.close()

        arr = np.dstack((train_acc,test_acc))
        arr=arr.reshape(Num_Exp,2)
        arr=np.concatenate((arr,Step_RMSE), axis=1)
        arr=arr.reshape(Num_Exp,2+n_steps_out)
        
        ExpIndex=np.array([])
        for j in range(Num_Exp):
            ExpIndex=np.concatenate((ExpIndex,["Exp"+str(j+1)]))

        TrainRMSE_mean[k-1]=np.mean(train_acc)
        TestRMSE_mean[k-1]=np.mean(test_acc)
        TrainRMSE_Std[k-1]=np.std(train_acc)
        TestRMSE_Std[k-1]=np.std(test_acc)
        ExpIndex1=['TrainRMSE','TestRMSE']
        for j in range(n_steps_out):
          Step_RMSE_mean[k-1][j]=np.mean(Step_RMSE[:,j])
          ExpIndex1=np.concatenate((ExpIndex1,["Step"+str(j+1)]))
            
        arr=np.round_(arr, decimals = 5) 
        arr = pd.DataFrame(arr, index = ExpIndex , columns = ExpIndex1)
        arr.to_csv("/content/drive/My Drive/covid project/Model/Results/"+name+"/"+Mname+"/ExpAnalysis" + '_' + str(Epochs) + '_' + str(Hidden) + ".csv")
        print(arr)
        
        Train_Mean=np.mean(train_acc)
        Train_Std=np.std(train_acc)
        Train_CI_LB= Train_Mean-1.96*(Train_Std/np.sqrt(Num_Exp))
        Train_CI_UB= Train_Mean+1.96*(Train_Std/np.sqrt(Num_Exp))
        
        Test_Mean=np.mean(test_acc)
        Test_Std=np.std(test_acc)
        Test_CI_LB= Test_Mean-1.96*(Test_Std/np.sqrt(Num_Exp))
        Test_CI_UB= Test_Mean+1.96*(Test_Std/np.sqrt(Num_Exp))
        
        Overall_Analysis[(i-1)*1+(k-1)][0]=Train_Mean
        Overall_Analysis[(i-1)*1+(k-1)][1]=Train_Std
        Overall_Analysis[(i-1)*1+(k-1)][2]=Train_CI_LB
        Overall_Analysis[(i-1)*1+(k-1)][3]=Train_CI_UB
        Overall_Analysis[(i-1)*1+(k-1)][4]=np.min(train_acc)
        Overall_Analysis[(i-1)*1+(k-1)][5]=Test_Mean
        Overall_Analysis[(i-1)*1+(k-1)][6]=Test_Std
        Overall_Analysis[(i-1)*1+(k-1)][7]=Test_CI_LB
        Overall_Analysis[(i-1)*1+(k-1)][8]=Test_CI_UB
        Overall_Analysis[(i-1)*1+(k-1)][9]=np.min(test_acc)
        
        arr1 = np.vstack(([Train_Mean,Train_Std,Train_CI_LB,Train_CI_UB,np.min(train_acc),np.max(train_acc)],[Test_Mean,Test_Std,Test_CI_LB,Test_CI_UB,np.min(test_acc),np.max(test_acc)]))
        
        for j in range(n_steps_out):
            Step_mean = np.mean(Step_RMSE[:,j])
            Step_std = np.std(Step_RMSE[:,j])
            Step_min = np.min(Step_RMSE[:,j])
            Step_CI_LB= Step_mean-1.96*(Step_std/np.sqrt(Num_Exp))
            Step_CI_UB= Step_mean+1.96*(Step_std/np.sqrt(Num_Exp))
            arr1=np.vstack((arr1,[Step_mean,Step_std,Step_CI_LB,Step_CI_UB,Step_min,np.max(Step_RMSE[:,j])]))
            Overall_Analysis[(i-1)*7+(k-1)][5*j+10]= Step_mean
            Overall_Analysis[(i-1)*7+(k-1)][5*j+11]= Step_std
            Overall_Analysis[(i-1)*7+(k-1)][5*j+12]= Step_CI_LB
            Overall_Analysis[(i-1)*7+(k-1)][5*j+13]= Step_CI_UB
            Overall_Analysis[(i-1)*7+(k-1)][5*j+14]= Step_min
        arr1=np.round_(arr1, decimals = 5) 
        arr1 = pd.DataFrame(arr1, index=ExpIndex1, columns = ['Mean','Standard Deviation','CI_LB','CI_UB','Min','Max'])
        print(arr1)
        arr1.to_csv("/content/drive/My Drive/covid project/Model/Results/"+name+"/"+Mname+"/OverallAnalysis" + '_' + str(Epochs) + '_' + str(Hidden) + ".csv")
        
        x_data=np.linspace(1,y_test.shape[0], num=y_test.shape[0], dtype = int)

        from sklearn.externals import joblib
        scaler_filename = "/content/drive/My Drive/covid project/Data/scalars/Maharashtra_moving"
        scaler = joblib.load(scaler_filename) 

        for j in range(n_steps_out):
            fig = plt.figure(figsize=(10,8))
            ax = plt.subplot(111)
            test_inversed = scaler.inverse_transform(np.reshape(y_test[:,j],(len(y_test[:,j]),1)))
            print ("Inversed Mapping of Tests")
            print (x_data)
            test_inversed_list = []
            for lis in test_inversed:
              test_inversed_list.append(lis[0])
            print (test_inversed_list)
            predict_inversed = scaler.inverse_transform(np.reshape(Best_Predict_Test[:,j],(len(Best_Predict_Test[:,j]),1)))
            predict_inversed_list = []
            for lis in predict_inversed:
              predict_inversed_list.append(lis[0])
            print(predict_inversed_list)
            w = 0.4
            ax.bar(x_data-w, test_inversed_list, label="Actual", color='maroon', align='center', width =0.4)
            ax.bar(x_data, predict_inversed_list, label='Predicted', align='center', width = 0.4)
            plt.ylabel('Daily New cases') 
            # plt.ylim((50000,150000)) 
            plt.xlabel('Time (samples)') 
            plt.title('Actual vs Predicted')
            plt.legend()
            plt.savefig("/content/drive/My Drive/covid project/Model/Results/"+name+"/"+Mname+'/pred_Step'+str(j+1)+'_' + '_' + str(Epochs) + '_' + str(Hidden) + '.png',dpi=300) 
            plt.show()
            plt.close()

    #Plot mean of train_RMSE and test_RMSE
    #Plot Std of train_RMSE and test_RMSE
    Plot_Mean(name + '_' + str(Epochs) + '_' + str(Hidden),Overall_Analysis[3*(i-1):(3*i),:],n_steps_out)
    #Plot Step wise RMSE mean for different methods
    Plot_Step_RMSE_Mean(name + '_' + str(Epochs) + '_' + str(Hidden),Overall_Analysis[3*(i-1):(3*i),:],n_steps_out)
        
# if __name__ == "__main__": main()

Plot_Mean(name + '_' + str(Epochs) + '_' + str(Hidden),Overall_Analysis[3*(i-1):(3*i),:],n_steps_out)
#Plot Step wise RMSE mean for different methods
Plot_Step_RMSE_Mean(name + '_' + str(Epochs) + '_' + str(Hidden),Overall_Analysis[3*(i-1):(3*i),:],n_steps_out)
