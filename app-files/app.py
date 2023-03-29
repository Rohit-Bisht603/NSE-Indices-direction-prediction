import streamlit as st
import datetime as dt
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import pickle

start = dt.datetime(2018,1,1)
end = dt.datetime.now()

st.title("NSE Indices direction predictor")
index = st.selectbox('Choose an index',
                     ('Nifty ^NSEI', 'NiftyBank ^NSEBANK'))

@st.cache_data
def load_data(tkr):
    dat = yf.download(tkr, start, end)
    return dat

dat = load_data(index.split()[1])
dat.columns = ['open', 'high', 'low', 'close', 'adj close', 'volume']
dat.index.name = 'datetime'

with st.sidebar:
    st.header(f'OHLC data - {index.split()[0]}')
    st.write(dat[['open', 'high', 'low', 'close', 'adj close']].tail(7))
    t = yf.Ticker('^NSEI')
    st.header('News')
    st.info(t.news[0]['title'], icon="ℹ")
    st.info(t.news[0]['link'])

with open('niftyclf.pkl', 'rb') as f:
    n = pickle.load(f)
with open('bniftyclf.pkl', 'rb') as f:
    bn = pickle.load(f)

dat['5_ma_ratio'] = dat['close'] / dat['close'].rolling(5).mean()
dat['21_ma_ratio'] = dat['close'] / dat['close'].rolling(21).mean()
dat['62_ma_ratio'] = dat['close'] / dat['close'].rolling(62).mean()
features = ['open', 'high', 'low', 'close', '5_ma_ratio', '21_ma_ratio', '62_ma_ratio']

def predict_n(data):
    return n.predict(data[features])
def predict_bn(data):
    return bn.predict(data[features])

if st.button('Predict direction'):
    if index == "Nifty ^NSEI":
        res = predict_n(dat.iloc[[-1]])
        if res == 1:
            st.success(f"{index.split()[0]} will close in Positive tomorrow", icon="✅")
        else:
            st.error(f"{index.split()[0]} will close in Negative tomorrow", icon="🚨")
    else:
        res = predict_bn(dat.iloc[[-1]])
        if res == 1:
            st.success(f"{index.split()[0]} will close in Positive tomorrow", icon="✅")
        else:
            st.error(f"{index.split()[0]} will close in Negative tomorrow", icon="🚨")

fig = go.Figure(data=[go.Candlestick(x=dat.index,
                                     open=dat['open'],
                                     high=dat['high'],
                                     low=dat['low'],
                                     close=dat['close'])])
st.plotly_chart(fig, use_container_width=True)