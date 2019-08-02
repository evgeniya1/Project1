#!/usr/bin/env python
# coding: utf-8

# In[40]:


import pandas as pd
import numpy as np


# In[62]:


def split_column(df,col_names):
    for i in range(len(col_names)):
        column = col_names[i]
        new_column = 'first_' + column
        #print(column)
        df[new_column] = [x.split(', ')[0] if x is not np.nan 
                                               else np.nan for x in df[column]]
    return df

def fill_missing(df,col_names=['genres',                              
                               'production_countries',
                               'production_companies',]):
    #fill missing values for run time with median
    df.runtime.fillna(df.runtime.median(),inplace=True)

    #fill mising values with 'missing'
    df.genres.fillna('missing',inplace=True)
    df.production_countries.fillna('missing',inplace=True)
    df.production_companies.fillna('missing',inplace=True)
    
    #rescale bugdet to list in million $
    scale = 10**6
    df['budget_M'] = df['budget'].div(scale)
    df['revenue_M'] = df['revenue'].div(scale)

    #total budget in million $ and %
    df['return_M'] = df.revenue_M - df.budget_M
    df['gain/loss_%'] = round((df.return_M/df.budget_M - 1) * 100, 2)

    #add positive/negative return %
    df['return_type'] = df['gain/loss_%'].map(lambda x: 'gain'
                                           if x > 0 else 'loss')

    #add year column
    df.release_date = df.release_date.astype('datetime64[ns]')
    df['year'] = df.release_date.dt.year.fillna(0).astype('int64')

    #add first item in given columns
    df = split_column(df,col_names)
    
    first_cols = ['first_'+ col for col in col_names]
    
    select_cols = ['title','year','budget_M',
                   'revenue_M','return_M','gain/loss_%',
                   'return_type','runtime'] + first_cols
    
    #select necessary columns
    df = df[select_cols]  
    return df

def quick_cat(_series,top_number):
    #count values in a column and normalize to show percentage
    top = _series.value_counts(normalize=True)[:top_number]        
    #print(f"Number of unique values is {_series.nunique()}.")
    #print(f"The first {top_number} items are present in {round(top.sum()*100,1)} % of data.")   
    return top


def transform_cat_columns(col_name,top_number,df):
    #select top # of most frequent values in categorical column
    select_col = quick_cat(df[col_name],top_number).index
    #assign a name for new column 
    col_rename = col_name.replace('first','select')
    #transform categotical data to a columns with fewer values
    df[col_rename] = df[col_name].map(lambda x: 
                                          x if x in select_col else 'other')
    return df
    

def add_cat_columns(df,col_names = ['first_genres'
                                         ,'first_production_countries'
                                         ,'first_production_companies'],
                    top_numbers = [6,6,21]):
    #add columns by transforming
    for i in range(len(col_names)):
        transform_cat_columns(col_names[i],top_numbers[i],df)
    
    return df

def add_budget_cat(df):
    #add column that categotize the budget
    df['budget_category'] = pd.cut(df.budget_M,[0,0.0005,0.01,1,10,30,100,1000],
                               labels=['< 0.5k','[0.5k, 10k]',
                                       '(10k, 1M)',
                                       '[1M, 10M]',
                                       '(10M, 30M)',
                                       '[30M, 100M)',
                                       '>= 100M'
                                      ])
    return df

def preprocess(df):
    #fill missing values
    df = fill_missing(df)
    #extract the first entry in a column and select 
    df = add_cat_columns(df)
    #add categorical budget column
    df = add_budget_cat(df)
    
    return df


# In[65]:


# df_init = pd.read_csv('final_movie_data.csv',index_col=0)
# df = preprocess(df_init)

# #show summary of the data
# display(df.describe())
# display(df.describe(include=['object']))


# In[64]:


# df.head()


# In[ ]:




