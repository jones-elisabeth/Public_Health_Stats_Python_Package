# %% [markdown]
# ### Frequencies, Descriptives, and Crosstabs Functions
# Purpose: this notebook was created to create functions to export count and percent frequencies in an orderly manner using python. 
# 
# Author: Elisabeth Jones
# 
# Date Created: 1/13/22
# 
# Instructions: 
#    * There are three functions created in this notebook:
#         * xtabs_cols(df, DV, IV)
#             * produces counts as well as column percentages
#         * xtabs_rows(df, DV, IV)
#             * produces counts as well as row percentages
#         * xtabs_all(df, DV, IV)
#             * produces counts as well as percentages out of the overall total
#    * Parameters: 
#         * df = dataframe you're analyzing
#         * DV = string of your dependent variable
#         * IV = string of your independent variable
#    * Example: 
#         * If I want to run crosstabs that include the row percentages on my datagframe "df" using the variables "Age_Groups" as IV and "Ever_Cig_Use" as my DV the syntax would looks as follows: 
#         * xtabs_rows(df, "Age_Groups", "Ever_Cig_Use") 
#    * To combine multiple xtabs: 
#         * Make a list of the variables you want to combine (i.e., xtab_list = [xtab1, xtab2, xtab3] 
#         * use the pd.concat() function to combine together and export into excel. 
#          

# %%
#Import libraries/packages

#Standard Packages
import pandas as pd
import numpy as np

# %% [markdown]
# #### Order vars function - not user facing

# %%
#orders variables for exports
def order_vars(df, first_vars_list):
#Creates list of all project vars/columns
    columns_list = df.columns.to_list()
#Joins first_vars_list with columns_list with duplicates
    combined_vars_list = first_vars_list + columns_list
#Creates vars list in desired ordered without duplicates
    ordered_vars_list = []
    for i in combined_vars_list:
        if i not in ordered_vars_list:
            ordered_vars_list.append(i)
    return ordered_vars_list  

# %% [markdown]
# #### Frequencies/Descriptives Functions

# %%
#single frequencies function - not user facing
def freqs_one(df, variable, DropNA_TrueorFalse):
    #counts
    x = df[variable].value_counts(dropna = DropNA_TrueorFalse)
    #percents
    y = df[variable].value_counts(dropna = DropNA_TrueorFalse, normalize = True) 
    #pushing into df
    freq_df = pd.DataFrame({'Counts': x, 'Pct': y}).reset_index()
    freq_df = freq_df.rename(columns={'index' : 'Values'})
    freq_df['Variable'] = variable
    freq_df['Percents'] = freq_df['Pct'] * 100
    freq_df['Percents'] = freq_df['Percents'].round(2)
    freq_df['Percents'] = freq_df['Percents'].astype(str)
    freq_df['Percents'] = freq_df['Percents'] + '%'
    freq_df = freq_df[['Variable', 'Values', 'Counts', 'Percents']]
    freq_df['Values'] = freq_df['Values'].astype(str)
    return freq_df

# %%
#multiple frequencies function - user facing - takes df, variable list, and True or False (to drop NAs)
def freqs(df, var_list, DropNA_TrueorFalse):
    freqs_all = pd.DataFrame()
    for x in var_list:
        y = freqs_one(df, x, DropNA_TrueorFalse)
        freqs_all = freqs_all.append(y)
    return freqs_all

# %%
#descriptive (count, mean, st dev, intervals), takes df and variable list
def desc(df, var_list):
    desc_df = pd.DataFrame()
    for x in var_list:
        y = pd.DataFrame(df[x].describe()).reset_index()
        y = y.rename(columns={'index' : 'Summary_Stats', x : 'Results'})
        y['Variable'] = x
        desc_df = desc_df.append(y)
        desc_df = desc_df[['Variable', 'Summary_Stats', 'Results']]
    return desc_df

#descriptives with subcategories (count, mean, st dev, intervals), takes df, variable list, sub categoy variable, and sub categories
def desc_subcats(df,var_list,sub_category_var,sub_category_list):
    desc_df = pd.DataFrame()
    for x in sub_category_list:
        y = desc(df[df[sub_category_var] == x],var_list)
        y['Subcategory'] = x
        desc_df = desc_df.append(y)
        desc_df = desc_df[['Variable','Subcategory', 'Summary_Stats', 'Results']]
    return desc_df

# %% [markdown]
# #### Crosstabs Functions

