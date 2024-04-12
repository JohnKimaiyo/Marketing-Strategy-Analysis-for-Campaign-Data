#!/usr/bin/env python
# coding: utf-8

# # Marketing Startegy Analysis

# # Table of Content
# 
# ## 1 Introduction
# ## 2 Data Loading and Quality
# ## 3 Feature Additions and Engineering
# ## 4 Exploration Data Analysis and Statistsical Analysis
# ## 5 Final Recommendation (Optimial Sales)

# # 1 Introduction
# 

# - What is the impact of each marketing strategy and sales visit on Sales (Amount Collected)?
# - Is the same strategy valid for all the different client types ?
# 

# # 2 Data loading and Quality Checks

# In[62]:


import pandas as pd
import numpy as np
import seaborn as sns
import scipy.stats


campaign_df = pd.read_csv(r"C:\Users\jki\Downloads\Campaign-Data.csv")
campaign_df.head(5)


# In[63]:


campaign_df.columns


# # 3 Feature Additions and Engineering

# In[64]:


## Creation of Additional Features 
campaign_df['Calendardate']=pd.to_datetime(campaign_df['Calendardate'])
campaign_df['Calendar_Month']=campaign_df['Calendardate'].dt.month
campaign_df['Calendar_Year']=campaign_df['Calendardate'].dt.year


# ### 4. Exploratory Data Analysis and Statistical Analysis
# We can have a detailed exploration that can be added to this section, but since we only need to answer three questions:
# 
# <b> 4.1 Exploring and Understanding basics data </b>
# 
# 1. Distribution of Data across different accounts
# 2. Difference of Sales in Account Types (Using Categorical Mean)
# 
# <b> 4.2 Statistical Analysis - Answering the Questions</b>
# 1. Impact of Marketing Strategy on Sales (Using Correlation, Regression and Decision Tree)
# 2. Impact of Competition on Sales
# 3. How different types of client can have different strategies (Broken down Question 1 and Question 2 based on Account Type)

# ### 4.2 Impact of Marketing Strategy on Sales 

# #### Understanding of distrubtions

# In[65]:


campaign_df['Client Type'].value_counts(normalize=True)


# In[67]:


pd.crosstab(campaign_df['Number of Competition'],campaign_df['Client Type'],margins=True,normalize='columns')


# In[68]:


campaign_df.groupby('Number of Competition').mean()


# In[69]:


campaign_df.groupby('Client Type').mean()


# In[71]:


campaign_df.corr()['Amount Collected']


# # Correlation Analysis

# In[72]:


## Consolidated Strategy for Targeting
        
import seaborn as sns
cm = sns.light_palette("green", as_cmap=True)
correlation_analysis=pd.DataFrame(campaign_df[['Amount Collected',
'Campaign (Email)', 'Campaign (Flyer)', 'Campaign (Phone)',
       'Sales Contact 1', 'Sales Contact 2', 'Sales Contact 3',
       'Sales Contact 4', 'Sales Contact 5']].corr()['Amount Collected']).reset_index()
correlation_analysis.columns=['Impacting Variable','Degree of Linear Impact (Correlation)']
correlation_analysis=correlation_analysis[correlation_analysis['Impacting Variable']!='Amount Collected']
correlation_analysis=correlation_analysis.sort_values('Degree of Linear Impact (Correlation)',ascending=False)
correlation_analysis.style.background_gradient(cmap=cm).set_precision(2)


# #### Market Strategy Impact on Sales (Broken by different account type)

# In[73]:


# Import seaborn library
import seaborn as sns
cm = sns.light_palette("green", as_cmap=True)
correlation_analysis=pd.DataFrame(campaign_df.groupby('Client Type')[['Amount Collected',
       'Campaign (Email)', 'Campaign (Flyer)', 'Campaign (Phone)',
       'Sales Contact 1', 'Sales Contact 2', 'Sales Contact 3',
       'Sales Contact 4', 'Sales Contact 5']].corr()['Amount Collected']).reset_index()
correlation_analysis=correlation_analysis.sort_values(['Client Type','Amount Collected'],ascending=False)
correlation_analysis.columns=['Acc Type','Variable Impact on Sales','Impact']
correlation_analysis=correlation_analysis[correlation_analysis['Variable Impact on Sales']!='Amount Collected'].reset_index(drop=True)
correlation_analysis.style.background_gradient(cmap=cm).set_precision(2)


# #### Regression Analysis (Market Sales and Strategies)

# In[74]:


import statsmodels.api as sm
import statsmodels.formula.api as smf

# Replace spaces and parentheses in column names
campaign_df.columns = [mystring.replace(" ", "_") for mystring in campaign_df.columns]
campaign_df.columns = [mystring.replace("(", "") for mystring in campaign_df.columns]
campaign_df.columns = [mystring.replace(")", "") for mystring in campaign_df.columns]

# Fit the OLS model
results = smf.ols(formula='Amount_Collected ~ Campaign_Email + Campaign_Flyer + Campaign_Phone + \
                    Sales_Contact_1 + Sales_Contact_2 + Sales_Contact_3 + Sales_Contact_4 + Sales_Contact_5',
                  data=campaign_df).fit()

