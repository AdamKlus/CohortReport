When run etl.py the app will generate 2 csv files with current date in the name.
It is running in loop so when new files are added it will generate reports automatically.

If there is no mapping file it will generate reports for all domains.
If there is no data files it will do nothing.
If there is missing month in the data the report will be generated but with a bit misleading column names.