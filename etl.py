import pandas as pd
import os
import glob

def main():
    # Get your current folder and subfolder event data
    filepath = os.getcwd() + '/data'
    # Create a for loop to create a list of files and collect each filepath
    for root, dirs, files in os.walk(filepath):
        # join the file path and roots with the subdirectories using glob
        file_path_list = glob.glob(os.path.join(root,'*'))
        print(file_path_list)
        
if __name__ == "__main__":
    main()