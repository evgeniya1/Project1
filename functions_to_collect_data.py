#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import time
import json
import requests

################Define functions########################
#get api keys provided a path
def get_keys(path):
    with open(path,'r') as f:
        return json.load(f)
        
#function to read the data from the json file
def read_dicts(_dicts):
    result = ''
    for item in _dicts:
        result += item['name'] + ', '
    return result.rstrip(', ')

#function to read 
def collect_data_moviedb(api_key, movie_ids
                         ,chunk_size = 10000
                         ,num_chunks = 15
                         ,start_chunk = 1
                         ,data_folder = 'data'
                         ,sleep_time = 0.25):
    #the movie number according to start chunk and chunk size
    i = (start_chunk - 1)*chunk_size + 1
    
    #run a for loop to read specific movie ids
    for chunk in range(start_chunk, start_chunk + num_chunks + 1):
        dfs = []
        for movie_id in movie_ids[i:i + chunk_size]:
            #include pause to accommodate 40 movies per 10 seconds allowed rate
            time.sleep(sleep_time)
            #run a request with specific movie id
            response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key={}'.format(movie_id,api_key))
            try:
                #open data in json format
                data = response.json()
                #append collected single movie data to a list of dataframes
                dfs.append(pd.DataFrame(dict(title = data['title']
                                       ,budget = data['budget']
                                       ,revenue = data['revenue']
                                       ,genres = read_dicts(data['genres'])
                                       ,production_countries = read_dicts(data['production_countries'])
                                       ,production_companies = read_dicts(data['production_companies'])
                                       ,adult = data['adult']
                                       ,popularity = data['popularity']
                                       ,original_language = data['original_language']
                                       ,release_date = data['release_date']
                                       ,runtime = data['runtime']
                                       ,vote_average = data['vote_average']
                                       ,vote_count = data['vote_count']),index=[movie_id]  
                                       )                             
                          )
            except:  
                print('Response error to movie_id {}.'.format(movie_id))
            i += 1

        df = pd.concat(dfs,ignore_index=True)
        df.to_csv('{}/moviesdb_chunk_{}.csv'.format(data_folder,chunk))
    return print('The specified data is collected in {}/'.format(data_folder))


# In[ ]:




