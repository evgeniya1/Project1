#!/usr/bin/env python
# coding: utf-8

# In[11]:


#import necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


##############################
#####preprocess functions#####
##############################

#function to define new column with first entry
def split_column(df,col_names):
    for i in range(len(col_names)):
        column = col_names[i]
        new_column = 'first_' + column
        #print(column)
        df[new_column] = [x.split(', ')[0] if x is not np.nan 
                                               else np.nan for x in df[column]]
    return df

#function to fill missing values in the initial data
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

#function to select top most frequent values from categorical variable
def quick_cat(_series,top_number):
    #count values in a column and normalize to show percentage
    top = _series.value_counts(normalize=True)[:top_number]        
    #print(f"Number of unique values is {_series.nunique()}.")
    #print(f"The first {top_number} items are present in {round(top.sum()*100,1)} % of data.")   
    return top


#function to transform categorical variable by leaving 
#most frequent values and putting the rest into 'other' category 
def transform_cat_columns(col_name,top_number,df):
    #select top # of most frequent values in categorical column
    select_col = quick_cat(df[col_name],top_number).index
    #assign a name for new column 
    col_rename = col_name.replace('first','select')
    #transform categotical data to a columns with fewer values
    df[col_rename] = df[col_name].map(lambda x: 
                                          x if x in select_col else 'other')
    return df
    
#add transformed columns using function above
def add_cat_columns(df,col_names = ['first_genres'
                                         ,'first_production_countries'
                                         ,'first_production_companies'],
                    top_numbers = [6,6,21]):
    #add columns by transforming
    for i in range(len(col_names)):
        transform_cat_columns(col_names[i],top_numbers[i],df)
    
    return df

#add column with budget categories
def add_budget_cat(df):
    #add column that categotize the budget
    df['budget_category'] = pd.cut(df.budget_M,[-10,0.0005,0.01,1,10,30,100,1000],
                               labels=['<= 0.5k','(0.5k, 10k]',
                                       '(10k, 1M]',
                                       '(1M, 10M]',
                                       '(10M, 30M]',
                                       '(30M, 100M]',
                                       '> 100M'
                                      ])
    return df

#all preprocessing
def preprocess(df):
    #fill missing values
    df = fill_missing(df)
    #extract the first entry in a column and select 
    df = add_cat_columns(df)
    #add categorical budget column
    df = add_budget_cat(df)
    
    return df

#functions to compute 25,75 percentiles
def perc_25(x):
    return np.percentile(x, q = [25])
def perc_75(x):
    return np.percentile(x, q = [75])

############################
#####plotting functions#####
############################

#plot count and box plots
def plot_count_box(df,filter_cond,_ylim):

    #analyze the filtered data
    fig, (ax1,ax2) = plt.subplots(1,2,figsize=(12,5))

    #plot the number of movies versus budget category
    sns.countplot(x='budget_category', data=df[filter_cond], ax=ax1)
    #change axis labels
    ax1.set_xticklabels(ax1.get_xticklabels(),rotation = 90)
    ax1.set_xlabel('budget category')
    ax1.set_ylabel('number of movies')

    #plot return in % versus budget category
    sns.boxplot(x='budget_category',y='gain/loss_%',data=df[filter_cond],showfliers=True,ax=ax2)
    #change axis labels
    ax2.set_xticklabels(ax2.get_xticklabels(),rotation = 90)
    ax2.set_xlabel('budget category')
    ax2.set_ylabel('return (%)')
    ax2.set_ylim(_ylim)
    
    ax2.axhline(linewidth=4, color='r')

    plt.tight_layout()
    return None

#add table with 1,2 and 3 quantiles
def table_Q123(df,filter_cond):
    #summary
    table = df[filter_cond].groupby('budget_category')['gain/loss_%']                       .agg([perc_25,np.median,perc_75])
    table.index.names = ['budget']
    table.rename(columns={'perc_25':'Q1','median':'Q2 (median)','perc_75':'Q3'},inplace=True)
    return table

#plot boxplot with filtered data
def plot_return_filter(df,filter_add,hue_by,hue_order
                       ,_xlim,_ylim,_title
                       ,_bbox_to_anchor = [1.15, 0.5]):
    
    fig, ax = plt.subplots(1,1,figsize=(18,6))

    #plot return in % versus budget category for most common genres
    ax = sns.boxplot(x='budget_category',y='gain/loss_%',hue=hue_by,
                     hue_order = hue_order,
                     data=df[filter_add],showfliers=True)

    #change legend location
    ax.legend(loc='right',bbox_to_anchor = _bbox_to_anchor)
    #change axis labels
    ax.set_xticklabels(ax.get_xticklabels(),rotation = 90)
    ax.set_xlabel('budget category')
    ax.set_ylabel('return (%)')
    ax.set_xlim(_xlim)
    ax.set_title(_title)
    ax.set_ylim(_ylim)
    
    ax.axhline(linewidth=4, color='r')

    plt.tight_layout()