# %%
#Counts + Col %'s' xtabs - not user facing - feed in dataframe, DV, and IV 
def xtab_cols1(df,DV,IV):
    #run counts using crosstab()
    x = pd.crosstab(df[DV],df[IV], margins = True, dropna=False, )
    x['Counts/Percents'] = 'Counts'
    
    #run percents using crosstab()
    y = pd.crosstab(df[DV],df[IV], dropna=False, margins = True, normalize = 'columns')
    sum = y.sum() #Adding All row 
    sum.name = 'All'
    y = y.append(sum.transpose())
    y = y * 100 #convert from decimal to %
    y = y.round(2) #round to 3 decimals
    y = y.astype(str)
    y = y + '%'
    y['Counts/Percents'] = 'Column Percents'
    
    #push both into df 
    z = pd.concat([x,y])
    z = z.reset_index()
    z[DV] = z[DV].astype(str)
    z = z.sort_values(by=[DV]) 
    z['DV'] = DV
    var_list = order_vars(z, ['Counts/Percents','DV'])
    z = z[var_list]
    z = z.rename(columns={DV : 'Values'})
    
    return z

# %%
#xtabs cols function - user facing - takes df, DV list, and IV
def xtab_cols(df,DV_list,IV):
    all_df = pd.DataFrame()
    for x in DV_list:
        z = xtab_cols1(df,x,IV)
        all_df = all_df.append(z)
    return all_df

# %%
##Counts + Row %'s' xtabs - not user facing - feed in dataframe, DV, and IV
#def xtab_rows1(df,DV,IV):
#    #run counts using crosstab()
#    x = pd.crosstab(df[DV],df[IV], margins = True, dropna=False, )
#    x['Counts/Percents'] = 'Counts'
#    
#    #run percents using crosstab()
#    y = pd.crosstab(df[DV],df[IV], dropna=False, margins = True, normalize = 'index')
#    y = y * 100 #convert from decimal to %
#    y = y.round(1) #round to 3 decimals
#    y = y.
#    y['Counts/Percents'] = 'Row Percents'
#    
#    #push both into df 
#    z = pd.concat([x,y])
#    z = z.reset_index()
#    z[DV] = z[DV].astype(str)
#    z = z.sort_values(by=[DV]) 
#    z['DV'] = DV
#    var_list = order_vars(z, ['Counts/Percents','DV'])
#    z = z[var_list]
#    z = z.rename(columns={DV : 'Values'})
#    
#    return z

# %%
#Counts + Row %'s' xtabs - not user facing - feed in dataframe, DV, and IV
def xtab_rows1(df,DV,IV):
    #run counts using crosstab()
    x = pd.crosstab(df[DV],df[IV], margins = True, dropna=False, )
    x['Counts/Percents'] = 'Counts'
    
    #run percents using crosstab()
    y = pd.crosstab(df[DV],df[IV], dropna=False, margins = True, normalize = 'index')
    y['All'] = y[y.columns.to_list()].sum(axis=1) #Adding All row
    y = y * 100 #convert from decimal to %
    y = y.round(2) #round to 3 decimals
    y = y.astype(str)
    y = y + '%'
    y['Counts/Percents'] = 'Row Percents'
    
    #push both into df 
    z = pd.concat([x,y])
    z = z.reset_index()
    z[DV] = z[DV].astype(str)
    z = z.sort_values(by=[DV]) 
    z['DV'] = DV
    var_list = order_vars(z, ['Counts/Percents','DV'])
    z = z[var_list]
    z = z.rename(columns={DV : 'Values'})
    
    return z

# %%
#xtabs rows function - user facing - takes df, DV list, and IV
def xtab_rows(df,DV_list,IV):
    all_df = pd.DataFrame()
    for x in DV_list:
        z = xtab_rows1(df,x,IV)
        all_df = all_df.append(z)
    return all_df

# %%
#Counts + All %'s' xtabs - not user facing- feed in dataframe, DV, and IV 
def xtab_all1(df,DV,IV):
    #run counts using crosstab()
    x = pd.crosstab(df[DV],df[IV], margins = True, dropna=False, )
    x['Counts/Percents'] = 'Counts'

    
    #run percents using crosstab()
    y = pd.crosstab(df[DV],df[IV], dropna=False, margins = True, normalize = 'all')
    y = y * 100 #convert from decimal to %
    y = y.round(2) #round to 3 decimals
    y = y.astype(str)
    y = y + '%'
    y['Counts/Percents'] = 'Total Percents'

    
    z = pd.concat([x,y])
    z = z.reset_index()
    z[DV] = z[DV].astype(str)
    z = z.sort_values(by=[DV]) 
    z['DV'] = DV
    var_list = order_vars(z, ['Counts/Percents','DV'])
    z = z[var_list]
    z = z.rename(columns={DV : 'Values'})
    return z

# %%
#xtabs rows function - user facing - takes df, DV list, and IV
def xtab_all(df,DV_list,IV):
    all_df = pd.DataFrame()
    for x in DV_list:
        z = xtab_all1(df,x,IV)
        all_df = all_df.append(z)
    return all_df
