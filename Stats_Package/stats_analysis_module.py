# %%
#Standard Packages
import pandas as pd
import numpy as np
import pickle
import qgrid
import matplotlib.pyplot as plt
#Creates view function for qgrid
def view(df_test):
   return qgrid.show_grid(df_test, grid_options={'forceFitColumns': False, 'defaultColumnWidth': 100})
import warnings
warnings.filterwarnings('ignore')
import researchpy as rp
from itertools import combinations
import scipy.stats
from statsmodels.stats.multitest import multipletests
from scipy.stats.stats import pearsonr


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
# ## Chi-Square & Post-Hoc Functions 

# %%
#Chi-Sq function, uses df, list of dependent variables, and your independent variable
def chi_sq(df, DV_list, IV, significance_level):
    df_chisq = pd.DataFrame()
    #chi sq test
    for x in DV_list:
        crosstab, test_results, expected = rp.crosstab(df[x], df[IV],
                                               test= "chi-square",
                                               expected_freqs= True,
                                               prop= "cell")
        #DV/IV columns
        test_results['DV'] = x
        test_results['IV'] = IV
        
        #appending all results & addt'l df items
        df_chisq = df_chisq.append(test_results).reset_index(drop=True) 
        df_chisq['Significance' + ' (<' + str(significance_level) + ")"] = np.where(((df_chisq['Chi-square test'] == 'p-value = ') & (df_chisq['results'] < significance_level)), 'True', 'False')
        df_chisq['Significance' + ' (<' + str(significance_level) + ")"] = np.where((df_chisq['Chi-square test'] != 'p-value = '), "", df_chisq['Significance' + ' (<' + str(significance_level) + ")"])
        var_list = order_vars(df_chisq, ['IV','DV'])
        df_chisq = df_chisq[var_list]

    return df_chisq

# %%
#Bonferonni post-hoc function for chi-square, just one test, not user facing.
def one_chisq_posthoc_bon(df, DV, IV, significance_level):
    # Store p-values of each pair
    p_vals_chi = []
    pairs_of_months = list(combinations(df[IV].unique(),2))
    
    #For Each Pair of Months compute Chi Square Stats
    for each_pair in pairs_of_months:
        
        each_df = df[(df[IV]==each_pair[0]) | (df[IV]==each_pair[1])]
        p_vals_chi.append(\
          scipy.stats.chi2_contingency(
          pd.crosstab(each_df[DV], each_df[IV]))[1])
    
    #Results of Bonferroni Adjustment - TRUE = it is significant
    bon = pd.DataFrame(columns=['IV pairs',\
                                'Original p value',\
                                'Corrected p value',\
                                'Significance' + ' (<' + str(significance_level) + ")"])
    
    bon['IV pairs'] = pairs_of_months
    bon['Original p value'] = p_vals_chi
    
    #Perform Bonferroni on the p-values and get the reject/fail to reject Null Hypothesis result.
    multi_test_results_bonferroni = multipletests(p_vals_chi, method='bonferroni')
    
    bon['Corrected p value'] = multi_test_results_bonferroni[1]
    #bon['Significance'] = multi_test_results_bonferroni[0]
    bon['Significance' + ' (<' + str(significance_level) + ")"] = np.where(bon['Corrected p value'] < significance_level, True, False)
    bon['DV'] = DV
    bon['IV'] = IV
    var_list = order_vars(bon, ['IV','IV pairs','DV'])
    bon = bon[var_list]
    
    return bon

# %%
#Bonferonni post-hoc function, able to add multiple DV's, user facing. Need to use brackets around DV_list if only using one variable
def chisq_posthoc_bon(df, DV_list, IV, significance_level):
    bon = pd.DataFrame()
    for x in DV_list:
        y = pd.DataFrame(one_chisq_posthoc_bon(df, x, IV,significance_level))
        bon = bon.append(y)
    return bon

# %% [markdown]
# ## T-tests Functions
# For further info on t-tests see this overview: https://www.jmp.com/en_us/statistics-knowledge-portal/t-test.html#:~:text=Types%20of%20t%2Dtests,and%20a%20paired%20t%2Dtest.

# %% [markdown]
# ### One Sample
# Requires: 1 continuous mesaurement (DV) & a "population" mean (IV).

# %%
#One sample t-test function, just one test, not user facing
def ttest_1sample_1(df, DV, population_mean, significance_level):
    t_statistic, pval = scipy.stats.ttest_1samp(df[DV].dropna(),population_mean)
    ttest_df = pd.DataFrame(data = {'t statistic': t_statistic, 'p value': pval}, index = [0])
    ttest_df['Significance' + ' (<' + str(significance_level) + ")"] = np.where(ttest_df['p value'] < significance_level, True, False)
    ttest_df['DV'] = DV
    ttest_df['IV'] = 'Population Mean'
    ttest_df = ttest_df[['IV', 'DV', 't statistic', 'p value', 'Significance (<0.05)']]
    return ttest_df