# Print summary
print(results.summary())



# In[78]:


df = pd.read_html(results.summary().tables[1].as_html(),header=0,index_col=0)[0]


# In[79]:


df =df.reset_index()
df =df[df ['P>|t|']<0.05][['index','coef']]
df.head(5)
campaign_df.head(5)


# #### Regression Analysis (Market Sales and Strategies) - Broken for different account types

# In[81]:


import statsmodels.api as sm
import statsmodels.formula.api as smf

# Replace spaces and parentheses in column names
campaign_df.columns = [mystring.replace(" ", "_") for mystring in campaign_df.columns]
campaign_df.columns = [mystring.replace("(", "") for mystring in campaign_df.columns]
campaign_df.columns = [mystring.replace(")", "") for mystring in campaign_df.columns]

# Fit the OLS model for the entire dataset
results = smf.ols(formula='Amount_Collected ~ Campaign_Email + Campaign_Flyer + Campaign_Phone + \
                    Sales_Contact_1 + Sales_Contact_2 + Sales_Contact_3 + Sales_Contact_4 + Sales_Contact_5',
                  data=campaign_df).fit()

# Print summary
print(results.summary())

consolidated_summary = pd.DataFrame()

# Iterate over unique values of 'Client_Type'
for acctype in campaign_df['Client_Type'].unique():
    temp_campaign_df = campaign_df[campaign_df['Client_Type'] == acctype].copy()
    
    # Fit the OLS model for each 'Client_Type'
    results = smf.ols(formula='Amount_Collected ~ Campaign_Email + Campaign_Flyer + Campaign_Phone + \
                    Sales_Contact_1 + Sales_Contact_2 + Sales_Contact_3 + Sales_Contact_4 + Sales_Contact_5',
                      data=temp_campaign_df).fit()
    
    # Extract coefficients and significant variables
    df = pd.read_html(results.summary().tables[1].as_html(), header=0, index_col=0)[0].reset_index()
    df = df[df['P>|t|'] < 0.05][['index', 'coef']]
    df.columns = ['Variable', 'Coefficient (Impact)']
    df['Account Type'] = acctype
    df = df.sort_values('Coefficient (Impact)', ascending=False)
    df = df[df['Variable'] != 'Intercept']
    print(acctype)
    print(df)
    consolidated_summary = consolidated_summary.append(df)

print(consolidated_summary)


# In[83]:


import statsmodels.api as sm
import statsmodels.formula.api as smf
consolidated_summary=pd.DataFrame()

for acctype in list(set(list(campaign_df['Client_Type']))):
    print(acctype)
    temp_campaign_df=campaign_df[campaign_df['Client_Type']==acctype].copy()
    formula = 'Amount_Collected ~ Campaign_Email + Campaign_Flyer + Campaign_Phone + \
               Sales_Contact_1 + Sales_Contact_2 + Sales_Contact_3 + Sales_Contact_4 + Sales_Contact_5'
    results = smf.ols(formula, data=temp_campaign_df).fit()
    df = pd.read_html(results.summary().tables[1].as_html(),header=0,index_col=0)[0].reset_index()
    df = df[df['P>|t|']<0.05][['index', 'coef']]
    df.columns=['Variable', 'Coefficient (Impact)']
    df['Account Type']=acctype
    df=df.sort_values('Coefficient (Impact)', ascending=False)
    df=df[df['Variable']!='Intercept']
    consolidated_summary=consolidated_summary.append(df)
    print(results.summary())  

print(consolidated_summary)


# ### 5. Final Recommendations

# Using the below table we can use the coefficent to see how much return we can derive from each dollar we spend, here we can clearly see that for different account type different Campaigns and Different Sales Contact are effective with different extend. 
# 
# <b>Case Explanation - Medium Facility </b><br>
# For Example Medium Facility shows decent results with Flyer Campiagns and each dollar spend return 4 dollars on average. Sales Contact 2 is highly effective followed by Sales Contact 1 and Sales Contact 3. Else all other strategy shows no impact can be dropped to save cost. 
# 

# In[84]:


consolidated_summary


# In[85]:


consolidated_summary.reset_index(inplace=True)
consolidated_summary.drop('index',inplace=True,axis=1)


# In[86]:


consolidated_summary.columns = ['Variable','Return on Investment','Account Type']
consolidated_summary['Return on Investment']= consolidated_summary['Return on Investment'].apply(lambda x: round(x,1))
consolidated_summary.style.background_gradient(cmap='RdYlGn')


# In[87]:


import seaborn as sns
import matplotlib.pyplot as plt 


# In[88]:


def format(x):
        return "${:.1f}".format(x)
consolidated_summary['Return on Investment']  = consolidated_summary['Return on Investment'].apply(format)


# In[89]:


consolidated_summary.columns = ['Variable','Return on Investment','Account Type']
consolidated_summary.style.background_gradient(cmap='RdYlGn')


# In[90]:


consolidated_summary.to_csv('consolidated_summary.csv')
files.download('consolidated_summary.csv')


# In[ ]:




