"""Instantiate a Dash app."""
import numpy as np
import pandas as pd
import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import time
from .layout import html_layout
from .data import prepare_data, prepare_line_chart, prepare_bar_chart, load_data

def init_dashboard(server):  
    
    # Custom HTML layout
    #dash_app.index_string = html_layout
    
    """ Define colors """
    colors = {'bg':'#F1F2F7',
              'avg':'#26CCA8',
              'my':'#3734A9'}
              
    raw_df = load_data()

    year = 2020
    start_month = 6
    end_month = 11
    reporting_month = 10
    categories = []
    
    """Create a Plotly Dash dashboard."""
    dash_app = dash.Dash(server=server, routes_pathname_prefix='/dashapp/', external_stylesheets=[dbc.themes.BOOTSTRAP])

    # Load data
    expenseMy, incomeMy, expenseAll, incomeAll = prepare_data(raw_df, year, 1, categories)
    
    dropdown_category_options = []
    initial_category_values = []
    all_categories = list(expenseAll.category.unique())
    for c in all_categories:
        dropdown_category_options.append({'label':c, 'value':c})
        initial_category_values.append(c)
        
    df_line = prepare_line_chart(expenseMy, expenseAll, start_month, end_month)
    df_bar = prepare_bar_chart(expenseMy, expenseAll, reporting_month)
    
    totalSpend = dbc.Card(
    [dbc.CardBody([html.P("SPEND", className="card-title"),
                   html.H4(id = 'totalSpendMainStr', children = [str(int(expenseMy[expenseMy.posting_time.dt.month == reporting_month].amount.sum()))+' EUR'],
                   className="card-value"),
                   html.Span(id = 'totalSpendSecondStr', children = [str(round((expenseMy[expenseMy.posting_time.dt.month==reporting_month].amount.sum()/expenseMy[expenseMy.posting_time.dt.month==(reporting_month-1)].amount.sum()-1)*100,1))+'%'],
                             className="card-diff"),
                   html.Span(" vs last month",
                             className="card-diff")])])
                   
    avgDailySpend = dbc.Card(
    [dbc.CardBody([html.P("AVG DAILY SPEND", className="card-title"),
                   html.H4(id = 'avgDailySpendMainStr', children = [str(int(expenseMy[expenseMy.posting_time.dt.month == reporting_month].amount.sum()/30))+' EUR'],
                   className="card-value"),
                   html.Span(id = 'avgDailySpendSecondStr', children = [str(round((expenseMy[expenseMy.posting_time.dt.month==reporting_month].amount.sum()/expenseMy[expenseMy.posting_time.dt.month==(reporting_month-1)].amount.sum()-1)*100,1))+'%'],
                             className="card-diff"),
                   html.Span(" vs last month",
                             className="card-diff")])])
                   
    totalIncome = dbc.Card(
    [dbc.CardBody([html.P("INCOME", className="card-title"),
                   html.H4(id = 'totalIncomeMainStr', children = [str(int(incomeMy[incomeMy.posting_time.dt.month == reporting_month].amount.sum()))+' EUR'],
                   className="card-value"),
                   html.Span(id = 'totalIncomeSecondStr', children = [str(round((incomeMy[incomeMy.posting_time.dt.month==reporting_month].amount.sum()/incomeMy[incomeMy.posting_time.dt.month==(reporting_month-1)].amount.sum()-1)*100,1))+'%'],
                             className="card-diff"),
                   html.Span(" vs last month",
                             className="card-diff")])])

    # Create Layout
    dash_app.layout = html.Div([
                    
            dbc.Row([dbc.Col(html.Img(src = '../static/img/logo.png', height = 70), 
                             width = {'size':3}),
                     dbc.Col(html.H3('WE ARE YOUR SAVINGS HEDGEHOG'),
                             width = {'size':6})],
                    style={'padding': '25px'}),
                             
            dbc.Row([dbc.Col(dcc.Dropdown(id = 'categories-dropdown',
                                          options=dropdown_category_options,
                                          value=initial_category_values,
                                          multi=True),
                    width = {'size':12})],
                    style = {'padding': '25px'}),
            
            dbc.Row(dbc.Col(html.Div(dbc.CardDeck([totalSpend, avgDailySpend, totalIncome])),
                            width = {'size':12}),
                    style={'padding': '25px'}),
            
            dbc.Row([                
                    dbc.Col(dcc.Graph(figure = dict(data = [dict(x = df_bar.sort_values(by='amountMy',ascending=False).index, y = df_bar.sort_values(by='amountMy',ascending=False).amountMy, type = 'bar', name = 'My expense', ascending = 'True'),
                                                             dict(x = df_bar.index, y = df_bar.amountAvg, type = 'bar', name = 'Comparison group', color = colors['avg'])],
                                                     layout = dict(title = 'Spend by category (EUR)',
                                                     legend = dict(orientation = 'h', x=0.25, y=-0.25),
                                                     showlegend = True)),
                                       id='my-bar-chart'),
                     width = {'size':6}),

     
                     dbc.Col(dcc.Graph(figure = dict(data = [dict(x = df_line.index, y = df_line.amountMy, name = 'My expense'),
                                                             dict(x = df_line.index, y = df_line.amountAvg, name = 'Comparison group')],
                                                     layout = dict(title = 'Spend development (EUR)',
                                                     legend = dict(orientation = 'h', x=0.25, y=-0.25),
                                                     showlegend = True)),
                                       id='my-line-chart'),
                     width = {'size':6})
                     ],
                     style={'padding': '25px'})         
    ],
    style={'backgroundColor':colors['bg']})
        
    @dash_app.callback([dash.dependencies.Output('my-bar-chart', 'figure'),
                   dash.dependencies.Output('my-line-chart', 'figure'),
                   dash.dependencies.Output('totalSpendMainStr', 'children'),
                   dash.dependencies.Output('totalSpendSecondStr', 'children'),
                   dash.dependencies.Output('avgDailySpendMainStr', 'children'),
                   dash.dependencies.Output('avgDailySpendSecondStr', 'children')
                   ],
                  [dash.dependencies.Input('categories-dropdown', 'value')])
    def update_image_src(selector):
        expenseMy, incomeMy, expenseAll, incomeAll = prepare_data(raw_df, year, 1, list(selector))
        df_line = prepare_line_chart(expenseMy, expenseAll, start_month, end_month)
        df_bar = prepare_bar_chart(expenseMy, expenseAll, reporting_month)
        
        figure_bar = dict(data = [dict(x = df_bar.sort_values(by='amountMy',ascending=False).index, y = df_bar.sort_values(by='amountMy',ascending=False).amountMy, type = 'bar', name = 'My expense', ascending = 'True'),
                                                                     dict(x = df_bar.index, y = df_bar.amountAvg, type = 'bar', name = 'Comparison group', color = colors['avg'])],
                                                              layout = dict(title = 'Spend by category (EUR)',
                                                              legend = dict(orientation = 'h', x=0.25, y=-0.25),
                                                              showlegend = True))
        
        figure_line = dict(data = [dict(x = df_line.index, y = df_line.amountMy, name = 'My expense'),
                                                                     dict(x = df_line.index, y = df_line.amountAvg, name = 'Comparison group')],
                                                               layout = dict(title = 'Spend development (EUR)',
                                                               legend = dict(orientation = 'h', x=0.25, y=-0.25),
                                                               showlegend = True))
        
        totalSpendMainStr = str(int(expenseMy[expenseMy.posting_time.dt.month == reporting_month].amount.sum()))+' EUR'
        totalSpendSecondStr = str(round((expenseMy[expenseMy.posting_time.dt.month==reporting_month].amount.sum()/expenseMy[expenseMy.posting_time.dt.month==(reporting_month-1)].amount.sum()-1)*100,1))+'%'
        avgDailySpendMainStr = str(int(expenseMy[expenseMy.posting_time.dt.month == reporting_month].amount.sum()/30))+' EUR'
        avgDailySpendSecondStr = str(round((expenseMy[expenseMy.posting_time.dt.month==reporting_month].amount.sum()/expenseMy[expenseMy.posting_time.dt.month==(reporting_month-1)].amount.sum()-1)*100,1))+'%'
  
        return figure_bar, figure_line, totalSpendMainStr, totalSpendSecondStr, avgDailySpendMainStr, avgDailySpendSecondStr
    
        
        
    return dash_app.server

    
    
   


