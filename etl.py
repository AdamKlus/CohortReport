import pandas as pd
import time
import os
import glob
import sqlite3

def process_file(filepath):
    print(filepath + " added")
    time.sleep(3)

def getFiles(folderPath):
    # create a for loop to create a list of files and collect each filepath
    for root, dirs, files in os.walk(folderPath):
        # join the file path and roots with the subdirectories using glob
        file_path_list = glob.glob(os.path.join(root,'*'))
        file_path_list.sort()
        return file_path_list


if __name__ == "__main__":

    # Get the data folder
    folderPath = os.getcwd() + '/data'

    processed_files = []
    while True:
        files = getFiles(folderPath)
        for file in files:
            if file not in processed_files:
                process_file(file)
                processed_files.append(file)
