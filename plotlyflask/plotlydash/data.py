"""Prepare data for Plotly Dash."""
import pandas as pd
import numpy as np
from datetime import datetime

def load_data(path_to_files = './data/'):
    df = pd.read_csv(path_to_files+'transactions_with_categories_short.csv', sep=';')
    dict_cols = {
     'category':'category',
     'tstamp':'posting_time',
     'arvopvm':'posting_date',
     'kirjauspvm':'payment_time',
     'maksupvm':'payment_date',
     'tilinro':'account_id',
     'rahamaara':'amount',
     'saldo':'balance',
     'vientiselitekd':'transaction_type_id',
     'taplajikd':'payment_type_id',
     'bic_saaja':'recipient_bic',
     'viite':'reference_no',
     'iban_saaja':'recipient_iban',
     'counterparty_account_id':'recipient_account_id'}
    df.rename(columns = dict_cols, inplace = True)
    df[["posting_time", "posting_date", "payment_time", 'payment_date']] = df[["posting_time", "posting_date", "payment_time", 'payment_date']].apply(pd.to_datetime)
    df = df[['posting_time','account_id','category','amount']]
    
    dict_categories = {
     'Ruoka_paivittaistavarakauppa':'Grocery',
     'Lapset':'Children',
     'Hyvinvointijakauneus':'Health',
     'Saastot_sijoitukset':'Savings',
     'Liikkuminen':'Sports',
     'Muut':'Other',
     'Ravintolat_kahvilat':'Restaurants',
     'Tulot':'Income',
     'Kulttuuri_viihde':'Enterainment',
     'Harrastukset':'Hobbies',
     'Luokittelemattomat':'Undefined',
     'Shoppailu':'Shopping',
     'Asuminen':'Rent',
     'Vakuutukset':'Insurance',
     'Matkailu':'Travel',
     'Luottojen_maksut':'Loan repayment',
     'Lemmikit':'Pets',
     'Hyvinvointi':'Wellbeing',
     'Terveys':'Medicine'}
    
    df.category = df.category.map(dict_categories)
        
    return df

def filter_by_year(df, y = 2020):
    return df[df.posting_time.dt.year == y]

def split_by_users(dfAll, account_id = 1):  
    expenseMy = dfAll[(dfAll.amount < 0)&(dfAll.account_id == account_id)]
    expenseMy.amount *= (-1)
    incomeMy = dfAll[(dfAll.amount > 0)&(dfAll.account_id == account_id)]
    
    expenseAll = dfAll[dfAll.amount < 0]
    expenseAll.amount *= (-1)
    incomeAll = dfAll[dfAll.amount > 0]
    
    return expenseMy, incomeMy, expenseAll, incomeAll

def filter_by_categories(df, categories):
    df = df[df.category.isin(categories)]
    return df

def prepare_line_chart(expenseMy, expenseAll, startMonth, endMonth):
    expenseMyByMonth = expenseMy.set_index('posting_time').amount.resample('M').sum()
    expenseAvgByMonth = expenseAll.set_index(['account_id','posting_time']).groupby([pd.Grouper(level='account_id'), pd.Grouper(level='posting_time', freq='M')]).sum().groupby(pd.Grouper(level='posting_time')).mean()
    
    expenseMyByMonth = expenseMyByMonth[(expenseMyByMonth.index.month >= startMonth)&(expenseMyByMonth.index.month <= endMonth)]
    expenseAvgByMonth = expenseAvgByMonth[(expenseAvgByMonth.index.month >= startMonth)&(expenseAvgByMonth.index.month <= endMonth)]
    return expenseMyByMonth.to_frame().join(expenseAvgByMonth,lsuffix='My',rsuffix='Avg')

def prepare_bar_chart(expenseMy, expenseAll, month):
    expenseMy = expenseMy[expenseMy.posting_time.dt.month == month]
    expenseAll = expenseAll[expenseAll.posting_time.dt.month == month]
    
    expenseMyByCategory = expenseMy.groupby(by='category').sum().amount #to code
    expenseAvgByCategory = expenseAll.set_index(['account_id','category']).groupby([pd.Grouper(level='account_id'), pd.Grouper(level='category')]).sum().groupby(pd.Grouper(level='category')).mean()
    return expenseMyByCategory.to_frame().join(expenseAvgByCategory,lsuffix='My',rsuffix='Avg')

def prepare_data(df, y, account_id, categories):
    #df = load_data()
    
    if len(categories) == 0:
        df2020 = filter_by_year(df, y)
    else:
        df2020 = filter_by_categories(filter_by_year(df, y), categories)
    expenseMy, incomeMy, expenseAll, incomeAll = split_by_users(df2020, account_id=account_id)
    
    return expenseMy, incomeMy, expenseAll, incomeAll

#print(prepare_line_chart(expenseMy, expenseAll, 9, 11))
#print(prepare_bar_chart(expenseMy, expenseAll, 9))
