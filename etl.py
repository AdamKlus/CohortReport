import pandas as pd
import os, time
from bi import generateReports

def processFiles(file, file2):
    # get reports date
    filename = os.path.basename(file)
    reportDate = filename.split('.')[0].split('c_')[0][2:]

    # get revenue data
    df_customerReport = pd.read_csv(file)
    df_customerReport = df_customerReport.dropna(how="all")[['Customer Reference ID', 'Marketing Source Name', 'Total Net Revenue']]

    # get deposit data
    df_customerDeposits = pd.read_csv(file2)
    df_customerDeposits = df_customerDeposits.dropna(how="all")[['Total First Deposit Count']]

    #merge both together and add month column
    df_merged = pd.concat([df_customerReport, df_customerDeposits], axis=1)
    df_merged['Month'] = reportDate

    return df_merged

if __name__ == "__main__":

    # get the data folder
    folderPath = os.getcwd() + '\\data'
    processed_files = [] # nothing processed yet

    # create dataframes
    df_db = pd.DataFrame(columns = ['Customer Reference ID', 'Marketing Source Name', 'Total Net Revenue', 'Total First Deposit Count', 'Month'])
    df_mapping = pd.DataFrame(columns = ['DomainID', 'Name'])

    while True:
        # get list of files
        files = os.listdir(folderPath)
        
        # loop through files
        for file in files:
            # if not yet processed
            if file not in processed_files:
                
                # process mapping first
                for file2 in files:
                    if ('MarketingSourceMapping' in file2) and (file2 not in processed_files):
                        processed_files.append(file2)
                        df_temp = pd.read_csv(folderPath + "\\" + file2)  
                        # only unique
                        df_temp = df_temp[['DomainID', 'Name']].drop_duplicates()
                        # append to mapping db
                        df_mapping = df_mapping.append(df_temp)   
                        print(file2 + " added to mapping")  

                # we wait for Customer Report to process the month
                if 'CustomerReport' in file:
                    other_file = file.replace('CustomerReport', 'CustomerDeposits') 
                    # but if Deposit Report is not there do nothing
                    if os.path.exists(folderPath + "\\" + other_file):  
                        processed_files.append(file)
                        processed_files.append(other_file)
                        #process and append to db          
                        df_db = df_db.append(processFiles(folderPath + "\\" + file, folderPath + "\\" + other_file))
                        print(file + " added to db")
                        print(other_file + " added to db")
                    else:
                        continue
                    
                # #if all files processed generate the reports
                # if set(files).issubset(processed_files):     
                if generateReports(df_db, df_mapping) == True:
                    print("Checking for new files at " + folderPath)