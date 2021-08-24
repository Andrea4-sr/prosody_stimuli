#!/usr/bin/env python
# coding: utf-8

# In[1]:


# This is a Python script to calculate the number of level 4 prosodic breaks in an annotated speech act.
import sys
import pandas as pd
from collections import Counter
# import numpy as np


# In[2]:


path = '/Users/andreasantos/Documents/Andrea/Studies/Universities/UZH/Internships/L\'ENS-CoLM/BU_Project_Bogdan/BU_Raw_Data/Annotations/f1a/j/f1ajrlp1.brk'
groups = []


# In[3]:


def read_break_files(file):
    df = pd.read_csv(file, skiprows=8, sep='\s+', header=None)
    df.columns = ['Seconds', 'Color', 'Break_Level_Annotation', 'NaN', 'End_of_Phrase']
    return df


# In[4]:


def convert_string_to_int(df):
    df['Seconds'] = pd.to_numeric(df['Seconds'])
    return df


# In[5]:


def check_seconds_constraint(data):
    return data[(data['Seconds'] - data['Seconds'] < 5.000000) & (data['Break_Level_Annotation'] == '4')]


# In[6]:


def extract_groups_between_four(data, new_group = []):
    
    row_iterator = data.iterrows()
    for i, row in row_iterator: #for index, row in row_iterator

        if row['Break_Level_Annotation'] == '4': #check if data in column 'Break_Level_Annotation' is  '4'
            new_group.append(row['Break_Level_Annotation']) #if data == '4', append row data to new_group arra
        
            new_group = [] # initialise empty new_group array
            new_group.append(row['Break_Level_Annotation']) # append last '4' as first '4' of next array
            
            groups.append(new_group) # add new_groups to group array
            
        if row['Break_Level_Annotation'] != '4': # 
            new_group.append(row['Break_Level_Annotation'])
            
            
    return groups


# In[7]:


def middle_break_4(data, new_group=[], first=int, last=int):
    
    row_iterator = data.iterrows()
    for i, row in row_iterator: #for index, row in row_iterator
        
        if row['Break_Level_Annotation'] == '4':
            first == row['Break_Level_Annotation']
            new_group.append(first)
            
            first == last 
            
            new_group=[]
            new_group.append(last)
            
            groups.append(new_group)
            
        if row['Break_Level_Annotation'] != '4':
            new_group.append(row['Break_Level_Annotation'])
        
            
    return groups


# In[8]:


def middle_break_3(phrases, dict_count={}, stimuli_groups=[], count=0): 
    
    for idx,item in enumerate(groups):
        count = item.count('3')+item.count('3-')
        dict_count[idx+1] = (count,item)
        
    for key,value in list(dict_count.items()):
        if value[0] != 1:
            del dict_count[key]
    
            
    return dict_count, len(dict_count)


# In[9]:


def main():
    results = middle_break_3(extract_groups_between_four(convert_string_to_int(read_break_files(path))))
    groups_4 = middle_break_4(convert_string_to_int(read_break_files(path)))
    return print(groups_4)


# In[10]:


if __name__ == '__main__':
    main()


# In[ ]:





# In[ ]:




