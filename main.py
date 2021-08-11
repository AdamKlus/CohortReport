import pandas as pd
import os
import datetime

def processMapping(file):
        df = pd.read_csv(file)  
        df = df[['DomainID', 'Name']].drop_duplicates()
        return df

def processFiles(file):
    # get report name
    filename = os.path.basename(file)
    reportDate = filename.split('.')[0].split('c_')[0][2:]

    # get revenue data
    df_customerReport = pd.read_csv(file)
    df_customerReport = df_customerReport.dropna(how="all")[['Customer Reference ID', 'Marketing Source Name', 'Total Net Revenue']]

    # get deposit data
    other_file = file.replace('CustomerReport', 'CustomerDeposits')
    df_customerDeposits = pd.read_csv(other_file)
    df_customerDeposits = df_customerDeposits.dropna(how="all")[['Total First Deposit Count']]

    #merge both together and add month column
    df_merged = pd.concat([df_customerReport, df_customerDeposits], axis=1)
    df_merged['Month'] = reportDate

    return df_merged

def generateReports(df_db, df_mapping):
    # drop totals
    df_db = df_db.reset_index(drop=True)    
    df_db.drop(df_db.index[df_db['Customer Reference ID'] == 'Totals:'], inplace=True)

    # drop if no deposit and no revenue
    df_db.fillna(0,inplace=True)
    df_db.drop(df_db.index[(df_db['Total Net Revenue'] == 0) & (df_db['Total First Deposit Count'] == 0)], inplace=True)
    
    # apply mapping
    mapping = df_mapping.set_index('Name')['DomainID'].to_dict()
    df_db['Marketing Source Name'] = df_db['Marketing Source Name'].map(mapping)
    
    # get cohorts
    df_cohorts = df_db[['Customer Reference ID', 'Month', 'Marketing Source Name']]
    df_cohorts = df_cohorts[df_db['Total First Deposit Count']==1].drop_duplicates(subset='Customer Reference ID', keep='first')

    # get columns names and create reports dataframes
    timescale = df_db['Month'][1:].drop_duplicates().tolist()
    report_columns = []
    for monthsLater in range(1,len(timescale)):
        report_columns.append('Retained ' + str(monthsLater) + ' months later')
    df_deposit_report = pd.DataFrame(columns = ['Month', 'DomainID', 'First Time Depositing'] + report_columns)
    df_revenue_report = pd.DataFrame(columns = ['Month', 'DomainID', 'Total Net Revenue'] + report_columns)

    # set customer id as index for speed
    df_db = df_db.set_index('Customer Reference ID')
    
    #get values for the reports row by row
    for month in timescale:
        for domain in df_mapping['DomainID']:

            #get cohort for given domain and month
            df_cohort = df_cohorts.loc[(df_cohorts['Month'] == month) & (df_cohorts['Marketing Source Name'] == domain), 'Customer Reference ID']
            cohort = df_cohort.to_list()

            #get values for reports column by column
            # month and domain
            df_deposit_report.loc[df_deposit_report.shape[0], 'Month'] = month
            df_deposit_report.loc[df_deposit_report.shape[0]-1, 'DomainID'] = domain
            df_revenue_report.loc[df_revenue_report.shape[0], 'Month'] = month
            df_revenue_report.loc[df_revenue_report.shape[0]-1, 'DomainID'] = domain

            #first time depositing and total revenue
            df_temp = df_db.loc[cohort] # to limit search
            df_temp2 = df_temp.loc[(df_temp['Month'] == month) & (df_temp['Total First Deposit Count'] != 0)]
            df_deposit_report.loc[df_deposit_report.shape[0]-1, 'First Time Depositing'] = df_temp2.shape[0]
            df_revenue_report.loc[df_revenue_report.shape[0]-1, 'Total Net Revenue'] = df_temp2['Total Net Revenue'].sum()

            # retained months
            column = 3 #starting column
            start_month = timescale.index(month)
            for retainedMonth in timescale[start_month+1:]:
                df_temp2 = df_temp.loc[(df_temp['Month'] == retainedMonth) & (df_temp['Total Net Revenue'] != 0)]
                df_deposit_report.iloc[df_deposit_report.shape[0]-1, column] = df_temp2.shape[0]
                df_revenue_report.iloc[df_revenue_report.shape[0]-1, column] = df_temp2['Total Net Revenue'].sum()
                column = column + 1               
    
    # drop empty rows
    df_deposit_report.drop(df_deposit_report.index[df_deposit_report['First Time Depositing']==0], inplace=True)
    df_revenue_report.drop(df_revenue_report.index[df_revenue_report['Total Net Revenue']==0], inplace=True)

    # save reports
    df_deposit_report.to_csv(os.getcwd() + '\\reports\\DepositsReport_{}.csv'.format(datetime.date.today()), index=False)
    df_revenue_report.to_csv(os.getcwd() + '\\reports\\RevenueReport_{}.csv'.format(datetime.date.today()), index=False)

if __name__ == "__main__":

    # get the data folder
    folderPath = os.getcwd() + '\\data'
    processed_files = [] # nothing processed yet
    
    # create dataframes
    df_db = pd.DataFrame(columns = ['Customer Reference ID', 'Marketing Source Name', 'Total Net Revenue', 'Total First Deposit Count', 'Month'])
    df_mapping = pd.DataFrame(columns = ['DomainID'])

    while True:
        # get list of files
        files = os.listdir(folderPath)

        # process mapping first
        for file in files:
            if ('MarketingSourceMapping' in file) and (file not in processed_files):
                processed_files.append(file)
                df_mapping = df_mapping.append(processMapping(folderPath + "\\" + file))                
                
        # loop through files
        for file in files:
            # if not yet processed then process and add to processed list
            if file not in processed_files:
                processed_files.append(file)
                # we wait for Customer Report to process the month because it has domain name
                if 'CustomerReport' in file:                    
                    df_db = df_db.append(processFiles(folderPath + "\\" + file))
                    
                #if all files processed generate the reports
                if set(files).issubset(processed_files):
                    generateReports(df_db, df_mapping)
                

