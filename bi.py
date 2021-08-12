import pandas as pd
import os
import datetime

def generateReports(df_db, df_mapping):
    if df_db.empty:
        print('No data available')

    else:
        # drop totals
        df_db = df_db.reset_index(drop=True)    
        df_db.drop(df_db.index[df_db['Customer Reference ID'] == 'Totals:'], inplace=True)

        # drop if no deposit and no revenue
        df_db.fillna(0,inplace=True)
        df_db.drop(df_db.index[(df_db['Total Net Revenue'] == 0) & (df_db['Total First Deposit Count'] == 0)], inplace=True)
        
        # apply mapping
        if df_mapping.empty: # if no mapping then do for all
            df_db['Marketing Source Name'] = 'All'
            domains = ['All']
        else:
            mapping = df_mapping.set_index('Name')['DomainID'].to_dict()
            df_db['Marketing Source Name'] = df_db['Marketing Source Name'].map(mapping)
            domains = list(mapping.values())
        
        # get cohorts
        df_cohorts = df_db[['Customer Reference ID', 'Month', 'Marketing Source Name']]
        # we want only firt occurence of customer id (month in which first time made deposit)
        df_cohorts = df_cohorts[df_db['Total First Deposit Count']==1].drop_duplicates(subset='Customer Reference ID', keep='first')

        # get columns names for reports (dynamic - depends on timescale of files) 
        timescale = df_db['Month'][1:].drop_duplicates().tolist()
        report_columns = []
        for monthsLater in range(1,len(timescale)):
            report_columns.append('Retained ' + str(monthsLater) + ' months later')

        # create reports dataframes
        df_deposit_report = pd.DataFrame(columns = ['Month', 'DomainID', 'First Time Depositing'] + report_columns)
        df_revenue_report = pd.DataFrame(columns = ['Month', 'DomainID', 'Total Net Revenue'] + report_columns)

        # set customer id as index for speed
        df_db = df_db.set_index('Customer Reference ID')
        
        #get values for the reports row by row
        for month in timescale:
            for domain in domains:

                #get cohort for given domain and month
                df_cohort = df_cohorts.loc[(df_cohorts['Month'] == month) & (df_cohorts['Marketing Source Name'] == domain), 'Customer Reference ID']
                cohort = df_cohort.to_list()

                #get values for reports column by column
                df_temp = df_db.loc[cohort] #temp table to limit search

                # month
                df_deposit_report.loc[df_deposit_report.shape[0], 'Month'] = month
                df_revenue_report.loc[df_revenue_report.shape[0], 'Month'] = month

                # domain
                df_deposit_report.loc[df_deposit_report.shape[0]-1, 'DomainID'] = domain          
                df_revenue_report.loc[df_revenue_report.shape[0]-1, 'DomainID'] = domain

                # first time depositing and revenue 
                df_temp2 = df_temp.loc[(df_temp['Month'] == month) & (df_temp['Total First Deposit Count'] != 0)] # firs time depositing  
                df_deposit_report.loc[df_deposit_report.shape[0]-1, 'First Time Depositing'] = df_temp2.shape[0] # count  
                df_revenue_report.loc[df_revenue_report.shape[0]-1, 'Total Net Revenue'] = df_temp2['Total Net Revenue'].sum() # ant theirs revenue

                # retained months
                column = 3 #starting column
                start_month = timescale.index(month)
                for retainedMonth in timescale[start_month+1:]: # check only folowing months

                    df_temp2 = df_temp.loc[(df_temp['Month'] == retainedMonth) & (df_temp['Total Net Revenue'] != 0)] # retained if made any revenue
                    df_deposit_report.iloc[df_deposit_report.shape[0]-1, column] = df_temp2.shape[0] # count
                    df_revenue_report.iloc[df_revenue_report.shape[0]-1, column] = df_temp2['Total Net Revenue'].sum() # ant theirs revenue

                    column = column + 1               
        
        # drop empty rows
        df_deposit_report.drop(df_deposit_report.index[df_deposit_report['First Time Depositing']==0], inplace=True)
        df_revenue_report.drop(df_revenue_report.index[df_revenue_report['Total Net Revenue']==0], inplace=True)

        # save reports
        deposit_path = os.getcwd() + '\\reports\\DepositsReport_{}.csv'.format(datetime.date.today())
        revenue_path = os.getcwd() + '\\reports\\RevenueReport_{}.csv'.format(datetime.date.today())
        df_deposit_report.to_csv(deposit_path, index=False)
        print(os.path.basename(deposit_path) + " generated")
        df_revenue_report.to_csv(revenue_path, index=False)
        print(os.path.basename(revenue_path)  + " generated")

    return True