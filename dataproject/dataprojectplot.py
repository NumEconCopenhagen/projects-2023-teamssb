# Imports 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widgets

# Plot for first dataset (regr11) 
def _plot_exp(dataframe, variable, region, years):

    
    fig = plt.figure(dpi=100)
    ax = fig.add_subplot(1,1,1)
    
    dataframe.loc[:,['year']] = pd.to_numeric(dataframe['year'])
    I = (dataframe['year'] >= years[0]) & (dataframe['year'] <= years[1]) & (dataframe['region'] == region)
        
    x = dataframe.loc[I,'year']
    y = dataframe.loc[I,variable]

    ax.set_title('Expenditure of Danish Regions')
    ax.set_xlabel('Years', fontsize = 10)
    ax.set_ylabel('Billion kr., 22-prices', fontsize = 10)
    ax.plot(x,y)

def plot_exp(dataframe):

    widgets.interact(_plot_exp, 
    dataframe = widgets.fixed(dataframe),
    
    variable = widgets.Dropdown(
        description='variable', 
        options=['expenditure'], 
        value='expenditure'),
        
    region = widgets.Dropdown(description='region', 
                                        options=dataframe.region.unique(), 
                                        region='Region Nordjylland'),

    years=widgets.IntRangeSlider(
            description="years",
            min=2007,
            max=2021,
            value=[2007, 2021],
            continuous_update=False,
        )   
    ); 

# Plot for second dataset, from KRL

def _plot_emp(dataframe, variable, region, years):
    
    fig = plt.figure(dpi=100)
    ax = fig.add_subplot(1,1,1)
    
    dataframe.loc[:,['year']] = pd.to_numeric(dataframe['year'])
    I = (dataframe['year'] >= years[0]) & (dataframe['year'] <= years[1]) & (dataframe['region'] == region)
        
    x = dataframe.loc[I,'year']
    y = dataframe.loc[I,variable]

    ax.set_title('Fulltime employees of Danish Regions')
    ax.set_xlabel('Years', fontsize = 10)
    ax.set_ylabel('Fulltime employees', fontsize = 10)
    ax.plot(x,y)

def plot_emp(dataframe):

    widgets.interact(_plot_emp, 
    dataframe = widgets.fixed(dataframe),
    
    variable = widgets.Dropdown(
        description='variable', 
        options=['fulltime_emp'], 
        value='fulltime_emp'),
        
    region = widgets.Dropdown(description='region', 
                                        options=dataframe.region.unique(), 
                                        region='Region Nordjylland'),

    years=widgets.IntRangeSlider(
            description="years",
            min=2007,
            max=2021,
            value=[2007, 2021],
            continuous_update=False,
        )   
    ); 

# Plot merged dataset

def _plot_merged(dataframe, variable1, variable2, region, years):
    
    fig = plt.figure(dpi=100)
    ax1 = fig.add_subplot(1,1,1)
    ax2 = ax1.twinx()
    
    dataframe.loc[:,['year']] = pd.to_numeric(dataframe['year'])
    I = (dataframe['year'] >= years[0]) & (dataframe['year'] <= years[1]) & (dataframe['region'] == region)
        
    x = dataframe.loc[I,'year']
    y1 = dataframe.loc[I,variable1]
    y2 = dataframe.loc[I,variable2]

    ax1.set_title('Fulltime employees and Expenditure of Danish Regions')
    ax1.set_xlabel('Years', fontsize = 10)
    ax1.set_ylabel('Fulltime employees', fontsize = 10, color = 'blue')
    ax1.plot(x,y1, color='blue')
    
    ax2.set_ylabel('Expenditure, billion kr. 22-prices', fontsize = 10, color='red')
    ax2.plot(x,y2, color='red')

def plot_merged(dataframe):

    widgets.interact(_plot_merged, 
    dataframe = widgets.fixed(dataframe),
    
    variable1 = widgets.Dropdown(
        description='variable1', 
        options=['fulltime_emp'], 
        value='fulltime_emp'),
    
    variable2 = widgets.Dropdown(
        description='variable2', 
        options=['expenditure'], 
        value='expenditure'),

    region = widgets.Dropdown(description='region', 
                              options=dataframe.region.unique(), 
                              value='Region Nordjylland'),

    years=widgets.IntRangeSlider(
            description="years",
            min=2007,
            max=2021,
            value=[2007, 2021],
            continuous_update=False,
        )   
    ); 
