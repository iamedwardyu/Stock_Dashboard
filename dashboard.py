
import streamlit as st
import finplot
import requests
import pandas as pd
from api import FMP_api
from stats import price_stats
import config
import datetime
import sqlite3
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from matplotlib import pyplot as plt
#from market_profile import MarketProfile
import pandas_market_calendars as mcal
import openpyxl
#import talib as ta
import urllib
#from helper import format_number_two

finplot.display_timezone = datetime.timezone.utc
st.set_page_config(layout="wide")
nyse = mcal.get_calendar('NYSE')
symbol = st.sidebar.text_input("Symbol",value="MSFT")
symbol = symbol.upper()
stock = FMP_api(config.api_key, symbol)
cprofile = stock.get_profile()
cprofile = pd.DataFrame.from_dict((cprofile))
if len(cprofile) > 0:
    name = cprofile['companyName'][0]
else:
    name = ""

quote = stock.get_quote()
quote = pd.DataFrame.from_dict(quote)

comp_cuisp = cprofile['cusip'][0]
CUSIP_select = comp_cuisp


screen = st.sidebar.selectbox("View",("Overview","News","Intraday Stats","Charts","P&L"))

#st.title(screen)
if screen =="Overview":
    st.subheader("| OVERVIEW")
    cprofile = stock.get_profile()
    cprofile = pd.DataFrame.from_dict((cprofile))
    shares = stock.get_shares()
    df_shares = pd.DataFrame.from_dict(shares)
    cusip_select = cprofile['cusip'][0]

    st.sidebar.markdown("[OVERVIEW](#overview)", unsafe_allow_html=True)
    st.sidebar.markdown("[FUNDAMENTALS](#fundamentals)", unsafe_allow_html=True)
    st.sidebar.markdown("[GAP STATS](#gap-stats)", unsafe_allow_html=True)
    st.sidebar.markdown("[RESISTANCE STATS](#resistance-stats)", unsafe_allow_html=True)


    #gets the o/s
    prevday = (datetime.datetime.today()) - pd.tseries.offsets.CustomBusinessDay(1, holidays=nyse.holidays().holidays)
    x = str(prevday).split()[0]
    r_details = requests.get(
        f"https://api.polygon.io/v3/reference/tickers/{symbol}?date={x}&apiKey={config.poly_api_key}")
    r_details = r_details.json()
    df_details = pd.json_normalize(r_details['results'])
    # if df_details['weighted_shares_outstanding'].empty:
    #recent_OS = df_details['weighted_shares_outstanding'][0] / 1000000
    recent_OS = 1
    recent_OS_clean = recent_OS
    recent_OS = '{:,.2f}'.format(recent_OS)



    if len(cprofile) > 0:
        comp_industry = cprofile['industry'][0]
        comp_description = cprofile['description'][0]

    else:
        comp_industry = 'nan'
        comp_description = 'nan'

    if len(df_shares) > 0:



        #io_perc = Total_recent_13F / recent_OS_clean* 100
        #io_perc = '{:,.1f}'.format(io_perc)
        #Total_recent_13F = '{:,.2f}'.format(Total_recent_13F)

        floatshares = df_shares['floatShares'][0]
        floatshares = floatshares / 1000000
        floatshares = '{:,.2f}'.format(floatshares)
        floatshares = str(floatshares + 'M')


    else:
        outshares = 'nan'
        floatshares = 'nan'
        #io_perc = 0

    comp_mktcap = cprofile['mktCap'][0] / 1000000
    comp_mktcap = '{:,.2f}'.format(comp_mktcap)
    comp_mktcap = str(comp_mktcap + 'M')

    country = cprofile['country'][0]
    exchange = cprofile['exchangeShortName'][0]

    last_quote = quote['price'][0]
    st.image(cprofile['image'][0])
    st.write(f'{symbol} | Last Price: {last_quote}')
    st.write(f'Industry: {comp_industry}')
    st.write(f'Country: {country} | Exchange: {exchange} | Float: {floatshares}\n'
            f' | O/S: {recent_OS} | Mkt Cap: {comp_mktcap}')
    st.write(comp_description)



    news = stock.get_news()
    news = pd.DataFrame.from_dict(news)

    st.markdown('***LATEST NEWS:***')



    news2 = stock.get_news()
    news_summ = ""
    for article in news2[0:3]:
        news_summ = news_summ + ' | ' + article['text']

        st.markdown('['+article['title']+']('+article['url']+') | ' + article['publishedDate'])
        st.caption(article['text'])





    cD1 = (datetime.datetime.today()) - pd.tseries.offsets.CustomBusinessDay(30, holidays=nyse.holidays().holidays)
    cD2 = (datetime.datetime.today()) - pd.tseries.offsets.CustomBusinessDay(1, holidays=nyse.holidays().holidays)
    x = str(cD1).split()[0]
    y = str(cD2).split()[0]


    #daily stock data
    r_daily = requests.get(f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{x}/{y}?adjusted=true&sort=asc&apiKey={config.poly_api_key}")
    r_daily = r_daily.json()
    daily = pd.json_normalize(r_daily['results'])
    daily['t'] = pd.to_datetime(daily['t'], unit='ms')
    daily['t'] = daily['t'].dt.tz_localize('UTC')
    daily['t'] = daily['t'].dt.tz_convert('America/New_York')
    daily['t'] = pd.to_datetime(daily['t']).dt.strftime("%Y-%m-%d")
    daily['v'] = daily['v'].astype(float)
    daily = daily.astype({'t':'datetime64[ns]'})

    fig_daily = make_subplots(rows=2,cols=1,row_width=[0.2, 0.7],vertical_spacing=0.07)
    stock_title = symbol + " - Daily"
    fig_daily.update_layout(title=stock_title)

    chart_daily = go.Candlestick(x=daily['t'], open=daily['o'],high=daily['h'],low=daily['l'],close=daily['c'])
    fig_daily.add_trace(chart_daily,row=1,col=1)

    vwap_daily = go.Scatter(x=daily['t'], y=daily['vw'],mode='lines', line = dict(color='#ff66ff'),name = 'vwap')
    fig_daily.add_trace(vwap_daily,row=1,col=1)
    fig_daily.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])
    fig_daily.add_trace(go.Bar(x=daily['t'], y=daily['v'],marker=dict(color='#F59DBB'),showlegend=False),row=2,col=1)
    fig_daily.update(layout_xaxis_rangeslider_visible=False)
    fig_daily.update_layout(height=600,width=800, showlegend=False)
    st.plotly_chart(fig_daily, use_container_width=True)


    st.text("")
    st.text("")
    st.subheader("| FUNDAMENTALS")

    bs = stock.get_bs()
    bs = pd.DataFrame.from_dict(bs)
    # transpose the headings to rows
    if len(bs) > 0:

        bs = bs.transpose()

        bs.columns = bs.iloc[0]
        bs = bs.iloc[1:, :4]
        # deletes rows not needed
        bs = bs.drop(['cik', 'acceptedDate', 'link', 'finalLink'])
        bs = bs.iloc[1:, :4]
        bs_header = bs.iloc[0:4, :4]
        bs_detail = bs.iloc[4:, :4]


        cols = bs_detail.columns
        bs_detail = bs_detail.loc[
            ['cashAndCashEquivalents', 'totalCurrentAssets', 'totalAssets', 'shortTermDebt', 'totalCurrentLiabilities',
             'longTermDebt', 'totalLiabilities', 'totalStockholdersEquity']]

        bs_detail[cols] = bs_detail[cols].apply(pd.to_numeric, errors='coerce')

        # combines the header and detail to one dataframe
        bs = [bs_header, bs_detail]
        bs_result = pd.concat(bs)
        bs_result.loc['NWC'] = bs_result.loc['totalCurrentAssets'] - bs_result.loc['totalCurrentLiabilities']
        bs_result.loc['BV'] = bs_result.loc['totalAssets'] - bs_result.loc['totalLiabilities']

        # slices up non adjacent columns from bs_result, keeps the labeled columns and then nonadjacent qtr columns
        # revised_bs_result = bs_result.iloc[:,np.r_[0,0:0]]
        bs_result.style.format('{:,.2f}')
        #pd.options.display.float_format = '{:,.0f}'.format
        bs_result = bs_result.to_string()
    else:
        bs_result = []

    st.markdown('**Balance Sheet**')
    st.text(bs_result)


    income = stock.get_is()
    is_qtr = pd.DataFrame.from_dict(income)
    # transpose the headings to rows
    if len(is_qtr) > 0:
        is_qtr = is_qtr.transpose()
        is_qtr.columns = is_qtr.iloc[0]
        is_qtr = is_qtr.iloc[1:, :4]
        # deletes rows not needed
        is_qtr = is_qtr.drop(['cik', 'acceptedDate', 'link', 'finalLink'])

        is_qtr = is_qtr.iloc[1:, :4]
        is_qtr_header = is_qtr.iloc[0:4, :4]
        is_qtr_detail = is_qtr.iloc[4:, :4]

        cols = is_qtr_detail.columns
        is_qtr_detail = is_qtr_detail.loc[['revenue','costOfRevenue','grossProfit','operatingExpenses','ebitda','ebitdaratio','operatingIncome',
        'incomeBeforeTax','incomeBeforeTaxRatio','netIncome','eps','epsdiluted','weightedAverageShsOut']]
        # converts data from object to float type
        is_qtr_detail[cols] = is_qtr_detail[cols].apply(pd.to_numeric, errors='coerce')

        is_qtr = [is_qtr_header, is_qtr_detail]
        is_qtr_result = pd.concat(is_qtr)

        is_qtr_detail.style.format('{:,.2f}')
        pd.options.display.float_format = "{:,.2f}".format
        #is_qtr_detail['eps'] = is_qtr_detail['eps'].apply(lambda x: float("{:.2f}".format(x)))

    else:
        is_qtr_detail=[]

    st.markdown('**Income Statement**')
    st.text(is_qtr_detail)

    cf = stock.get_cf_qtr()
    cf_qtr = pd.DataFrame.from_dict(cf)
    # transpose the headings to rows
    if len(cf_qtr) > 0:
        cf_qtr = cf_qtr.transpose()
        cf_qtr.columns = cf_qtr.iloc[0]
        cf_qtr = cf_qtr.iloc[1:, :4]

        # deletes rows not needed
        cf_qtr = cf_qtr.drop(['cik', 'acceptedDate', 'link', 'finalLink'])

        cf_qtr = cf_qtr.iloc[1:, :4]
        cf_qtr_header = cf_qtr.iloc[0:4, :4]
        cf_qtr_detail = cf_qtr.iloc[4:, :4]

        cols = cf_qtr_detail.columns
        cf_qtr_detail = cf_qtr_detail.loc[['netIncome','depreciationAndAmortization','netCashProvidedByOperatingActivities',
                                           'netCashUsedForInvestingActivites','netCashUsedProvidedByFinancingActivities','netChangeInCash',
                                           'cashAtEndOfPeriod','cashAtBeginningOfPeriod','operatingCashFlow','capitalExpenditure','freeCashFlow']]


        cf_qtr_detail[cols] = cf_qtr_detail[cols].apply(pd.to_numeric, errors='coerce')

        cf_qtr = [cf_qtr_header, cf_qtr_detail]
        cf_qtr = pd.concat(cf_qtr)

        cf_qtr.style.format('{:,.2f}')


    else:
        cf_qtr = []
    st.markdown('**Cash Flow Statement**')
    st.text(cf_qtr)

    st.markdown('**Reverse Splits History**')
    r_split = requests.get(
        f"https://api.polygon.io/v3/reference/splits?ticker={symbol}&reverse_split=true&apiKey={config.poly_api_key}")
    r_split = r_split.json()
    df_split= pd.json_normalize(r_split['results'])
    st.dataframe(df_split)




    st.text("")
    st.text("")
    st.subheader("| GAP STATS")

    D1 = st.text_input('Enter Start Date', '2015-01-01')
    D2 = st.text_input('Enter End Date', f'{y}')
    GU = 0.19999999
    r_price = requests.get(f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{D1}/{D2}?adjusted=true&sort=asc&apiKey={config.poly_api_key}")
    r_price = r_price.json()
        #st.write(r_price)
    price = pd.json_normalize(r_price['results'])

    price_stats(price)
    fp = f"C:\\Users\\yusun\\Dropbox\\Stocks\\Stock Models\\Data\\{symbol}-gap stats.xlsx"

    revised_df = price[price['Gap Up%'] > GU]
    #fp2 = f"C:\\Users\\yusun\\Dropbox\\Stocks\\Stock Models\\Data\\{symbol}-gap stats revised.xlsx"
    #revised_df.to_excel(fp2, header=True)

    totalentries = revised_df.shape[0]

    print(revised_df)

    revised_df['t'] = pd.to_datetime(revised_df['t']).dt.strftime('%Y-%m-%d')
    PM_high_list = []
    time_stamp_PMH_list = []
    time_stamp_HOD_list = []

    for items in revised_df['t']:
        # items = items.strftime('%Y-%m-%d')

        intra_price = requests.get(
            f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{items}/{items}?adjusted=true&sort=asc&apiKey={config.poly_api_key}")
        intra_price = intra_price.json()
        df_intra = pd.json_normalize(intra_price['results'])
        df_intra['t'] = pd.to_datetime(df_intra['t'], unit='ms')
        df_intra['t'] = df_intra['t'].dt.tz_localize('UTC')
        df_intra['t'] = df_intra['t'].dt.tz_convert('America/New_York')
        df_intra['t'] = pd.to_datetime(df_intra['t']).dt.strftime("%H:%M")
        PM_high = df_intra.loc[(df_intra['t'] >= "04:00") & (df_intra['t'] <= "09:29"), 'h'].max()
        #time_PMH = df_intra['t'][PM_high]
        #id_time_PMH = df_intra[].idxmax()
        PM_high_list.append(PM_high)

        PM_high_index = df_intra.loc[(df_intra['t'] >= "04:00") & (df_intra['t'] <= "09:29"), 'h'].idxmax()
        PMH = df_intra.at[PM_high_index, 'h']

        time_stamp_PMH = df_intra.at[PM_high_index, 't']
        time_stamp_PMH_list.append(time_stamp_PMH)

        high_index = df_intra.loc[(df_intra['t'] >= "09:30") & (df_intra['t'] <= "16:00"), 'h'].idxmax()
        HOD = df_intra.at[high_index, 'h']

        time_stamp_HOD = df_intra.at[high_index, 't']
        time_stamp_HOD_list.append(time_stamp_HOD)

        # print(PM_stats)
        # revised_df.columns = [*revised_df.columns[:1],'PMH']
    num_C_less_O = revised_df[revised_df['Close Below Open?'] == 1].value_counts().shape[0]
    num_C_greater_O = revised_df[revised_df['Close Below Open?'] == 0].value_counts().shape[0]
    revised_df['PMH'] = PM_high_list
    revised_df['Time of PMH'] = time_stamp_PMH_list
    revised_df['Time of HOD'] = time_stamp_HOD_list
    revised_df['HOD vs PMH'] = revised_df['h'] / revised_df['PMH'] - 1
    revised_df['HOD greater PMH?'] = np.where((revised_df['HOD vs PMH'] > 0), 1, 0)

    revised_df.to_excel(fp, header=True)



    num_h_greater_pmh = revised_df[revised_df['HOD greater PMH?'] == 1].value_counts().shape[0]

    combo_close_less_o_greater_pmh = revised_df[(revised_df['Close Below Open?'] == 1) & (revised_df['HOD greater PMH?'] == 1)].value_counts().shape[0]
    combo_close_greater_o_greater_pmh = revised_df[(revised_df['Close Below Open?'] == 0) & (revised_df['HOD greater PMH?'] == 1)].value_counts().shape[0]
    #print(combo_close_less_o_greater_pmh)

    if totalentries == 0:
        perc_c_less_o = 'nan'
        vol_max = 'nan'
        date_vol_max = 'nan'
        vwap_vol_max = 'nan'
        dollar_vol_max = 'nan'
        below_perc_h_greater_pmh = 'nan'
        above_perc_h_greater_pmh = 'nan'
        perc_h_greater_pmh = 'nan'
    else:
        perc_c_less_o = num_C_less_O / totalentries * 100
        perc_c_less_o = '{:,.2f}'.format(perc_c_less_o)
        perc_c_less_o = str(perc_c_less_o)


        perc_h_greater_pmh = num_h_greater_pmh/totalentries*100
        perc_h_greater_pmh = '{:,.2f}'.format(perc_h_greater_pmh)
        perc_h_greater_pmh = str(perc_h_greater_pmh)



        if num_C_greater_O == 0:
            above_perc_h_greater_pmh = 'nan'
        else:
            above_perc_h_greater_pmh = combo_close_greater_o_greater_pmh/num_C_greater_O*100
            above_perc_h_greater_pmh = '{:,.2f}'.format(above_perc_h_greater_pmh)
            above_perc_h_greater_pmh = str(above_perc_h_greater_pmh)

        if num_C_less_O == 0:
            below_perc_h_greater_pmh = 'nan'
        else:
            below_perc_h_greater_pmh = combo_close_less_o_greater_pmh / num_C_less_O * 100
            below_perc_h_greater_pmh = '{:,.2f}'.format(below_perc_h_greater_pmh)
            below_perc_h_greater_pmh = str(below_perc_h_greater_pmh)
        
        vol_max = revised_df['v'].max()
        i_vol_max = revised_df['v'].idxmax()
        vwap_vol_max = revised_df['vw'][i_vol_max]
        dollar_vol_max = vol_max * vwap_vol_max
        vol_max = '{:,.2f}'.format(vol_max)
        vol_max = str(vol_max + 'M')

        date_vol_max = revised_df['t'][i_vol_max]
        vwap_vol_max = '{:,.2f}'.format(vwap_vol_max)
        vwap_vol_max = str('$'+vwap_vol_max)
        dollar_vol_max = '{:,.2f}'.format(dollar_vol_max)
        dollar_vol_max = str('$'+dollar_vol_max+'M')

    totalentries = str(totalentries)
    avgHOD = revised_df['HOD%'].mean() * 100
    avgHOD = '{:,.2f}'.format(avgHOD)
    avgHOD = str(avgHOD)
    avgLOD = revised_df['Low vs Open%'].mean() * 100
    avgLOD = '{:,.2f}'.format(avgLOD)
    avgLOD = str(avgLOD)
    avgClose = revised_df['Close vs Open%'].mean() * 100
    avgClose = '{:,.2f}'.format(avgClose)
    avgClose = str(avgClose)

    avgGU_bo = revised_df[(revised_df['Close Below Open?'] == 1)]['Gap Up%'].mean() * 100
    avgGU_bo = '{:,.2f}'.format(avgGU_bo)
    avgGU_bo = str(avgGU_bo)

    avgGU_ao = revised_df[(revised_df['Close Below Open?'] == 0)]['Gap Up%'].mean() * 100
    avgGU_ao = '{:,.2f}'.format(avgGU_ao)
    avgGU_ao = str(avgGU_ao)

    avgHOD_bo = revised_df[(revised_df['Close Below Open?'] == 1)]['HOD%'].mean() * 100
    avgHOD_bo = '{:,.2f}'.format(avgHOD_bo)
    avgHOD_bo = str(avgHOD_bo)

    avgLOD_bo = revised_df[(revised_df['Close Below Open?'] == 1)]['Low vs Open%'].mean() * 100
    avgLOD_bo = '{:,.2f}'.format(avgLOD_bo)
    avgLOD_bo = str(avgLOD_bo)

    avgC_bo = revised_df[(revised_df['Close Below Open?'] == 1)]['Close vs Open%'].mean() * 100
    avgC_bo = '{:,.2f}'.format(avgC_bo)
    avgC_bo = str(avgC_bo)

    avgPMH_bo = revised_df[(revised_df['Close Below Open?'] == 1)]['HOD vs PMH'].mean() * 100
    avgPMH_bo = '{:,.2f}'.format(avgPMH_bo)
    avgPMH_bo = str(avgPMH_bo)



    avgHOD_ao = revised_df[(revised_df['Close Below Open?'] == 0)]['HOD%'].mean() * 100
    avgHOD_ao = '{:,.2f}'.format(avgHOD_ao)
    avgHOD_ao = str(avgHOD_ao)

    avgLOD_ao = revised_df[(revised_df['Close Below Open?'] == 0)]['Low vs Open%'].mean() * 100
    avgLOD_ao = '{:,.2f}'.format(avgLOD_ao)
    avgLOD_ao = str(avgLOD_ao)

    avgC_ao = revised_df[(revised_df['Close Below Open?'] == 0)]['Close vs Open%'].mean() * 100
    avgC_ao = '{:,.2f}'.format(avgC_ao)
    avgC_ao = str(avgC_ao)

    avgPMH_ao = revised_df[(revised_df['Close Below Open?'] == 0)]['HOD vs PMH'].mean() * 100
    avgPMH_ao = '{:,.2f}'.format(avgPMH_ao)
    avgPMH_ao = str(avgPMH_ao)

    st.markdown('**Gap Up Summary (>20%+)**')



    gcol1,gcol2,gcol3 = st.columns([4,4,4])

    with gcol1:
        st.markdown('**Overall**')
        st.write(f'How often Close < Often: {perc_c_less_o}%')
        st.write(f'Avg. HOD%: {avgHOD}%')
        st.write(f'Avg. LOD%: {avgLOD}%')
        st.write(f'Avg. Close vs Open%: {avgClose}%')
        st.write(f'How often High > PMH: {perc_h_greater_pmh}%')

    with gcol2:
        st.markdown('**When Close Below Open**')
        st.write(f'Avg. GU%:  {avgGU_bo}%')
        st.write(f'Avg. HOD%:  {avgHOD_bo}%')
        st.write(f'Avg. LOD%:  {avgLOD_bo}%')
        st.write(f'Avg. Close vs Open%:  {avgC_bo}%')
        st.write(f'How often High > PMH: {below_perc_h_greater_pmh}%')
        st.write(f'Avg. PMH vs HOD%:  {avgPMH_bo}%')
    with gcol3:
        st.markdown('**When Close Above Open**')
        st.write(f'Avg. GU%:  {avgGU_ao}%')
        st.write(f'Avg. HOD%:  {avgHOD_ao}%')
        st.write(f'Avg. LOD%:  {avgLOD_ao}%')
        st.write(f'Avg. Close vs Open%:  {avgC_ao}%')
        st.write(f'How often High > PMH: {above_perc_h_greater_pmh}%')
        st.write(f'Avg. PMH vs HOD%:  {avgPMH_ao}%')

    st.markdown(f'Sample Size: {totalentries}\n'
             f' | Previous Gap Highest Vol Date: {date_vol_max}\n' 
            f' | Previous Gap Day Volume: {vol_max}\n'
            f' | Previous Gap Day VWAP: {vwap_vol_max}\n' 
            f' | Previous Gap Day Dollar Volume: {dollar_vol_max}')



    revised_data = price[-200:]
    revised_df = revised_df[['t','Gap Up%','HOD%','Close vs Open%','Low vs Open%','Time of PMH','Time of HOD','Close Below Open?', 'HOD vs PMH','HOD greater PMH?',]]
    st.dataframe(revised_df)


    st.subheader("| RESISTANCE STATS")

    h_max = revised_data['h'].max()
    i_h_max = revised_data['h'].idxmax()
    vwap_h_max = revised_data['vw'][i_h_max]
    v_h_max = revised_data['v'][i_h_max]
    d_h_max = revised_data['$ Vol'][i_h_max]
    v_h_max = '{:,.2f}'.format(v_h_max)
    v_h_max = str(v_h_max + 'M')

    date_h_max = revised_data['t'][i_h_max]
    h_max = '{:,.2f}'.format(h_max)
    vwap_h_max = '{:,.2f}'.format(vwap_h_max)
    vwap_h_max = str('$' + vwap_h_max)
    d_h_max = '{:,.2f}'.format(d_h_max)
    d_h_max = str('$' + d_h_max + 'M')


    vol_max = revised_data['v'].max()
    i_vol_max = revised_data['v'].idxmax()
    vwap_vol_max = revised_data['vw'][i_vol_max]
    high_vol_max = revised_data['h'][i_vol_max]
    d_vol_max = revised_data['$ Vol'][i_vol_max]
    vol_max = '{:,.2f}'.format(vol_max)
    vol_max = str(vol_max + 'M')

    date_vol_max = revised_data['t'][i_vol_max]
    high_vol_max = '{:,.2f}'.format(high_vol_max)
    vwap_vol_max = '{:,.2f}'.format(vwap_vol_max)
    vwap_vol_max = str('$' + vwap_vol_max)
    d_vol_max = '{:,.2f}'.format(d_vol_max)
    d_vol_max = str('$' + d_vol_max + 'M')


    recent_days = st.slider('How many days back?', 0, 120, 30)
    recent_data = price[-recent_days:]


    r_vol_max = recent_data['v'].max()
    i_r_vol_max = recent_data['v'].idxmax()
    vwap_r_vol_max = recent_data['vw'][i_r_vol_max]
    high_r_vol_max = recent_data['h'][i_r_vol_max]
    r_dvol_max = recent_data['$ Vol'][i_r_vol_max]
    r_vol_max = '{:,.2f}'.format(r_vol_max)
    r_vol_max = str(r_vol_max + 'M')

    date_r_vol_max = recent_data['t'][i_r_vol_max]
    high_r_vol_max = '{:,.2f}'.format(high_r_vol_max)
    vwap_r_vol_max = '{:,.2f}'.format(vwap_r_vol_max)
    vwap_r_vol_max = str('$' + vwap_r_vol_max)
    r_dvol_max = '{:,.2f}'.format(r_dvol_max)
    r_dvol_max = str('$' + r_dvol_max + 'M')

    rcol1,rcol2,rcol3 = st.columns([4,4,4])
    with rcol1:
        st.write(f'Highest Resistance Date: {date_h_max}')
        st.write(f'Highest Resistance High: {h_max}')
        st.write(f'Highest Resistance VWAP: {vwap_h_max}')
        st.write(f'Highest Resistance Volume: {v_h_max}')
        st.write(f'Highest Resistance Dol Block: {d_h_max}')
    with rcol2:
        st.write(f'Highest Vol Resistance Date: {date_vol_max}')
        st.write(f'Highest Vol Resistance High: {high_vol_max}')
        st.write(f'Highest Vol Resistance VWAP: {vwap_vol_max}')
        st.write(f'Highest Vol Resistance Volume: {vol_max}')
        st.write(f'Highest Vol Resistance Dol Block: {d_vol_max}')
    with rcol3:
        st.write(f'Recent Vol Resistance Date: {date_r_vol_max}')
        st.write(f'Recent Vol Resistance High: {high_r_vol_max}')
        st.write(f'Recent Vol Resistance VWAP: {vwap_r_vol_max}')
        st.write(f'Recent Vol Resistance Volume: {r_vol_max}')
        st.write(f'Recent Vol Resistance Dol Block: {r_dvol_max}')



if screen == "News":
    st.write(f"**{name}**")
    st.write("___")
    st.subheader(screen)


    news = stock.get_news()

    for article in news:
        st.subheader(article['title'])
        st.write(article['url'])
        #dt = datetime.utcfromtimestamp(article['publishedDate'] / 1000).isoformat()
        st.write(f"Posted by {article['site']} at {article['publishedDate']}")
    #news = pd.DataFrame.from_dict(news)
    #st.dataframe(news)




if screen == "Intraday Stats":
    st.subheader("| SUMMARY STATS")

    prevweek = (datetime.datetime.today()) - pd.tseries.offsets.CustomBusinessDay(30, holidays=nyse.holidays().holidays)
    y = str(prevweek).split()[0]
    today = (datetime.datetime.today()) - pd.tseries.offsets.CustomBusinessDay(2, holidays=nyse.holidays().holidays)
    today = str(today).split()[0]
    #start = y
    start = st.text_input('Enter start Date', f'{y}')
    end = st.text_input('Enter End Date', f'{today}')
    #d_end = pd.to_datetime(end)
    #print(d_end)
    #start = d_end - pd.tseries.offsets.CustomBusinessDay(31, holidays=nyse.holidays().holidays)

    # end = D2
    num = st.sidebar.text_input('Enter minute range', '1')
    export = st.sidebar.button('Export intraday vol. base data')
    exportPOC = st.sidebar.button('Export POC VP data')

    ##intraday volume statistics
    stats_export = st.sidebar.button('Export detailed volume stats')
    df2 = []

    orig_day = pd.to_datetime(end)
    D2 = orig_day + pd.tseries.offsets.CustomBusinessDay(1, holidays=nyse.holidays().holidays)
    orig_day = orig_day.strftime('%Y-%m-%d')
    D2 = D2.strftime('%Y-%m-%d')

    date_list = [start]
    s_date = pd.to_datetime(start)
    e_date = pd.to_datetime(end)
    date_modified = s_date
    while date_modified < e_date:
        date_modified = date_modified + pd.tseries.offsets.CustomBusinessDay(1, holidays=nyse.holidays().holidays)
        result_date = date_modified.strftime('%Y-%m-%d')
        date_list.append(result_date)

    for items in date_list:

        intra_price = requests.get(
            f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{items}/{items}?adjusted=true&sort=asc&apiKey={config.poly_api_key}")
        intra_price = intra_price.json()
        df = pd.json_normalize(intra_price['results'])

        # get stock daily ohlc data
        r_daily = requests.get(
            f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{items}/{items}?adjusted=true&sort=asc&apiKey={config.poly_api_key}")
        r_daily = r_daily.json()
        df_daily = pd.json_normalize(r_daily['results'])

        r_details = requests.get(
            f"https://api.polygon.io/v3/reference/tickers/{symbol}?date={items}&apiKey={config.poly_api_key}")
        r_details = r_details.json()
        df_details = pd.json_normalize(r_details['results'])
        # if df_details['weighted_shares_outstanding'].empty:
        os = df_details['weighted_shares_outstanding'][0] / 1000000
        # else:
        #    os='nan'

        df['t'] = pd.to_datetime(df['t'], unit='ms')
        df['t'] = df['t'].dt.tz_localize('UTC')
        df['t'] = df['t'].dt.tz_convert('America/New_York')
        df['t'] = pd.to_datetime(df['t']).dt.strftime("%H:%M")
        df['v'] = df['v'].astype(float)
        df['v'] = df['v'] / 1000000

        PM_high = df.loc[(df['t'] >= "04:00") & (df['t'] <= "09:29"), 'h'].max()
        PM_low = df.loc[(df['t'] >= "04:00") & (df['t'] <= "09:29"), 'h'].min()
        vol_PM = df.query('t>="04:00" & t<="09:29"')['v'].sum()
        vola931 = df.query('t>="09:30" & t<="09:30"')['v'].sum()
        vola935 = df.query('t>="09:30" & t<="09:34"')['v'].sum()
        vola940 = df.query('t>="09:30" & t<="09:39"')['v'].sum()
        vola945 = df.query('t>="09:30" & t<="09:44"')['v'].sum()
        vola950 = df.query('t>="09:30" & t<="09:49"')['v'].sum()
        vola955 = df.query('t>="09:30" & t<="09:54"')['v'].sum()
        vola1000 = df.query('t>="09:30" & t<="10:00"')['v'].sum()
        vola1005 = df.query('t>="09:30" & t<="10:04"')['v'].sum()
        vola1010 = df.query('t>="09:30" & t<="10:09"')['v'].sum()
        vola1015 = df.query('t>="09:30" & t<="10:14"')['v'].sum()
        vola1020 = df.query('t>="09:30" & t<="10:19"')['v'].sum()
        vola1025 = df.query('t>="09:30" & t<="10:24"')['v'].sum()
        vola1030 = df.query('t>="09:30" & t<="10:29"')['v'].sum()
        vola1100 = df.query('t>="09:30" & t<="10:59"')['v'].sum()
        vol_EOD = df.query('t>="04:00" & t<="19:59"')['v'].sum()

        #h_1m = df.loc[(df['t'] >= "09:30") & (df['t'] <= "09:30"), 'h'].max()
        #h_5m = df.loc[(df['t'] >= "09:31") & (df['t'] <= "09:34"), 'h'].max()
        #h_10m = df.loc[(df['t'] >= "09:35") & (df['t'] <= "09:39"), 'h'].max()
        h_15m = df.loc[(df['t'] >= "09:30") & (df['t'] <= "09:44"), 'h'].max()
        #h_20m = df.loc[(df['t'] >= "09:45") & (df['t'] <= "09:49"), 'h'].max()
        #h_25m = df.loc[(df['t'] >= "09:50") & (df['t'] <= "09:54"), 'h'].max()
        h_30m = df.loc[(df['t'] >= "09:30") & (df['t'] <= "09:59"), 'h'].max()
        #h_35m = df.loc[(df['t'] >= "10:00") & (df['t'] <= "10:04"), 'h'].max()
        #h_40m = df.loc[(df['t'] >= "10:05") & (df['t'] <= "10:09"), 'h'].max()
        h_45m = df.loc[(df['t'] >= "09:30") & (df['t'] <= "10:14"), 'h'].max()
        #h_50m = df.loc[(df['t'] >= "10:15") & (df['t'] <= "10:19"), 'h'].max()
        #h_55m = df.loc[(df['t'] >= "10:20") & (df['t'] <= "10:24"), 'h'].max()
        h_60m = df.loc[(df['t'] >= "09:30") & (df['t'] <= "10:29"), 'h'].max()

        #l_1m = df.loc[(df['t'] >= "09:30") & (df['t'] <= "09:30"), 'l'].min()
        #l_5m = df.loc[(df['t'] >= "09:31") & (df['t'] <= "09:34"), 'l'].min()
        #l_10m = df.loc[(df['t'] >= "09:35") & (df['t'] <= "09:39"), 'l'].min()
        l_15m = df.loc[(df['t'] >= "09:30") & (df['t'] <= "09:44"), 'l'].min()
        #l_20m = df.loc[(df['t'] >= "09:45") & (df['t'] <= "09:49"), 'l'].min()
        #l_25m = df.loc[(df['t'] >= "09:50") & (df['t'] <= "09:54"), 'l'].min()
        l_30m = df.loc[(df['t'] >= "09:30") & (df['t'] <= "09:59"), 'l'].min()
        #l_35m = df.loc[(df['t'] >= "10:00") & (df['t'] <= "10:04"), 'l'].min()
        #l_40m = df.loc[(df['t'] >= "10:05") & (df['t'] <= "10:09"), 'l'].min()
        l_45m = df.loc[(df['t'] >= "09:30") & (df['t'] <= "10:14"), 'l'].min()
        #l_50m = df.loc[(df['t'] >= "10:15") & (df['t'] <= "10:19"), 'l'].min()
        #l_55m = df.loc[(df['t'] >= "10:20") & (df['t'] <= "10:24"), 'l'].min()
        l_60m = df.loc[(df['t'] >= "09:30") & (df['t'] <= "10:29"), 'l'].min()
        #l_65m = df.loc[(df['t'] >= "10:30") & (df['t'] <= "10:34"), 'l'].min()
        #l_70m = df.loc[(df['t'] >= "10:35") & (df['t'] <= "10:39"), 'l'].min()
        #l_75m = df.loc[(df['t'] >= "10:40") & (df['t'] <= "10:44"), 'l'].min()
        #l_80m = df.loc[(df['t'] >= "10:45") & (df['t'] <= "10:49"), 'l'].min()
        #l_85m = df.loc[(df['t'] >= "10:50") & (df['t'] <= "10:54"), 'l'].min()
        l_90m = df.loc[(df['t'] >= "09:30") & (df['t'] <= "10:59"), 'l'].min()

        # o931 = df.loc[(df['t'] == "09:30"), 'o'].values[0]

        df['$ Vol'] = df['v'] * df['vw']
        df['cum $Vol'] = df['$ Vol'].cumsum()
        # h_D250m = df.loc[(df['cum $Vol'] <= 250), 'h'].max()
        # h_D500m = df.loc[(df['cum $Vol'] <= 500), 'h'].max()
        # h_D750m = df.loc[(df['cum $Vol'] <= 750), 'h'].max()
        # h_D1000m = df.loc[(df['cum $Vol'] <= 1000), 'h'].max()
        # h_D1500m = df.loc[(df['cum $Vol'] <= 1000), 'h'].max()
        # h_D2000m = df.loc[(df['cum $Vol'] <= 2000), 'h'].max()
        # h_D2500m = df.loc[(df['cum $Vol'] <= 2500), 'h'].max()
        i_HOD = df[(df['t'] >= "09:30") & (df['t'] <= "15:59")]['h'].idxmax()
        HOD = df['h'][i_HOD]
        Time_HOD = df['t'][i_HOD]
        Vol_HOD = df['v'].iloc[0:(i_HOD + 1)].sum()
        Dol_Vol_HOD = df['$ Vol'].iloc[0:(i_HOD + 1)].sum()
        i_low_after_HOD = df[(df['t'] >= Time_HOD) & (df['t'] <= "15:59")]['l'].idxmin()
        Dol_Vol_10AM = df.query('t>="04:00" & t<="09:59"')['$ Vol'].sum()
        Dol_Vol_1030AM = df.query('t>="04:00" & t<="10:29"')['$ Vol'].sum()
        if len(df[(df['t'] >= "04:00") & (df['t'] <= "09:29")]) > 0:
            i_PM_high = df.loc[(df['t'] >= "04:00") & (df['t'] <= "09:29"), 'h'].idxmax()
            Time_PM_high = df['t'][i_PM_high]
            i_PM_low = df.loc[(df['t'] >= "04:00") & (df['t'] <= "09:29"), 'l'].idxmin()
            PM_low = df['l'][i_PM_low]
            Time_PM_low = df['t'][i_PM_low]
        else:
            Time_PM_high = 'nan'
            PM_low = 'nan'
            Time_PM_low = 'nan'

        low_after_HOD = df['l'][i_low_after_HOD]
        t_low_after_HOD = df['t'][i_low_after_HOD]
        vwap_HOD = Dol_Vol_HOD / Vol_HOD
        i_LOD = df[(df['t'] >= "09:30") & (df['t'] <= "15:59")]['l'].idxmin()
        LOD = df['l'][i_LOD]
        Time_LOD = df['t'][i_LOD]
        Dol_Vol_EOD = df['$ Vol'].iloc[:].sum()
        Day_VWAP = Dol_Vol_EOD / vol_EOD
        open = df_daily['o'][0]
        close = df_daily['c'][0]

        df2.append(
            [items, symbol, os, open, HOD, LOD, close, vol_PM, PM_high, PM_low, vola931, vola935, vola940, vola945,
             vola950,
             vola1000, vola1015, vola1030, vola1100, vol_EOD, low_after_HOD, Time_PM_high, Time_PM_low, Time_HOD,
             Time_LOD, Vol_HOD, vwap_HOD, Day_VWAP, Dol_Vol_10AM, Dol_Vol_1030AM, Dol_Vol_EOD, h_15m,
             h_30m, h_45m, h_60m, l_15m, l_30m, l_45m, l_60m, l_90m, t_low_after_HOD])

        voldf = pd.DataFrame(df2,
                             columns=['Date', 'Symbol', 'O/S', 'Open', 'High', 'Low', 'Close', 'PM Vol', 'PM High',
                                      'PML',
                                      '931am', '935am', '940am', '945am', '950am', '1000am', '1015am', '1030am',
                                      '1100am',
                                      'EOD Vol', 'Low after High', 'Time of PMH', 'Time of PML', 'Time of HOD',
                                      'Time of LOD', "Vol at HOD",
                                      "VWAP at HOD", "Day VWAP", "$Vol at 10AM", "$Vol at 1030AM", "Total $ Vol",
                                        '15m high', '30m high', '45m high', '60m high', '15m low',
                                      '30m low', '45m low','60m low', '90m low', 'Time of L After HOD'])

        voldf[['Date', 'Time of PMH', 'Time of PML', 'Time of HOD', 'Time of LOD']] = voldf[
            ['Date', 'Time of PMH', 'Time of PML', 'Time of HOD', 'Time of LOD']].apply(pd.to_datetime)
        # voldf.fillna(0)
        voldf['Vol 5 day Avg'] = voldf['EOD Vol'].shift(1).rolling(5).mean()
        voldf['Vol 30 day Avg'] = voldf['EOD Vol'].shift(1).rolling(30).mean()
        voldf['PM Vol 5 day Avg'] = voldf['PM Vol'].shift(1).rolling(5).mean()

        if stats_export:
            fp = f"C:\\Users\\yusun\\Dropbox\\Stocks\\Stock Models\\Data\\{symbol}-stats-data.xlsx"
            voldf.to_excel(fp, header=True)

        s_pmvol = voldf['PM Vol'][0]
        s_pmvol = '{:,.2f}'.format(s_pmvol)
        low_after_HOD = '{:,.2f}'.format(low_after_HOD)
        s_vwapDay = voldf['Day VWAP'][0]
        s_vwapDay = '{:,.2f}'.format(s_vwapDay)
        s_volEOD = voldf['EOD Vol'][0]
        s_volEOD = '{:,.2f}'.format(s_volEOD)
        s_volHOD = '{:,.2f}'.format(Vol_HOD)
        s_VWAP_HOD = '{:,.2f}'.format(vwap_HOD)

    df_summary = voldf[
        ['Date', 'Open', 'High', 'Low', 'Close', 'Low after High', 'Day VWAP', 'EOD Vol', 'PM Vol', 'PM High',
         'PML','Time of PMH',
         'Time of PML', 'Time of HOD', 'Time of LOD', 'Time of L After HOD', 'Vol at HOD', '945am','1000am','1015am','1030am',
        '1100am','VWAP at HOD', 'O/S',
         'Vol 5 day Avg', 'Vol 30 day Avg', 'PM Vol 5 day Avg', '15m low','30m low','45m low','60m low','90m low']]
    df_summary['Date'] = df_summary['Date'].dt.strftime('%Y-%m-%d')

    cols = df_summary.select_dtypes('datetime64').columns
    df_summary['Time of PMH'] = pd.to_datetime(df_summary['Time of PMH']).dt.strftime("%H:%M")
    df_summary['Time of PML'] = pd.to_datetime(df_summary['Time of PML']).dt.strftime("%H:%M")
    df_summary['Time of HOD'] = pd.to_datetime(df_summary['Time of HOD']).dt.strftime("%H:%M")
    df_summary['Time of LOD'] = pd.to_datetime(df_summary['Time of LOD']).dt.strftime("%H:%M")
    # df_summary[['Time of HOD','Time of LOD']]= df_summary[['Time of HOD','Time of LOD']].apply(pd.to_datetime, format='%H:%M')
    df_summary.reset_index()
    #df_summary = df_summary.sort_index(ascending=False)

    #st.dataframe(df_summary)
    t_OS = df_summary['O/S'].iloc[-1]
    t_PM_VOl = df_summary['PM Vol'].iloc[-1]
    t_PMH = df_summary['PM High'].iloc[-1]
    t_PML = df_summary['PML'].iloc[-1]
    t_15mvol=df_summary['945am'].iloc[-1]
    t_30mvol=df_summary['1000am'].iloc[-1]
    t_45mvol=df_summary['1015am'].iloc[-1]
    t_60mvol=df_summary['1030am'].iloc[-1]
    t_90mvol=df_summary['1100am'].iloc[-1]
    t_volHOD = df_summary['Vol at HOD'].iloc[-1]
    t_15l=df_summary['15m low'].iloc[-1]
    t_30l=df_summary['30m low'].iloc[-1]
    t_45l=df_summary['45m low'].iloc[-1]
    t_60l=df_summary['60m low'].iloc[-1]
    t_90l=df_summary['90m low'].iloc[-1]
    t_timePMH = df_summary['Time of PMH'].iloc[-1]
    t_timeHOD = df_summary['Time of HOD'].iloc[-1]
    t_timeLOD = df_summary['Time of LOD'].iloc[-1]
    t_30davg = df_summary['Vol 30 day Avg'].iloc[-1]
    t_5davg = df_summary['Vol 5 day Avg'].iloc[-1]
    t_PM5davg = df_summary['PM Vol 5 day Avg'].iloc[-1]

    st.write(f'O/S: {t_OS}')
    st.write(f'PM Vol: {t_PM_VOl}')
    st.write(f'PMH: {t_PMH}')
    st.write(f'PML: {t_PML}')
    st.write(f'15m vol: {t_15mvol}')
    st.write(f'30m vol: {t_30mvol}')
    st.write(f'45m vol: {t_45mvol}')
    st.write(f'60m vol: {t_60mvol}')
    st.write(f'90m vol: {t_90mvol}')
    st.write(f'Vol at HOD: {t_volHOD}')
    st.write(f'15m low: {t_15l}')
    st.write(f'30m low: {t_30l}')
    st.write(f'45m low: {t_45l}')
    st.write(f'60m low: {t_60l}')
    st.write(f'90m low: {t_90l}')
    st.write(f'Time of PMH: {t_timePMH}')
    st.write(f'Time of HOD: {t_timeHOD}')
    st.write(f'Time of LOD: {t_timeLOD}')
    st.write(f'5 day vol avg: {t_5davg}')
    st.write(f'30 day vol avg: {t_30davg}')
    st.write(f'5 day PM vol avg: {t_PM5davg}')
    ##VP and POC Section
    #st.write("")
    #st.markdown("**Volume Profile Analysis**")
    colb1, colb2 = st.columns([2, 2])
    with colb1:
        l_c_price = st.number_input("Enter consolidation price low range")
        h_c_price = st.number_input("Enter consolidation price high range")
    with colb2:
        vp_date = st.text_input("Enter VP date", f'{end}')
        r_price = requests.get(
            f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/{num}/minute/{vp_date}/{vp_date}?adjusted=true&sort=asc&apiKey={config.poly_api_key}")
        r_price = r_price.json()
        data = pd.json_normalize(r_price['results'])

        data['t'] = pd.to_datetime(data['t'], unit='ms')
        data['t'] = data['t'].dt.tz_localize('UTC')
        data['t'] = data['t'].dt.tz_convert('America/New_York')
        data['t'] = pd.to_datetime(data['t']).dt.strftime("%Y-%m-%d %H:%M")
        data['v'] = data['v'].astype(float)
        data = data.astype({'t': 'datetime64[ns]'})

        con_vol = data.query(f'c>= {l_c_price} & c<= {h_c_price}')['v'].sum() / 1000000
        con_vol = '{:,.2f}'.format(con_vol)
        st.write("")
        st.write("")
        st.write(f'Consolidation Vol between {l_c_price} and {h_c_price}: {con_vol}M')

    #data = data.rename(columns={'t': 'Date', 'c': 'Close', 'v': 'Volume'})
    ##data.set_index('Date', inplace=True, drop=True)
    #mp = MarketProfile(data)
    #mp_slice = mp[data.index.min():data.index.max()]
    #poc = mp_slice.poc_price
    #df_hvn = pd.DataFrame(mp_slice.high_value_nodes)
    #df_hvn = df_hvn.reset_index()
    #df_hvn['Volume'] = df_hvn['Volume'] / 1000000
    #df_hvn['$ Vol'] = df_hvn['Volume'] * df_hvn['Close']
    #st.write(f'The POC is: {poc}')
    #poc_low = poc * 0.95
    #poc_high = 1.05 * poc
    #st.write(f'low range of POC is: {poc_low}')
    #st.write(f'how range of POC is: {poc_high}')
    #st.table(df_hvn)
    if export:
        fp = f"C:\\Users\\yusun\\Dropbox\\Stocks\\Stock Models\\Data\\{symbol}-vol-data.xlsx"
        data.to_excel(fp, header=True)

    if exportPOC:
        fpPOC = f"C:\\Users\\yusun\\Dropbox\\Stocks\\Stock Models\\Data\\{symbol}-poc-data.xlsx"
        df_hvn.to_excel(fpPOC, header=True)



#################I/O CODE###################

if screen == "P&L":
    st.write("P&L Comparison")
    df_raw = pd.read_excel("C:\\Users\\yusun\\OneDrive - Huntington Hospitality Financial Corporation\\EDWARDY HHG\\P&L Review\\data_pl.xlsx")

    st.write(df_raw)

    options_hotel = st.multiselect(
        'Select hotel',
        ['107', '121', '124'], ['107'])

    options_mon = ['Jan', 'Feb', 'Mar', 'Apr','May','Jun','Jul','Aug','Sept','Oct','Nov','Dec']

    enter_month = st.number_input("Enter month",min_value=1,max_value=12)

    #filtered_df = df_profit.loc[
    #    (df_profit['CompanyID'].isin(options_hotel)) & (df_profit['Acct Class ID'] == 'RMRENTREV')]
    df = df_raw[df_raw['CompanyID'].isin(options_hotel)& (df_raw['Acct Class ID'] == 'RMRENTREV')& (df_raw['Actual/Budget'] == 'A')]
    #filtered_df = filtered_df.loc[filtered_df['Acct Class ID'] == 'RMRENTREV']
    #filtered_df = filtered_df[options_mon]


    st.write("Room Revenue")
    st.dataframe(df)
    #print(filtered_df.dtypes)

    #filtered_df = df_profit[(df_profit['CompanyID'].isin(options_hotel)) & (df_profit['Acct Class ID']=='PYWROOM')]
    df = df[options_mon]

    #slices the first n columns with enter_month
    df=df.iloc[:,:enter_month]
    df['YTD Total'] = df.sum(axis=1)
    #df.loc['YTD Totals'] = df.sum(axis=0)
    #result = df[options_mon].sum()
    #st.write("Room pay")
    st.dataframe(df)

    month_rev = enter_month-1
    df_current = df.iloc[:,[enter_month-1]]
    st.dataframe(df_current)