# %%
#One sample t-test function, user facing, takes df, list of DV's, and list of population means
def ttest_1sample(df, DV_list, population_mean_list, significance_level):
    all_df = pd.DataFrame()
    df[DV_list] = df[DV_list].astype(float) #convert dv's to float
    for x, y in zip(DV_list, population_mean_list,):
        z = ttest_1sample_1(df, x, y, significance_level)
        all_df = all_df.append(z)
    return all_df

# %% [markdown]
# ### Two-Sample (aka independent samples)
# Requires: 1 continuous measurement (DV) & two IV subcategories to compare 

#Two sample t-test function, just one test, not user facing
def ttest_2sample_1(df, DV, IV, subcategory_list, significance_level):
    t_statistic, pval = scipy.stats.ttest_ind(df[DV][df[IV] == subcategory_list[0]], 
                                              df[DV][df[IV] == subcategory_list[1]], nan_policy = 'omit')
    ttest_df = pd.DataFrame(data = {'t statistic': t_statistic, 'p value': pval}, index = [0])
    ttest_df['Significance' + ' (<' + str(significance_level) + ")"] = np.where(ttest_df['p value'] < significance_level, True, False)
    ttest_df['DV'] = DV
    ttest_df['IV'] = IV
    ttest_df['Subcategories'] = str(subcategory_list)
    ttest_df = ttest_df[['IV', "Subcategories", 'DV', 't statistic', 'p value', 'Significance (<0.05)']]
    return ttest_df

#Two sample t-test function, user facing, takes df, list of DV's, your IV, and your subcategories (only 2 allowed)
def ttest_2sample(df, DV_list, IV, subcategory_list, significance_level):
    all_df = pd.DataFrame()
    df[DV_list] = df[DV_list].astype(float) #convert dv's to float
    for x in DV_list:
        z = ttest_2sample_1(df, x, IV, subcategory_list, significance_level)
        all_df = all_df.append(z)
    return all_df

# %% [markdown]
# ### Paired-Sample 
# Requires: 1 continuous measurement (DV) & a binary categorical measurement to define relationnal groups (IV). Paired sample is less common than two-sample.

# %%
#Paired t-test function, just one test, not user facing
def ttest_paired_1(df, DV, IV, significance_level):
    t_statistic, pval = scipy.stats.ttest_rel(df[DV].dropna(), df[IV].dropna())
    ttest_df = pd.DataFrame(data = {'t statistic': t_statistic, 'p value': pval}, index = [0])
    ttest_df['Significance' + ' (<' + str(significance_level) + ")"] = np.where(ttest_df['p value'] < significance_level, True, False)
    ttest_df['DV'] = DV
    ttest_df['IV'] = IV
    ttest_df = ttest_df[['IV', 'DV', 't statistic', 'p value', 'Significance (<0.05)']]
    return ttest_df

# %%
#Paired t-test function, user facing, takes df, list of DV's, and one IV
def ttest_paired(df, DV_list, IV, significance_level):
    all_df = pd.DataFrame()
    for x in DV_list:
        z = ttest_2sample_1(df, x, IV, significance_level)
        all_df = all_df.append(z)
    return all_df

# %% [markdown]
# ## Correlations Functions

# %%
#Correlations function, not user facing, just one test
def corr_pearson1(df, DV, IV, significance_level):
    x = df[[DV,IV]].dropna()
    r, pval = pearsonr(x[DV].dropna(),x[IV].dropna())
    corr_df = pd.DataFrame(data = {'Pearsons R': r, 'p value': pval}, index = [0])
    corr_df['Significance' + ' (<' + str(significance_level) + ")"] = np.where(corr_df['p value'] < significance_level, True, False)
    corr_df['DV'] = DV
    corr_df['IV'] = IV
    var_list = order_vars(corr_df, ['IV','DV'])
    corr_df = corr_df[var_list]
    
    return corr_df

# %%
#Correlations function, user facing, takes df, list of DV's, one IV, and sig level
def corr_pearson(df, DV_list, IV, significance_level):
    all_df = pd.DataFrame()
    for x in DV_list:
        z = corr_pearson1(df, x, IV, significance_level)
        all_df = all_df.append(z)
    return all_df

# %% [markdown]
# ## ANOVA

# %% [markdown]
# ## Kruskal-Wallis  & Post-Hoc Functions 
# (non-normal ANOVA)

# %% [markdown]
# ### Assumptions

# %%
#KW shape assumption, takes df, DV variable, IV variable, and IV labels
def KW_shape_assumption(df, DV, IV, IV_labels):
        for x in IV_labels:
            plt.hist(df[df[IV] == x][DV], alpha = 0.5, label = x)
            plt.legend(loc='best')
            plt.title('Testing KW shape assumption: do the variables have the same shape? If yes - youre good to move onto the KW test')
        return plt.show




