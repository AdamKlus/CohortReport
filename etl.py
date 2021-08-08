import pandas as pd
import time
import os
import glob
import sqlite3

def process_file(filepath):
    print(filepath + " added")
    time.sleep(3)

def getFiles(folderPath):
    # loop through files
    for root, dirs, files in os.walk(folderPath):
        # join the file path and roots with the subdirectories
        file_path_list = glob.glob(os.path.join(root,'*'))
        # sort so we process older files first
        file_path_list.sort()

        return file_path_list

if __name__ == "__main__":
    # get the data folder
    folderPath = os.getcwd() + '/data'
    # nothing processed yet
    processed_files = []
    while True:
        #get list of files
        files = getFiles(folderPath)
        # loop through files
        for file in files:
            # if not yet processed then process and add to processed list
            if file not in processed_files:
                process_file(file)
                processed_files.append(file)
