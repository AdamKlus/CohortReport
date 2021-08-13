import pandas as pd
import os
from bi import generateReports

def processFiles(files):
    # get reports date
    filename = os.path.basename(files[0])
    reportDate = filename.split('.')[0].split('c_')[0][2:]

    # get deposit data
    df_customerDeposits = pd.read_csv(files[0])
    df_customerDeposits = df_customerDeposits.dropna(how="all")[['Total First Deposit Count']]

    # get revenue data
    df_customerReport = pd.read_csv(files[1])
    df_customerReport = df_customerReport.dropna(how="all")[['Customer Reference ID', 'Marketing Source Name', 'Total Net Revenue']]

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
                        if generateReports(df_db, df_mapping) == True:
                            print("Checking for new files at " + folderPath)

                #then data files
                if file not in processed_files:
                    if 'CustomerReport' in file:
                        other_file = file.replace('CustomerReport', 'CustomerDeposits')
                    elif 'CustomerDeposits' in file:
                        other_file = file.replace('CustomerDeposits', 'CustomerReport')
                    
                    # we wait for both files to process the month
                    if os.path.exists(folderPath + "\\" + other_file):  
                        processed_files.append(file)
                        processed_files.append(other_file)
                        #process and append to db    
                        sorted_files = [folderPath + "\\" + file, folderPath + "\\" + other_file]
                        sorted_files.sort() # deposit first    
                        df_db = df_db.append(processFiles(sorted_files))
                        print(file + " added to db")
                        print(other_file + " added to db")
    
                        if generateReports(df_db, df_mapping) == True:
                            print("Checking for new files at " + folderPath)