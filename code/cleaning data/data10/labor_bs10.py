# -*- coding: utf-8 -*-
"""
Created on Thu May 31 10:50:45 2018

@author: Albert
"""
# =============================================================================
# Labor and business income Uganda 2010-11
# =============================================================================


'''
DESCRIPTION
     Uses the data from the household questionnaire in the UNPS 2010-2011 (ISA-LSMS) and computes:
         - household labor income, labor supply, business proftis, and other sources of income
Main outcome: income_hhsec_2010.csv
'''

import pandas as pd
import numpy as np
import os
from pathlib import Path
import sys
dirct  = Path('Master_data.py').resolve().parent
sys.path.append(str(dirct))

from data_functions_albert import remove_outliers

if '\\' in str(dirct):
    print(True)
    dirct= str(dirct).replace('\\', '/')

else:
    dirct = str(dirct)


my_dirct = str(dirct)+'/data/raw data/2010/'
folder =  str(dirct)+'/data/data10/'
folder2 = str(dirct)+'/data/auxiliary data/'
# To pass all monetary variables to US 2013 $
dollars = 2586.89



#%%Income 

lab9 = pd.read_stata(my_dirct+"GSEC8.dta")
lab9 = lab9[["HHID","PID","h8q30","h8q30b", "h8q31a","h8q31b","h8q31c","h8q44","h8q44_1","h8q45a","h8q45b","h8q45c"]]     
lab9.columns = ["hh","pid", "months1","weeks1", "cash1","inkind1", "time1","months2","weeks2", "cash2","inkind2", "time2"]



lab9["pay1"] = lab9.loc[:,["cash1","inkind1"]].sum(axis=1)
lab9["pay2"] = lab9.loc[:,["cash2","inkind2"]].sum(axis=1)
del lab9["cash1"], lab9["inkind1"], lab9["cash2"], lab9["inkind2"]


#Creating week wages
# From Besamuscka, Tijdens (2012),  https://wageindicator.org/main/Wageindicatorfoundation/publications/2012/wages-in-uganda-wage-indicator-survey-2012
# we take mean average hours and days worked per week: 60 and 6
lab9.loc[lab9.time1 == "Day", 'pay1'] = lab9.loc[lab9.time1 == "Day", 'pay1']*6
lab9.loc[lab9.time1 == "Month", 'pay1'] = lab9.loc[lab9.time1 == "Month", 'pay1']/4
lab9.loc[lab9.time1 == "Hour", 'pay1'] = lab9.loc[lab9.time1 == "Hour", 'pay1']*60

lab9.loc[lab9.time1 == "Day", 'pay2'] = lab9.loc[lab9.time1 == "Day", 'pay2']*6
lab9.loc[lab9.time1 == "Month", 'pay2'] = lab9.loc[lab9.time1 == "Month", 'pay2']/4
lab9.loc[lab9.time1 == "Hour", 'pay2'] = lab9.loc[lab9.time1 == "Hour", 'pay2']*60

#We don't have info about months and weeks worked. We use the sample mean of 2013-2014. Note that this can hidden important inequality on work time.
lab9["wage1"] = lab9.months1*lab9.weeks1*lab9.pay1
lab9["wage2"] = lab9.months2*lab9.weeks2*lab9.pay2


lab99 = lab9.groupby(by="hh")[["wage1","wage2"]].sum()
lab99["wage_total"] = lab99.loc[:,["wage1","wage2"]].sum(axis=1)
lab99= lab99.replace(0, np.nan)
summaryw = lab99.describe()/dollars
print(summaryw)

del lab9

#%% business

bus12 = pd.read_stata(my_dirct+'GSEC12.dta')
bus12 = bus12[["HHID","h12q12", "h12q13","h12q15","h12q16","h12q17"]]
bus12.rename(columns={'HHID':'hh'}, inplace=True)
bus12.rename(columns={'h12q13':'revenue'}, inplace=True)
bus12["cost"] = -bus12.loc[:,["h12q15","h12q16","h12q17"]].sum(axis=1)
bus12["bs_profit"] = bus12.loc[:,["revenue","cost"]].sum(axis=1)
bus12["bs_profit"] = bus12["bs_profit"].replace(0,np.nan)*bus12['h12q12']
bus12['bs_revenue'] = bus12['revenue'].replace(0,np.nan)*bus12['h12q12']
bus12 = bus12[["hh","bs_profit", 'bs_revenue']]
bus12 = bus12.groupby(by="hh").sum()
bus12 = bus12.replace(0, np.nan)

summarybus = bus12.describe()/dollars

print(summarybus)

#%% Other income

other = pd.read_stata(my_dirct+'GSEC11.dta', convert_categoricals=False)
other = other[["HHID",'h11q2',"h11q5","h11q6"]]
other.rename(columns={'HHID':'hh'}, inplace=True)
other= other.loc[(other['h11q2']!=11) & (other['h11q2']!=12) &(other['h11q2']!=13) ] 
other["other_inc"] = other.loc[:,["h11q5","h11q6"]].sum(axis=1)
other = other[["hh","other_inc"]]
other = other.groupby(by="hh").sum()
other = other
summaryo = other.describe()/dollars





#%% Merge datasets
income_gsec = pd.merge(lab99, bus12, on="hh", how="outer")
income_gsec = pd.merge(income_gsec, other, on="hh", how="outer")
del income_gsec["wage1"], income_gsec["wage2"], bus12, other, lab99, summarybus, summaryo, summaryw

sumlab = income_gsec[["wage_total","bs_profit", "other_inc"]].describe()/dollars
print(sumlab)

income_gsec.to_csv(folder+'income_hhsec_2010.csv')
